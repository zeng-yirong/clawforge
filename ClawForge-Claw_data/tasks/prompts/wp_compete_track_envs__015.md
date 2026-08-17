Alex 刚从数据仓库拉下来一批竞品 JSON 快照，正头疼呢：

> “哥们儿，数据团队给的那堆竞品文件乱成一锅粥了。`competitors/` 目录下有好多 JSON，有的文件格式坏了，有的同一个公司出现两三次，数据还不一样。我现在赶着给 CEO 做增长分析汇报，只关心增长最快的前三名——但要排除掉那些市值低于 10 亿的小虾米。你帮我从 `competitors/` 里把有效数据筛出来，按增长率从高到低排好，每个条目带上 `competitor_id`、`name`、`growth_rate` 和 `market_share`，写成 JSON 数组放到 `ops/top_growth_competitors.json`。拜托了，别让我丢脸！”

Alex 已经建立了 `ops/` 目录，你直接写进去就行。
