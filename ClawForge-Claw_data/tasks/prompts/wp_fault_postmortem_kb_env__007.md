早上好！昨晚 3 点，`order-service` 又出大事了，整个支付链路卡死，用户投诉炸了。我紧急把现场数据捞了下来，放在 `data/` 目录下。

故障案例已经录进了 `data/faults/fault_cases.json`，里面还有一个严重等级为 critical、根因和修复方案都是空白的条目——就是那个还没定位的。相关附件在 `data/attachments.json` 里列出了，日志文件也在 `data/attachments/` 下。

麻烦你帮我把根因分析出来，按照 `ops/postmortem/example.json` 的格式，生成一份完整的回顾报告，放在 `ops/postmortem/` 下，文件名就用故障 ID 加上 `_postmortem.json`。老板等着开会用，拜托了！
