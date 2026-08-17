哈喽，我是客户运营部的Tom。最近我们上线了一套新的客户分层自动标签规则，想趁今天把老数据刷一遍。  

有几个客户档案本来就有标签，比如“existing”、“vip”什么的，需要保留；新规则再追加一些。  

规则手册我截图放附件了，核心逻辑记在脑子里了：  
- 最近30天内有活跃的（last_active_days < 30） → 加 “active”  
- 超过90天没动弹、而且风险等级是 high 的 → 加 “churn_risk”  
- 季度消费超过 10000 并且使用趋势在上升 → 加 “high_value”  
- 季度消费不到 5000 的 → 加 “low_spend”  
- 使用趋势下降 → 加 “declining”  

原始数据都在 `data/` 下面：  
- 客户主档：`data/customers/customers.json`  
- 活动日志：`data/logs/activity_logs.json`  
- 消费流水：`data/logs/consumption_logs.json`  

处理完以后，你把更新后的完整客户列表（保持原 JSON 结构，labels 字段里保留旧标签、追加新标签）写到 `ops/updated_customers.json` 就行，我这边直接拿去推给 CRM。  

拜托了，今天下班前要！  
