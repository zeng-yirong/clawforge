from __future__ import annotations

from pathlib import Path
from typing import Any

from without_skill._shared.paper_memory import PaperMemoryEnvironmentBase, append_paper_cache_entry


def _unique_keywords(papers: list[dict[str, Any]], limit: int = 5) -> list[str]:
    seen: list[str] = []
    for paper in papers:
        for keyword in paper.get("keywords", []):
            keyword_str = str(keyword)
            if keyword_str not in seen:
                seen.append(keyword_str)
            if len(seen) >= limit:
                return seen
    return seen


class ArxivReviewRoadmapEnvironment(PaperMemoryEnvironmentBase):
    state_root_env_var = "ARXIV_REVIEW_ROADMAP_STATE_ROOT"
    default_state_dir_name = ".arxiv_review_roadmap_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        resolved_data_root = Path(data_root) if data_root is not None else Path(__file__).parent
        super().__init__(data_root=resolved_data_root, state_root=state_root)

    def generate_review(
        self,
        session_id: str,
        *,
        direction: str,
        paper_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            selected = [
                paper
                for paper in session["papers"]
                if str(paper["direction"]).lower() == direction.lower()
                and (paper_ids is None or paper["paper_id"] in paper_ids)
            ]
            if not selected:
                raise ValueError(f"No papers found for direction: {direction}")

            selected.sort(key=lambda item: (-int(item["year"]), str(item["paper_id"])))
            keywords = _unique_keywords(selected, limit=4)
            mermaid_lines = ["graph TD"]
            for idx, keyword in enumerate(keywords):
                mermaid_lines.append(f"  K{idx}[{keyword}]")
                if idx > 0:
                    mermaid_lines.append(f"  K{idx-1} --> K{idx}")

            markdown_lines = [
                f"# Review: {direction}",
                "",
                "## Selected Papers",
            ]
            for paper in selected:
                markdown_lines.extend(
                    [
                        f"- **{paper['title']}** ({paper['year']})",
                        f"  - Abstract: {paper['abstract']}",
                    ]
                )

            payload = {
                "direction": direction,
                "paper_ids": [paper["paper_id"] for paper in selected],
                "paper_count": len(selected),
                "review_markdown": "\n".join(markdown_lines),
                "roadmap_mermaid": "\n".join(mermaid_lines),
            }
            return append_paper_cache_entry(
                session,
                cache_key=f"review::{direction}",
                entry_type="arxiv_direction_review",
                payload=payload,
                event_at=event_at,
                action_index=action_index,
            )

        return self._run_logged_action(
            session_id,
            "generate_review",
            {"direction": direction, "paper_ids": paper_ids},
            handler,
        )

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session

        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)
