Hey, I'm Tom from the travel coordination team. We've got a bit of a mess this morning – UA123 from SFO to JFK just got slapped with a 120-minute delay. That means John Smith, one of our VIPs, will land around 20:00 instead of 18:00. He's got a limo waiting for pickup at 18:30, and that's obviously not gonna work anymore.

I need you to sort out two things:

1. **Adjust the transportation booking** – find the limo reservation tied to UA123 and John Smith, then move the pickup time to match the new arrival (accounting for an extra 30 minutes after landing to clear customs). Put the updated booking info into `ops/transport_updates.json` so our ground team can see the change.

2. **Draft a delay notification** for John – let him know his flight is delayed, the new ETA, and that his limo has been rescheduled. Send this draft as a JSON object into `ops/notification_draft.json`. Keep it professional and include his contact email.

All the raw data is sitting in the workspace under `data/` and `bookings/` – flights, customers, transport bookings, contacts, you name it. The usual file names apply. I trust you to figure out the exact fields and structure. Just make sure the outputs are clean, correct, and ready for the next step.

Cheers,
Tom
