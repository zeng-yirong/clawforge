嘿，昨晚产品侧又吵起来了！我们同时跑了两个实验批次，编号 b1 和 b3，放在 `data/experiments/` 下面，文件名分别是 `batch_b1.csv` 和 `batch_b3.csv`。数据格式每个批次里都有 group_id、accuracy、latency_ms、cost_usd 这几个字段，但有些行可能录入时格式乱了，你帮我把能用的数据清洗干净。

我现在最关心的是：每个 group 的 accuracy 在前后两次实验里变化了多少？latency 和 cost 的差异也一并算出来。然后你帮我盯一下哪个 group 的 accuracy 差异绝对值最大（注意是绝对值），那个组很可能就是我们需要重点排查的。把所有差异数据按 group 整理好，加上 top_diff_group 标记，输出到 `ops/diff_analysis.json`。里面要包含每个组的差异详情和最终结论。拜托了，数据就这些，靠你了！
