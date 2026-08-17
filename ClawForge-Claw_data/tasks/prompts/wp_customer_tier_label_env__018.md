嘿，小A，帮我看一下客群分层的事。

最近运营那边提交了一套新的客户分层规则，我直接放到了 `ops/segment_rules.json` 里，规则优先级从上到下，命中第一条就停止。你拿 `data/logs/activity_logs.json` 和 `data/logs/consumption_logs.json` 的数据，跟 `data/customers/customers.json` 里的客户对上，给每个有效客户（那些标记了删除的不要管）更新一下标签。注意日志里可能有些脏数据——比如 `last_active_days` 是负数或者 `quarter_spend_usd` 是负数，这种就当没有这条记录处理。如果某个客户两项指标都不完整（或者都因为脏数据被丢弃），就标成“Unknown”。

更新规则只动 `labels` 字段，其他字段原样保留。整理完的新客户列表写成一个 JSON 文件，放到 `data/updated_customers.json` 里。我等着拿这个去跑后续流程，辛苦啦！
