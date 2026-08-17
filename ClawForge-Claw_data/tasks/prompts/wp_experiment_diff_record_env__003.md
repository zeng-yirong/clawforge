😤 嘿，凌晨三点被 on-call 叫醒，线上模型今天下午要切新版本，但我手头两个实验批次的结果让人头疼。

我把 `data/experiments/` 下的实验结果拖下来了，里面有两个关键批次：`batch_001`（我们的新方案）和 `batch_002`（线上基线）。但 `data/experiments/` 里还混了一堆旧批次和几行格式乱掉的数据，你别把它们算进去。

帮我干一件事：读这个 CSV，把这两个批次的 **核心指标平均值** 对比出来——准确率（accuracy）、延迟（latency_ms）、成本（cost_usd）。然后整理成一份差异报告，存到 `ops/diff_record.json`。

对了，报告里要附上分析人署名，你去 `data/accounts.json` 里找 `account_id` 是 `analyst_001` 的 `display_name` 写上。

报告结构就这样（你按自己理解组织，但必须包含这俩批次 ID 和三个指标的平均值差以及署名）：

- batch_a_id: "batch_001"
- batch_b_id: "batch_002"
- avg_accuracy_diff: （batch_001 平均值 - batch_002 平均值）
- avg_latency_diff: （batch_001 平均值 - batch_002 平均值）
- avg_cost_diff: （batch_001 平均值 - batch_002 平均值）
- analyst: （那个人的名字）

处理好直接丢到 `ops/diff_record.json`，我等着用。谢谢！
