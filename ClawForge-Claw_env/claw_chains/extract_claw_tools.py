"""Stage A — Extract the two-layer tool surface for claw-style training envs.

This is the claw analogue of ``gen_chains/generate_graphs.py``. The key
difference: a claw env does NOT expose free-standing function tools. The agent
sees two layers:

  L1  scaffold tools (read/write/edit/ls/find/grep/execute_bash/finish/...)
      shared by every env, taken from ``uni_agent.tools`` registry.
  L2  the env's own CLI verbs (``list-customers``/``get-customer``/...),
      invoked *through* ``execute_bash``. Parsed from each env's ``cli.py``.

Unlike the generic pipeline, claw dependencies do not need to be guessed by an
LLM: ``cli.py`` argument requirements + ``evaluator.py``/scenario metadata
already pin the data flow and the gold workflow. We extract those signals here
deterministically.

Output: ``claw_tool_env_docs/<env>.json`` per env, plus a shared
``claw_tool_env_docs/_scaffold_tools.json`` for the L1 layer.

Usage:
    python extract_claw_tools.py                       # every discovered env
    python extract_claw_tools.py --env churn_retention_mail_env
    python extract_claw_tools.py --roots without_skill .   # custom search roots
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("extract_claw_tools")

# claw_envs/ root (parent of this file's directory)
CLAW_ROOT = Path(__file__).resolve().parent.parent
# repo root that contains the ``uni_agent`` package
REPO_ROOT = CLAW_ROOT.parent
OUT_DIR = Path(__file__).resolve().parent / "claw_tool_env_docs"

# Scaffold tools the agent always has, regardless of env. Registry names.
SCAFFOLD_TOOL_NAMES = [
    "read", "write", "edit", "str_replace_editor",
    "ls", "find", "grep", "execute_bash", "finish",
]

# Verbs that are trainer-only plumbing even when not marked SUPPRESS.
TRAINER_VERB_HINTS = (
    "prepare-rollout", "create-session", "reset-rollout", "reset-session",
)

# Heuristic role tags for L2 verbs, used downstream for L1<->L2 bridging.
READ_VERB_PREFIXES = ("list-", "get-", "view-", "read-", "show-", "inspect-", "search-")
WRITE_VERB_PREFIXES = (
    "generate-", "create-", "publish-", "reply-", "save-", "write-", "update-",
    "record-", "archive-", "store-", "dispatch-", "approve-", "label-",
    "schedule-", "provision-", "recover-", "compute-", "draft-",
)


# ── L1 scaffold layer ────────────────────────────────────────────────────

def extract_scaffold_tools() -> list[dict[str, Any]]:
    """Pull L1 tool schemas from the uni_agent registry.

    Falls back to a static stub list if the package can't be imported (e.g.
    extraction is run outside the training venv). The stub keeps the rest of
    the pipeline functional; only the JSON-schema detail is lost.
    """
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        from uni_agent.tools.registry import get_tool  # noqa: WPS433

        tools = []
        for name in SCAFFOLD_TOOL_NAMES:
            try:
                schema = get_tool(name).get_tool_schema()
                fn = schema.get("function", schema)
                tools.append({
                    "name": name,
                    "layer": "scaffold",
                    "description": fn.get("description", ""),
                    "parameters": fn.get("parameters", {}),
                })
            except Exception as exc:  # unknown/optional tool
                log.warning("  scaffold tool %s unavailable: %s", name, exc)
        if tools:
            return tools
    except Exception as exc:
        log.warning("Could not import uni_agent registry (%s); using stubs", exc)

    return [{"name": n, "layer": "scaffold", "description": "", "parameters": {}}
            for n in SCAFFOLD_TOOL_NAMES]


# ── L2 CLI layer (AST over cli.py) ───────────────────────────────────────

class _CliParserVisitor(ast.NodeVisitor):
    """Collect ``subparsers.add_parser(...)`` and the ``.add_argument`` calls
    attached to each returned parser variable.

    Handles the canonical claw shape::

        sub = parser.add_subparsers(...)
        sub.add_parser("task", parents=[...])
        cmd = sub.add_parser("get-customer", parents=[...])
        cmd.add_argument("--customer-id", required=True, type=str)
    """

    def __init__(self) -> None:
        self.subparser_objs: set[str] = set()
        # verb -> {"hidden": bool, "args": [ {name, required, has_default} ]}
        self.verbs: dict[str, dict[str, Any]] = {}
        # maps a local variable name -> verb it holds (from add_parser return)
        self._var_to_verb: dict[str, str] = {}

    # ---- detect ``X = <something>.add_subparsers(...)`` -----------------
    def visit_Assign(self, node: ast.Assign) -> None:
        call = node.value
        if isinstance(call, ast.Call) and _attr_name(call.func) == "add_subparsers":
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    self.subparser_objs.add(tgt.id)
        elif isinstance(call, ast.Call) and _attr_name(call.func) == "add_parser":
            verb = self._record_add_parser(call)
            if verb:
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        self._var_to_verb[tgt.id] = verb
        self.generic_visit(node)

    # ---- detect bare ``sub.add_parser("task", ...)`` (no assignment) ----
    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Call):
            fname = _attr_name(node.value.func)
            if fname == "add_parser":
                self._record_add_parser(node.value)
        # add_argument is handled solely by visit_Call (reached via
        # generic_visit) to avoid double-recording the same call node.
        self.generic_visit(node)

    # ---- also catch ``<var>.add_argument(...)`` in Assign/Expr bodies ---
    def visit_Call(self, node: ast.Call) -> None:
        if _attr_name(node.func) == "add_argument":
            self._record_add_argument(node)
        self.generic_visit(node)

    def _record_add_parser(self, call: ast.Call) -> Optional[str]:
        # receiver must be a known subparsers object (best-effort)
        recv = _receiver_name(call.func)
        if self.subparser_objs and recv not in self.subparser_objs:
            # still accept if we never resolved the subparsers var
            pass
        if not call.args:
            return None
        verb = _str_const(call.args[0])
        if verb is None:
            return None
        hidden = _has_suppress_help(call)
        aliases = _aliases(call)
        help_text = _help_str(call)
        entry = self.verbs.setdefault(
            verb, {"hidden": False, "args": [], "aliases": [], "help": ""})
        entry["hidden"] = entry["hidden"] or hidden
        entry["aliases"] = aliases
        if help_text:
            entry["help"] = help_text
        return verb

    def _record_add_argument(self, call: ast.Call) -> None:
        recv = _receiver_name(call.func)
        verb = self._var_to_verb.get(recv)
        if verb is None or not call.args:
            return
        argname = _str_const(call.args[0])
        if argname is None or not argname.startswith("--"):
            return
        required = False
        has_default = False
        default_val = None
        type_name = "str"
        choices: list[str] = []
        suppressed = _has_suppress_help(call)
        for kw in call.keywords:
            if kw.arg == "required":
                required = bool(getattr(kw.value, "value", False))
            if kw.arg == "default":
                if isinstance(kw.value, ast.Constant):
                    default_val = kw.value.value
                    has_default = kw.value.value is not None
            if kw.arg == "type" and isinstance(kw.value, ast.Name):
                type_name = kw.value.id  # int/str/float
            if kw.arg == "action" and _str_const(kw.value) in ("store_true", "store_false"):
                type_name = "bool"
            if kw.arg == "choices" and isinstance(kw.value, (ast.List, ast.Tuple)):
                choices = [v for v in (_str_const(e) for e in kw.value.elts) if v]
        self.verbs[verb]["args"].append({
            "name": argname,
            "required": required,
            "has_default": has_default,
            "default": default_val,
            "type": type_name,
            "choices": choices,
            "help": _help_str(call),
            "hidden": suppressed,
        })


def _attr_name(func: ast.AST) -> Optional[str]:
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _receiver_name(func: ast.AST) -> Optional[str]:
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id
    return None


def _str_const(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _help_str(call: ast.Call) -> str:
    for kw in call.keywords:
        if kw.arg == "help":
            s = _str_const(kw.value)
            if s:
                return s
    return ""


def _has_suppress_help(call: ast.Call) -> bool:
    for kw in call.keywords:
        if kw.arg == "help":
            # argparse.SUPPRESS is an Attribute; treat any non-str help that
            # references SUPPRESS as hidden.
            src = ast.dump(kw.value)
            if "SUPPRESS" in src:
                return True
    return False


def _aliases(call: ast.Call) -> list[str]:
    for kw in call.keywords:
        if kw.arg == "aliases" and isinstance(kw.value, (ast.List, ast.Tuple)):
            return [v for v in (_str_const(e) for e in kw.value.elts) if v]
    return []


def _verbs_from_file(path: Path) -> dict[str, dict[str, Any]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("  cannot parse %s: %s", path, exc)
        return {}
    visitor = _CliParserVisitor()
    visitor.visit(tree)
    return visitor.verbs


# Shared CLI factory modules: ``from ..._shared.<mod> import <factory>``.
# Some envs (e.g. the *_guard_env family) define no parser locally and instead
# delegate to a factory in ``_shared``. We follow that import to recover verbs.
_SHARED_IMPORT_RE = re.compile(
    r"from\s+[\w.]*_shared\.(?P<mod>\w+)\s+import\s+(?P<names>[\w,\s]+)")


def _resolve_shared_cli_files(cli_path: Path) -> list[Path]:
    """Return shared ``_shared/<mod>.py`` files imported by an env's cli.py that
    look like CLI builders (name contains 'cli')."""
    text = cli_path.read_text(encoding="utf-8")
    shared_dir = CLAW_ROOT / "without_skill" / "_shared"
    files: list[Path] = []
    for m in _SHARED_IMPORT_RE.finditer(text):
        mod = m.group("mod")
        if "cli" not in mod.lower():
            continue
        cand = shared_dir / f"{mod}.py"
        if cand.exists():
            files.append(cand)
    return files


def extract_cli_verbs(cli_path: Path) -> dict[str, dict[str, Any]]:
    """Return ``{verb: {hidden, args, aliases}}`` for an env, following any
    delegation to a shared ``_shared`` CLI factory when the local cli.py builds
    no parser of its own."""
    verbs = _verbs_from_file(cli_path)
    if not verbs:
        for shared_file in _resolve_shared_cli_files(cli_path):
            shared_verbs = _verbs_from_file(shared_file)
            if shared_verbs:
                log.info("  %s: verbs resolved via shared %s",
                         cli_path.parent.name, shared_file.name)
                verbs.update(shared_verbs)
    return verbs


def extract_env_var_bindings(cli_path: Path) -> dict[str, Optional[str]]:
    """Best-effort recovery of the SESSION/STATE/SCENARIO env-var names and the
    default scenario id, covering both the explicit-constant and inline-string
    styles seen across claw envs.
    """
    text = cli_path.read_text(encoding="utf-8")
    bindings: dict[str, Optional[str]] = {
        "session_env": None, "state_env": None, "scenario_env": None,
        "default_scenario_id": None,
    }

    def _find(patterns: list[str]) -> Optional[str]:
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1)
        return None

    bindings["session_env"] = _find([
        r'SESSION[_A-Z]*\s*=\s*"([A-Z0-9_]*SESSION_ID)"',
        r'session_env_var\s*=\s*"([A-Z0-9_]*SESSION_ID)"',
        r'getenv\(\s*"([A-Z0-9_]*SESSION_ID)"',
        r'environ(?:\.get)?\(\s*"([A-Z0-9_]*SESSION_ID)"',
        r'"([A-Z0-9_]*SESSION_ID)"',
    ])
    bindings["state_env"] = _find([
        r'STATE[_A-Z]*\s*=\s*"([A-Z0-9_]*STATE_ROOT)"',
        r'state_root_env_var\s*=\s*"([A-Z0-9_]*STATE_ROOT)"',
        r'"([A-Z0-9_]*STATE_ROOT)"',
    ])
    bindings["scenario_env"] = _find([
        r'SCENARIO[_A-Z]*\s*=\s*"([A-Z0-9_]*SCENARIO_ID)"',
        r'scenario_env_var\s*=\s*"([A-Z0-9_]*SCENARIO_ID)"',
        r'"([A-Z0-9_]*SCENARIO_ID)"',
    ])
    bindings["default_scenario_id"] = _find([
        r'DEFAULT_SCENARIO_ID\s*=\s*"([^"]+)"',
    ])
    return bindings


# ── evaluator + scenario signals ─────────────────────────────────────────

# scenario keys we treat as gold-fact anchors (do not mutate blindly downstream)
_ANCHOR_KEY_RE = re.compile(r"^(target_|expected_|deny_|required_|forbidden_)")


def extract_scenario_signals(scenario_dir: Path) -> dict[str, Any]:
    """Read every scenario JSON and union their structural signals: which keys
    act as anchors, the ``required_actions`` sequences, and the raw scenarios.
    """
    scenarios: list[dict[str, Any]] = []
    anchor_keys: set[str] = set()
    required_actions_by_scn: dict[str, list[str]] = {}
    if scenario_dir.is_dir():
        for f in sorted(scenario_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception as exc:
                log.warning("  bad scenario %s: %s", f.name, exc)
                continue
            scenarios.append(data)
            for k in data:
                if _ANCHOR_KEY_RE.match(k):
                    anchor_keys.add(k)
            sid = str(data.get("scenario_id", f.stem))
            ra = data.get("required_actions")
            if isinstance(ra, list):
                required_actions_by_scn[sid] = [str(x) for x in ra]
    return {
        "scenarios": scenarios,
        "anchor_keys": sorted(anchor_keys),
        "required_actions_by_scenario": required_actions_by_scn,
    }


def extract_evaluator_dims(evaluator_path: Path) -> dict[str, Any]:
    """Lightweight scan of evaluator.py to label which scoring dimensions exist
    and whether the env penalizes forbidden behavior (guard envs). Follows a
    ``from ..._shared.<mod> import evaluate_session`` delegation."""
    if not evaluator_path.is_file():
        return {"dimensions": [], "has_forbidden_penalty": False}
    text = evaluator_path.read_text(encoding="utf-8")
    # follow shared evaluator delegation
    m = re.search(r"from\s+[\w.]*_shared\.(\w+)\s+import\s+.*evaluate", text)
    if m:
        shared = CLAW_ROOT / "without_skill" / "_shared" / f"{m.group(1)}.py"
        if shared.exists():
            text = shared.read_text(encoding="utf-8")
    dims = []
    for token in ("required_action_score", "retrieval_score", "artifact_score",
                  "reply_score", "order_score", "penalty", "decision_score",
                  "deny_score", "audit_score"):
        if token in text:
            dims.append(token)
    has_forbidden = bool(re.search(r"forbidden|penalt|deny|impersonat|block", text))
    return {"dimensions": dims, "has_forbidden_penalty": has_forbidden}


# ── verb role tagging + dataflow edges ───────────────────────────────────

def tag_verb_role(verb: str, args: list[dict[str, Any]]) -> str:
    if any(p in verb for p in ("guard", "deny", "block", "reject")):
        return "guard"
    if verb.startswith(WRITE_VERB_PREFIXES):
        return "produce"
    if verb.startswith(READ_VERB_PREFIXES):
        return "read"
    return "other"


_ID_ARG_RE = re.compile(r"^--(?P<entity>[a-z0-9]+(?:-[a-z0-9]+)*)-id$")


def _entity_of_id_arg(argname: str) -> Optional[str]:
    m = _ID_ARG_RE.match(argname)
    return m.group("entity") if m else None


def build_dataflow_edges(verbs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive ``produces_id_for`` edges with zero LLM guessing.

    A verb that *requires* ``--<entity>-id`` consumes an id that some list/get
    verb of the same entity produces. We connect the producer (a read verb
    whose name mentions the entity, taking no required id of that entity) to the
    consumer.
    """
    edges: list[dict[str, Any]] = []
    # producers: read verbs that surface ids of an entity (heuristic: entity
    # token appears in verb name and the verb has no required id arg)
    consumers: dict[str, list[str]] = {}  # entity -> [consumer verbs]
    for verb, meta in verbs.items():
        if meta.get("hidden"):
            continue
        for a in meta["args"]:
            if a.get("hidden") or not a.get("required"):
                continue
            ent = _entity_of_id_arg(a["name"])
            if ent:
                consumers.setdefault(ent, []).append(verb)

    for entity, consumer_verbs in consumers.items():
        # find producers: visible verbs mentioning the entity that do NOT
        # require that entity's id themselves
        producers = []
        ent_token = entity.replace("-", "")
        for verb, meta in verbs.items():
            if meta.get("hidden"):
                continue
            requires_same = any(
                not a.get("hidden") and a.get("required")
                and _entity_of_id_arg(a["name"]) == entity
                for a in meta["args"]
            )
            if requires_same:
                continue
            vtoken = verb.replace("-", "")
            if ent_token in vtoken or entity in verb:
                producers.append(verb)
        for p in producers:
            for c in consumer_verbs:
                if p == c:
                    continue
                edges.append({
                    "src": p, "dst": c, "weight": 0.8,
                    "relationship": f"produces_{entity}_id_for",
                })
    # dedupe (same src,dst,relationship can arise from overlapping entities)
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for e in edges:
        key = (e["src"], e["dst"], e["relationship"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


# ── per-env driver ───────────────────────────────────────────────────────

def discover_envs(roots: list[Path]) -> list[Path]:
    """Return env package dirs (those containing both cli.py and evaluator.py)."""
    found: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for cli in root.glob("*/cli.py"):
            env_dir = cli.parent
            if env_dir in seen:
                continue
            if (env_dir / "evaluator.py").exists():
                seen.add(env_dir)
                found.append(env_dir)
    return sorted(found, key=lambda p: p.name)


def process_env(env_dir: Path) -> dict[str, Any]:
    name = env_dir.name
    rel = env_dir.relative_to(CLAW_ROOT)
    cli_path = env_dir / "cli.py"

    verbs = extract_cli_verbs(cli_path)
    bindings = extract_env_var_bindings(cli_path)
    scn = extract_scenario_signals(env_dir / "data" / "scenarios")
    eval_dims = extract_evaluator_dims(env_dir / "evaluator.py")

    visible, hidden = [], []
    for verb, meta in sorted(verbs.items()):
        is_hidden = meta.get("hidden") or verb in TRAINER_VERB_HINTS or \
            any(a in TRAINER_VERB_HINTS for a in meta.get("aliases", []))
        record = {
            "verb": verb,
            "action": verb.replace("-", "_"),  # evaluator/required_actions form
            "role": tag_verb_role(verb, meta["args"]),
            "help": meta.get("help", ""),
            "args": [a for a in meta["args"] if not a.get("hidden")],
            "aliases": meta.get("aliases", []),
        }
        (hidden if is_hidden else visible).append(record)

    dataflow = build_dataflow_edges(verbs)

    # module-as-package import path, e.g. without_skill.churn_retention_mail_env.cli
    module_path = ".".join(rel.parts)

    return {
        "env_name": name,
        "rel_path": str(rel).replace("\\", "/"),
        "cli_module": f"{module_path}.cli",
        "has_skill_md": (env_dir / "SKILL.md").exists(),
        "bindings": bindings,
        "visible_verbs": visible,
        "hidden_verbs": hidden,
        "dataflow_edges": dataflow,
        "gold_actions_by_scenario": scn["required_actions_by_scenario"],
        "anchor_keys": scn["anchor_keys"],
        "evaluator": eval_dims,
        "scenario_ids": [str(s.get("scenario_id", "")) for s in scn["scenarios"]],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env", help="single env name to process")
    p.add_argument("--roots", nargs="*", default=["without_skill", "."],
                   help="search roots under claw_envs/ (default: without_skill .)")
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # L1 scaffold layer — shared, written once.
    scaffold = extract_scaffold_tools()
    (OUT_DIR / "_scaffold_tools.json").write_text(
        json.dumps(scaffold, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("scaffold tools: %d -> _scaffold_tools.json", len(scaffold))

    roots = [(CLAW_ROOT / r).resolve() for r in args.roots]
    env_dirs = discover_envs(roots)
    if args.env:
        env_dirs = [d for d in env_dirs if d.name == args.env]
        if not env_dirs:
            log.error("no env matching --env %s", args.env)
            return 1

    n_ok = 0
    for env_dir in env_dirs:
        try:
            doc = process_env(env_dir)
        except Exception as exc:
            log.warning("FAILED %s: %s", env_dir.name, exc)
            continue
        out = OUT_DIR / f"{doc['env_name']}.json"
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("%-34s skill=%-5s verbs=%2d hidden=%2d edges=%2d scenarios=%d",
                 doc["env_name"], doc["has_skill_md"], len(doc["visible_verbs"]),
                 len(doc["hidden_verbs"]), len(doc["dataflow_edges"]),
                 len(doc["scenario_ids"]))
        n_ok += 1

    print(f"\nDone. Envs documented: {n_ok}/{len(env_dirs)}  ->  {OUT_DIR}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
