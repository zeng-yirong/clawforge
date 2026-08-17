# Excel Data Processing Environment

This environment trains agents to perform Excel data cleaning, deduplication, analysis, and reporting tasks.

## Workflow

1. **Read raw data** - List and read available raw datasets
2. **Deduplicate** - Remove duplicate transactions using a key column
3. **Fill missing data** - Complete missing customer information
4. **Create pivot tables** - Generate summaries by category/region, salesperson, and city
5. **Create charts** - Generate bar, pie, line, or column charts for visualization
6. **Create formulas** - Add calculation formulas for totals and averages

## Key Commands

- `task` - Get current task prompt
- `list-raw-data` - List available datasets
- `deduplicate --data-id <id> --key-column <col>` - Remove duplicates
- `fill-missing --data-id <id>` - Fill missing customer data
- `create-pivot-category-region` - Create pivot by category and region
- `create-pivot-salesperson` - Create pivot by salesperson
- `create-pivot-city` - Create pivot by city
- `create-bar-chart --chart-id <id> --title <title> --x-axis <col> --y-axis <col>` - Create bar chart
- `create-pie-chart --chart-id <id> --title <title> --label-column <col> --value-column <col>` - Create pie chart
- `create-total-revenue` - Create total revenue formula
- `create-average-order` - Create average order value formula
- `create-total-transactions` - Create transaction count formula
- `session-summary` - Get session progress

## Important Constraints

- Always deduplicate before creating pivots or charts
- Run `fill-missing` after deduplication to complete customer data
- Create at least 2 charts for visualization score
- Create the 3 required formulas for formula score
