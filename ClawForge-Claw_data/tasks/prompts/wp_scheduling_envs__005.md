Subject: Living Room AC schedule conflict - needs investigation

Hi there,

My Living Room AC is supposed to turn on at 2 PM every weekday, but it keeps shutting off shortly after. I’ve verified the unit is online, so it’s not a hardware issue.

I’ve placed the current schedule entries in `data/schedules.json` and the device info in `data/devices.json`. Could you check if there’s a rule that conflicts with the 2 PM turn‑on? If you find a problematic schedule, please write its ID into a JSON file at `ops/fix_schedule.json` using the key `schedule_id`. I just need the ID so I can delete it.

Thanks!
- Home Automation Manager
