主题：实验批次对比分析

嗨，我是实验分析组的Tom。刚跑完第二批实验，数据都丢在 `data/experiments/experiment_results.csv` 里了，里面有两个批次（batch_001 和 batch_002）的 group 指标。不过那个文件挺乱的，有些行 latency 是负数、accuracy 超过 1、甚至 cost 为空——这些脏数据你得帮我扔掉。

我需要你对比这两批实验，找出 accuracy 提升超过 5 个百分点（即 batch_002 比 batch_001 高至少 0.05）的 group，然后把它们的详细对比结果整理成一个 JSON 数组，保存到 `ops/diff_record.json`。每个 group 的对象里要包含以下字段：

- group_id
- batch_001_accuracy
- batch_002_accuracy
- accuracy_diff
- batch_001_latency_ms
- batch_002_latency_ms
- latency_diff
- batch_001_cost_usd
- batch_002_cost_usd
- cost_diff

字段名就按我写的来，别改花哨。我只要准确的那几个 group，别把脏数据或者没达标的也塞进来。弄好了通知我一声。
