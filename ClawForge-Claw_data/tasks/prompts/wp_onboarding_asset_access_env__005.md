Hey,

Sarah and Mike are supposed to start tomorrow, but the onboarding pipeline choked halfway. I've dropped the raw data into the workspace — contracts, employee accounts, equipment inventory, permission packs, and some contact records. Everything you need is in `data/` and `data/onboarding/`.

Please go through the signed contracts (we only care about ones that are actually signed), grab the employee details, then:

- Figure out what email profile they’d get (just the email from the accounts file).
- Assign the correct system access based on their department – the permission packs are in `data/onboarding/permission_packs.json`.
- Find a piece of available equipment from the inventory for each of them (prefer the first matching one that isn't already assigned).
- Finally, drop a welcome note into `ops/slack_cache/welcome_{employee_id}.txt` – just a simple "Welcome to the team, {name}!" is fine.

Once you’ve done all that, compile a single summary file `onboarding_result.json` in the root of the workspace. It should list each processed employee along with the email we used, the systems they got access to, the asset tag of the equipment assigned, and whether the welcome tick was written.

I need this done before the morning standup – thanks.

– Jeff
