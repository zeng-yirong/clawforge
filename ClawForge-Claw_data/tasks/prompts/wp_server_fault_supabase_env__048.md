Subject: [URGENT] Main DB I/O spike – need kill target

Hey Agent,

凌晨3点主库IO飙到100%了！我已经把今天的慢查询日志和数据库快照拉下来了，都放在 `db_dumps/` 下面。日志里能看到明显的表级锁堆积，应该是一个长事务卡住了。我需要你从这些日志里找出那个持有锁的罪魁祸首事务ID，然后写进 `ops/kill_target.json`，我这边马上强杀它。别搞错了，我只要准确的数字ID。

多谢！

- Ops Team
