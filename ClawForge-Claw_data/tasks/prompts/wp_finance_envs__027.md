Subject: Urgent: Need Tech Sector Summary for Quarterly Review

Hi there,

I'm working on the Technology sector quarterly review and the data distribution is a mess — someone mixed old backups into the active folders. I need you to piece together a concise summary for the most promising tech stock based on the latest available data.

Here's what I need:

- Go through the `data/` directory. There are multiple versions of stock and earnings files; please use only the ones that are clearly the most recent (ignore anything with '_backup' in the name or inside a backup folder).
- Focus on the Technology sector. Find the stock with the highest year-over-year revenue growth among all tech stocks.
- For that stock, grab its most recent quarterly earnings (the latest quarter by report date) from the correct earnings data.
- Also find the most recent news article (by published date) that mentions this stock and has a defined sentiment.
- Combine these findings into a single JSON file at `briefs/tech_summary.json`. The structure should include: ticker, company_name, sector, latest_quarter, revenue_beat_pct, eps_beat_pct, revenue_growth_yoy, news_headline, news_sentiment, and a recommendation. The recommendation should be "Buy" if the news sentiment is bullish AND the earnings report shows an EPS beat; otherwise "Hold".

Make sure you pick the correct files — I don't want any outdated data slipping in. Let me know if anything's unclear.

Thanks,
Sarah Chen
