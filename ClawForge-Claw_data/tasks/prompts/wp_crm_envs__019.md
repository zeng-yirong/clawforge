Hey Alex, it's Rachel from CRM ops.

We just had an audit flag on TechCorp Industries. Their contacts are a mess – some are still sitting in the personal folder, and half of them don't even have the 'tech-partner' tag. I need you to clean this up.

Make sure every contact belonging to TechCorp ends up in the business folder and has that tag. Also, give me a separate list of the ones that were already in the business folder but were missing the tag – so I can figure out who dropped the ball.

You'll find all the data under `data/`. The contact list is in `data/contacts.json`, company info in `data/companies.json`, and tag definitions live in `data/tags/`. Drop the result into `ops/techcorp_fix.json`.

Thanks!
