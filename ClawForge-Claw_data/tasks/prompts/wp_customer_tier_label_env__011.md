Hey team,

季度分析报告刚出来，销售那边催着要更新客户标签。Data team 已经把最新数据放在 `data/logs/` 下面了——`activity_logs.json` 和 `consumption_logs.json`。客户基础信息在 `data/customers/customers.json`。

之前开会确定的分层规则还记得吧？季度消费高、近期活跃的给 VIP 标签；中等消费、还算活跃的标 Active Grower；低消费或长期不活跃的标 At Risk。另外，如果某个客户风险等级高，就额外加一个 High Risk 标签。注意别把客户原来已有的标签弄丢了，合并的时候去重就行。

结果放到 `ops/labels_update.json` 里，格式简单点：一个列表，每项写清楚 `customer_id` 和更新后的 `labels`。别漏了客户，也别被 `data_backup/` 里那些旧文件干扰。

快点搞，销售等着用。

——运营老张
