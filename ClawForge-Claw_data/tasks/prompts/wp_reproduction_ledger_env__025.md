嘿，我这边刚跑完一批开源项目文档的复现验证，数据都在 `project_docs/` 目录下了。我需要你帮忙整理一份复现账本归档到 `ledger/` 目录。

具体来说，找到所有项目 ID 为 `proj-025` 的文档，提取它们的 **doc_id、title、path 和 project_id**，按 doc_id 升序排列，生成一个 JSON 文件命名为 `reproduction_ledger.json`。账本格式我习惯用：

{
  "project_id": "proj-025",
  "documents": [ ... ]
}
注意，里面有些文件是其他项目的，还有个别文件格式不太对劲，跳过去就行。动作快点，我等着归档呢！
