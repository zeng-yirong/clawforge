# Mail Client Automation Environment

A synthetic training environment for RL agents to practice automated email management tasks including classification, archiving, reply generation, and TODO extraction.

## Task Description

The agent acts as an AI assistant managing an email inbox. Tasks include:
- Classifying emails into appropriate folders (work, personal, spam, newsletter, finance, hr)
- Archiving emails that don't need action
- Reading important emails and attachments to extract key information
- Generating TODO items from actionable emails
- Replying to emails that require a response

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
    ["python", "-m", "mail_client_envs.cli", "prepare-rollout", "--show-bindings"],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `list-emails` | List emails with optional query/folder/label filters |
| `read-email` | Open an email and mark it as read |
| `read-attachment` | Read attachment content |
| `classify-email` | Classify email into folder with labels |
| `archive-email` | Archive an email |
| `delete-email` | Move email to trash |
| `list-todos` | List TODO items |
| `create-todo` | Create TODO from email |
| `complete-todo` | Mark TODO as completed |
| `create-reply` | Send reply to email |
| `list-replies` | List sent replies |
| `session-summary` | Show session progress |

## Trainer-Only Commands (hidden from agent)

- `prepare-rollout` - Create new session
- `reset-rollout` - Reset existing session

## Environment Variables

- `MAIL_CLIENT_SESSION_ID` - Session binding (injected by trainer)
- `MAIL_CLIENT_STATE_ROOT` - State directory
- `MAIL_CLIENT_SCENARIO_ID` - Scenario ID

## Running Tests

```bash
python -m mail_client_envs.concurrency_test
```
