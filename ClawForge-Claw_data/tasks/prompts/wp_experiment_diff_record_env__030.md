嘿，我是数据科学组的 Amy。昨天晚上我们一口气跑了两轮实验：批次 `batch-001` 是新模型压测，`batch-002` 是旧模型回放。我现在急需一份每个实验组（group_id）的准确率差分报告，量化新模型的优化效果。

数据在 `data/experiments/experiment_results.csv` 里，里面混杂了好几个批次的数据，你只关心我说的这两个。找出每个组在 `batch-002` 和 `batch-001` 之间的 accuracy 差值（`batch_002.accuracy - batch_001.accuracy`），然后把结果扔到 `ops/diff_record.json` 里。注意：如果一个组只出现在其中一个批次，说明数据不完整，直接忽略它，别写进报告。

格式上，我需要一个 JSON 列表，每个元素只有两个字段：`group_id` 和 `delta_accuracy`。快点搞定，我等着补汇报材料。
