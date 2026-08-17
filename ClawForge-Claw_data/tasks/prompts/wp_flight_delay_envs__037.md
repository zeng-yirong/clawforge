Hey, this is urgent. UA123 just got slammed with a 2-hour delay — new arrival is going to be 20:30 instead of 18:30. That messes up the whole evening plan.

I've pulled the latest data dumps into `data/`. You'll find the flight manifests, hotel bookings, and transport schedules there. The hotel check-ins and pickup times were all set based on the original flight time, so we need to shift everything that's tied to this flight.

Dig through the records, figure out which active hotel and transport bookings are affected (look for the flight ID in each booking), and recalculate the new times by adding the delay. Then write the adjustment plan to `ops/delay_plan.json`. Use the exact same time format as in the source data — don't change the string pattern.

Only include the bookings that actually need to move. Leave everything else alone. And make sure the file is clean JSON — no comments, no extra fields. I'll feed it straight into the operations pipeline.

Thanks — I owe you one.
