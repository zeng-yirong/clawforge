from __future__ import annotations

from pathlib import Path

from without_skill._shared.paper_memory import PaperMemoryEnvironmentBase, append_paper_cache_entry


class PaperCitationGraphEnvironment(PaperMemoryEnvironmentBase):
    state_root_env_var = "PAPER_CITATION_GRAPH_STATE_ROOT"
    default_state_dir_name = ".paper_citation_graph_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        resolved_data_root = Path(data_root) if data_root is not None else Path(__file__).parent
        super().__init__(data_root=resolved_data_root, state_root=state_root)

    def generate_citation_graph(
        self,
        session_id: str,
        *,
        paper_ids: list[str] | None = None,
    ) -> dict[str, object]:
        def handler(session: dict[str, object], event_at: str, action_index: int) -> dict[str, object]:
            selected = [
                paper
                for paper in session["papers"]
                if paper_ids is None or paper["paper_id"] in paper_ids
            ]
            if not selected:
                raise ValueError("No papers available for citation graph generation.")

            node_ids = [paper["paper_id"] for paper in selected]
            edges: list[dict[str, str]] = []
            mermaid_lines = ["graph LR"]
            for paper in selected:
                mermaid_lines.append(f"  {paper['paper_id']}[{paper['paper_id']}]")
                for cited in paper.get("citation_ids", []):
                    if cited in node_ids:
                        edges.append({"source": paper["paper_id"], "target": cited})
                        mermaid_lines.append(f"  {paper['paper_id']} --> {cited}")

            payload = {
                "paper_ids": node_ids,
                "node_count": len(node_ids),
                "edge_count": len(edges),
                "edges": edges,
                "graph_mermaid": "\n".join(mermaid_lines),
            }
            return append_paper_cache_entry(
                session,
                cache_key="citation_graph::snapshot",
                entry_type="paper_citation_graph",
                payload=payload,
                event_at=event_at,
                action_index=action_index,
            )

        return self._run_logged_action(
            session_id,
            "generate_citation_graph",
            {"paper_ids": paper_ids},
            handler,
        )

    def evaluate_session(self, session_id: str) -> dict[str, object]:
        from .evaluator import evaluate_session

        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)
