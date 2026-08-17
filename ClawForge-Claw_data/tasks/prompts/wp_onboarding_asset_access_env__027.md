Subject: Urgent: Onboarding tasks for new hires

Hi there,

We've got a fresh batch of new employees coming in, and I'm buried in manual work. I've prepared all the necessary data in the `data/` folder:

- `data/onboarding/contracts.json` has the signed contracts (look for status "signed"). Each contract includes employee_id, employee_name, status, email, and department.
- `data/onboarding/permission_packs.json` defines system access packs. Each pack has a pack_id (which matches the department name) and a list of systems.
- `data/onboarding/equipment_inventory.json` lists all equipment with asset_tag, asset_type, status, and the department it's intended for. We only want to assign equipment that is "available".
- There are also `data/accounts.json` and `data/contacts.json`, but you probably don't need them for this task.

Could you please generate a consolidated JSON file at `ops/onboarding_tasks.json` that lists one task per signed employee? Each task should include:
- The employee's ID (employee_id)
- The email to use for their new account (from the contract)
- The list of systems they need access to (based on matching their department to a permission pack's pack_id)
- The specific equipment they should receive (the first available piece that matches their department)

This will help me quickly process all new hires. The output doesn't need to be fancy, just clear and accurate.

Thanks!
HR
