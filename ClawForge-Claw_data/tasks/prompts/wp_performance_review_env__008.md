嗨，又到月底了，绩效汇总表一塌糊涂！我手工对了好几遍，眼睛都花了。你赶紧帮我理一理：

1. 员工花名册在 `data/employees/employees.json`，里面包含了所有人的信息。
2. 他们这个月的产出数据在 `data/ledgers/monthly_outputs.json`，注意有些人可能有重复记录（系统抽风多写了一次），以最后出现的那个为准。
3. 公司的评分规则在 `data/rules/scoring_rules.json`，别用错了版本（旁边还有个旧的，别碰）。
4. 只用算正式员工，实习生（role_code 是 `INTERN`）的不算。
5. 产出数据缺失的员工（找不到对应员工ID）直接跳过，不放进档案。
6. 算总分：加权平均值 = feature_delivery * 权重 + quality_score * 权重 + collaboration_score * 权重（权重从规则里取）。
7. 定等级：总分 ≥ 90 给 A；75 ≤ 总分 < 90 给 B；60 ≤ 总分 < 75 给 C；总分 < 60 给 D。
8. 把最终结果整理成一个 JSON 文件，放在 `output/performance_profiles.json` 里，每个员工一个对象，包含 employee_id、employee_name、department、total_score、rating。

弄好了直接发我，我明天要交老板。谢啦！
