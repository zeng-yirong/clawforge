Hey team, quick morning check. I just pulled the zone status snapshots – they're in `zones.json`. We've got some intrusion flags, but not all need police involvement. Cross-reference with `accounts.json` to find which account owns each flagged zone, then dig into `contacts/contacts.json` for their emergency contacts.  

We only want to escalate if the contact's role is either "Police" or "Police Non-Emergency". Please compile a clean list of those zones with their corresponding police phone numbers, sorted by zone_id, and drop it into `ops/acknowledge.json`.  

No extra fields, no commentary – just the facts. I'll use it in the 10‑o‑clock briefing. Cheers.
