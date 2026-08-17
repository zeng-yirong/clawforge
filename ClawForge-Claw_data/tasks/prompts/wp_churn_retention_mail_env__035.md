嗨，我是客户成功团队的小张。我们系统刚刚拉了一份高风险客户名单，但我需要你帮忙筛选出那个最紧急的客户，再搭配一条能打动他的行业新闻，最后生成一封挽留邮件缓存下来。

具体是这样的：
- 客户数据在 `data/customers/customers.json` 里，顶层有个 `customers` 数组，每条记录包含客户名称、行业、等级等信息。
- 活动日志在 `data/logs/activity_logs.json`，同样顶层 `activity_logs` 数组，记录了风险等级、最后活跃天数、使用趋势、工单情绪。
- 行业新闻样本在 `data/news/news_samples.json`，顶层 `news_samples` 数组，有行业、标题、语气（opportunity 或 pain_point）等。

我希望你找出那个最应该发挽留邮件的客户：他的活动日志显示风险等级是“high”，已经超过一个月没活跃（最后活跃天数 > 30），使用趋势持续下降（down），而且工单情绪是负面的（negative）。然后从他的行业中，挑一条语气是“opportunity”（机会）的新闻，作为邮件的切入点。

最后，把生成的邮件内容整理成结构化数据（比如 JSON），存入 `ops/retention_cache.json`。邮件正文里要有客户名称和新闻标题，以 "Dear [客户名称]" 开头。我下午开会要用，谢谢！
