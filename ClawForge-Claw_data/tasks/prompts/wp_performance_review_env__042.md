嗨，我是HR的李姐。上个月系统崩溃了一次，数据恢复后我手动从后台导出了最新的输出台账和评分规则，放在 `data/ledgers/monthly_outputs.json` 和 `data/rules/scoring_rules.json` 里。员工名单在 `data/employees/employees.json`。

现在需要你帮我生成一份上个月的绩效得分报告。请务必注意：有一些员工已经离职了，他们的角色代码在评分规则里根本不存在，直接忽略就行。另外我只想要最新那一个月（2025年3月）的记录，旧数据不准用。最终把报告写到 `ops/performance_profile.json` 里，每个员工只要写上员工ID、姓名、部门、角色代码和加权得分就行。辛苦啦，我等着拿这个去开绩效会呢。
