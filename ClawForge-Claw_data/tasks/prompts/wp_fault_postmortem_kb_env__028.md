嘿，Simba，线上出事了！

昨晚线上突然爆出一个 Critical 级别的故障，我从工单系统里拉到了故障快照，放在 `faults/fault_cases.json` 里面，故障 ID 是 `fault-001`。堆栈显示是个空指针问题，我大致看了一眼调用链，感觉跟 `AccountService.getAccountBalance` 有关。另外我还把相关的知识库附件拖到了 `attachments/` 下面，我记得有个知识条目正好记录了类似的修复方案。

你帮我做一份事后分析归档吧，把根因和修复方案整理清楚，放到 `postmortem/` 目录下，文件名就叫 `analysis.json`。记得把参考的那条知识条目标题也带上，方便以后复盘追查。

尽快搞定，我等着提交报告。
