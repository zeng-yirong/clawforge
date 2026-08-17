Hey Security Ops,

We just got a batch of access request logs from last hour. Some of them look suspicious — external parties trying to pull our yet-to-be-released technical blueprints and financial summaries from the restricted asset repository.

I've dumped the raw request records into `data/requests/requests.json` and the asset manifests into `data/assets/assets.json`. You'll also find supporting data in `data/accounts.json`, `data/attachments/`, and `data/contacts.json` if you need context.

What I need from you: a clean, sorted list of request IDs that should be immediately denied. Only those that target unpublished assets (classification = "unpublished") and have the risk type "unauthorized_access" — no internal requests, no legacy stuff. Drop the list as a JSON array into `ops/deny_list.json` so I can feed it straight to the blocking pipeline.

I don't have time to dig through the noise myself — make it accurate, and make it quick. Thanks.
