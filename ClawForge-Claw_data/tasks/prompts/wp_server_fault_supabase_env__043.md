嘿，NOC 值班同学，今晚 west4 机房的 UPS 又炸了，边缘集群的 spine uplink 直接掉线，好几个核心服务跟着扑街。我已经把当前所有工单快照放在 `data/incidents/incident_pool.json` 里了，你赶紧看一下。

我们需要优先处理那些因为 UPS 断电导致的服务中断 —— 这类工单的类别标记是“ups_outage”，而且只有严重等级达到“最高”的才需要我们立即介入（别的等级先放放）。按照 `data/attachments/` 下的那个 runbook（UPS and Service Outage Runbook）里的步骤进行批次修复，每个修复的工单要记录最终状态和操作动作。

修完之后，把处理结果写成一份清晰的记录，放到 `ops/resolution.json` 里，方便后续审计。同时，把你这次处理的全流程动作都记在 `ops/audit.log` 里，一行一个步骤，标明时间戳和动作名称就行。

别搞混了，我只想要那个跑完之后的最终成果文件，别留多余的东西。赶紧搞完发我，兄弟们还等着恢复呢。
