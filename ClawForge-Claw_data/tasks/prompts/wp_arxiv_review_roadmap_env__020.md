嘿，哥们！我刚从ArXiv上扒了一批论文，全部扔在 `data/papers/papers.json` 里了。这些论文方向很杂，但我现在急着要整理 **tool_augmented_reasoning** 方向的综述。  

你帮我干两件事：  
1. 把这个方向的所有论文都挑出来，按年份排好顺序，每篇的 `paper_id`、`title`、`year` 和 `abstract` 列清楚。  
2. 根据论文里的 `citation_ids` 字段，把它们之间的引用关系理成一张发展路线图。  

最后全塞进 `ops/review_summary.json`，结构就跟我们上次项目讨论的模板一样：  
- `papers` 数组，每个元素包含 `paper_id`、`title`、`year`、`abstract`（顺序按年份升序）  
- `roadmap` 数组，每条边是一个对象，有 `from`（引用方）、`to`（被引用方）、`label`（统一填 `"builds upon"`）  

注意：  
- `data/attachments.json` 里有些附件简述，你看看就行，不一定用。  
- 别把其他方向的论文混进来，也别漏掉任何一篇属于 `tool_augmented_reasoning` 的。  
- 有个别论文的 `direction` 字段可能不规范，你照着 schema 严格过滤。  

搞快点，今天就要出图了！
