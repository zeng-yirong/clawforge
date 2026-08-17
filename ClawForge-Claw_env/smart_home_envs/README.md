# Smart Home Energy-Aware Climate Control Environment

A synthetic RL training environment for managing smart home climate control with energy awareness.

## Scenario

The agent manages a smart home environment with multiple devices (air conditioners, humidifiers, smart plugs). The goal is to control climate devices optimally given electricity pricing, weather conditions, and user health preferences.

## Session Model

Each rollout sample is bound to a single session:

```
session_id: auto-generated or trainer-supplied
scenario_id: references data/scenarios/<id>.json
state_root: directory where session state is persisted
```

Session state is stored as JSON under `<state_root>/<session_id>/session.json` with a lock file for concurrency safety.

## Trainer Bootstrap

The trainer must prepare a rollout session before launching agents:

```bash
python -m smart_home_envs.cli prepare-rollout --scenario-id energy_aware_climate --show-bindings
```

Response:
```json
{
  "status": "success",
  "data": {
    "session_id": "smh-20250612T120000Z-1234",
    "scenario_id": "energy_aware_climate",
    "state_root": "/path/to/state",
    "bindings": {
      "SMART_HOME_SESSION_ID": "smh-...",
      "SMART_HOME_STATE_ROOT": "/path/to/state",
      "SMART_HOME_SCENARIO_ID": "energy_aware_climate"
    }
  }
}
```

Inject bindings into the agent process environment, then run agent commands without `--session-id`.

To reset a session for a new rollout:
```bash
python -m smart_home_envs.cli reset-rollout
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SMART_HOME_SESSION_ID` | Active session identifier |
| `SMART_HOME_STATE_ROOT` | Directory for session state files |
| `SMART_HOME_SCENARIO_ID` | Scenario to load for new sessions |

## Agent Commands

Agent-visible commands (available without `--session-id`):

| Command | Description |
|---------|-------------|
| `list-scenarios` | List available scenarios |
| `task` | Show current task prompt and workspace summary |
| `get-weather` | Get current weather information |
| `analyze-weather-comfort` | Analyze weather comfort level |
| `get-weather-forecast` | Get weather forecast |
| `check-extreme-weather` | Check for extreme weather conditions |
| `get-electricity-rate` | Get current electricity rate |
| `get-daily-rate-schedule` | Get daily electricity rate schedule |
| `get-optimal-window` | Get optimal operation window for device |
| `check-cost-saving` | Check cost saving opportunities |
| `get-user-health` | Get user health profile |
| `analyze-health-conflicts` | Analyze health-comfort conflicts |
| `get-health-recommendations` | Get health-based recommendations |
| `check-health-alerts` | Check health alerts |
| `get-device-status` | Get device status |
| `get-all-devices` | Get all devices |
| `get-devices-by-type` | Get devices by type |
| `set-air-conditioner` | Set air conditioner settings |
| `set-humidifier` | Set humidifier settings |
| `set-smart-plug` | Set smart plug state |
| `turn-off-device` | Turn off a device |
| `calculate-power-consumption` | Calculate device power consumption |
| `get-recommended-temperature` | Get recommended temperature |
| `session-summary` | Show session progress and summary |

## Concurrency Testing

Run stress tests to verify session isolation and locking:

```bash
python smart_home_envs/concurrency_test.py --mode both --sessions 32 --workers 8
```

Options:
- `--mode`: `isolated`, `contention`, or `both`
- `--sessions`: Number of isolated sessions to create
- `--workers`: Number of concurrent workers
- `--executor`: `threads` or `processes`
- `--keep-state`: Retain state directory after test
