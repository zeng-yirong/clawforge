嘿，Jason，我是人力资源部的Mia。刚刚收到 Sam（技术总监）的抱怨邮件，他说上个月绩效数据里 **E001**（张伟，后端架构师）的结果看起来不对劲，他记得张伟交付了两个大功能，质量分也很高，但系统生成的绩效总分只有72分？Sam觉得是不是权重配错了或者用了旧数据。你能帮我把这个搞清楚吗？

我在 `data/employees/employees.json` 里放了最新的员工花名册；`data/ledgers/monthly_outputs.json` 里是本周刚导出的各个员工的月度产出数据，但听说这个文件可能有几条旧记录还没来得及清理；`data/rules/scoring_rules.json` 里是各职级的评分规则，不过上个月HR调整过一次权重，我要确保你用的一定是最新生效的那一套规则（留意规则文件中的生效日期字段）。

你核实完之后，帮我生成一份正确的绩效档案，放在 `profiles/performance_profile.json` 里。张伟的档案只需要包含：`employee_id`、`employee_name`、`department`、`role_code`，以及按照正确规则算出来的 `feature_delivery_score`、`quality_score`、`collaboration_score` 和 `total_score`。总分保留一位小数即可。

别搞错人了，也别用了过期的规则。搞定了告诉我一声，我直接拿去回复Sam。
