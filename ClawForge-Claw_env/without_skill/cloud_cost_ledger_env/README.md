# Cloud Cost Ledger Environment

`cloud_cost_ledger_env` is a CLI-first training environment for this workflow:

1. Traverse a simulated cloud resource ledger.
2. Aggregate compute and storage usage for business clusters.
3. Apply the approved monthly pricing catalog.
4. Generate a monthly cost detail report and store it in session cache.
5. Preserve deterministic action logs for the entire rollout.

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
python -m without_skill.cloud_cost_ledger_env.cli prepare-rollout --scenario-id cloud_cluster_monthly_cost_q2_2026 --show-bindings --show-task
```

Returned bindings:

- `CLOUD_COST_LEDGER_SESSION_ID`
- `CLOUD_COST_LEDGER_STATE_ROOT`
- `CLOUD_COST_LEDGER_SCENARIO_ID`

## Agent Commands

After rollout preparation, the agent uses the CLI without session arguments:

```bash
python -m without_skill.cloud_cost_ledger_env.cli task
python -m without_skill.cloud_cost_ledger_env.cli list-clusters --cluster-role business
python -m without_skill.cloud_cost_ledger_env.cli list-ledger-entries --cluster-id cluster_retail_core
python -m without_skill.cloud_cost_ledger_env.cli list-pricing-catalogs --current-only
python -m without_skill.cloud_cost_ledger_env.cli get-pricing-catalog --catalog-id cat_apac_q2_2026_current
python -m without_skill.cloud_cost_ledger_env.cli read-attachment --attachment-path cost_accounting_rules.md
python -m without_skill.cloud_cost_ledger_env.cli aggregate-cluster-usage --cluster-id cluster_retail_core
python -m without_skill.cloud_cost_ledger_env.cli generate-cost-report --catalog-id cat_apac_q2_2026_current
python -m without_skill.cloud_cost_ledger_env.cli list-cache
python -m without_skill.cloud_cost_ledger_env.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and permissions.
- `data/contacts.json`: infrastructure finance and operations contacts.
- `data/attachments.json`: attachment manifest for accounting rules and report schema.
- `data/resources/*.json`: cluster metadata and simulated resource ledger entries.
- `data/pricing/pricing_catalogs.json`: archived and current pricing catalogs.
- `data/scenarios/*.json`: prompts and evaluation metadata.

## Cached Artifacts

Session cache stores two artifact types:

- `cluster_usage_aggregate`
- `monthly_cost_detail_report`

Use:

- `list-cache`
- `get-cache-entry`

## Concurrency Test

Use the stress script to validate session isolation and locking:

```bash
python -m without_skill.cloud_cost_ledger_env.concurrency_test --mode both --executor processes --sessions 16 --workers 6 --report-json ./.tmp/cloud_cost_ledger_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session
