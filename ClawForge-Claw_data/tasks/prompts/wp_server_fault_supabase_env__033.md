**紧急：生产主库 IO 打满，疑似表级锁死锁**

凌晨3点主库 IO 飙到 100%！我把 `db_dumps/` 的快照和慢查询日志拖下来了，同时把 `data/incidents/` 里的工单池也拉来了。

你看看 `data/attachments/` 里的 runbook，有几类工单需要我们立即处理。根据 runbook 的指引，找出所有需要修复的工单，然后按照 runbook 里给出的 resolution 模板，生成一份修复决议放到 `ops/resolution.json` 里。

我只需要准确的工单 ID 和对应的操作，别放多余的信息。生产环境在冒烟，快点搞定！
