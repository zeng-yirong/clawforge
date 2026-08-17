Hi there,

我这边在赶技术板块的周报，刚把数据库快照拖到 data/ 目录下了。麻烦你帮我整理一下 TECH 这只股票的核心指标。

具体来说，我需要你从 data/ 下面的 stocks.json、earnings.json 和 news.json 里找出 TECH 的最新数据，然后生成一个简单的分析文件，放在 reports/ 目录下，文件名就叫 tech_analysis.json。

文件里放这些信息就行：
- ticker (就写 "TECH")
- latest_quarter (最新的那个财报季度名称，比如 "Q2 2026")
- eps_beat_pct (最新季度的 eps 超预期百分比，从 earnings 里拿)
- bullish_high_impact_news (统计与 TECH 相关的、sentiment 为 bullish 且 impact 为 high 的新闻条数)
- pe_ratio (从 stocks 里拿 TECH 的 pe_ratio)

注意只使用最新的季度数据，别把过时的季度算进去。新闻也只算 bullish 且 high impact 的，别混进 low 或 medium 的。输出 JSON 语法要正确，别多字段也别少字段。

弄好了通知我一声，我直接读文件。谢啦！

Sarah Chen
