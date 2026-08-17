"""Execute LLM-generated graph code to produce tool dependency graphs.

Reads tool definitions from tool_env_docs/ and LLM-generated graph code from
source_env/, executes the code in a sandboxed namespace to build NetworkX
DiGraphs, and serializes them to tool_env_graphs/.

Usage:
    cd AgentRl
    python build_graphs.py                    # all envs
    python build_graphs.py --env web_search   # single env
    python build_graphs.py --dry-run          # print stats only
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import networkx as nx
from networkx.readwrite import json_graph as nx_json_graph

log = logging.getLogger(__name__)

AUTH_KEYWORDS = {"login", "logout", "authenticate", "auth", "get_login_status"}


def is_auth(func_name: str) -> bool:
    return any(kw in func_name.lower() for kw in AUTH_KEYWORDS)


# ── Graph builder ───────────────────────────────────────────────────────

def build_graph(env_name: str, tool_defs: list, code: str) -> nx.DiGraph:
    """Build a tool dependency graph by executing LLM-generated code.

    Creates the NetworkX DiGraph, adds nodes and auth edges, then exec()s
    the LLM code to add semantic edges.
    """
    G = nx.DiGraph()

    for tool in tool_defs:
        G.add_node(tool["name"], name=tool["name"],
                   **{k: v for k, v in tool.items() if k != "name"})

    funcs = [t["name"] for t in tool_defs]

    # Auth -> all non-auth
    auths = {n for n in funcs if is_auth(n)}
    non_auth = [n for n in funcs if n not in auths]
    for a in auths:
        for t in non_auth:
            G.add_edge(a, t, weight=0.5, relationship="auth_provides_access_to")

    if len(non_auth) >= 2 and code:
        exec_namespace = {
            "G": G,
            "tools": tool_defs,
            "json_graph": nx_json_graph,
            "nx": nx,
        }
        try:
            exec(code, exec_namespace)
            log.info("  Edges: %d", G.number_of_edges())
        except Exception as e:
            log.warning("  LLM code exec failed for %s: %s", env_name, e)

    return G


# ── Code file loader ────────────────────────────────────────────────────

def load_graph_code(code_path: Path) -> Optional[str]:
    """Load LLM-generated graph code from a cache file, stripping metadata."""
    if not code_path.exists():
        return None
    text = code_path.read_text(encoding="utf-8")
    if text.startswith("#"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    return text.strip() or None


# ── Main ────────────────────────────────────────────────────────────────

def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--env", help="Single env name")
    p.add_argument("--start", help="Start env name (alphabetical range)")
    p.add_argument("--stop", help="Stop  env name (alphabetical range, inclusive)")
    args = p.parse_args()

    root = Path(__file__).parent
    source_dir = root / "source_env"
    docs_dir = root / "env_chains" / "tool_env_docs"
    out_dir = root / "env_chains" / "tool_env_graphs"
    out_dir.mkdir(parents=True, exist_ok=True)

    tool_doc_files = sorted(docs_dir.glob("*.json"))
    tool_doc_files = [f for f in tool_doc_files if f.stem != "env_docs"]

    total_graphs = 0
    total_tools = 0

    for doc_file in tool_doc_files:
        env_name = doc_file.stem

        if args.env and env_name != args.env:
            continue
        if args.start and env_name < args.start:
            continue
        if args.stop and env_name > args.stop:
            continue

        code_path = source_dir / f"{env_name}_graph_code_cache.py"
        code = load_graph_code(code_path)

        if code is None:
            log.warning("  SKIP %s: no graph code file", env_name)
            continue

        tool_defs = json.loads(doc_file.read_text(encoding="utf-8"))
        log.info("Processing: %s (%d tools)", env_name, len(tool_defs))

        G = build_graph(env_name, tool_defs, code)

        if args.dry_run:
            log.info("  nodes=%d edges=%d", G.number_of_nodes(), G.number_of_edges())
            total_graphs += 1
            total_tools += G.number_of_nodes()
            continue

        graph_data = nx.node_link_data(G)
        out_path = out_dir / f"{env_name}_tool_graph.json"
        out_path.write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info("  graph -> %s", out_path.name)

        total_graphs += 1
        total_tools += G.number_of_nodes()

    print(f"\nDone. Graphs: {total_graphs}, Tools: {total_tools}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
