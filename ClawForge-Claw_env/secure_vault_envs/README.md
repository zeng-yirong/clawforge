# Secure Vault Environment

A synthetic training environment for RL agents to practice password management, credential storage, and autofill automation.

## Task Description

The agent acts as a secure credential manager. Tasks include:
- Generating secure passwords
- Storing and retrieving credentials
- Managing credential categories
- Setting up autofill rules
- Checking password strength

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
    ["python", "-m", "secure_vault_envs.cli", "prepare-rollout", "--scenario-id", "credential_management", "--show-bindings"],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `generate-password` | Generate a secure password |
| `store-credential` | Store a credential |
| `retrieve-credential` | Retrieve a credential |
| `list-credentials` | List all credentials |
| `classify-credential` | Classify credential into category |
| `setup-autofill` | Setup autofill for platform |
| `check-strength` | Check password strength |
| `session-summary` | Show session progress |
| `evaluate` | Score the session (trainer only) |

## Trainer-Only Commands (hidden from agent)

- `prepare-rollout` - Create new session
- `reset-rollout` - Reset existing session
- `evaluate` - Get reward score

## Environment Variables

- `VAULT_SESSION_ID` - Session binding (injected by trainer)
- `VAULT_STATE_ROOT` - State directory
- `VAULT_SCENARIO_ID` - Scenario ID

## Running Tests

```bash
python -m secure_vault_envs.concurrency_test
```
