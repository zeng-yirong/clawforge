# Simulated Supabase Write Contract

After remediation, processed target incidents must be written into the simulated Supabase memory table `incident_resolutions`.

Required fields:

- `incident_id`
- `service`
- `category`
- `severity`
- `resolution_state`
- `remediation_mode`
- `operator_note`

Only write rows for the target actionable incidents in this scenario. Do not write unrelated tickets into the table.
