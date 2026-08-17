# Security Monitoring Environment

`security_envs` is a CLI-first training environment for intrusion detection and response tasks:

1. Detect intrusion through zone sensors and alerts
2. Lock doors and arm zones to contain the threat
3. Place emergency calls to authorities
4. Capture evidence and notify security contacts

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
python -m security_envs.cli prepare-rollout --scenario-id intrusion_response --show-bindings
```

The returned bindings should be injected into the rollout process:

- `SECURITY_SESSION_ID`
- `SECURITY_STATE_ROOT`
- `SECURITY_SCENARIO_ID`

## Agent Commands

After the rollout is prepared, the agent uses the CLI without session arguments:

```bash
python -m security_envs.cli status
python -m security_envs.cli doors list
python -m security_envs.cli doors lock-all
python -m security_envs.cli zones arm-all
python -m security_envs.cli alerts check
python -m security_envs.cli emergency dial --type police --description "Intrusion detected" --location "Main Building"
python -m security_envs.cli evidence save --type photo --description "Evidence of breach" --source camera_01
python -m security_envs.cli notifications compose --recipient "Security Team" --contact "555-0100" --alert-id alert_001
python -m security_envs.cli evaluate
```

## Data Layout

- `data/accounts.json`: workspace account profile and tone
- `data/contacts/contacts.json`: security contacts for notifications
- `data/doors/doors.json`: door sensor and lock status
- `data/zones/zones.json`: security zone configuration and sensors
- `data/scenarios/*.json`: scenario prompts and rollout configuration

## Concurrency Test

Use the stress script to validate isolation and locking:

```bash
python -m security_envs.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/security_envs_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session