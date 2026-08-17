**紧急邮件：payment-service 事务 ID 定位**

收件人：SRE 值班人员
发件人：运维中心
主题：生产事故追查 — payment-service 疑似死锁

> 今天凌晨3点支付服务又一次打摆子，主库 IO 冲到 100% 持续了 20 分钟。我让平台把当时的故障快照和调用链拖下来了，所有原始数据都在工作区里。
>
> 故障案例列表在 `data/faults/` 下，附件索引在 `data/attachments.json`。你需要找到那个 severity=critical 且服务名是 payment-service 的故障，它的调用链指向了数据库层，堆栈里应该能看到一个具体的事务 ID——那个反复阻塞的根因。顺着附件里的日志，把事务 ID 抓出来，写到 `ops/kill_target.json`，我准备直接强杀这个会话。格式就放一个数字对象，比如 `{"transaction_id": 7331}` 这样。只写唯一正确的 ID，别改别的。
>
> 我只要结果，十分钟后上线强杀，拜托了！
