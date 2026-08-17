From: Sarah, Travel Manager
To: AI Assistant
Subject: Urgent - Lily's London trip next week

Hey,

Lily needs to fly from JFK to London Heathrow on Jun 15, 2026. Business class is okay but economy is preferred if it fits the policy. I've dumped the latest platform quotes in `data/platforms/` and the corporate policy files are in `data/policies/`. Make sure you use the current version (v2) of the policy – the old v1 is outdated.

We need the cheapest flight that meets all policy rules. Put the result in `ops/flight_decision.json` with these fields: `platform_id`, `flight_id`, `price`, `cabin_class`, `policy_id`. That's all we need for now.

Thanks!
