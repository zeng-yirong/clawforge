# Itinerary Planning Environment

A synthetic training environment for RL agents to practice multi-city trip planning, route optimization, and travel preference management.

## Task Description

The agent acts as a travel assistant managing itinerary planning. Tasks include:
- Loading and searching city information
- Finding optimal routes between cities
- Comparing transport options (flights, trains, buses)
- Planning multi-stop transfers
- Generating detailed itineraries
- Optimizing routes based on preferences (cost, time, balanced)

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
    ["python", "-m", "itinerary_envs.cli", "prepare-rollout", "--scenario-id", "itinerary_planning", "--show-bindings"],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `list-cities` | List all available cities |
| `load-city` | Load details for a specific city |
| `search-routes` | Search routes between origin and destination |
| `compare-transport` | Compare transport options for a route |
| `plan-transfer` | Plan multi-stop transfer with waypoints |
| `generate-itinerary` | Generate detailed itinerary from routes |
| `optimize-route` | Optimize route based on criteria |
| `session-summary` | Show session progress |
| `evaluate` | Score the session (trainer only) |

## Trainer-Only Commands (hidden from agent)

- `prepare-rollout` - Create new session
- `reset-rollout` - Reset existing session
- `evaluate` - Get reward score

## Environment Variables

- `ITINERARY_SESSION_ID` - Session binding (injected by trainer)
- `ITINERARY_STATE_ROOT` - State directory
- `ITINERARY_SCENARIO_ID` - Scenario ID

## Running Tests

```bash
python -m itinerary_envs.concurrency_test
```
