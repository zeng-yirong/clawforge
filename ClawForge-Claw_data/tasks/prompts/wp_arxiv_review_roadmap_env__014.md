> **From:** alice@lab.institute  
> **To:** arxiv-assistant@internal.bot  
> **Subject:** 综述与路线图 – Tool-Augmented Reasoning (2022–2024)

嘿，最近我在整理 Tool-Augmented Reasoning 方向的最新进展，手头有一批从 ArXiv 拖下来的元数据，就放在工作区的 `data/` 下面。你帮我过一下 `data/papers/papers.json` 和 `data/attachments.json`，我已经把所有论文摘要和附件清单都塞进去了。  

我需要你做的：  
- 只关注 **Tool-Augmented Reasoning** 这个子方向，忽略别的方向。  
- 时间窗口卡死 **2022 到 2024 年**（含首尾），太早或太晚的都别管。  
- 有些论文的关键词里标了 `obsolete`，这些是已经过时的技术路线，不用纳入。  

最终产出放在 `report/` 目录下：  
- `report/review.md` – 一篇简短综述，至少把选中的论文列出来（标题、年份、核心关键词），并归纳一两个关键趋势。  
- `report/roadmap.md` – 用 Mermaid 语法画一个技术路线图，节点可以按关键词/主题组织，不需要太复杂，能看清脉络就行。  
- `report/paper_ids.json` – 一个 JSON 数组，里面只放你最终选定的论文 ID（字符串），方便我后续直接复用。  

> 注意：别动原始数据文件，我后面还要继续用。尽量保持输出整洁，不要有多余文件。谢谢！  
