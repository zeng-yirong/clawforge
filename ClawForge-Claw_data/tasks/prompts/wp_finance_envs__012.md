Hey,

I'm wrapping up a brief on TechVentures (ticker: TECH) and need your help with the data grind. I've dumped the latest snapshot into the `data/` folder – you'll find stocks, earnings, and news there.

Could you do a quick check for me?

- First, confirm TECH is in the Technology sector (it should be).
- Pull out its most recent earnings report – I need the exact EPS beat percentage if they beat estimates.
- Scan the news for any bullish, high-impact stories that mention TECH. Those are the ones that could really move the stock.
- Finally, pack everything into a JSON file under `reports/analysis_TECH.json`. The file should include:
  - `ticker` (string)
  - `company_name` (string)
  - `latest_earnings_date` (string, format YYYY-MM-DD)
  - `eps_beat_pct` (number, e.g. 0.15)
  - `bullish_news_headlines` (array of strings – only the headlines of bullish, high-impact news)

Ignore old backups or anything not related to TECH. Just the clean, current data.

Thanks,
Sarah
