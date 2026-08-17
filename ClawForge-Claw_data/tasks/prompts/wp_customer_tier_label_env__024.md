销售总监今早摔了电话——客户分层还是三个月前的旧数据，给VIP客户发错了活动邮件！你赶紧处理一下。

财务那边刚把季度消费数据扔到了 `data/logs/consumption_logs.json`，IT也导出了最新的用户活跃日志 `data/logs/activity_logs.json`。客户主数据在 `data/customers/customers.json` 里，每个客户当前挂着什么等级你一看便知。

新规矩是这样的：  
- 季度消费超过1万块，而且最近一个月内（≤30天）登录过的，升 **VIP**；  
- 季度消费超过5千，并且最近两个月内（≤60天）有活动的，升 **Premium**；  
- 剩下的统统归为 **Standard**。  
注意：如果某个客户既没有消费记录也没有活跃记录，就保持他原来的等级，别动他。

结果按客户ID和新等级整理成 JSON，放到 `ops/tier_updates.json` 里，我直接导入系统。格式就像这样：  
`[{"customer_id": "xxx", "new_tier": "VIP"}, ...]`  
别漏了人，也别多出莫名其妙的字段，销售部等着用呢。
