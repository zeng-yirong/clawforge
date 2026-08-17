Hi Agent,

昨晚北数据中心 UPS 故障导致主库 replication 卡住，我怀疑之前有几个工单没处理干净。我把最新的事件快照放在 `incidents/incident_pool.json` 了，另外还上传了对应的 runbook 到 `attachments/runbook_ups_and_service.md`。

请你帮忙：

- 从 incident pool 里找出所有 **UPS 中断（category 为 ups_outage）且严重程度为 critical 且状态为 open** 的工单。要小心，有些工单虽然标题里写了 UPS 但类别其实是 db_replica_lag，别搞混了。
- runbook 里有一行关键指令，要求杀掉一个特定的事务 ID 来解除锁定。请把那个事务 ID 提取出来。
- 将找到的工单的信息（至少包含 incident_id）和那个事务 ID 打包成一个文件，命名为 `ops/remediation.json`。格式你自己定，但要把必要字段放进去，方便我直接读。
- 最后，把你这次操作的过程记录一份简单的审计日志，存到 `logs/audit.json`。日志里应该说明你处理了哪个工单、用了哪个事务 ID。

手头的资料就这些，请尽快完成。

—— Nikhil Rao, NOC Lead
