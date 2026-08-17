# Finance Investment Brief Environment

`finance_envs` is a CLI-first training environment for this task:

1. Analyze market data, news, and earnings for a assigned sector.
2. Generate a multi-dimensional investment brief with recommendations.
3. Submit the brief for review.

The environment is built for parallel rollout:

- each rollout owns one isolated session
- session state is file-backed under a configurable state root
- mutable state is protected by a per-session lock
- there is no shared Flask process or port coordination

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample.
- The trainer binds that session through environment variables.
- Agent commands do not need `--session-id`.

Trainer bootstrap:

```bash
python -m finance_envs.cli prepare-rollout --scenario-id multi_dim_brief_tech_sector --show-bindings --show-task
```

The returned bindings should be injected into the rollout process:

- `FINANCE_SESSION_ID`
- `FINANCE_STATE_ROOT`
- `FINANCE_SCENARIO_ID`

## Agent Commands

After the rollout is prepared, the agent uses the CLI without session arguments:

```bash
python -m finance_envs.cli task
python -m finance_envs.cli list-stocks
python -m finance_envs.cli get-stock --symbol TECH
python -m finance_envs.cli screen-stocks --sector Technology --analyst-rating Buy
python -m finance_envs.cli list-news
python -m finance_envs.cli get-news --news-id news_001
python -m finance_envs.cli list-earnings
python -m finance_envs.cli get-earnings --earnings-id earn_001
python -m finance_envs.cli create-earnings-summary --sector Technology
python -m finance_envs.cli generate-sector-overview --sector Technology
python -m finance_envs.cli provide-recommendations --sector Technology
python -m finance_envs.cli create-brief --ticker TECH --title "Tech Sector Brief" ...
python -m finance_envs.cli update-brief --brief-id brief_001 ...
python -m finance_envs.cli submit-brief --brief-id brief_001
python -m finance_envs.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and permissions.
- `data/contacts.json`: analysts and stakeholders.
- `data/stocks/*.json`: stock market data.
- `data/news/*.json`: financial news articles.
- `data/earnings/*.json`: earnings reports and guidance.
- `data/analysts/*.json`: analyst profiles.
- `data/briefs/*.json`: sample investment briefs.
- `data/scenarios/*.json`: scenario prompts and rollout configuration.

## Concurrency Test

Use the stress script to validate isolation and locking:

```bash
python -m finance_envs.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/finance_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session
