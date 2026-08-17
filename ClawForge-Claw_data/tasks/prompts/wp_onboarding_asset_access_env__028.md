Hi there,

We've just closed a batch of contract signings and I need you to push these new hires through onboarding before Monday. The relevant data is sitting in `data/onboarding/`. I've got:

- `contracts.json` — contains the signed agreements (look for status "signed")
- `permission_packs.json` — standard system access packs (pack_id: "standard")
- `equipment_inventory.json` — hardware stock with availability

Please do the following for me:

1. For each signed contract, consider the employee.
2. Assign them the standard system access (the list of systems from the "standard" pack).
3. Assign them one available piece of equipment from the inventory (any type, just the first available based on asset tag order; mark as null if none left).
4. Build a summary file that lists every processed employee with their email, sorted list of systems (alphabetically), and the assigned asset tag (or `null` if unavailable).

Drop the result as `ops/onboarding_summary.json` in the workspace. I'll use it to trigger further provisioning.

Make it clean — no extra fields, no missing entries. Thanks!

— IT Ops Lead
