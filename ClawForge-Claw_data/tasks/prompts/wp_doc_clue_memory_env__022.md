我是Keiko Han，市场情报组的。老板催我要一份关于「HelioSync Edge Inference Fabric」的技术解决方案线索清单，最好是按来源归类。

我把所有数据都放在工作区了：`reports/reports.json`、`presentations/presentations.json`、`media_samples/media_samples.json`。每个JSON文件里都有一个同名的数组（比如`reports`），每个对象都有 `id`、`title`、`summary`、`solution_aliases` 等字段。`solution_aliases` 字段列出了该文档涉及的技术方案。

请你找出所有在 `solution_aliases` 中**明确包含** `"HelioSync Edge Inference Fabric"` 的条目，然后提取每个条目的：**来源类型**（`report`/`presentation`/`media_sample`）、`id`、`title`，以及**关键线索摘要**（就是 `summary` 字段的内容）。

最后把这些信息汇总成一个JSON列表，保存到 `ops/target_clues.json` 文件里，格式类似：
[
  {"type": "report", "id": "RPT-001", "title": "...," "clue": "..."},
  ...
]
注意：只选精确匹配的，别把拼写近似但不完全一致的误选进来。我半小时后要用！快！
