Hey, ops team lead here – we just noticed from the latest activity logs that a few high-touch customers are slipping fast. Their usage is dropping, last interaction was weeks ago, and the last ticket they opened ended with negative sentiment. We need to act before they churn.

I’ve dumped the raw data into the working area:
- `data/customers/customers.json` has all our active customer profiles.
- `data/logs/activity_logs.json` tracks each customer’s recent behavior.
- `data/news/news_samples.json` contains curated industry news we can use in outreach.

I need you to:
1. Identify the customers that are clearly **high risk** (the ones with both dropping usage and negative ticket sentiment).
2. For each of those customers, pick the most relevant **pain point news** from the industry they belong to.
3. Compose a short retention message that references that pain point news (you can pull the summary directly – just put “Retention note: ” before the summary text).
4. Save everything into a single file at `ops/retention_cache.json` with the following structure for each high-risk customer:
   - `customer_id`
   - `customer_name`
   - `industry`
   - `selected_news_headline`
   - `retention_message`

Keep it clean – only the high-risk customers, no extras. I’ll pick up that file and queue the sends. Let me know when it’s done.
