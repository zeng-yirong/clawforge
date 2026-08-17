Hey there,

I'm drowning in new hire paperwork today. HR sent over a bunch of files for the latest batch – contracts, inventory, permission packs – but I can't tell who's actually ready to onboard. 

Here's what I've got dumped into the project workspace:

- `data/onboarding/contracts.json` – signed employment contracts
- `data/onboarding/equipment_inventory.json` – what we have in stock
- `data/onboarding/permission_packs.json` – system access bundles by department
- `data/accounts.json` – existing company accounts (just for reference)

I need you to figure out which employees are legally good to go (contracts that are fully signed), then for each of them:

1. **Create their company email** – standard format: firstname.lastname@company.com (all lowercase, based on the `employee_name` field in the contract).  
2. **Assign system access** – match their `department` to the correct permission pack in `permission_packs.json`.  
3. **Allocate equipment** – find any available laptop (asset_type = "Laptop" with status = "available") and assign it to them.  
4. **Write a welcome message** – something like "Welcome aboard, {first name}! Please check your onboarding package." You can use the first name from the employee name.

Please compile everything into a single JSON file called `onboarding_completion.json` at the root of the workspace. The structure should be an object with a key `completed_onboardings` and an array of objects, each containing:
- `employee_id`
- `email_profile`
- `system_access` (list of system names)
- `equipment_assigned` (asset tag of the laptop)
- `welcome_message`

I only want the people who truly qualify – don't guess or include incomplete contracts, unavailable gear, or mismatched permission packs. Double-check every piece.

Thanks – I owe you one!

– Jamie (HR Ops)
