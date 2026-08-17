"""Stage B: build claw tool graphs with deterministic constraints plus LLM plans.

The claw pipeline has two sources of signal:

1. Deterministic constraints recovered from code and scenarios.
   - dataflow edges from required ``--<entity>-id`` arguments
   - gold sequence edges from scenario ``required_actions``
   - scaffold bridge edges between L1 scaffold tools and L2 CLI verbs

2. Semantic workflow hints that are hard to recover with simple rules.
   - cross-entity read/read or read/write follow-ups
   - verification reads after state-changing actions
   - entry-point reads that make sampled chains look more realistic

The generic reference pipeline in ``ref/`` lets the LLM build most of the
semantic graph. This claw version keeps deterministic edges as the authority,
then layers an LLM-generated semantic edge plan and sampling hints on top. The
LLM output is cached as structured JSON instead of executable code.

Output: ``claw_tool_graphs/<env>_tool_graph.json`` in NetworkX node-link format.

Usage:
    python build_claw_graph.py
    python build_claw_graph.py --env churn_retention_mail_env
    python build_claw_graph.py --no-llm
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

import networkx as nx
from networkx.readwrite import json_graph as nx_json_graph

from llm_client import llm_available, llm_json, llm_text

log = logging.getLogger("build_claw_graph")

HERE = Path(__file__).resolve().parent
DOCS_DIR = HERE / "claw_tool_env_docs"
OUT_DIR = HERE / "claw_tool_graphs"
CACHE_DIR = HERE / "claw_graph_plan_cache"

SCAFFOLD_FILTER = ["grep", "find"]
SCAFFOLD_WRITE = ["write", "edit"]
SCAFFOLD_READ = "read"
SCAFFOLD_FINISH = "finish"
ENTRY_ACTION = "task"

PATTERN_ALIASES = {
    "minimal": "minimal_gold",
    "minimal_gold": "minimal_gold",
    "gold_only": "minimal_gold",
    "inspect_then_act": "investigate_then_act",
    "investigate_then_act": "investigate_then_act",
    "search_then_filter": "search_then_filter",
    "verify_before_commit": "verify_before_commit",
    "double_check_before_commit": "verify_before_commit",
    "audit_then_decide": "audit_then_decide",
    "audit_before_decision": "audit_then_decide",
    "persist_and_submit": "persist_and_submit",
    "report_then_submit": "persist_and_submit",
}
ALLOWED_PATTERNS = {
    "minimal_gold",
    "investigate_then_act",
    "search_then_filter",
    "verify_before_commit",
    "audit_then_decide",
    "persist_and_submit",
}

PROMPT_SEMANTIC_PLAN = """You are designing a semantic tool-dependency plan for a claw-style
agent environment.

The deterministic graph already contains:
- strong dataflow edges from required IDs
- strong gold workflow edges from required_actions
- fixed scaffold bridge edges

Your job is to add semantic L2->L2 edges and a few sampling hints so the final
tool chains are more realistic and diverse.

### Environment
{{ENV_NAME}} - {{ENV_DES}}

### Visible CLI verbs (JSON)
{{VERBS_JSON}}

### Existing deterministic edges (JSON)
{{STRONG_EDGES_JSON}}

### Scenario workflow anchors (JSON)
{{WORKFLOW_JSON}}

### Rules
- Only use exact verb names from the visible CLI list.
- Do not repeat deterministic edges already listed above.
- Focus on plausible workflow steps:
  - read -> read narrowing or verification
  - read -> produce/guard action
  - produce/guard -> read verification or follow-up inspection
- Prefer 6-16 semantic edges total.
- Edge weights:
  - 0.55-0.75 for strong semantic follow-ups
  - 0.35-0.54 for moderate/plausible follow-ups
  - 0.20-0.34 for weak optional follow-ups
- Use concise English relationship labels.
- Sampling hints should pick from these patterns only:
  minimal_gold, investigate_then_act, search_then_filter,
  verify_before_commit, audit_then_decide, persist_and_submit

