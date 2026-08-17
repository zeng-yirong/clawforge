Subject: 🔴 Urgent – Block external requests to confidential documents

Hey team,

We just got a red alert from the security monitoring system. A bunch of external requests have been flooding in, trying to access our unpublished technical architecture plans and finance archive bundles. These are marked as high-risk and are targeting assets classified as confidential. Our internal policy demands that we block them immediately.

I've pulled the latest request log and asset registry into the usual locations:
- `data/requests/requests.json` – all incoming requests with details like risk level, target asset, etc.
- `data/assets/assets.json` – asset metadata including classification and read policies.
- `data/accounts.json` and `data/contacts.json` are also there if you need to cross‑reference actors.

Can you go through the requests, figure out which ones must be denied, and put the list into `ops/deny_list.json`? I need a JSON object with a field `"denied_request_ids"` holding an array of request IDs. I'll feed that into our automated deny workflow.

The clock is ticking – please get this done as soon as possible.

Thanks,
Mia (Security Ops)
