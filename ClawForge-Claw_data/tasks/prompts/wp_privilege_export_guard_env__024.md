Subject: Urgent: Block unauthorized bulk export request

Hey,

I'm Alice, the account admin for this environment. I just got an automated alert about a high-risk bulk export request (request ID: req_007). The system flagged it because the target asset (asst_003) is classified as highly restricted, but our account permissions in `data/accounts.json` only give us basic read access to customer_data. I double-checked the asset details in `data/assets/assets.json` — we definitely don't have the right level.

Could you please review the request and block it? I need you to create a simple JSON file at `ops/reject.json` with two fields:
- `request_id`: the ID of the rejected request
- `signed_by`: my name, Alice

That's all. Once the file is in place, the system will pick it up and perform the actual denial.

Thanks,
Alice
