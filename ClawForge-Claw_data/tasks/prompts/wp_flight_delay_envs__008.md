Hi there – this is Maria from TravelOps. We’ve got a brewing situation: AA456 (ATL → JFK) got hammered by that tropical storm system and is running almost two and a half hours late. I’ve pulled the latest data snapshots into the `data/` directory – flight manifests, hotel inventory, transport schedules, and our booking ledger.

I need you to pull together a clear operational action plan and save it as `ops/disruption_report.json`. Here’s what I’m after:
- The details of the delayed flight (which one, how late).
- Any hotel bookings that are tied to this flight and still active – I want the new check‑in and check‑out dates after we shift everything by the delay.
- Any transport bookings linked to this flight and still confirmed – adjust the pickup time to match the new arrival.
- A list of the travelers who need to be notified, with their full name and email address so I can send out the update.

Keep it clean and structured – I’ll be feeding this straight into our notification system. We don’t have time to sort through irrelevant data. Thanks!
