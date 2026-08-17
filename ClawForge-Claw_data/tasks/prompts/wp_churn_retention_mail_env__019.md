Hey, 我是市场部的 Jamie。我们注意到好几个重要客户最近活动量暴跌，很可能要流失。我把活动日志扔在了 `data/logs/activity_logs.json`，里面标了每个客户的风险等级。另外，我在 `data/news/news_samples.json` 里整理了一批行业新闻，有些是讲市场机遇的，特别适合用来做挽留邮件的内容。客户的基本信息在 `data/customers/customers.json`。

帮我个忙：把那些高风险客户筛出来，每个客户找一条他们所在行业里的“机会型”新闻（就是 tone 是 opportunity 的那种），然后把客户 ID、客户名称、所属行业、新闻标题和摘要一起整理到 `ops/retention_cache.json` 里。格式你定，但字段得清楚，我后面直接拿这个缓存去批量发邮件。辛苦啦！
