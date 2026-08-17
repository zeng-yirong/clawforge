哎呀，小李，实验平台那边又出乱子了！我刚把两个批次的结果拖到 `experiments/` 目录下——一个是 `batch_alpha.csv`，另一个是 `batch_beta.csv`。领导让我赶紧对比一下每个实验组（group）的核心指标变化，好决定下一步是回滚还是加量。

不过垃圾数据也不少：那个 `batch_old.csv` 是上个月的历史残留，还有 `batch_incomplete.csv` 字段不全、`batch_corrupt.txt` 根本就不是个正经 CSV……这些统统别碰，别浪费你的时间。

我需要你帮我算清楚：对于每一种实验组 （group_id），求出它在 alpha 和 beta 两个批次之间的指标差值 —— 具体就是 accuracy、latency_ms 和 cost_usd 这三项的差值（alpha 减 beta）。然后把结果按 group_id 从小到大的顺序整理好，存到 `diff_records/result.json` 里。格式你自己定，但一定要方便我后续程序读，别搞成什么花哨的表格。

对了，一定要保证数据准！我懒得检查，直接拿去给领导汇报，错了咱俩都得挨批。搞快点！
