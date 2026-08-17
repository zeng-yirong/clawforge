嘿，Alice发来一封紧急邮件——

“我们刚跑完v2和v3两轮实验，数据在 `data/experiments/experiment_results.csv` 里。最近数据质量堪忧，有些行重复了，还有的字段写成了字符串（比如 latency_ms 填了 'ninety'），你清理一下，只保留格式正确的行，再去掉完全重复的记录。

然后帮我对比 v2 和 v3 这两个 batch，每个实验组（group_id）的核心指标（accuracy, latency_ms, cost_usd）变化有多大，把结果整理成一份结构化的差异记录，丢到 `ops/diff_record.json` 里。我要的是干净、准确的数据，谢谢！”

你收到邮件后，开始动手处理。
