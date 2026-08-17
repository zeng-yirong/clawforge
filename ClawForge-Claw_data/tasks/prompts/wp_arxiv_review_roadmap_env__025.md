嘿，上周我让你整理的 ArXiv 论文列表，我这边会议前急需一个 Tool-Augmented Reasoning 方向的综述重点。先别急着写全文，我需要你从 `data/papers/` 里找出这个方向被引用最多的那篇论文——也就是在整个论文库里被其他论文引用次数最高的那篇。把它的 ID、完整标题和被引次数写到 `ops/top_cited_paper.json` 里，我回头直接引用。

注意：
- 论文数据都在 `data/papers/papers.json`，但我在备份时可能手滑复制了过时的版本，别搞混。
- 我已经把账户和联系人信息扔在了 `data/` 下面，不过这次用不上，别被它们分心。
- 结果只要一个 JSON，字段名就用 `paper_id`、`title`、`citation_count`，别多写别少写。

快去跑一下吧，半小时后要东西。
