# Device Scheduling Environment

A synthetic training environment for RL agents to practice smart device scheduling and automation tasks.

## Task Description

The agent acts as a home automation assistant managing device schedules. Tasks include:
- Controlling devices (lights, AC, humidifiers, smart plugs)
- Creating and managing device schedules
- Executing scheduled tasks
- Monitoring device status and scheduling metrics

## Session Model

Each rollout uses an isolated session stored as JSON:
```
<state_root>/<session_id>/session.json
```

Sessions are created by the trainer and bound via environment variables, not visible to the agent.

## Trainer Bootstrap

```python
import json
import subprocess

result = subprocess.run(
    ["python", "-m", "scheduling_envs.cli", "prepare-rollout", "--scenario-id", "device_scheduling", "--show-bindings"],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `list-devices` | List all devices |
| `get-device` | Get device status |
| `turn-on-device` | Turn on a device |
| `turn-off-device` | Turn off a device |
| `control-light` | Control a light |
| `control-ac` | Control AC |
| `control-humidifier` | Control humidifier |
| `control-plug` | Control smart plug |
| `list-schedules` | List all schedules |
| `get-schedule` | Get schedule details |
| `create-schedule` | Create a new schedule |
| `enable-schedule` | Enable a schedule |
| `disable-schedule` | Disable a schedule |
| `delete-schedule` | Delete a schedule |
| `execute-tasks` | Execute scheduled tasks |
| `upcoming-tasks` | Get upcoming tasks |
| `task-history` | Get execution history |
| `scheduling-status` | Get scheduling status |
| `session-summary` | Show session progress |

## Trainer-Only Commands (hidden from agent)

- `prepare-rollout` - Create new session
- `reset-rollout` - Reset existing session

## Environment Variables

- `SCHEDULING_SESSION_ID` - Session binding (injected by trainer)
- `SCHEDULING_STATE_ROOT` - State directory
- `SCHEDULING_SCENARIO_ID` - Scenario ID

## Running Tests

```bash
python -m scheduling_envs.concurrency_test
```
