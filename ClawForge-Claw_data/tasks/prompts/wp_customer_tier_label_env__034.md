嘿，帮我看一下客户标签的事情。

上个季度刚结束，财务那边甩过来一份季度消费明细，放在 `data/logs/consumption_logs.json`。运营团队也把客户活跃度报告导出来了，在 `data/logs/activity_logs.json`。我估计现有标签早就过期了——很多客户实际消费很高但还挂着“mid_market”，或者活跃度很高的客户居然没被打“premium”。

我们的分层规则其实挺直白：季度消费超过10万美金、最近30天内活跃过且风险低的，就该是 enterprise，带 premium 和 high_value 标签；消费在5万到10万之间并且活跃度上升的，给 mid_market 和 growth 标签。其他的保持不动就行。

你别管那些干扰文件——`ops/` 下面有个旧更新列表已经没用了，直接忽略。客户主数据在 `data/customers/customers.json`。你根据消费和活跃数据，把真正需要更新标签的客户挑出来，生成一个清单放到 `ops/label_updates.json` 里。我要的就是一个 JSON 列表，每项带上客户 ID、新的 tier、新的 labels。别画蛇添足，只输出真正需要改的那几个客户。

辛苦，尽快搞定。
