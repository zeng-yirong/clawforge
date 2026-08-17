# Excel Data Processing Training Environment

This environment provides a simulated workspace for training agents to handle Excel data processing tasks including deduplication, data enrichment, pivot table generation, charting, and formula creation.

## Overview

The agent acts as a data analyst who receives raw sales data with duplicates and missing values, and must:
1. Clean and deduplicate the data
2. Fill missing information
3. Generate meaningful pivot tables
4. Create visualizations
5. Add calculation formulas

## Session Model

Each training sample corresponds to a session. Sessions are created by the trainer using `prepare-rollout` and bound via environment variables.

### Trainer Bootstrap

```python
import json
import os
import subprocess

result = subprocess.run(
    [
        "python", "-m", "excel_data_envs.cli",
        "prepare-rollout",
        "--scenario-id", "sales_data_processing",
        "--show-bindings",
    ],
    check=True, capture_output=True, text=True,
)
payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

### Required Environment Variables

- `EXCEL_DATA_SESSION_ID` - Session identifier
- `EXCEL_DATA_STATE_ROOT` - Session state directory
- `EXCEL_DATA_SCENARIO_ID` - Scenario to load

## Agent Commands

### Data Operations
- `task` - Show task prompt
- `list-raw-data` - List available datasets
- `read-raw-data --data-id <id>` - Read dataset metadata
- `deduplicate --data-id <id> --key-column <col>` - Remove duplicates
- `fill-missing --data-id <id>` - Fill missing customer data
- `get-cleaned-data` - View cleaned data
- `get-data-summary` - View data summary

### Pivot Tables
- `create-pivot --row-dimensions <cols> --value-column <col> --aggregation <type>` - Custom pivot
- `create-pivot-category-region` - Pivot by category and region
- `create-pivot-salesperson` - Pivot by salesperson
- `create-pivot-city` - Pivot by city (average)
- `get-pivots` - List all pivots

### Charts
- `create-bar-chart --chart-id <id> --title <title> --x-axis <col> --y-axis <col>` - Bar chart
- `create-pie-chart --chart-id <id> --title <title> --label-column <col> --value-column <col>` - Pie chart
- `create-line-chart --chart-id <id> --title <title> --x-axis <col> --y-axis <col>` - Line chart
- `create-column-chart --chart-id <id> --title <title> --x-axis <col> --y-axis <col>` - Column chart
- `get-charts` - List all charts
- `get-chart --chart-id <id>` - Get chart details

### Formulas
- `create-formula --name <name> --expression <expr> --description <desc>` - Custom formula
- `create-total-revenue` - Total revenue (SUM)
- `create-average-order` - Average order value (AVERAGE)
- `create-total-transactions` - Transaction count (COUNT)
- `get-formulas` - List all formulas

### Session
- `session-summary` - View progress

## Evaluation

Scoring is based on four dimensions:
- **Deduplication (25%)** - Number of duplicates removed
- **Pivot Completeness (30%)** - Required pivots created
- **Chart Quality (20%)** - At least 2 charts created
- **Formula Accuracy (25%)** - Required formulas created

## Running Tests

```bash
python -m excel_data_envs.concurrency_test
```

## Hidden Commands (Trainer Only)

- `prepare-rollout` / `create-session` - Create new session
- `reset-rollout` / `reset-session` - Reset session state
