紧急！销售总监明早要一份董事会用的竞品格局总结。我手头有份最新的竞品快照放在 `data/competitors/` 下，每个活跃竞品一个 JSON。用户数据在 `data/users/` 里，每个用户一个 JSON，标注了属于哪家竞品。

但 `data/competitors/` 里混了些旧备份和说明文件，别管它们，只认那几份标记了 `status: "active"` 的。另外用户数千万别抄竞品自己标的（不准），你得从 `data/users/` 里按 `competitor_id` 逐个统计实际用户数。

帮我把这些东西算清楚写到 `ops/competitor_summary.json` 里：
- 所有活跃竞品的市值加起来
- 它们增长率的平均值
- 用户数最多的那家竞品的名字和它的实际用户数

我赶着做 PPT，快搞定它！
