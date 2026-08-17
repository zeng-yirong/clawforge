Subject: Urgent: Top tech beat needed for Q3 rebalance

Hey,

I've dumped the latest stock universe and earnings snapshots into the workspace. You'll find them under:

- data/stocks/stocks.json (the full universe with ticker, sector, price, etc.)
- data/earnings/earnings.json (all the recent earnings reports with revenue/beat numbers)

We're doing a Q3 sector rotation and I need the Technology stock with the **highest revenue_beat_pct** in its most recent earnings report. Only one winner – just the ticker and the beat percentage.

Please drop the result into a file called `result.json` in the workspace root. The format should be exactly:

{
  "ticker": "TICKER",
  "revenue_beat_pct": 12.34
}

Make sure you filter by sector "Technology" and only use the most recent quarter for each stock. I don't expect ties, but if there is one, pick the ticker that comes first alphabetically. Don't overthink it, just give me the numbers.

Thanks,
Alex
