> **发件人:** 李娜 (HR 绩效主管)  
> **主题:** 紧急：月度绩效评分自动生成

小张，帮个忙。

季度绩效评估下周就要，我一堆手工算的表格快疯了。  
技术那边已经把这个月的产出数据导出来了，规则文件也是现成的，都在工作区 `data/` 下面：

- 员工花名册：`data/employees/employees.json`
- 月度产出明细：`data/ledgers/monthly_outputs.json`
- 各岗位的评分权重：`data/rules/scoring_rules.json`

你按权重公式（产出×权重 + 质量×权重 + 协作×权重）把每个人的综合分算出来，然后按照老规矩打上等级：  
**优秀**（≥80）、**良好**（≥60）、**待改进**（<60）。  

把结果整理成一份清晰的报告，放到 `reports/performance_summary.json`，格式就按我们一直用的：  
每条记录包含 `employee_id`、`total_score`（保留一位小数）、`grade`。  

明天晨会就要用，别漏掉任何人啊。谢了！
