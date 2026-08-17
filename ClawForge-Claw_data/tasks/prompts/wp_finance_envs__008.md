Hey Jim here,

I've dumped the latest stock snapshot and news feed in `data/stocks.json` and `data/news.json`. Need a quick hand before the morning meeting.

We're looking at the Technology sector specifically. I want you to go through the stocks and pick out the ones that look healthy based on a couple of no‑bullshit metrics: PE ratio under 30, and year‑over‑year revenue growth above 10%. Also, I only want stocks that have recent bullish news coverage – check the news file for that.

Ignore any entries that are missing critical data (like blank PE or growth numbers). Once you have the list, sort it by PE ratio from lowest to highest.

Drop the final output as a JSON array into `ops/tech_picks.json`. For each stock, include:
- ticker
- company_name
- pe_ratio
- revenue_growth_yoy
- the headline of the bullish news article
- a short sentence on why it qualifies

That's it. Get it done and I'll review it before the 9am call.

Thanks,
Jim
