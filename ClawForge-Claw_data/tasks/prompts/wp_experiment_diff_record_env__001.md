嘿，我是算法组的。刚刚跑完了新版本 v2 的 A/B 实验，需要跟上一轮的 baseline v1 做个对比。数据我已经放在 `experiments/` 下面了，baseline 在 `batch_v1.csv`，新版本在 `batch_v2.csv`。每个 CSV 里都有几条 group 记录，分别记录了准确率（accuracy）、延迟（latency_ms）和成本（cost_usd）。

麻烦你帮我把这两个批次的核心指标算一下平均值，然后计算它们之间的变化量（v2 减去 v1）。最后把结果整理成一份差异报告，存到 `reports/diff_v1_v2.json`。报告里我希望明确包含 baseline 标识（batch_1）、新版本标识（batch_2），以及一个 metrics_diff 对象，里面放 accuracy、latency_ms、cost_usd 这三个指标的差值。其他文件不用动，目录结构也别乱加东西。

先谢了，急用！