### Output JSON
{
  "semantic_edges": [
    {
      "src": "list-customers",
      "dst": "get-customer",
      "weight": 0.62,
      "relationship": "inspect_selected_customer",
      "reason": "short rationale"
    }
  ],
  "sampling_hints": {
    "preferred_patterns": ["investigate_then_act", "verify_before_commit"],
    "entry_reads": ["list-customers", "search-customers"],
    "verification_reads": ["get-customer"],
    "followup_reads": ["list-audit-log"]
  }
}

Return JSON only. No markdown fences and no prose outside JSON."""

PROMPT_WEAK_EDGES = """You are enriching a tool dependency graph for an agentic environment.
The strong edges (data-flow dependencies and the gold workflow order) are
already added. Add only plausible weak follow-up edges that the deterministic
rules missed.

### Environment
{{ENV_NAME}} - {{ENV_DES}}

### Visible verbs (name - role - short help)
{{VERBS}}

### Rules
- Only connect verbs from the list above and use the exact names.
- Use weight 0.20-0.30 only.
- Do not duplicate obvious list->get edges of the same entity.
- Aim for 3-8 extra edges and skip if nothing sensible.

### Output
Output only lines of the form:
src_verb -> dst_verb : relationship
No prose and no markdown fences."""

SEMANTIC_PROMPT_HASH = hashlib.md5(PROMPT_SEMANTIC_PLAN.encode("utf-8")).hexdigest()[:8]


def _normalize_pattern(name: Any) -> Optional[str]:
    if not isinstance(name, str):
        return None
    key = name.strip().lower().replace(" ", "_")
    pattern = PATTERN_ALIASES.get(key)
    if pattern in ALLOWED_PATTERNS:
        return pattern
    return None


def _env_des(doc: dict[str, Any]) -> str:
    rel = doc.get("rel_path", "")
    readme = HERE.parent / rel / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped[:300]
    return doc["env_name"].replace("_", " ")


def _load_scaffold() -> list[dict[str, Any]]:
    path = DOCS_DIR / "_scaffold_tools.json"
    if not path.exists():
        log.warning("scaffold tools doc missing; run extract_claw_tools.py first")
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _semantic_cache_path(env_name: str) -> Path:
    return CACHE_DIR / f"{env_name}_semantic_plan.json"


def _load_semantic_cache(doc_path: Path, env_name: str) -> Optional[dict[str, Any]]:
    cache_path = _semantic_cache_path(env_name)
    if not cache_path.exists():
        return None
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        meta = payload.get("_meta", {})
        if (
            meta.get("doc_mtime", 0) >= doc_path.stat().st_mtime
            and meta.get("prompt_hash") == SEMANTIC_PROMPT_HASH
        ):
            return payload.get("plan", {})
    except Exception as exc:  # pragma: no cover - cache corruption is non-fatal
        log.warning("failed to read semantic cache for %s: %s", env_name, exc)
    return None


def _save_semantic_cache(doc_path: Path, env_name: str, plan: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            "doc_mtime": doc_path.stat().st_mtime,
            "prompt_hash": SEMANTIC_PROMPT_HASH,
        },
        "plan": plan,
    }
    _semantic_cache_path(env_name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _visible_payload(doc: dict[str, Any]) -> list[dict[str, Any]]:
    payload = []
    for verb in doc["visible_verbs"]:
        payload.append({
            "verb": verb["verb"],
            "action": verb["action"],
            "role": verb["role"],
            "help": verb.get("help", ""),
            "required_args": [
                arg["name"] for arg in verb.get("args", []) if arg.get("required")
            ],
            "optional_args": [
                arg["name"] for arg in verb.get("args", []) if not arg.get("required")
            ],
        })
    return payload


def _strong_signal_payload(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataflow_edges": doc.get("dataflow_edges", []),
        "gold_actions_by_scenario": doc.get("gold_actions_by_scenario", {}),
        "anchor_keys": doc.get("anchor_keys", []),
        "evaluator_dimensions": doc.get("evaluator", {}).get("dimensions", []),
        "has_forbidden_penalty": bool(
            doc.get("evaluator", {}).get("has_forbidden_penalty")
        ),
    }


def _normalize_sampling_hints(
    raw_hints: Any,
    valid_verbs: set[str],
) -> dict[str, Any]:
    if not isinstance(raw_hints, dict):
        return {}

    def _filter_verbs(key: str) -> list[str]:
        values = raw_hints.get(key)
        if not isinstance(values, list):
            return []
        out: list[str] = []
        for item in values:
            if isinstance(item, str) and item in valid_verbs and item not in out:
                out.append(item)
        return out

    preferred: list[str] = []
    values = raw_hints.get("preferred_patterns")
    if isinstance(values, list):
        for item in values:
            pattern = _normalize_pattern(item)
            if pattern and pattern not in preferred:
                preferred.append(pattern)

    hints = {
        "preferred_patterns": preferred,
        "entry_reads": _filter_verbs("entry_reads"),
        "verification_reads": _filter_verbs("verification_reads"),
        "followup_reads": _filter_verbs("followup_reads"),
    }
    return {key: value for key, value in hints.items() if value}


def _normalize_semantic_edges(
    raw_edges: Any,
    valid_verbs: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(raw_edges, list):
        return []

    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in raw_edges:
        if not isinstance(raw, dict):
            continue
        src = str(raw.get("src", "")).strip()
        dst = str(raw.get("dst", "")).strip()
        if src not in valid_verbs or dst not in valid_verbs or src == dst:
            continue
        try:
            weight = float(raw.get("weight", 0.45))
        except (TypeError, ValueError):
            weight = 0.45
        weight = max(0.20, min(0.75, weight))
        relationship = str(raw.get("relationship", "")).strip() or "semantic_followup"
        rationale = str(raw.get("reason", "")).strip()
        tier = "llm_semantic" if weight >= 0.35 else "llm_weak"
        key = (src, dst)
        current = unique.get(key)
        candidate = {
            "src": src,
            "dst": dst,
            "weight": weight,
            "relationship": relationship,
            "tier": tier,
            "rationale": rationale[:200],
        }
        if current is None or candidate["weight"] > current["weight"]:
            unique[key] = candidate
    return list(unique.values())


def _fetch_llm_semantic_plan(
    doc: dict[str, Any],
    doc_path: Path,
    env_des: str,
) -> dict[str, Any]:
    cached = _load_semantic_cache(doc_path, doc["env_name"])
    if cached is not None:
        return cached
    if not llm_available():
        return {}

    prompt = (
        PROMPT_SEMANTIC_PLAN
        .replace("{{ENV_NAME}}", doc["env_name"])
        .replace("{{ENV_DES}}", env_des or doc["env_name"])
        .replace(
            "{{VERBS_JSON}}",
            json.dumps(_visible_payload(doc), ensure_ascii=False, indent=2),
        )
        .replace(
            "{{STRONG_EDGES_JSON}}",
            json.dumps(doc.get("dataflow_edges", []), ensure_ascii=False, indent=2),
        )
        .replace(
            "{{WORKFLOW_JSON}}",
            json.dumps(_strong_signal_payload(doc), ensure_ascii=False, indent=2),
        )
    )
    plan = llm_json(prompt, temperature=0.2)
    if not isinstance(plan, dict):
        return {}

    valid_verbs = {verb["verb"] for verb in doc["visible_verbs"]}
    normalized = {
        "semantic_edges": _normalize_semantic_edges(plan.get("semantic_edges"), valid_verbs),
        "sampling_hints": _normalize_sampling_hints(plan.get("sampling_hints"), valid_verbs),
    }
    if normalized["semantic_edges"] or normalized["sampling_hints"]:
        _save_semantic_cache(doc_path, doc["env_name"], normalized)
        return normalized
    return {}


def _llm_weak_edges(doc: dict[str, Any], G: nx.DiGraph, env_des: str) -> int:
    if not llm_available():
        return 0

    visible = doc["visible_verbs"]
    verb_names = {verb["verb"] for verb in visible}
    lines = "\n".join(
        f"{verb['verb']} - {verb['role']} - {verb.get('help', '')}"
        for verb in visible
    )
    prompt = (
        PROMPT_WEAK_EDGES
        .replace("{{ENV_NAME}}", doc["env_name"])
        .replace("{{ENV_DES}}", env_des or doc["env_name"])
        .replace("{{VERBS}}", lines)
    )
    out = llm_text(prompt, temperature=0.35)
    if not out:
        return 0

    added = 0
    for line in out.splitlines():
        if "->" not in line:
            continue
        left, rest = line.split("->", 1)
        dst, _, rel = rest.partition(":")
        src = left.strip()
        dst = dst.strip()
        rel = rel.strip() or "plausible_followup"
        if src not in verb_names or dst not in verb_names or src == dst:
            continue
        if G.has_edge(src, dst):
            continue
        G.add_edge(src, dst, weight=0.25, relationship=rel, tier="llm_weak")
        added += 1
    return added


def _apply_semantic_plan(
    doc: dict[str, Any],
    doc_path: Path,
    G: nx.DiGraph,
    env_des: str,
) -> int:
    plan = _fetch_llm_semantic_plan(doc, doc_path, env_des)
    added = 0

    for edge in plan.get("semantic_edges", []):
        src = edge["src"]
        dst = edge["dst"]
        if G.has_edge(src, dst):
            current = G[src][dst]
            if current.get("tier") in {"dataflow", "gold"}:
                continue
            if edge["weight"] > float(current.get("weight", 0.0)):
                current.update({
                    "weight": edge["weight"],
                    "relationship": edge["relationship"],
                    "tier": edge["tier"],
                })
                if edge.get("rationale"):
                    current["rationale"] = edge["rationale"]
            continue
        G.add_edge(
            src,
            dst,
            weight=edge["weight"],
            relationship=edge["relationship"],
            tier=edge["tier"],
            **({"rationale": edge["rationale"]} if edge.get("rationale") else {}),
        )
        added += 1

    if plan.get("sampling_hints"):
        G.graph["sampling_hints"] = plan["sampling_hints"]

    if added == 0 and not plan.get("sampling_hints"):
        added += _llm_weak_edges(doc, G, env_des)
    return added


def build_graph(doc: dict[str, Any], scaffold: list[dict[str, Any]]) -> nx.DiGraph:
    G = nx.DiGraph()
    G.graph.update({
        "env_name": doc["env_name"],
        "anchor_keys": doc.get("anchor_keys", []),
        "evaluator_dimensions": doc.get("evaluator", {}).get("dimensions", []),
        "has_forbidden_penalty": bool(
            doc.get("evaluator", {}).get("has_forbidden_penalty")
        ),
        "sampling_hints": {},
    })

    for tool in scaffold:
        G.add_node(
            tool["name"],
            layer="scaffold",
            role="scaffold",
            description=tool.get("description", ""),
        )

    visible = doc["visible_verbs"]
    verb_by_action: dict[str, str] = {}
    for verb in visible:
        node_id = verb["verb"]
        G.add_node(
            node_id,
            layer="cli",
            role=verb["role"],
            action=verb["action"],
            help=verb.get("help", ""),
            required_args=[arg["name"] for arg in verb["args"] if arg.get("required")],
        )
        verb_by_action[verb["action"]] = node_id

    for edge in doc.get("dataflow_edges", []):
        if G.has_node(edge["src"]) and G.has_node(edge["dst"]):
            G.add_edge(
                edge["src"],
                edge["dst"],
                weight=edge["weight"],
                relationship=edge["relationship"],
                tier="dataflow",
            )

    for scenario_id, actions in doc.get("gold_actions_by_scenario", {}).items():
        prev_node: Optional[str] = None
        for action in actions:
            node = verb_by_action.get(action)
            if node is None:
                prev_node = None
                continue
            if prev_node is not None and prev_node != node:
                if G.has_edge(prev_node, node):
                    G[prev_node][node]["weight"] = max(
                        float(G[prev_node][node].get("weight", 0.0)),
                        0.9,
                    )
                    G[prev_node][node]["tier"] = "gold"
                else:
                    G.add_edge(
                        prev_node,
                        node,
                        weight=0.9,
                        relationship=f"gold_next::{scenario_id}",
                        tier="gold",
                    )
            prev_node = node

    read_verbs = [verb["verb"] for verb in visible if verb["role"] == "read"]
    produce_verbs = [
        verb["verb"]
        for verb in visible
        if verb["role"] in {"produce", "guard", "other"}
    ]

    if G.has_node(SCAFFOLD_READ) and ENTRY_ACTION in verb_by_action:
        G.add_edge(
            SCAFFOLD_READ,
            verb_by_action[ENTRY_ACTION],
            weight=0.5,
            relationship="inspect_task",
            tier="bridge",
        )

    entry_node = verb_by_action.get(ENTRY_ACTION)
    for read_verb in read_verbs:
        if entry_node and entry_node != read_verb:
            G.add_edge(
                entry_node,
                read_verb,
                weight=0.5,
                relationship="task_then_read",
                tier="bridge",
            )

    for read_verb in read_verbs:
        for filter_tool in SCAFFOLD_FILTER:
            if G.has_node(filter_tool):
                G.add_edge(
                    read_verb,
                    filter_tool,
                    weight=0.3,
                    relationship="read_then_filter",
                    tier="bridge",
                )
                for produce_verb in produce_verbs:
                    G.add_edge(
                        filter_tool,
                        produce_verb,
                        weight=0.3,
                        relationship="filter_then_act",
                        tier="bridge",
                    )

    for produce_verb in produce_verbs:
        for write_tool in SCAFFOLD_WRITE:
            if G.has_node(write_tool):
                G.add_edge(
                    produce_verb,
                    write_tool,
                    weight=0.4,
                    relationship="act_then_persist",
                    tier="bridge",
                )

    if G.has_node(SCAFFOLD_FINISH):
        for produce_verb in produce_verbs:
            G.add_edge(
                produce_verb,
                SCAFFOLD_FINISH,
                weight=0.6,
                relationship="complete_task",
                tier="bridge",
            )
        for write_tool in SCAFFOLD_WRITE:
            if G.has_node(write_tool):
                G.add_edge(
                    write_tool,
                    SCAFFOLD_FINISH,
                    weight=0.5,
                    relationship="complete_task",
                    tier="bridge",
                )

    return G


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", help="single env name")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="skip the LLM semantic-plan pass and keep deterministic edges only",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scaffold = _load_scaffold()
    use_llm = (not args.no_llm) and llm_available()
    log.info("LLM semantic plan: %s", "ON" if use_llm else "OFF (deterministic)")

    doc_files = sorted(
        path for path in DOCS_DIR.glob("*.json") if path.stem != "_scaffold_tools"
    )
    if args.env:
        doc_files = [path for path in doc_files if path.stem == args.env]
        if not doc_files:
            log.error("no doc for --env %s", args.env)
            return 1

    built = 0
    for doc_path in doc_files:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        G = build_graph(doc, scaffold)
        env_des = _env_des(doc)
        if use_llm:
            try:
                added = _apply_semantic_plan(doc, doc_path, G, env_des)
                if added:
                    log.info("  %s: added %d LLM semantic edges", doc["env_name"], added)
            except Exception as exc:  # pragma: no cover - LLM failures are non-fatal
                log.warning("  LLM semantic plan failed for %s: %s", doc["env_name"], exc)

        tier_counts: dict[str, int] = {}
        for _, _, data in G.edges(data=True):
            tier = str(data.get("tier", "?"))
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        log.info(
            "%-34s nodes=%2d edges=%3d %s",
            doc["env_name"],
            G.number_of_nodes(),
            G.number_of_edges(),
            dict(sorted(tier_counts.items())),
        )
        if not args.dry_run:
            out_path = OUT_DIR / f"{doc['env_name']}_tool_graph.json"
            out_path.write_text(
                json.dumps(
                    nx_json_graph.node_link_data(G),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        built += 1

    print(f"\nDone. Graphs: {built} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
