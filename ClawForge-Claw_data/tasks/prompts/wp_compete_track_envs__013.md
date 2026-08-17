Hey, it's Sarah from Competitive Intel. I’m drowning in policy data — our legal team just flagged that CloudMajor is about to get hammered by the new EU digital regulations. I need a crisp, machine-readable risk summary for our ops team to act on.

Here’s the mess: you’ll find competitor profiles under `data/competitors/` — there’s a bunch, including CloudMajor, DataFlow AI, and some others. The policy files live in `data/policies/`. I need you to comb through them and pull out **only** the policies that directly threaten CloudMajor — the ones that are both **active** EU regulations with a **high** impact level. Don’t waste time on proposed regulations or low/medium impact stuff.

I want the result in a single clean JSON file — an array of objects. Each object should contain the policy’s unique ID (`policy_id`), its official title (`title`), and the impact level (`impact_level`). Name the file `ops/eu_risk_report.json` — under the current workspace root.

That’s it. No fluff, no extra fields. Just the hard facts our skeleton crew needs to start drafting compliance responses. I’m trusting you to get this right on the first pass — we don’t have time for second-guessing. Go!
