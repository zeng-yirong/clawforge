Subject: 本月绩效汇总 – 急着用

Hi 团队，

又到月底了，老板催着要每个人的综合绩效分。员工花名册在 `data/employees/employees.json`，里面每个人的岗位代码都标好了。他们这个月的产出数据（交付、质量、协作三个维度）我放在 `data/ledgers/monthly_outputs.json` 了。另外不同岗位的权重定义在 `data/rules/scoring_rules.json` 里，各维度权重乘一下再相加，就是综合得分。

请把你算好的结果整理成一个 JSON 文件，放到 `profiles/performance_profiles.json` 里。每条记录要包含员工 ID、姓名、部门、岗位代码和最终得分（保留一位小数就行）。我直接用这个文件出报告，谢谢！

—— HR 经理
