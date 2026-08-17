嘿，我是 DBA 小周。昨晚主库又出幺蛾子了 —— 一个长事务锁死了 billing 表，整个支付链路都堵住了。我紧急抓了一份锁分析报告，放在 `db_dumps/lock_analysis.txt` 里。同时我把今天的工单池快照也拷到了 `data/incidents_pool.json`。

你帮我快速定位一下：哪个工单造成了这个锁？把那一个工单的 ID 记下来，写到 `ops/resolve_target.json` 里，我直接拿去找经理审批强杀。只写那个唯一匹配的 ID，别搞混。格式就一个 JSON 对象，比如 `{"incident_id": "xxx"}`。快点，生产等着呢！
