"""Stage C: sample claw tool chains from graphs with LLM variants and graph guidance.

The old claw sampler mostly wrapped the gold action sequence with random reads
and scaffold noise. That guarantees coverage, but the resulting chains are often
too templated and not diverse enough.

This version keeps the two hard claw constraints:

1. every chain must preserve the scenario's gold action subsequence
2. verbs that require ``--<entity>-id`` must be reachable from an earlier
   producer of that entity ID

On top of that it improves chain quality in two ways:

- optional LLM-generated chain variants per scenario, cached as structured JSON
- graph-guided fallback sampling that uses edge tiers, weights, and LLM graph
  hints instead of injecting arbitrary reads

Output: ``claw_chains_out/<env>.jsonl``.

Usage:
    python sample_claw_chains.py
    python sample_claw_chains.py --env post_mails --n 12
    python sample_claw_chains.py --seed 0 --no-llm
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any, Optional

import networkx as nx
from networkx.readwrite import json_graph as nx_json_graph

from llm_client import llm_available, llm_json

log = logging.getLogger("sample_claw_chains")

HERE = Path(__file__).resolve().parent
DOCS_DIR = HERE / "claw_tool_env_docs"
GRAPHS_DIR = HERE / "claw_tool_graphs"
OUT_DIR = HERE / "claw_chains_out"
CACHE_DIR = HERE / "claw_chain_plan_cache"

SCAFFOLD_READ = "read"
SCAFFOLD_FILTER = ["grep", "find"]
SCAFFOLD_WRITE = ["write", "edit"]
SCAFFOLD_FINISH = "finish"
SCAFFOLD_OPS = {SCAFFOLD_READ, *SCAFFOLD_FILTER, *SCAFFOLD_WRITE, SCAFFOLD_FINISH}

DEFAULT_PATTERNS = [
    "minimal_gold",
    "investigate_then_act",
    "search_then_filter",
    "verify_before_commit",
    "audit_then_decide",
    "persist_and_submit",
]
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

PROMPT_CHAIN_VARIANTS = """You are planning realistic tool chains for a claw-style
agent environment.

Return several distinct successful chains that preserve the gold action
subsequence. The deterministic graph and required actions are already correct;
your job is to choose plausible extra reads, filters, verification steps, and
artifact persistence steps around them.

### Environment
{{ENV_NAME}} - {{ENV_DES}}

### Scenario
scenario_id: {{SCENARIO_ID}}
gold_actions: {{GOLD_ACTIONS_JSON}}
gold_cli_verbs: {{GOLD_VERBS_JSON}}

### Visible CLI verbs (JSON)
{{VERBS_JSON}}

### Important graph edges (JSON)
{{EDGE_JSON}}

### Sampling hints (JSON)
{{HINTS_JSON}}

### Allowed scaffold ops
["read", "grep", "find", "write", "edit", "finish"]

### Rules
- Use exact op names only.
- CLI steps must use verb names, not action names.
- Start with "read".
- If the environment has "task", include it exactly once near the start unless
  it is already part of the gold sequence.
- End with "finish".
- Preserve the gold_cli_verbs subsequence exactly in order, though other steps
  may appear between them.
- Keep each chain between 6 and 18 ops.
- Use different patterns across variants. Allowed pattern labels:
  minimal_gold, investigate_then_act, search_then_filter,
  verify_before_commit, audit_then_decide, persist_and_submit

### Output JSON
{
  "variants": [
    {
      "pattern": "investigate_then_act",
      "ops": ["read", "task", "list-customers", "get-customer", "write", "finish"]
    }
  ]
}

