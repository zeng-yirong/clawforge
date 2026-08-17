Hi,

上个月的绩效评分汇总搞到最后发现版本全乱了，我重新整理了一份干净的放在下面：

- **员工花名册**：`data/employees/employees.json`（只包含当前在职人员）
- **月度个人产出**：`data/ledgers/monthly_outputs.json`（每人的 feature_delivery、quality_score、collaboration_score）
- **各角色评分规则**：`data/rules/scoring_rules.json`（每个 role_code 对应的三个权重系数）

我需要你把每位在职员工（以`employees.json`为准）的月度绩效总分算出来，**只算那些既有产出记录又有对应评分规则的人**。公式就是标准的加权和：

> **总分 = feature_delivery × feature_delivery_weight + quality_score × quality_weight + collaboration_score × collaboration_weight**

请把最终结果写在 `ops/performance_profiles.json` 里，我急着发给财务。每条记录至少包含：
- `employee_id`
- `employee_name`
- `role_code`
- `total_score`（保留两位小数）
- `component_scores`（详细列出三项原始分和所用权重，结构自定）

辛苦了，这周五之前要贴板。

—— Alice（HR）
