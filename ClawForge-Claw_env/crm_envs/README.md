# CRM Contact Management Environment

A synthetic training environment for RL agents to practice automated CRM contact organization, tagging, birthday reminders, and search operations.

## Task Description

The agent acts as a CRM administrator managing customer data. Tasks include:
- Organizing contacts into appropriate folders (business, personal, archive, inactive)
- Adding and managing tags for contacts based on their attributes
- Setting up birthday reminders for contacts
- Archiving inactive contacts
- Searching and matching contacts based on various criteria

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
    ["python", "-m", "crm_envs.cli", "prepare-rollout", "--show-bindings"],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

## Agent Commands

| Command | Description |
|---------|-------------|
| `list-contacts` | List contacts with optional query/folder/type/tag filters |
| `get-contact` | Get full contact details |
| `classify-contact` | Classify contact into folder with tags |
| `add-tags` | Add tags to contact |
| `remove-tags` | Remove tags from contact |
| `archive-contact` | Archive a contact |
| `search-contacts` | Search contacts by name/email/company/tag/folder |
| `list-reminders` | List reminders |
| `create-birthday-reminder` | Create birthday reminder for contact |
| `enable-reminder` | Enable a reminder |
| `disable-reminder` | Disable a reminder |
| `list-tags` | List available tag definitions |
| `get-or-create-tag` | Get or create a tag |
| `session-summary` | Show session progress |

## Trainer-Only Commands (hidden from agent)

- `prepare-rollout` - Create new session
- `reset-rollout` - Reset existing session

## Environment Variables

- `CRM_SESSION_ID` - Session binding (injected by trainer)
- `CRM_STATE_ROOT` - State directory
- `CRM_SCENARIO_ID` - Scenario ID

## Running Tests

```bash
python -m crm_envs.concurrency_test
```
