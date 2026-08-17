嗨，我是 Rhea，信号研究这边的。我们正在追踪 HelioSync Edge Inference Fabric 的落地线索，这个方案在物流和工业场景里开始冒头了。

我把最新的行业报告、内部演示和媒体录音都丢在了 `data/` 下面，具体结构是：
- `data/reports/` 下的报告 JSON
- `data/presentations/` 下的演示 JSON
- `data/media_samples/` 下的媒体样本 JSON

每个文档里都有个 `solution_aliases` 字段，里面列了它关联的技术别名。我们关心的那个技术，常用名是“HelioSync Edge Inference Fabric”，但文档里也可能写成“HEIF”或者中文的“边缘推理框架”。你翻一下就能找到。

帮我做一件事：把所有明确提到这个技术的文档找出来，把它们各自的文档 ID、文档类型（report/presentation/media_sample）以及对应的 `summary`（就是那个摘要字段）整理成一个 list，写到 `ops/clue_list.json` 里。我后面要拿这个清单去对线索。

要求就一个：准确，别漏也别多。附件 `data/attachments/solution_matching_notes.md` 里有更详细的匹配说明，不过核心规则就上面那些。

辛苦了！
