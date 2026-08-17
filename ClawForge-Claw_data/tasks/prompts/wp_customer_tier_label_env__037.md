嘿，运营那边昨晚开了个会，给客户分层定了新规矩。具体规则他们发在了即时消息里，我转述给你：

- 季度消费超过1万美金，并且最近30天内有活动的，标为 "VIP"
- 季度消费超过1万美金，但最近30天内没有活动的，标为 "High_Value"
- 季度消费低于1万美金，并且超过90天没有活动的，标为 "At_Risk"
- 其他所有客户，标为 "Standard"  

他们让我今天就把更新后的标签整理出来，明天系统要用。我已经把原始的客户档案、消费流水和活动日志都放在了工作区里，就这些文件：

- `data/customers/customers.json` – 客户主数据，每个客户有 `customer_id` 和初始 `labels`
- `data/logs/consumption_logs.json` – 每位客户的季度消费金额（`quarter_spend_usd`）
- `data/logs/activity_logs.json` – 客户的活跃度信息，包括 `last_active_days`

你按上面的规则算一下，把每个客户的最新标签写到 `ops/label_updates.json` 里面去。格式就按这个结构来：

{
  "label_updates": [
    { "customer_id": "…", "labels": ["VIP"] },
    { "customer_id": "…", "labels": ["Standard"] }
  ]
}
里面有空记录、脏数据什么的，你自己看着处理，别把无效的客户算进去。弄好了告诉我一声，我直接拿去部署。
