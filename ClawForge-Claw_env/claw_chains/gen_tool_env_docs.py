"""Generate ``tool_env_docs`` for claw envs in the reference function-tool format.

Reference shape (one JSON array per env, see
``30clawenv/tool_env_docs/cross_modal_transcription__pipeline.json``)::

    [
      {
        "name": "add_media_source",
        "description": "Register a new media source.",
        "parameters": {
          "type": "dict",
          "properties": {
            "name": {"type": "string", "description": "Unique source identifier"},
            ...
          },
          "required": ["name", "source_type"]
        },
        "response": {"type": "dict", "properties": {}}
      },
      ...
    ]

This is the claw analogue of the generic pipeline's per-env tool docs. Both the
shared L1 scaffold tools and the env's L2 CLI verbs are emitted as function
entries (L2 verb names use the ``action`` form, e.g. ``generate_retention_email``,
so they line up with evaluator ``required_actions``).

LLM usage mirrors the generic pipeline: where a verb/arg has no ``help`` text we
ask the LLM to write a concise description (this is the same role
``_fill_env_docs_via_llm`` plays in ``gen_chains/generate_graphs.py``). When the
LLM is unavailable we fall back to the ``help`` text or a templated description,
so the docs are always produced.

Output: ``tool_env_docs/<env>.json`` (+ ``tool_env_docs/_scaffold.json``).

Usage:
    python gen_tool_env_docs.py                  # all envs
    python gen_tool_env_docs.py --env post_mails
    python gen_tool_env_docs.py --no-llm         # force deterministic descriptions
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from llm_client import llm_json, llm_available

log = logging.getLogger("gen_tool_env_docs")

HERE = Path(__file__).resolve().parent
DOCS_DIR = HERE / "claw_tool_env_docs"
OUT_DIR = HERE / "tool_env_docs"

_TYPE_MAP = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}


# ── LLM enrichment (mirrors generic _fill_env_docs_via_llm) ──────────────

PROMPT_DESCRIBE = """You are documenting the CLI tools of an agentic training environment.
For each tool below, write a concise one-sentence English description of what it does,
and a <=8-word description for each of its parameters. Base it on the verb name,
the env summary, and any hint text provided. Do NOT invent parameters.

### Environment
{{ENV_NAME}} — {{ENV_DES}}

### Tools (JSON)
{{TOOLS}}

### Output JSON (exact shape)
{
  "tools": {
    "<tool_name>": {
      "description": "one sentence",
      "params": { "<param_name>": "short description", ... }
    },
    ...
  }
}
Only include tools/params present in the input."""


def _enrich_via_llm(env_name: str, env_des: str,
                    skeleton: list[dict[str, Any]]) -> dict[str, Any]:
    """Ask the LLM for descriptions of tools/params that lack help text."""
    need = []
    for t in skeleton:
        missing_params = [p for p, meta in t["_param_help"].items() if not meta]
        if not t["description"] or missing_params:
            need.append({
                "name": t["name"],
                "current_description": t["description"],
                "params_needing_desc": missing_params,
                "all_params": list(t["_param_help"].keys()),
            })
    if not need:
        return {}
    prompt = (PROMPT_DESCRIBE
              .replace("{{ENV_NAME}}", env_name)
              .replace("{{ENV_DES}}", env_des or env_name)
              .replace("{{TOOLS}}", json.dumps(need, ensure_ascii=False)))
    out = llm_json(prompt)
    if not out or "tools" not in out:
        return {}
    return out["tools"]


# ── deterministic fallback descriptions ──────────────────────────────────

def _fallback_verb_desc(verb: str, help_text: str) -> str:
    if help_text:
        return help_text
    pretty = verb.replace("-", " ").replace("_", " ")
    return f"{pretty[:1].upper()}{pretty[1:]}."


def _fallback_param_desc(name: str, help_text: str, required: bool) -> str:
    if help_text:
        return help_text
    base = name.lstrip("-").replace("-", " ")
    return ("" if required else "[Optional] ") + base


# ── builders ─────────────────────────────────────────────────────────────

def _arg_to_property(arg: dict[str, Any]) -> dict[str, Any]:
    prop: dict[str, Any] = {"type": _TYPE_MAP.get(arg.get("type", "str"), "string")}
    prop["description"] = ""  # filled later
    if arg.get("choices"):
        prop["enum"] = arg["choices"]
    if arg.get("has_default") and arg.get("default") is not None:
        prop["default"] = arg["default"]
    return prop


def build_l2_tool_skeletons(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """One function-tool skeleton per visible L2 verb (action-named)."""
    tools = []
    for v in doc["visible_verbs"]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        param_help: dict[str, str] = {}
        for a in v["args"]:
            pname = a["name"].lstrip("-").replace("-", "_")
            properties[pname] = _arg_to_property(a)
            param_help[pname] = a.get("help", "")
            if a.get("required"):
                required.append(pname)
        tools.append({
            "name": v["action"],
            "description": v.get("help", ""),
            "parameters": {"type": "dict", "properties": properties, "required": required},
            "response": {"type": "dict", "properties": {}},
            # private scratch fields, stripped before write
            "_param_help": param_help,
            "_verb": v["verb"],
        })
    return tools


def build_l1_tool_docs(scaffold: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render shared L1 scaffold tools into the reference format from their
    registry JSON schema."""
    tools = []
    for t in scaffold:
        params = t.get("parameters", {}) or {}
        props = params.get("properties", {})
        tools.append({
            "name": t["name"],
            "description": t.get("description", "") or f"Scaffold tool: {t['name']}.",
            "parameters": {
                "type": "dict",
                "properties": props,
                "required": params.get("required", []),
            },
            "response": {"type": "dict", "properties": {}},
        })
    return tools


