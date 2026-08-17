Hey, quick one – new hire Alice Johnson's onboarding stalled at step 3. Her contract is signed and sitting in `data/onboarding/contracts.json` (status: "signed"), but the rest of the provisioning never fired.

I need you to finish it manually:

1. **Email profile** – Create `ops/email_profile.json` with her name, email (from the contract), and the department she belongs to. You'll find the department somewhere in the same file.
2. **System access** – Based on her department, pick the right permission pack from `data/onboarding/permission_packs.json` and write the assigned system list into `ops/system_access.json`. Include her employee_id too.
3. **Equipment** – Grab a laptop from `data/onboarding/equipment_inventory.json` that's marked as "available". Assign it to her and write the assignment record into `ops/equipment_assignment.json`.
4. **Welcome message** – Drop a friendly welcome message into `ops/welcome_message.json` so the Slack cache picks it up. Make sure it includes her name.

All raw data is in the `data/` directory. Just get it done – I need the four ops files ready before the audit starts.
