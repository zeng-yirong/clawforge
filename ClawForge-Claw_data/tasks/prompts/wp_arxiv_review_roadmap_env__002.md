嘿，小陈，终于有空找你了。我们组最近在整理 Tool-Augmented Reasoning 方向的文献，准备投一篇综述。前天我把从 ArXiv 扒下来的论文摘要扔到了 `data/papers/` 里，还有几份我写的阅读笔记在 `data/attachments/` 下。不过那些论文很杂，不止我们这个方向的，还有一些旧版本和重复的，你帮我筛一筛。

帮我做两件事：第一，写一篇简短的综述，总结我们方向关键论文的贡献和思路；第二，画一个技术路线图，用 Mermaid 格式，把论文之间的演进关系串起来。你以前整理过这个方向，应该知道哪些是重点。

整理好的结果放到 `results.json` 里，我后面要用脚本批量处理，所以请严格按照 JSON 格式，包含三个字段：`review`（综述文本）、`roadmap`（Mermaid 代码字符串）、`papers_used`（你实际引用的论文 ID 列表，方便我核对）。综述里务必提到每篇你引用的论文标题，路线图里要用 `graph TD` 开头。别搞错了，别漏了。

哦对了，`data/papers/papers.json` 里每条记录都有 `paper_id`、`title`、`direction` 这些字段，附件信息在 `data/attachments/attachments.json` 里。需要什么你自己读。动作快点，晚上组会要用。