Return JSON only. No markdown fences and no prose outside JSON."""

VARIANT_PROMPT_HASH = hashlib.md5(PROMPT_CHAIN_VARIANTS.encode("utf-8")).hexdigest()[:8]


def _graph_path(env: str) -> Path:
    return GRAPHS_DIR / f"{env}_tool_graph.json"


def _load_graph(env: str) -> Optional[nx.DiGraph]:
    path = _graph_path(env)
    if not path.exists():
        return None
    return nx_json_graph.node_link_graph(json.loads(path.read_text(encoding="utf-8")))


def _env_des(doc: dict[str, Any]) -> str:
    rel = doc.get("rel_path", "")
    readme = HERE.parent / rel / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped[:300]
    return doc["env_name"].replace("_", " ")


def _variant_cache_path(env_name: str, scenario_id: str) -> Path:
    return CACHE_DIR / f"{env_name}__{scenario_id}_variants.json"


def _gold_hash(gold_actions: list[str]) -> str:
    payload = json.dumps(gold_actions, ensure_ascii=False)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()[:8]


def _load_variant_cache(
    doc_path: Path,
    graph_path: Path,
    env_name: str,
    scenario_id: str,
    gold_actions: list[str],
) -> Optional[list[dict[str, Any]]]:
    cache_path = _variant_cache_path(env_name, scenario_id)
    if not cache_path.exists():
        return None
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        meta = payload.get("_meta", {})
        if (
            meta.get("doc_mtime", 0) >= doc_path.stat().st_mtime
            and meta.get("graph_mtime", 0) >= graph_path.stat().st_mtime
            and meta.get("prompt_hash") == VARIANT_PROMPT_HASH
            and meta.get("gold_hash") == _gold_hash(gold_actions)
        ):
            variants = payload.get("variants")
            if isinstance(variants, list):
                return variants
    except Exception as exc:  # pragma: no cover - cache corruption is non-fatal
        log.warning("failed to read chain cache for %s/%s: %s", env_name, scenario_id, exc)
    return None


def _save_variant_cache(
    doc_path: Path,
    graph_path: Path,
    env_name: str,
    scenario_id: str,
    gold_actions: list[str],
    variants: list[dict[str, Any]],
) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {
            "doc_mtime": doc_path.stat().st_mtime,
            "graph_mtime": graph_path.stat().st_mtime,
            "prompt_hash": VARIANT_PROMPT_HASH,
            "gold_hash": _gold_hash(gold_actions),
        },
        "variants": variants,
    }
    _variant_cache_path(env_name, scenario_id).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_pattern(name: Any) -> str:
    if not isinstance(name, str):
        return "investigate_then_act"
    key = name.strip().lower().replace(" ", "_")
    return PATTERN_ALIASES.get(key, "investigate_then_act")


def _verb_lookup(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {verb["verb"]: verb for verb in doc["visible_verbs"]}


def _action_to_verb(doc: dict[str, Any]) -> dict[str, str]:
    return {verb["action"]: verb["verb"] for verb in doc["visible_verbs"]}


def _gold_verbs(doc: dict[str, Any], gold_actions: list[str]) -> list[str]:
    action_to_verb = _action_to_verb(doc)
    verbs: list[str] = []
    for action in gold_actions:
        verb = action_to_verb.get(action)
        if verb:
            verbs.append(verb)
    return verbs


def _graph_hints(G: nx.DiGraph) -> dict[str, Any]:
    raw = G.graph.get("sampling_hints", {}) or {}
    valid_verbs = {
        node for node, data in G.nodes(data=True) if data.get("layer") == "cli"
    }

    def _filter_verbs(key: str) -> list[str]:
        values = raw.get(key)
        if not isinstance(values, list):
            return []
        out: list[str] = []
        for item in values:
            if isinstance(item, str) and item in valid_verbs and item not in out:
                out.append(item)
        return out

    preferred: list[str] = []
    values = raw.get("preferred_patterns")
    if isinstance(values, list):
        for item in values:
            pattern = _normalize_pattern(item)
            if pattern not in preferred:
                preferred.append(pattern)

    return {
        "preferred_patterns": preferred,
        "entry_reads": _filter_verbs("entry_reads"),
        "verification_reads": _filter_verbs("verification_reads"),
        "followup_reads": _filter_verbs("followup_reads"),
    }


def _tier_bonus(tier: str) -> float:
    return {
        "gold": 0.45,
        "dataflow": 0.35,
        "llm_semantic": 0.25,
        "bridge": 0.10,
        "llm_weak": 0.05,
    }.get(tier, 0.0)


def _contains_subsequence(seq: list[str], target: list[str]) -> bool:
    if not target:
        return True
    idx = 0
    for item in seq:
        if item == target[idx]:
            idx += 1
            if idx == len(target):
                return True
    return False


def _collapse_adjacent(seq: list[str]) -> list[str]:
    out: list[str] = []
    for item in seq:
        if not out or out[-1] != item:
            out.append(item)
    return out


def _allowed_ops(doc: dict[str, Any]) -> set[str]:
    return set(SCAFFOLD_OPS) | {verb["verb"] for verb in doc["visible_verbs"]}


def _sanitize_ops(
    ops: list[str],
    task_present: bool,
    gold_verbs: list[str],
) -> list[str]:
    cleaned = _collapse_adjacent([op for op in ops if op])

    cleaned = [op for op in cleaned if op != SCAFFOLD_FINISH]
    if not cleaned or cleaned[0] != SCAFFOLD_READ:
        cleaned.insert(0, SCAFFOLD_READ)

    if task_present:
        cleaned = [op for op in cleaned if op != "task"]
        cleaned.insert(1, "task")

    cleaned = _collapse_adjacent(cleaned)

    gold_limits = {verb: gold_verbs.count(verb) + 1 for verb in set(gold_verbs)}
    seen_counts: dict[str, int] = {}
    pruned: list[str] = []
    for op in cleaned:
        if op == SCAFFOLD_READ:
            limit = 1
        elif op == "task":
            limit = 1 if task_present else 0
        elif op in SCAFFOLD_FILTER:
            limit = 2
        elif op in SCAFFOLD_WRITE:
            limit = 1
        else:
            limit = gold_limits.get(op, 1)
        if seen_counts.get(op, 0) >= limit:
            continue
        pruned.append(op)
        seen_counts[op] = seen_counts.get(op, 0) + 1

    cleaned = pruned
    cleaned.append(SCAFFOLD_FINISH)

    while len(cleaned) > 18 and len(cleaned) > len(gold_verbs) + 2:
        for idx in range(len(cleaned) - 2, 1, -1):
            if cleaned[idx] not in gold_verbs and cleaned[idx] not in {
                SCAFFOLD_READ,
                "task",
                SCAFFOLD_FINISH,
            }:
                cleaned.pop(idx)
                break
        else:
            break

    return cleaned


def _edge_payload(G: nx.DiGraph) -> list[dict[str, Any]]:
    priority = {"gold": 0, "dataflow": 1, "llm_semantic": 2, "llm_weak": 3, "bridge": 4}
    edges: list[dict[str, Any]] = []
    for src, dst, data in G.edges(data=True):
        if not G.nodes[src].get("layer") == "cli":
            continue
        if not G.nodes[dst].get("layer") == "cli":
            continue
        edges.append({
            "src": src,
            "dst": dst,
            "tier": data.get("tier", ""),
            "weight": float(data.get("weight", 0.0)),
            "relationship": data.get("relationship", ""),
        })
    edges.sort(key=lambda item: (priority.get(str(item["tier"]), 9), -item["weight"], item["src"], item["dst"]))
    return edges[:40]


def _fetch_llm_chain_variants(
    doc: dict[str, Any],
    doc_path: Path,
    graph_path: Path,
    G: nx.DiGraph,
    scenario_id: str,
    gold_actions: list[str],
) -> list[dict[str, Any]]:
    cached = _load_variant_cache(doc_path, graph_path, doc["env_name"], scenario_id, gold_actions)
    if cached is not None:
        return cached
    if not llm_available():
        return []

    gold_verbs = _gold_verbs(doc, gold_actions)
    prompt = (
        PROMPT_CHAIN_VARIANTS
        .replace("{{ENV_NAME}}", doc["env_name"])
        .replace("{{ENV_DES}}", _env_des(doc))
        .replace("{{SCENARIO_ID}}", scenario_id)
        .replace("{{GOLD_ACTIONS_JSON}}", json.dumps(gold_actions, ensure_ascii=False))
        .replace("{{GOLD_VERBS_JSON}}", json.dumps(gold_verbs, ensure_ascii=False))
        .replace(
            "{{VERBS_JSON}}",
            json.dumps(
                [
                    {
                        "verb": verb["verb"],
                        "role": verb["role"],
                        "help": verb.get("help", ""),
                        "required_args": [
                            arg["name"]
                            for arg in verb.get("args", [])
                            if arg.get("required")
                        ],
                    }
                    for verb in doc["visible_verbs"]
                ],
                ensure_ascii=False,
                indent=2,
            ),
        )
        .replace("{{EDGE_JSON}}", json.dumps(_edge_payload(G), ensure_ascii=False, indent=2))
        .replace("{{HINTS_JSON}}", json.dumps(_graph_hints(G), ensure_ascii=False, indent=2))
    )

    payload = llm_json(prompt, temperature=0.3)
    if not isinstance(payload, dict):
        return []

    allowed_ops = _allowed_ops(doc)
    action_to_verb = _action_to_verb(doc)
    task_present = "task" in allowed_ops
    variants: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for raw in payload.get("variants", []):
        if not isinstance(raw, dict):
            continue
        ops_raw = raw.get("ops")
        if not isinstance(ops_raw, list):
            continue
        ops: list[str] = []
        for item in ops_raw:
            if not isinstance(item, str):
                continue
            token = action_to_verb.get(item.strip(), item.strip())
            if token in allowed_ops:
                ops.append(token)
        ops = _sanitize_ops(ops, task_present=task_present, gold_verbs=gold_verbs)
        if len(ops) < max(4, len(gold_verbs) + 2):
            continue
        if not _contains_subsequence(ops, gold_verbs):
            continue
        signature = tuple(ops)
        if signature in seen:
            continue
        seen.add(signature)
        variants.append({
            "pattern": _normalize_pattern(raw.get("pattern")),
            "ops": ops,
            "source": "llm",
        })

    if variants:
        _save_variant_cache(
            doc_path,
            graph_path,
            doc["env_name"],
            scenario_id,
            gold_actions,
            variants,
        )
    return variants


def _choose_from_top(
    candidates: list[tuple[float, str]],
    rng: random.Random,
) -> Optional[str]:
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[0], item[1]))
    top = candidates[: min(3, len(candidates))]
    return rng.choice(top)[1]


def _producers_of(doc: dict[str, Any]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for edge in doc.get("dataflow_edges", []):
        rel = edge["relationship"]
        if rel.startswith("produces_") and rel.endswith("_id_for"):
            entity = rel[len("produces_"):-len("_id_for")]
            out.setdefault(entity, set()).add(edge["src"])
    return out


def _required_id_entities(verb_rec: dict[str, Any]) -> list[str]:
    entities: list[str] = []
    for arg in verb_rec.get("args", []):
        if (
            arg.get("required")
            and arg["name"].startswith("--")
            and arg["name"].endswith("-id")
        ):
            entities.append(arg["name"][2:-3])
    return entities


def _mark_produced_entities(
    op: str,
    producers: dict[str, set[str]],
    produced_entities: set[str],
) -> None:
    for entity, verbs in producers.items():
        if op in verbs:
            produced_entities.add(entity)


def _scaffold_call(op: str, read_count: int) -> str:
    if op == SCAFFOLD_READ:
        return "read task prompt" if read_count == 0 else "review local notes"
    if op in SCAFFOLD_FILTER:
        return "filter discovered records"
    if op in SCAFFOLD_WRITE:
        return "persist artifact note"
    if op == SCAFFOLD_FINISH:
        return "submit final answer"
    return op


def _emit_step(steps: list[dict[str, Any]], layer: str, op: str, call: str) -> bool:
    if steps and steps[-1]["layer"] == layer and steps[-1]["op"] == op:
        return False
    steps.append({"layer": layer, "op": op, "call": call})
    return True


def _choose_producer(
    entity: str,
    target_verb: str,
    doc: dict[str, Any],
    G: nx.DiGraph,
    producers: dict[str, set[str]],
    used_cli_ops: list[str],
    hints: dict[str, Any],
) -> Optional[str]:
    verb_lookup = _verb_lookup(doc)
    candidates: list[tuple[float, str]] = []
    for op in sorted(producers.get(entity, set())):
        score = 0.30
        if G.has_edge(op, target_verb):
            score += float(G[op][target_verb].get("weight", 0.0))
            score += _tier_bonus(str(G[op][target_verb].get("tier", "")))
        if op in hints.get("entry_reads", []):
            score += 0.15
        if verb_lookup.get(op, {}).get("role") == "read":
            score += 0.10
        if op in used_cli_ops:
            score -= 0.10
        candidates.append((score, op))
    if candidates:
        candidates.sort(key=lambda item: (-item[0], item[1]))
        return candidates[0][1]

    entity_token = entity.replace("-", "")
    if G.has_node(target_verb):
        for pred in G.predecessors(target_verb):
            if pred not in verb_lookup or pred == "task":
                continue
            if verb_lookup[pred].get("role") != "read":
                continue
            normalized = pred.replace("-", "")
            if entity_token not in normalized and entity not in pred:
                continue
            score = 0.20
            if G.has_edge(pred, target_verb):
                score += float(G[pred][target_verb].get("weight", 0.0))
                score += _tier_bonus(str(G[pred][target_verb].get("tier", "")))
            if pred in used_cli_ops:
                score -= 0.10
            score += 0.10
            candidates.append((score, pred))
    if candidates:
        candidates.sort(key=lambda item: (-item[0], item[1]))
        return candidates[0][1]

    for verb in doc["visible_verbs"]:
        name = verb["verb"]
        if name == "task" or verb.get("role") != "read":
            continue
        normalized = name.replace("-", "")
        if entity_token in normalized or entity in name:
            return name
    return None


def _materialize_chain(
    doc: dict[str, Any],
    G: nx.DiGraph,
    scenario_id: str,
    gold_actions: list[str],
    ops: list[str],
    pattern: str,
    source: str,
) -> Optional[dict[str, Any]]:
    verb_lookup = _verb_lookup(doc)
    producers = _producers_of(doc)
    hints = _graph_hints(G)
    gold_verbs = _gold_verbs(doc, gold_actions)
    allowed_ops = _allowed_ops(doc)
    task_present = "task" in allowed_ops

    ops = [op for op in ops if op in allowed_ops]
    ops = _sanitize_ops(ops, task_present=task_present, gold_verbs=gold_verbs)
    if not _contains_subsequence(ops, gold_verbs):
        return None

    steps: list[dict[str, Any]] = []
    produced_entities: set[str] = set()
    dataflow_ok = True
    read_count = 0

    for op in ops:
        if op in SCAFFOLD_OPS:
            if _emit_step(steps, "scaffold", op, _scaffold_call(op, read_count)):
                if op == SCAFFOLD_READ:
                    read_count += 1
            continue

        rec = verb_lookup.get(op)
        if rec is None:
            continue

        used_cli_ops = [step["op"] for step in steps if step["layer"] == "cli"]
        for entity in _required_id_entities(rec):
            if entity in produced_entities:
                continue
            producer = _choose_producer(
                entity,
                op,
                doc,
                G,
                producers,
                used_cli_ops,
                hints,
            )
            if producer is None:
                log.info(
                    "  %s/%s: unresolved producer for '%s' (needed by %s)",
                    doc["env_name"],
                    scenario_id,
                    entity,
                    op,
                )
                dataflow_ok = False
                produced_entities.add(entity)
                continue
            if producer != op and _emit_step(
                steps,
                "cli",
                producer,
                f"execute_bash: python -m {doc['cli_module']} {producer} ...",
            ):
                _mark_produced_entities(producer, producers, produced_entities)
            produced_entities.add(entity)

        if _emit_step(
            steps,
            "cli",
            op,
            f"execute_bash: python -m {doc['cli_module']} {op} ...",
        ):
            _mark_produced_entities(op, producers, produced_entities)

    if not steps or steps[-1]["op"] != SCAFFOLD_FINISH:
        _emit_step(steps, "scaffold", SCAFFOLD_FINISH, _scaffold_call(SCAFFOLD_FINISH, read_count))

    cli_ops = [step["op"] for step in steps if step["layer"] == "cli"]
    if not _contains_subsequence(cli_ops, gold_verbs):
        return None

    return {
        "env_name": doc["env_name"],
        "scenario_id": scenario_id,
        "has_skill_md": doc["has_skill_md"],
        "gold_actions": gold_actions,
        "pattern": pattern,
        "chain_source": source,
        "chain": steps,
        "n_cli_steps": sum(1 for step in steps if step["layer"] == "cli"),
        "n_scaffold_steps": sum(1 for step in steps if step["layer"] == "scaffold"),
        "dataflow_ok": dataflow_ok,
    }


def _pick_entry_read(
    doc: dict[str, Any],
    G: nx.DiGraph,
    hints: dict[str, Any],
    focus_verb: Optional[str],
    blocked_ops: set[str],
    used_ops: set[str],
    rng: random.Random,
) -> Optional[str]:
    verb_lookup = _verb_lookup(doc)
    seed_ops = hints.get("entry_reads") or [
        verb["verb"]
        for verb in doc["visible_verbs"]
        if verb["role"] == "read" and verb["verb"] != "task"
    ]
    candidates: list[tuple[float, str]] = []
    for op in seed_ops:
        if op in used_ops or op in blocked_ops or op not in verb_lookup:
            continue
        score = 0.15
        if focus_verb and G.has_edge(op, focus_verb):
            score += float(G[op][focus_verb].get("weight", 0.0))
            score += _tier_bonus(str(G[op][focus_verb].get("tier", "")))
        if op in hints.get("entry_reads", []):
            score += 0.15
        if verb_lookup[op].get("role") == "read":
            score += 0.10
        candidates.append((score, op))
    return _choose_from_top(candidates, rng)


def _pick_context_op(
    doc: dict[str, Any],
    G: nx.DiGraph,
    gold_verb: str,
    prev_cli: Optional[str],
    blocked_ops: set[str],
    used_ops: set[str],
    hints: dict[str, Any],
    pattern: str,
    rng: random.Random,
) -> Optional[str]:
    if pattern == "minimal_gold" or gold_verb == "task" or not G.has_node(gold_verb):
        return None

    verb_lookup = _verb_lookup(doc)
    gold_role = verb_lookup.get(gold_verb, {}).get("role", "other")
    candidates: list[tuple[float, str]] = []

    for pred in G.predecessors(gold_verb):
        if pred in SCAFFOLD_OPS or pred == "task" or pred not in verb_lookup:
            continue
        if pred == gold_verb or pred == prev_cli or pred in blocked_ops:
            continue
        edge = G[pred][gold_verb]
        score = float(edge.get("weight", 0.0)) + _tier_bonus(str(edge.get("tier", "")))
        pred_role = verb_lookup[pred].get("role")
        if gold_role in {"produce", "guard", "other"} and pred_role == "read":
            score += 0.25
        if pattern in {"investigate_then_act", "search_then_filter"} and pred_role == "read":
            score += 0.10
        if pattern == "audit_then_decide" and pred in hints.get("verification_reads", []):
            score += 0.20
        if pred in used_ops:
            score -= 0.10
        candidates.append((score, pred))

    if prev_cli and G.has_node(prev_cli):
        for mid in G.successors(prev_cli):
            if mid in SCAFFOLD_OPS or mid == "task" or mid not in verb_lookup:
                continue
            if mid in {prev_cli, gold_verb} or mid in blocked_ops or not G.has_edge(mid, gold_verb):
                continue
            edge = G[mid][gold_verb]
            score = 0.20 + float(edge.get("weight", 0.0))
            score += _tier_bonus(str(edge.get("tier", "")))
            if mid in used_ops:
                score -= 0.05
            candidates.append((score, mid))

    return _choose_from_top(candidates, rng)


def _pick_followup_op(
    doc: dict[str, Any],
    G: nx.DiGraph,
    current_verb: str,
    next_gold: Optional[str],
    blocked_ops: set[str],
    used_ops: set[str],
    hints: dict[str, Any],
    pattern: str,
    rng: random.Random,
) -> Optional[str]:
    if pattern not in {"verify_before_commit", "audit_then_decide"}:
        return None
    if not G.has_node(current_verb):
        return None

    verb_lookup = _verb_lookup(doc)
    current_role = verb_lookup.get(current_verb, {}).get("role", "other")
    candidates: list[tuple[float, str]] = []

    for succ in G.successors(current_verb):
        if succ in SCAFFOLD_OPS or succ == next_gold or succ in blocked_ops or succ not in verb_lookup:
            continue
        if succ == current_verb:
            continue
        succ_role = verb_lookup[succ].get("role")
        if current_role in {"produce", "guard", "other"} and succ_role != "read":
            continue
        edge = G[current_verb][succ]
        score = float(edge.get("weight", 0.0)) + _tier_bonus(str(edge.get("tier", "")))
        if succ in hints.get("verification_reads", []):
            score += 0.20
        if next_gold and G.has_edge(succ, next_gold):
            score += 0.10
        if succ in used_ops:
            score -= 0.10
        candidates.append((score, succ))

    return _choose_from_top(candidates, rng)


def _build_graph_guided_ops(
    doc: dict[str, Any],
    G: nx.DiGraph,
    gold_actions: list[str],
    rng: random.Random,
    pattern: str,
) -> list[str]:
    hints = _graph_hints(G)
    verb_lookup = _verb_lookup(doc)
    gold_verbs = _gold_verbs(doc, gold_actions)
    task_present = "task" in _allowed_ops(doc)

    ops: list[str] = [SCAFFOLD_READ]
    used_ops = {SCAFFOLD_READ}

    if task_present and (not gold_verbs or gold_verbs[0] != "task"):
        ops.append("task")
        used_ops.add("task")

    focus_verb = next((verb for verb in gold_verbs if verb != "task"), None)
    if pattern in {"investigate_then_act", "search_then_filter", "audit_then_decide"}:
        blocked_ops = set(gold_verbs)
        entry_read = _pick_entry_read(doc, G, hints, focus_verb, blocked_ops, used_ops, rng)
        if entry_read:
            ops.append(entry_read)
            used_ops.add(entry_read)
            if pattern == "search_then_filter":
                ops.append(rng.choice(SCAFFOLD_FILTER))

    for idx, gold_verb in enumerate(gold_verbs):
        if gold_verb == "task":
            if "task" not in used_ops:
                ops.append("task")
                used_ops.add("task")
            continue

        prev_cli = next((op for op in reversed(ops) if op not in SCAFFOLD_OPS), None)
        blocked_ops = set(gold_verbs[idx:])
        context = _pick_context_op(
            doc,
            G,
            gold_verb,
            prev_cli,
            blocked_ops,
            used_ops,
            hints,
            pattern,
            rng,
        )
        if context:
            ops.append(context)
            used_ops.add(context)
            if (
                pattern == "search_then_filter"
                and verb_lookup.get(context, {}).get("role") == "read"
                and ops[-1] not in SCAFFOLD_FILTER
            ):
                ops.append(rng.choice(SCAFFOLD_FILTER))
        elif (
            pattern == "search_then_filter"
            and verb_lookup.get(gold_verb, {}).get("role") in {"produce", "guard", "other"}
            and ops[-1] not in SCAFFOLD_FILTER
        ):
            ops.append(rng.choice(SCAFFOLD_FILTER))

        ops.append(gold_verb)
        used_ops.add(gold_verb)

        next_gold = None
        for later in gold_verbs[idx + 1:]:
            if later != gold_verb:
                next_gold = later
                break

        followup = _pick_followup_op(
            doc,
            G,
            gold_verb,
            next_gold,
            set(gold_verbs[idx + 1:]),
            used_ops,
            hints,
            pattern,
            rng,
        )
        if followup:
            ops.append(followup)
            used_ops.add(followup)

    if (
        pattern == "persist_and_submit"
        or (
            gold_verbs
            and verb_lookup.get(gold_verbs[-1], {}).get("role") in {"produce", "guard"}
        )
    ):
        ops.append(rng.choice(SCAFFOLD_WRITE))

    return _sanitize_ops(ops, task_present=task_present, gold_verbs=gold_verbs)


def _fallback_gold(doc: dict[str, Any]) -> list[str]:
    reads = [
        verb["action"]
        for verb in doc["visible_verbs"]
        if verb["role"] == "read" and verb["verb"] not in {"list-scenarios"}
    ]
    produce = [
        verb["action"]
        for verb in doc["visible_verbs"]
        if verb["role"] in {"produce", "guard", "other"} and verb["verb"] != "task"
    ]
    skeleton = reads[:3] + produce[:1]
    return skeleton or reads[:1] or ["task"]


def _scenario_targets(gold_map: dict[str, list[str]], n: int) -> dict[str, int]:
    scenario_ids = list(gold_map)
    if not scenario_ids or n <= 0:
        return {}
    if n < len(scenario_ids):
        return {sid: (1 if idx < n else 0) for idx, sid in enumerate(scenario_ids)}
    base = n // len(scenario_ids)
    rem = n % len(scenario_ids)
    return {
        sid: base + (1 if idx < rem else 0)
        for idx, sid in enumerate(scenario_ids)
    }


def _pattern_pool(G: nx.DiGraph, rng: random.Random) -> list[str]:
    hints = _graph_hints(G).get("preferred_patterns", [])
    tail = [pattern for pattern in DEFAULT_PATTERNS if pattern not in hints]
    rng.shuffle(tail)
    return hints + tail


def process_env(env: str, n: int, rng: random.Random, use_llm: bool) -> list[dict[str, Any]]:
    doc_path = DOCS_DIR / f"{env}.json"
    graph_path = _graph_path(env)
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    G = _load_graph(env)
    if G is None:
        log.warning("  no graph for %s; run build_claw_graph.py", env)
        return []

    gold_map = doc.get("gold_actions_by_scenario", {})
    if not gold_map:
        scenario_ids = doc.get("scenario_ids") or ["_default"]
        gold_map = {sid: _fallback_gold(doc) for sid in scenario_ids}

    targets = _scenario_targets(gold_map, n)
    patterns = _pattern_pool(G, rng)
    chains: list[dict[str, Any]] = []
    seen_sig: set[str] = set()

    for scenario_id, gold_actions in gold_map.items():
        target = targets.get(scenario_id, 0)
        if target <= 0:
            continue

        scenario_chains: list[dict[str, Any]] = []
        if use_llm:
            variants = _fetch_llm_chain_variants(
                doc,
                doc_path,
                graph_path,
                G,
                scenario_id,
                gold_actions,
            )
            for variant in variants:
                chain = _materialize_chain(
                    doc,
                    G,
                    scenario_id,
                    gold_actions,
                    variant["ops"],
                    variant["pattern"],
                    variant["source"],
                )
                if chain is None:
                    continue
                signature = "|".join(f"{step['layer']}:{step['op']}" for step in chain["chain"])
                if signature in seen_sig:
                    continue
                seen_sig.add(signature)
                scenario_chains.append(chain)
                if len(scenario_chains) >= target:
                    break

        attempts = 0
        while len(scenario_chains) < target and attempts < target * 10:
            pattern = patterns[attempts % len(patterns)] if patterns else "investigate_then_act"
            ops = _build_graph_guided_ops(doc, G, gold_actions, rng, pattern)
            chain = _materialize_chain(
                doc,
                G,
                scenario_id,
                gold_actions,
                ops,
                pattern,
                "graph_guided",
            )
            attempts += 1
            if chain is None:
                continue
            signature = "|".join(f"{step['layer']}:{step['op']}" for step in chain["chain"])
            if signature in seen_sig:
                continue
            seen_sig.add(signature)
            scenario_chains.append(chain)

        chains.extend(scenario_chains)

    return chains


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", help="single env name")
    parser.add_argument("--n", type=int, default=8, help="chains per env (default 8)")
    parser.add_argument("--seed", type=int, default=0, help="rng seed (default 0)")
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="skip cached/online LLM chain variants and use graph-guided sampling only",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    use_llm = (not args.no_llm) and llm_available()
    log.info("LLM chain variants: %s", "ON" if use_llm else "OFF (graph-guided)")

    doc_files = sorted(
        path for path in DOCS_DIR.glob("*.json") if path.stem != "_scaffold_tools"
    )
    if args.env:
        doc_files = [path for path in doc_files if path.stem == args.env]
        if not doc_files:
            log.error("no doc for --env %s", args.env)
            return 1

    total = 0
    for doc_path in doc_files:
        env = doc_path.stem
        chains = process_env(env, args.n, rng, use_llm=use_llm)
        if chains:
            out_path = OUT_DIR / f"{env}.jsonl"
            out_path.write_text(
                "\n".join(json.dumps(chain, ensure_ascii=False) for chain in chains),
                encoding="utf-8",
            )
        log.info("%-34s chains=%d", env, len(chains))
        total += len(chains)

    print(f"\nDone. Chains: {total} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