def finalize(skeletons: list[dict[str, Any]], enrich: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for t in skeletons:
        name = t["name"]
        e = enrich.get(name, {})
        desc = e.get("description") or _fallback_verb_desc(t["_verb"], t["description"])
        params_desc = e.get("params", {})
        for pname, prop in t["parameters"]["properties"].items():
            required = pname in t["parameters"]["required"]
            prop["description"] = (params_desc.get(pname)
                                   or _fallback_param_desc(pname, t["_param_help"].get(pname, ""), required))
        out.append({
            "name": name,
            "description": desc,
            "parameters": t["parameters"],
            "response": t["response"],
        })
    return out


def process_env(doc_path: Path, scaffold: list[dict[str, Any]], use_llm: bool) -> list[dict[str, Any]]:
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    env_des = _read_env_des(doc)
    skeletons = build_l2_tool_skeletons(doc)
    enrich = _enrich_via_llm(doc["env_name"], env_des, skeletons) if use_llm else {}
    l2 = finalize(skeletons, enrich)
    # L1 scaffold tools are shared; emit alongside so each env's doc is
    # self-contained (matches the reference, which lists every callable tool).
    l1 = build_l1_tool_docs(scaffold)
    return l1 + l2


def _read_env_des(doc: dict[str, Any]) -> str:
    """Best-effort env description from README or the verbs themselves."""
    rel = doc.get("rel_path", "")
    readme = (HERE.parent / rel / "README.md")
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return s[:300]
    return doc["env_name"].replace("_", " ")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env", help="single env name")
    p.add_argument("--no-llm", action="store_true", help="skip LLM, deterministic only")
    args = p.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scaffold_path = DOCS_DIR / "_scaffold_tools.json"
    scaffold = json.loads(scaffold_path.read_text(encoding="utf-8")) if scaffold_path.exists() else []

    # write shared L1 docs once for reference
    (OUT_DIR / "_scaffold.json").write_text(
        json.dumps(build_l1_tool_docs(scaffold), ensure_ascii=False, indent=1),
        encoding="utf-8")

    use_llm = (not args.no_llm) and llm_available()
    log.info("LLM enrichment: %s", "ON" if use_llm else "OFF (deterministic)")

    doc_files = sorted(f for f in DOCS_DIR.glob("*.json") if f.stem != "_scaffold_tools")
    if args.env:
        doc_files = [f for f in doc_files if f.stem == args.env]
        if not doc_files:
            log.error("no extracted doc for --env %s; run extract_claw_tools.py first", args.env)
            return 1

    n = 0
    for f in doc_files:
        tools = process_env(f, scaffold, use_llm)
        out = OUT_DIR / f"{f.stem}.json"
        out.write_text(json.dumps(tools, ensure_ascii=False, indent=1), encoding="utf-8")
        log.info("%-34s tools=%d (L1=%d L2=%d)", f.stem, len(tools),
                 len(scaffold), len(tools) - len(scaffold))
        n += 1

    print(f"\nDone. tool_env_docs: {n} envs -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
