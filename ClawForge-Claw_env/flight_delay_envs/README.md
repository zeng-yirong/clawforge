# Flight Delay Cascade Management Environment

A synthetic training environment for RL agents to practice managing cascading flight delays and their downstream effects on hotel bookings, transport reservations, and traveler notifications.

## Task Description

The agent acts as a travel coordinator handling flight delay cascades. Tasks include:
- Detecting and analyzing flight delays
- Identifying affected hotel bookings
- Rescheduling transport bookings
- Composing and sending delay notifications to travelers
- Managing conference attendee updates

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
    ["python", "-m", "flight_delay_envs.cli", "prepare-rollout", "--scenario-id", "flight_delay_cascade", "--show-bindings"],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `list-flights` | List available flights |
| `get-flight` | Get detailed flight information |
| `check-flight-status` | Check flight status and delay info |
| `detect-delayed-flights` | Detect all delayed flights |
| `get-affected-connections` | Get affected hotel/transport bookings |
| `list-hotel-bookings` | List hotel bookings |
| `get-hotel-booking` | Get hotel booking details |
| `create-hotel-booking` | Create new hotel booking |
| `adjust-hotel-booking` | Adjust hotel check-in/check-out times |
| `cancel-hotel-booking` | Cancel hotel booking |
| `list-transport-bookings` | List transport bookings |
| `get-transport-booking` | Get transport booking details |
| `create-transport-booking` | Create transport booking |
| `reschedule-transport-booking` | Reschedule transport pickup time |
| `cancel-transport-booking` | Cancel transport booking |
| `list-notifications` | List notifications |
| `get-notification` | Get notification details |
| `compose-delay-notification` | Compose delay notification |
| `send-notification` | Send notification |
| `list-conferences` | List conferences |
| `get-conference` | Get conference details |
| `list-attendees` | List conference attendees |
| `notification-stats` | Get notification statistics |
| `session-summary` | Show session progress |

## Trainer-Only Commands (hidden from agent)

- `prepare-rollout` - Create new session
- `reset-rollout` - Reset existing session

## Environment Variables

- `FLIGHT_DELAY_SESSION_ID` - Session binding (injected by trainer)
- `FLIGHT_DELAY_STATE_ROOT` - State directory
- `FLIGHT_DELAY_SCENARIO_ID` - Scenario ID

## Running Tests

```bash
python -m flight_delay_envs.concurrency_test
```
