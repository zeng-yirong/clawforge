Hi,

I'm Tom from Security Operations. We've got a problem — someone is pretending to be our internal security auditor and trying to access the restricted knowledge base. I've pulled all the relevant data into the workspace under `data/`:

- `data/accounts.json` — user accounts and departments
- `data/contacts.json` — known contacts with roles and email
- `data/assets/assets.json` — all assets we manage, including the sensitive one
- `data/requests/requests.json` — recent access requests that we need to review

I need you to go through these requests and figure out which ones are from impersonators. The real security auditor is already in our contacts list. Please create a JSON file at `ops/denied_requests.json` with a field `denied_request_ids` that lists the IDs of requests that should be rejected. Only include the true impersonators; don't deny legitimate requests from the actual auditor.

I'll use your list to take action. Thanks!

— Tom
