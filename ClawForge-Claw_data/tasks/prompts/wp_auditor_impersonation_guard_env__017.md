Hey, this is Jane from Security Ops.

We've got a batch of access requests that came in overnight. Several of them claim to be internal auditors and want to read our most sensitive knowledge bases and metadata stores. I already checked the approved audit team roster—something feels off.

Could you go through all the pending requests in `data/requests/requests.json`, cross‑reference with the actual employee accounts in `data/accounts.json`, and figure out which ones are trying to impersonate an auditor? The assets they're targeting are listed in `data/assets/assets.json`.

Once you've identified the suspicious ones, dump their request IDs into a file at `ops/denied_requests.json`. I need it clean and accurate so I can action it immediately.

Thanks!
