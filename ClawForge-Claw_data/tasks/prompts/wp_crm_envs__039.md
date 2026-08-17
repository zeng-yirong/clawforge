Subject: Need help prepping birthday care & cleanup

Hey there,

I'm Sarah from the CRM team. We're rolling out a quarterly birthday care campaign and I'm drowning in messy data. I've pulled the latest contact snapshot into `data/contacts.json`, the existing reminders live in `data/reminders/reminders.json`, and the tag definitions are in `data/tags/tag_definitions.json`. There's also a `current_date.txt` at the root so you know where we stand today.

What I need from you:

- For every **business** contact that's *not* in the `inactive` folder: if they don't have an **enabled** birthday reminder already, please log that we need to create one. The reminder date should be the contact's birthday this year (just use the month/day from their `birthday` field, year from the current date).
- For those same contacts (the ones missing a reminder), also add the tag `birthday-pending` to them.
- For any contact that's in the `inactive` folder AND has `contact_type` = `personal`, add the tag `inactive-personal`.

Don't touch anyone else.

Please prepare a clean action plan and write it to `ops/contact_updates.json`. I'll leave the format to you, but make sure it's clear which contact needs what — reminder date, tags to add. Keep it simple and accurate.

Thanks,
Sarah
