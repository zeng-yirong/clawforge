嘿，市场情报那边刚扔过来一个紧急追踪需求——他们需要确认 **HelioSync Edge Inference Fabric** 在我们最近收拢的报告、演示稿和媒体样本里出现过哪些，以及每份文档对应的线索标签。老周说 Q2 的竞品分析报告就差这一块了，今晚必须补上。

具体来说，你帮我把几堆文件翻一遍：

- `data/reports/reports.json` 里是各行业的分析报告，注意字段 `solution_aliases` 会列出文档关联的技术方案名。
- `data/presentations/presentations.json` 是合作方分享的演示文稿，同样有 `solution_aliases`。
- `data/media_samples/media_samples.json` 是剪报、播客逐字稿和 keynote 草稿，也是同样的匹配规则。

我只要那些 **明确包含 “HelioSync Edge Inference Fabric”** 的文档（大小写别搞错），其他的都是干扰项。从每份命中文档里，把它的 `id`（报告是 `report_id`，演示稿是 `presentation_id`，媒体样本是 `sample_id`）和它身上挂着的 `tags` 列表取出来，作为一条线索记录。最后把所有线索汇总成一个 JSON 数组，扔到 `ops/clue_list.json` 里，结构大概像：

[
  {"id": "xxx", "clue_bullets": ["tag1", "tag2"]},
  ...
]
注意不要混进那些只写了 “HelioSync Edge Inference” 或 “HelioSync Fabric” 的文档——老周只要完整全名。另外如果某个文档根本不在 `solution_aliases` 列表里出现这个词，说明它不相关，别拿。

辛苦你了，弄好之后告诉我一声，老周等着要。
