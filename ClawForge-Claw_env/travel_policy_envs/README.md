# Travel Policy Environment

`travel_policy_envs` is a CLI-first training environment for booking business travel while complying with corporate travel policies.

The workflow:
1. Compare flight prices across platforms.
2. Validate booking against travel policy.
3. Initiate approval if needed.
4. Complete the booking.

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample.
- The trainer binds that session through environment variables.
- Agent commands do not need `--session-id`.

Trainer bootstrap:

```bash
python -m claw_envs.travel_policy_envs.cli prepare-rollout --scenario-id q2_business_travel_2026 --show-task
```

The returned bindings should be injected into the rollout process:

- `TRAVEL_POLICY_SESSION_ID`
- `TRAVEL_POLICY_STATE_ROOT`
- `TRAVEL_POLICY_SCENARIO_ID`

## Agent Commands

After the rollout is prepared, the agent uses the CLI without session arguments:

```bash
python -m claw_envs.travel_policy_envs.cli list-platforms
python -m claw_envs.travel_policy_envs.cli search-flights --platform-id skybook --origin JFK --destination LHR --departure-date 2026-06-15 --cabin-class business --passengers 1
python -m claw_envs.travel_policy_envs.cli compare-platform-prices --origin JFK --destination LHR --departure-date 2026-06-15 --cabin-class business --passengers 1
python -m claw_envs.travel_policy_envs.cli list-policies
python -m claw_envs.travel_policy_envs.cli get-policy --policy-id travel_policy_001
python -m claw_envs.travel_policy_envs.cli validate-booking-against-policy --policy-id travel_policy_001 --flight-cost 2500
python -m claw_envs.travel_policy_envs.cli get-policy-approval-chain --policy-id travel_policy_001
python -m claw_envs.travel_policy_envs.cli initiate-approval-request --policy-id travel_policy_001 --flight-cost 2500
python -m claw_envs.travel_policy_envs.cli create-booking --platform-id skybook --flight-cost 2500
python -m claw_envs.travel_policy_envs.cli session-summary
```

## Data Layout

- `data/policies/*.json`: travel policy definitions.
- `data/platforms/*.json`: flight booking platform configurations.
- `data/scenarios/*.json`: scenario prompts and rollout configuration.
- `data/accounts.json`: workspace account profile.
- `data/contacts.json`: people referenced in policies.

## Concurrency Test

Use the stress script to validate isolation and locking:

```bash
python -m claw_envs.travel_policy_envs.concurrency_test --mode both --executor processes --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/travel_policy_report.json
```

It checks both:
- isolated parallel sessions
- multi-worker contention on a shared session