Subject: Urgent Onboarding Request – Alice Johnson (EMP-037)

Hi IT Team,

We just got the green light for Alice Johnson (工号 EMP-037), our new R&D engineer. Her signed contract is in `data/onboarding/contracts.json` – I double-checked, it's the only one with status "signed" for that employee. Please take care of the usual onboarding steps:

- Create her company email profile (standard firstname.lastname@company.com).
- Assign the standard R&D permission pack (the one that includes Slack and Portal).
- From the equipment inventory (`data/onboarding/equipment_inventory.json`), allocate a laptop that's actually available – don't grab one that's already assigned to someone else.

Also, we need a welcome message pushed into our Slack cache. Write it to `ops/welcome_cache.json` using the usual format: `"Welcome, {Full Name}!"`. Finally, summarize everything you did in `ops/onboarding_summary.json` so I can review at a glance.

The files in `data/onboarding/` are the authoritative ones – ignore anything in `backups/` or `old/` folders. Let me know if anything looks off.

Thanks,
HR Lead
