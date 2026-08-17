from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from without_skill._shared.base_env import LoggedEnvironmentBase, utc_now_iso
from without_skill._shared.json_repository import load_json
from without_skill._shared.records import append_indexed_record, list_indexed_records, make_action_record_id


class ResumeRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent
        self.data_root = base_root.resolve()
        self.accounts_file = self.data_root / "data" / "accounts.json"
        self.contacts_file = self.data_root / "data" / "contacts.json"
        self.attachments_file = self.data_root / "data" / "attachments.json"
        self.candidates_file = self.data_root / "data" / "candidates" / "candidates.json"
        self.jobs_file = self.data_root / "data" / "jobs" / "jobs.json"
        self.attachments_dir = self.data_root / "data" / "attachments"
        self.scenario_dir = self.data_root / "data" / "scenarios"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.accounts_file)
        return {item["account_id"]: item for item in payload["accounts"]}

    def load_contacts(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.contacts_file)
        return {item["contact_id"]: item for item in payload["contacts"]}

    def load_attachment_manifest(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.attachments_file)
        return {item["path"]: item for item in payload["attachments"]}

    def load_candidates(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.candidates_file)
        return {item["candidate_id"]: item for item in payload["candidates"]}

    def load_jobs(self) -> dict[str, dict[str, Any]]:
        payload = load_json(self.jobs_file)
        return {item["job_id"]: item for item in payload["jobs"]}

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        return load_json(self.scenario_dir / f"{scenario_id}.json")

    def list_scenarios(self) -> list[dict[str, Any]]:
        return [load_json(path) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_attachment(self, relative_path: str) -> str:
        attachment_path = self.attachments_dir / relative_path
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {relative_path}")
        return attachment_path.read_text(encoding="utf-8")


class ResumeInterviewSchedulerEnvironment(LoggedEnvironmentBase):
    state_root_env_var = "RESUME_INTERVIEW_SCHEDULER_STATE_ROOT"
    default_state_dir_name = ".resume_interview_scheduler_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        self.repository = ResumeRepository(data_root)
        super().__init__(state_root=state_root)
        self.accounts = self.repository.load_accounts()
        self.contacts = self.repository.load_contacts()
        self.attachment_manifest = self.repository.load_attachment_manifest()

    def list_candidates(self, session_id: str, *, query: str = "", limit: int | None = None) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            results = []
            for candidate in session["candidates"]:
                searchable = " ".join([candidate["candidate_name"], " ".join(candidate["skills"])])
                if query and query.lower() not in searchable.lower():
                    continue
                results.append({"candidate_id": candidate["candidate_id"], "candidate_name": candidate["candidate_name"], "skills": candidate["skills"]})
                self._append_unique(session["observations"]["candidate_ids_seen"], candidate["candidate_id"])
            return results[:limit] if limit is not None else results
        return self._run_logged_action(session_id, "list_candidates", {"query": query}, handler)

    def get_candidate(self, session_id: str, candidate_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for candidate in session["candidates"]:
                if candidate["candidate_id"] == candidate_id:
                    self._append_unique(session["observations"]["candidate_ids_seen"], candidate_id)
                    return deepcopy(candidate)
            raise KeyError(f"Candidate not found: {candidate_id}")
        return self._run_logged_action(session_id, "get_candidate", {"candidate_id": candidate_id}, handler)

    def list_jobs(self, session_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> list[dict[str, Any]]:
            return [{"job_id": job["job_id"], "title": job["title"], "required_skills": job["required_skills"]} for job in session["jobs"]]
        return self._run_logged_action(session_id, "list_jobs", {}, handler)

    def get_job(self, session_id: str, job_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            for job in session["jobs"]:
                if job["job_id"] == job_id:
                    self._append_unique(session["observations"]["job_ids_seen"], job_id)
                    return deepcopy(job)
            raise KeyError(f"Job not found: {job_id}")
        return self._run_logged_action(session_id, "get_job", {"job_id": job_id}, handler)

    def read_attachment(self, session_id: str, attachment_path: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            metadata = deepcopy(self.attachment_manifest[attachment_path])
            metadata["content"] = self.repository.read_attachment(attachment_path)
            self._append_unique(session["observations"]["attachments_read"], attachment_path)
            return metadata
        return self._run_logged_action(session_id, "read_attachment", {"attachment_path": attachment_path}, handler)

    def match_candidate(self, session_id: str, candidate_id: str, job_id: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], _event_at: str, _action_index: int) -> dict[str, Any]:
            candidate = next(item for item in session["candidates"] if item["candidate_id"] == candidate_id)
            job = next(item for item in session["jobs"] if item["job_id"] == job_id)
            overlap = sorted(set(candidate["skills"]) & set(job["required_skills"]))
            score = round((len(overlap) / len(job["required_skills"])) * 100, 2)
            self._append_unique(session["observations"]["candidate_ids_seen"], candidate_id)
            self._append_unique(session["observations"]["job_ids_seen"], job_id)
            return {"candidate_id": candidate_id, "job_id": job_id, "match_score": score, "matched_skills": overlap}
        return self._run_logged_action(session_id, "match_candidate", {"candidate_id": candidate_id, "job_id": job_id}, handler)

    def schedule_interview(self, session_id: str, candidate_id: str, job_id: str, slot: str) -> dict[str, Any]:
        def handler(session: dict[str, Any], event_at: str, action_index: int) -> dict[str, Any]:
            entry = {
                "invite_id": make_action_record_id("invite", action_index),
                "record_type": "interview_invite",
                "created_at": event_at,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "slot": slot,
            }
            append_indexed_record(session, collection_name="schedule_entries", index_name="schedule_entry_index", id_field="invite_id", record=entry)
            reminder = {
                "reminder_id": make_action_record_id("reminder", action_index),
                "record_type": "schedule_reminder",
                "created_at": event_at,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "slot": slot,
            }
            append_indexed_record(session, collection_name="reminders", index_name="reminder_index", id_field="reminder_id", record=reminder)
            return {"invite": deepcopy(entry), "reminder": deepcopy(reminder)}
        return self._run_logged_action(session_id, "schedule_interview", {"candidate_id": candidate_id, "job_id": job_id, "slot": slot}, handler)

    def evaluate_session(self, session_id: str) -> dict[str, Any]:
        from .evaluator import evaluate_session
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return evaluate_session(session, scenario)

    def _build_session_payload(self, *, session_id: str, scenario: dict[str, Any]) -> dict[str, Any]:
        all_candidates = self.repository.load_candidates()
        all_jobs = self.repository.load_jobs()
        attachments = [deepcopy(self.attachment_manifest[path]) for path in scenario.get("attachment_paths", []) if path in self.attachment_manifest]
        return {
            "session_id": session_id,
            "scenario_id": scenario["scenario_id"],
            "created_at": utc_now_iso(),
            "meta": {"base_time": scenario["current_time"], "action_index": 0},
            "workspace_account": deepcopy(self.accounts[scenario["workspace_account_id"]]),
            "candidates": [deepcopy(all_candidates[cid]) for cid in scenario["candidate_ids"]],
            "jobs": [deepcopy(all_jobs[jid]) for jid in scenario["job_ids"]],
            "attachments": attachments,
            "contacts": [deepcopy(item) for item in self.contacts.values()],
            "schedule_entries": [],
            "schedule_entry_index": {},
            "reminders": [],
            "reminder_index": {},
            "observations": {
                "candidate_ids_seen": [],
                "job_ids_seen": [],
                "attachments_read": [],
            },
            "actions": [],
        }

    def _build_task_payload(self, session_id: str, session: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "task_prompt": scenario["task_prompt"],
            "workspace_account": session["workspace_account"],
            "candidate_count": len(session["candidates"]),
            "job_count": len(session["jobs"]),
        }

    def session_summary(self, session_id: str) -> dict[str, Any]:
        session = self.store.load_session(session_id)
        scenario = self.repository.load_scenario(session["scenario_id"])
        return {
            "session_id": session_id,
            "scenario_id": session["scenario_id"],
            "title": scenario["title"],
            "workspace_account": session["workspace_account"],
            "state_root": str(self.store.state_root),
            "invite_count": len(session["schedule_entries"]),
            "reminder_count": len(session["reminders"]),
            "action_count": len(session["actions"]),
        }
