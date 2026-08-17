**Subject:** 🚀 New Hire Onboarding – Alice Chen starts today!

**Hi there,**

I'm swamped with payroll, so I need you to handle Alice's onboarding. All the source files are waiting in the workspace:

- **Contract snapshot**: `data/onboarding/contracts.json`
- **Employee accounts**: `data/accounts.json`
- **Permission packs**: `data/onboarding/permission_packs.json`
- **Equipment inventory**: `data/onboarding/equipment_inventory.json`
- (Ignore `data/contacts.json` and any other files – those are for other teams.)

Please find Alice's **signed** contract, then walk through the standard onboarding flow:

1. **Create her email profile** – use her account info from `data/accounts.json`.
2. **Assign system access** – match her department to the right permission pack.
3. **Allocate equipment** – grab the first available laptop from the inventory.
4. **Generate a welcome message** – something like "Welcome aboard, {full name}!".

Finally, **consolidate everything** into a single JSON file at `ops/onboarding_complete.json`.  
I need the following top‑level keys so I can quickly review:

- `employee_id`
- `employee_name`
- `email`
- `department`
- `email_profile` – an object with `email` and `display_name`
- `systems_access` – a list of system names (e.g. `["git", "jira", "wiki"]`)
- `equipment` – an object with `asset_tag` and `asset_type`
- `welcome_message` – the exact string you would post

Let me know if anything is missing – thanks!  

**– Maya, HR**
