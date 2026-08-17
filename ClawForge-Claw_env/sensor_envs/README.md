# Sensor Monitoring Environment

`sensor_envs` is a CLI-first training environment for this task:

1. Monitor real-time sensor data (temperature, humidity, air quality, energy).
2. Detect anomalies and create alerts.
3. Generate reports (hourly/daily/monthly) and perform trend analysis.
4. Send notifications based on alerts and anomalies.

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
python -m sensor_envs.cli prepare-rollout --scenario-id sensor_monitoring --show-bindings
```

The returned bindings should be injected into the rollout process:

- `SENSOR_SESSION_ID`
- `SENSOR_STATE_ROOT`
- `SENSOR_SCENARIO_ID`

## Agent Commands

After the rollout is prepared, the agent uses the CLI without session arguments:

```bash
python -m sensor_envs.cli sensors list
python -m sensor_envs.cli sensors read <sensor_id>
python -m sensor_envs.cli monitoring check
python -m sensor_envs.cli alerts list --status active
python -m sensor_envs.cli reports hourly
python -m sensor_envs.cli trends analyze <sensor_id>
python -m sensor_envs.cli notifications create --type anomaly --recipient "ops" --contact "ops@example.com" --subject "Alert" --body "Details"
python -m sensor_envs.cli info
python -m sensor_envs.cli evaluate
```

## Data Layout

- `data/accounts.json`: workspace account profile and tone.
- `data/sensors/sensors.json`: sensor definitions with thresholds and initial values.
- `data/locations/`: location metadata.
- `data/scenarios/sensor_monitoring.json`: scenario prompts and rollout configuration.

## Concurrency Test

Use the stress script to validate isolation and locking:

```bash
python -m sensor_envs.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/sensor_envs_report.json
```

It checks both:

- isolated parallel sessions
- multi-worker contention on a shared session