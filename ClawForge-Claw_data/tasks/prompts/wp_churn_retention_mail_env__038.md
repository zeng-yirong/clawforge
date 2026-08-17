你好！我是Amanda，客户成功团队的负责人。昨晚我跑了一下活动日志，发现有些客户的状态让我很担心——风险等级标了“high”，而且已经超过30天没登录了。这种客户最容易悄悄流失，我得赶紧发一封挽留邮件过去。

我把客户的基本信息放在了 `data/customers/customers.json`，活动日志在 `data/logs/activity_logs.json`。另外，市场部的小伙伴整理了一批行业新闻样本，在 `data/news/news_samples.json` 里，每篇都标注了语气（机会还是痛点）。我想针对每一个高危客户，挑一条他们所在行业的“机会”类新闻（tone 是 "opportunity" 的那种），把新闻标题和摘要附在邮件里，让客户觉得我们还在持续关注他们。

请你帮忙整理一份缓存文件，放在 `ops/retention_draft.json` 里，格式是按客户排列的列表，每个元素包含：客户的ID（customer_id）、客户名称（customer_name）、新闻标题（headline）、新闻摘要（summary）。这样我后续可以直接拿这个文件批量生成邮件了。谢谢啦！
