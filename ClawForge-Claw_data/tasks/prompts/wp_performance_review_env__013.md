嗨，我这边是 HR 系统组的。这月绩效汇总又把我搞得头大 —— 各部门的 Output Ledger 和 Scoring Rules 散落在各个文件夹里，数据虽然全，但格式不统一，还有几个旧版本的规则文件混在里面。

你能不能帮我从 `data/` 底下把东西理清楚？具体的：
- `data/employees/` 下有个员工主表，里面每个人有唯一的 employee_id 和角色代码 role_code。
- `data/ledgers/` 里放的是各员工本月的输出明细，每个员工一条记录，包括 feature_delivery、quality_score、collaboration_score（都是整数）。
- `data/rules/` 下有一份最新的评分规则，每条规则按 role_code 定义了三个指标的权重（百分比的小数形式）。

我要你根据每个员工的角色代码，找到对应的权重，然后计算加权总分（保留两位小数）。把计算结果整理成绩效档案，放到 `performance_profiles/` 目录下。每个员工一个 JSON 文件，命名就用 `{employee_id}.json`，里面至少要包含员工 ID、总分（total_score），以及各项得分乘权重后的明细（breakdown），这样我下个月对比起来方便。

注意：有些员工可能没有输出记录，或者规则里找不到对应角色，那些就直接跳过不生成档案。所有合法的结果都放进去就行。

另外，我观察到 `data/rules/` 里好像有几个旧版本的规则文件（名字里带 `_old` 或 `_v1` 之类的），别搞混了，用最新的那个 `scoring_rules.json`。

搞完后告诉我一声，我这边等着发绩效邮件呢。
