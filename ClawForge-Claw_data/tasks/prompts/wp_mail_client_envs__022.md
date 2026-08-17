Hey, great you're here. The inbox is a mess and I've got a fire to put out.

Bob from vendor services just pinged me on Slack saying he sent two urgent emails about our SSL certificate expiring – I haven't even opened them yet. Can you dig into the `data/emails/` folder and find everything from Bob that's about that certificate emergency? I need the key details (ID, subject, sender, timestamp) pulled into `ops/cert_alert.json` so I can forward it to the sysadmin.

Also, once you've got the details, draft a quick reply back to Bob telling him I'm on it. Drop the reply as a JSON structure into `drafts/reply.json` with the `to`, `subject`, and `body` fields. Keep the body short and professional – something like “I will handle the certificate issue immediately.”

And one more thing – that Tech Weekly newsletter keeps piling up. I want to auto‑archive all those newsletters going forward. List their email IDs into `ops/archive_list.json` so we can feed it to the archiving script.

Thanks – I’ll be in the meeting but I trust you to get this sorted.
