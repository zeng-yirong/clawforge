Hey, 刚刚收到战略团队的消息：下季度的技术方案筛选要提前了，他们点名要 **HelioSync Edge Inference Fabric** 的所有关联线索。我把手头的文档全都拖到工作区了——报告、演示稿、媒体样本，乱七八糟什么都有。有些是旧版本，有些只是沾了点边，别被它们骗了。

你去看 `data/reports/`、`data/presentations/` 和 `data/media_samples/` 下面的 JSON，每个文档的 `solution_aliases` 字段会告诉我们它到底是不是在讲这个方案。只把明确列了 **HelioSync Edge Inference Fabric**（注意大小写和空格，必须完全一致）的那些文档找出来。

每个匹配的文档，你记下它的 ID（比如报告就是 `report_id`）和一条关键线索——从 `summary` 里摘出开头一句话就行。另外，别忘了标注它属于哪种类型（report / presentation / media_sample）。`data/attachments/` 里有个 `temp_record_guidelines.md`，里面有标准的线索清单格式，照着那个来。

整理好的结果放到 `ops/clue_list.json`。我这边等着导入系统，别耽误事。
