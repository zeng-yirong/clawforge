# 故障事后分析

你好！我是 SRE 值班同事。刚刚 payment-service 的 fault-003 又出故障了，严重级别 critical。我把故障数据和附件都放在工作区里了：

- 故障案例列表在 `data/faults/fault_cases.json`
- 附件清单在 `data/attachments.json`，对应的日志文件在 `logs/` 下

这个故障的堆栈显示死锁，但具体原因还不清楚。你帮我深入分析一下，然后写一份事后分析（postmortem）放到 `ops/postmortem.json` 里。文件内容用 JSON 格式，包含两个字段：
- `root_cause`：根因分析结果
- `repair_plan`：修复计划

注意：ops 目录如果不存在就先创建一下。

我急着要，尽快搞定！
