# Expense Management Environment - Agent Workflow Guide

## Overview

This environment simulates an expense reimbursement audit assistant. Agents load travel policies, calculate budgets, load consumption records, and generate budget vs actual analysis reports.

## Key Commands

### Policy Loading
- `load-policy --tier <tier>` - Load travel policy (standard/senior/executive)

### Budget Calculation
- `calculate-budget --tier <tier> --destination <dest> --duration-days <n>` - Calculate expense budget

### Consumption Loading
- `load-consumption --trip-id <id>` - Load actual consumption records (trip_001 available)

### Analysis
- `generate-analysis` - Compare budget vs actual and identify overruns
- `export-report` - Export final expense report

## Session Model

Sessions are managed by the trainer. The agent receives bindings via environment variables:
- `EXPENSE_SESSION_ID` - Current session identifier
- `EXPENSE_STATE_ROOT` - State file directory
- `EXPENSE_SCENARIO_ID` - Active scenario

## Workflow

1. Load travel policy with `load-policy --tier standard`
2. Calculate budget with `calculate-budget --destination 北京 --duration-days 3`
3. Load consumption with `load-consumption --trip-id trip_001`
4. Generate analysis with `generate-analysis`
5. Export report with `export-report`

## Policy Tiers

| Tier | Daily Food | Daily Accommodation | Local Transport | Taxi Limit |
|------|------------|---------------------|-----------------|------------|
| standard | 200 | 500 | 150 | 100 |
| senior | 300 | 800 | 200 | 150 |
| executive | 500 | 1500 | 300 | 200 |

## Constraints

- Always use the bound session (do not pass `--session-id` manually)
- Actions are logged with timestamps
- State is persisted atomically with file locking