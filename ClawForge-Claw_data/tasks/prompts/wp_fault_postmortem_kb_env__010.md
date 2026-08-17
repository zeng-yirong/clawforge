嘿，昨晚支付服务又瘫了，主库 IO 飙到 100%，我连夜把现场数据都 dump 到了 `data/` 下。

故障案例在 `data/faults/fault_cases.json` 里，每个案例都带了一个附件清单在 `data/attachments.json`，附件文件存放在 `data/attachments/` 下。另外，团队联系人在 `data/contacts.json`，每个故障案例里标明了负责人的 ID。

我想要一份事故事后分析（postmortem）存到 `ops/reports/` 目录下，文件名就用该故障的 ID（例如 `fault-xxx.json`），内容必须包含：
- 根因（Root Cause）
- 修复计划（Repair Plan）
- 负责人的邮箱（从联系人里找对应 ID）

这次事故是最严重的那个 **critical** 级别，它的附件里写了详细的分析过程和结论，你先把那个 critical 的故障挑出来，再读一下它的附件，把关键信息摘出来写进报告。注意附件可能有旧版干扰，请用标题里带“Analysis”且包含故障ID的那个。

拜托了，我等着拿这份报告去跟 leader 汇报。
