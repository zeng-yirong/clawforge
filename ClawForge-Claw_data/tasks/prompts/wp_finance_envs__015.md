Subject: 科技板块简报，急！

Hi,

刚把数据拖下来扔到 `data/` 下面了，时间紧张。老规矩，那帮系统集成的家伙给的数据从来一团糟——`stocks.json` 里一堆其他板块的，还有些奇怪的重复；`earnings.json` 里同一个股票同一个季度能出现好几条记录，真假难辨；`news.json` 还算凑合，但也混了无关旧闻。

我需要你帮我把 **Technology 板块** 唯一那支股票找出来，结合它最新的财报表现和相关的新闻，做一个判断：**Buy / Hold / Sell**。最后把结论放到工作区根目录的 `tech_brief.json` 里，格式你自己定，但必须包含：

- 股票代码 ticker  
- 推荐评级 recommendation  
- 你引用的 earnings 记录 ID 列表（earnings_ids）  
- 你引用的 news 记录 ID 列表（news_ids）  

这样我下午见客户之前还能快速复核一遍。拜托了！

—— Alice
