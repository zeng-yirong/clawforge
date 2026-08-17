Hey, it's me from Ops. So I just ran a sync check on our birthday reminder system for March and things look messy. I've got the latest contact list sitting in `raw_data/contacts.json` and the existing reminders live in `reminders/reminders.json`. 

The issue: we need every contact whose birthday falls in March (any day) to have an active, enabled reminder. Some reminders got accidentally disabled during the last migration, and a few March birthdays are totally missing a reminder entry. 

I don't want anyone touching the original data files – we need a clean report. Could you scan through the contacts, figure out which ones have March birthdays, check their reminder status, and then create one file: `ops/summary.json`. In that file, for each March birthday contact, tell me the `contact_id`, the `name`, and what action we should take – either `skipped` (already enabled), `enable` (exists but disabled), or `create` (none exists). That's it. Just the report, no changes to the data files.

Thanks, and try to get it right – we're launching the reminder campaign next Monday.
