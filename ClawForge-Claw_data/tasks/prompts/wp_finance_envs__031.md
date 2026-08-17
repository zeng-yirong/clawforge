早安！我是投资研究部的分析师小李。老板让我今天下班前交一份科技板块的量化推荐，要用数据说话，不要拍脑袋。我手头的数据都放在 `data/` 下面了：

- `data/stocks/stocks.json` 里有所有股票的 sector、价格等信息。
- `data/earnings/earnings.json` 记录了每个季度的营收和 EPS 实际情况，以及是否超出预期。
- `data/news/news.json` 则列出了近期新闻，每条都有 sentiment 标签（bullish / bearish / neutral）和关联的 ticker。

我的想法是这样的：先只看 sector 为 Technology 的股票，然后给每支股票算一个综合得分 —— 最近一个季度的 EPS 超预期百分比（就是 eps_beat_pct）加上该股票近期 bullish 新闻的数量乘以 5。谁的得分最高，就把它作为推荐标的。

麻烦你帮我把得分最高的那个股票 ticker 和它的总分整理成一个 JSON 文件，放到 `ops/sector_score.json` 里。格式就写 `{"ticker": "xxxx", "score": 数字}`。

注意一定要用最新的季度数据（按 report_date 最晚的），只考虑科技股，新闻只算 sentiment 为 bullish 的。多谢！
