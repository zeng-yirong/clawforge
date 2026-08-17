Hey, this is Jess from Ops. We've got a cascade situation with flight UA123 from SFO to JFK — just got the alert, 120 minutes delay. I already pulled the flight logs and dumped them into `data/flights/`. The booking manifests are in `data/bookings/` — hotel and transport reservations linked to that flight are about to go sideways. 

I need you to put together a disruption plan: list out exactly which hotel bookings and which transport bookings are tied to that delayed flight. Don't touch the other flights; they're fine. Put the plan in `ops/disruption_plan.json` so I can push the adjustments to the vendors. Keep it clean — just the flight ID, the delay minutes, and two arrays with the booking IDs. I'll handle the actual cancellations and rebookings.

Make sure you check the delay minutes — if a delay is under 60 minutes, the downstream stuff is usually still okay. UA123 is way past that threshold, so everything linked is affected.

Thanks. Need this in the next 10 minutes before the system tries to auto-check-in everyone.
