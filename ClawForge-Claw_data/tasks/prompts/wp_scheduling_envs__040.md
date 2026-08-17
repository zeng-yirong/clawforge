Hi support team,

I tried to set up a morning automation yesterday, but this morning nothing happened. I double-checked the schedule list in `data/schedules.json` and also looked at the device inventory in `data/devices/devices.json`. Something seems off — I think one of the schedules is pointing to a device that doesn't exist in the inventory.

Could you dig into those two files, figure out which schedule is the culprit, and then create a small JSON file at `ops/bad_schedule.json` with the ID of that broken schedule? Just a simple `{"schedule_id": "<id>"}`, no extra fields.

Thanks,
Alice
