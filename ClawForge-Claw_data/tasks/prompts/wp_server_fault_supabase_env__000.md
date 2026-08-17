嘿，值夜班呢？刚才主库 IO 飙到 100% 告警了！我查了一下，有表级锁堆积，把正常写入全堵死了。

我手动把 InnoDB 状态快照存到了 `db_dumps/innodb_status.txt`，同时把最近 5 分钟的慢查询日志也拖下来了，在 `logs/slow_queries.log`。

你帮我顺着日志把那个锁持有者的事务 ID 找出来，直接写到 `ops/kill_target.json` 里，我马上 kill 它。

只要准确的 ID，其它废话别写。快！
