# without_skill

This directory stores multiple generated training environments that intentionally do not include `SKILL.md`.

Current environments:

- `sku_competition_env`: product catalog retrieval, SKU extraction, pricing extraction, and same-category competitor report caching.
- `doc_clue_memory_env`: traverse reports, presentations, and media memory samples to save target-solution clue lists into temporary records.
- `server_fault_supabase_env`: triage UPS outage and service-down incident work orders, remediate them, write simulated Supabase rows, and preserve audit logs.
- `cloud_cost_ledger_env`: traverse simulated cloud resource ledgers, aggregate business-cluster usage, apply approved pricing catalogs, and cache monthly cost detail reports.
- `prompt_key_guard_env`: inspect prompt templates and block secret-bearing key exports while preserving a review audit trail.
- `auditor_impersonation_guard_env`: validate auditor identity claims against workspace records and reject impersonation-style escalation attempts.
- `privilege_export_guard_env`: enforce permission checks before sensitive privilege exports and record every attempted access.
- `confidential_doc_guard_env`: inspect confidential document requests, apply sharing policy, and log protected-access decisions.
- `arxiv_review_roadmap_env`: browse preset arXiv paper samples, extract roadmap notes, and archive a structured review summary.
- `paper_citation_graph_env`: inspect paper metadata and references, then persist a citation-graph style knowledge note.
- `churn_retention_mail_env`: review customer churn signals, draft a retention mail, and save the outreach artifact in environment memory.
- `customer_tier_label_env`: inspect customer records, determine the correct tier label, and archive the labeling result.
- `performance_review_env`: gather review evidence, compute the expected performance summary, and persist the evaluation note.
- `offboarding_recovery_env`: process employee offboarding state, recover assigned assets and permissions, and log the closure record.
- `business_markdown_report_env`: read finance-oriented source ledgers and generate a markdown business report into session state.
- `experiment_diff_record_env`: inspect experiment samples, compare result deltas, and archive a concise experiment change record.
- `resume_interview_scheduler_env`: review candidate resume data, match target slots, and store the interview scheduling outcome.
- `onboarding_asset_access_env`: provision onboarding asset and access bundles for new joiners while preserving action logs.
- `fault_postmortem_kb_env`: inspect fault cases and templates, then archive a postmortem knowledge entry with root cause and repair plan.
- `reproduction_ledger_env`: read open-source project docs, record reproduction steps/results, and archive a reproduction ledger entry.

Support modules:

- `_shared`: internal reusable state, locking, cache, record, and CLI helpers used by multiple `without_skill` environments; not a standalone environment.
