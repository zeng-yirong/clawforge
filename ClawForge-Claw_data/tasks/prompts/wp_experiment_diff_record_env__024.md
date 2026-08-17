嘿，小何，实验平台那边又搞乌龙了！刚才我跑了两个批次的对比，结果发现前一个版本（v2.1）的"batch_20250301"和后一个版本（v2.2）的"batch_20250315"在核心指标上差得离谱，但没有汇总差异报告，没法向老板汇报。  

我把两个批次的原始数据放在 `data/experiments/` 下面了，里面混了一些杂七杂八的旧文件和空文件，别管它们。每个批次有多个实验组（group_id），同一个组在两个批次里都有记录，但部分组可能只出现在其中一个批次里。我需要你：  

1. 对比这两个批次，找出同时存在于两个批次中的组（group_id）。  
2. 对每个共同组，计算三个核心指标的差异：准确率差值（accuracy_diff = batch_20250315的accuracy - batch_20250301的accuracy）、延迟差值（latency_diff = batch_20250315的latency_ms - batch_20250301的latency_ms）、成本差值（cost_diff = batch_20250315的cost_usd - batch_20250301的cost_usd）。  
3. 把计算结果整理成一份 JSON 文件，放在 `ops/` 目录下，命名为 `diff_report.json`。格式示例：  
{
  "diff_record": [
    {
      "group_id": "g1",
      "accuracy_diff": 0.05,
      "latency_diff": -10.2,
      "cost_diff": 0.3
    }
  ]
}
强调：所有数值保留两位小数，字段名严格一致，不要漏掉任何共同组，也别把单批次出现的组加进去。  

搞定了告诉我一声，我直接拿去钉钉上发。谢啦！  
