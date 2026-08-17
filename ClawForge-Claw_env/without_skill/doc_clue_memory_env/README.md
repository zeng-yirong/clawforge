# Document Clue Memory Environment

`doc_clue_memory_env` is a CLI-first training environment for this workflow:

1. Traverse preset industry reports, presentation decks, and media copy memory samples.
2. Locate documents that match a target technology solution.
3. Collect associated document identifiers and clue bullets.
4. Save the clue list into environment temporary records.

The environment follows the rollout/session pattern defined in `claw_env_recipe.md`:

- each rollout owns one isolated session
- mutable state is file-backed under a configurable state root
- per-session locking protects concurrent writes
- agent commands do not require `--session-id`

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample.
- The trainer binds that session through environment variables.
- Agent commands read those bindings automatically.

Trainer bootstrap:

```bash
python -m without_skill.doc_clue_memory_env.cli prepare-rollout --scenario-id tech_solution_signal_trace_q2_2026 --show-bindings --show-task
```

Returned bindings:

- `DOC_CLUE_MEMORY_SESSION_ID`
- `DOC_CLUE_MEMORY_STATE_ROOT`
- `DOC_CLUE_MEMORY_SCENARIO_ID`

## Agent Commands

After rollout preparation, the agent uses the CLI without session arguments:

```bash
python -m without_skill.doc_clue_memory_env.cli task
python -m without_skill.doc_clue_memory_env.cli search-library --query "HelioSync Edge Inference Fabric"
python -m without_skill.doc_clue_memory_env.cli get-report --report-id rep_001
python -m without_skill.doc_clue_memory_env.cli get-presentation --presentation-id deck_001
python -m without_skill.doc_clue_memory_env.cli get-media-sample --sample-id media_001
python -m without_skill.doc_clue_memory_env.cli read-attachment --attachment-path solution_matching_notes.md
python -m without_skill.doc_clue_memory_env.cli save-clue-list --solution-id sol_heliosync_fabric --solution-name "HelioSync Edge Inference Fabric" --document-ids rep_001,rep_003,deck_001,media_001 --clues-json "[\"...\"]" --summary "..." --confidence high
python -m without_skill.doc_clue_memory_env.cli list-temp-records
python -m without_skill.doc_clue_memory_env.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and permissions.
- `data/contacts.json`: operating stakeholders.
- `data/attachments.json`: attachment manifest for scenario reading.
- `data/reports/reports.json`: industry report samples.
- `data/presentations/presentations.json`: presentation deck notes.
- `data/media_samples/media_samples.json`: media copy memory samples and transcripts.
- `data/attachments/*.md`: matching rules and temp record guidance.
- `data/scenarios/*.json`: scenario prompts and evaluation metadata.

## Temporary Record Model

Generated outputs are stored in `temp_records`:

- `clue_list`

Use `list-temp-records` to inspect summaries and `get-temp-record` to inspect the full saved payload.

## Concurrency Test

Use the stress script to validate session isolation and locking:

```bash
python -m without_skill.doc_clue_memory_env.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/doc_clue_memory_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session
