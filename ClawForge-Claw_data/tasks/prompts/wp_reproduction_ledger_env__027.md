Hi! 我正在整理研究项目的复现账本，数据有点乱。工作区里有 `data/projects/project_docs.json` 存放了所有项目文档的快照，以及 `data/contacts.json` 记录了项目联系人的信息。

请你帮我生成一份归档的复现账本，只考虑那些状态标记为 `active`（激活）的文档，不要包含已经归档或过期的。对于每个这样的文档，我需要记录它的 `doc_id`、`title`，以及该文档对应的负责人姓名（可以通过文档中的 `contact_id` 在联系人列表中找到对应的 `name` 字段）。如果联系人找不到，负责人姓名用 `"Unknown"` 代替。

最终输出一个 JSON 文件，保存到 `archive/reproduction_ledger.json`。格式为包含一个 `documents` 数组，每个元素是一个对象，包含上述三个字段。谢谢帮忙！
