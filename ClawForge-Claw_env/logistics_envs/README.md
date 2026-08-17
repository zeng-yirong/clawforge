# Logistics Envs

`logistics_envs` is a CLI-first training environment for e-commerce order processing, returns management, and inventory reconciliation.

## Task Overview

1. Process customer returns (approve/reject/inspect)
2. Update shipment tracking status
3. Reconcile inventory discrepancies
4. Generate reconciliation reports

The environment supports parallel rollout with session isolation.

## Session Model

Session management is trainer-owned, not agent-owned.

- The trainer prepares one session per rollout sample
- The trainer binds that session through environment variables
- Agent commands do not need `--session-id`

Trainer bootstrap:

```bash
python -m claw_envs.logistics_envs.cli prepare-rollout --scenario-id fulfillment_inventory_reconcile --show-bindings --show-task
```

The returned bindings should be injected into the rollout process:

- `LOGISTICS_SESSION_ID`
- `LOGISTICS_STATE_ROOT`
- `LOGISTICS_SCENARIO_ID`

## Agent Commands

After the rollout is prepared, the agent uses the CLI without session arguments:

```bash
# Task
python -m claw_envs.logistics_envs.cli task

# Orders
python -m claw_envs.logistics_envs.cli list-orders
python -m claw_envs.logistics_envs.cli get-order --order-id ord_001
python -m claw_envs.logistics_envs.cli update-order-status --order-id ord_001 --new-status shipped

# Shipments
python -m claw_envs.logistics_envs.cli list-shipments
python -m claw_envs.logistics_envs.cli get-shipment --shipment-id ship_001
python -m claw_envs.logistics_envs.cli update-shipment-status --shipment-id ship_005 --new-status shipped

# Returns
python -m claw_envs.logistics_envs.cli list-returns --status pending_review
python -m claw_envs.logistics_envs.cli get-return --return-id ret_001
python -m claw_envs.logistics_envs.cli approve-return --return-id ret_001 --notes "Defective product confirmed"
python -m claw_envs.logistics_envs.cli inspect-return --return-id ret_003 --inspection-notes "Wrong item received" --resolution exchange
python -m claw_envs.logistics_envs.cli receive-return --return-id ret_001

# Inventory
python -m claw_envs.logistics_envs.cli list-inventory --low-stock-only
python -m claw_envs.logistics_envs.cli get-inventory --sku SKU-1001
python -m claw_envs.logistics_envs.cli adjust-inventory --sku SKU-1002 --warehouse-id wh_001 --quantity-change -5 --reason-code DAMAGE
python -m claw_envs.logistics_envs.cli reserve-inventory --sku SKU-1001 --warehouse-id wh_001 --quantity 10

# Reports & Attachments
python -m claw_envs.logistics_envs.cli generate-reconciliation-report
python -m claw_envs.logistics_envs.cli read-attachment --attachment-id att_return_policy

# Session
python -m claw_envs.logistics_envs.cli session-summary
```

## Data Layout

- `data/accounts.json`: workspace account profile and permissions
- `data/contacts.json`: customers, CS reps, warehouse managers, vendors
- `data/warehouses.json`: warehouse locations and capacity
- `data/orders/*.json`: order records with items and status
- `data/shipments/*.json`: shipment tracking with carrier events
- `data/returns/*.json`: return requests with status flow
- `data/inventory/*.json`: inventory levels by SKU and warehouse
- `data/attachments/*.md`: policy documents and guides
- `data/scenarios/*.json`: scenario prompts and rollout configuration

## Concurrency Test

Use the stress script to validate isolation and locking:

```bash
python -m claw_envs.logistics_envs.concurrency_test --mode both --executor threads --sessions 16 --workers 8 --contention-loops 4 --report-json ./.tmp/logistics_report.json
```

It checks both:
- isolated parallel sessions
- multi-worker contention on a shared session
