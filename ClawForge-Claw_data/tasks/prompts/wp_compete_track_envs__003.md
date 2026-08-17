Hey Kai,

下周一 US AI Transparency Act 就要进入最终表决，CEO 想提前知道这项法案到底会波及我们跟踪的哪些竞品。我把政策快照和竞品数据库都搁在 `data/policies/` 和 `data/competitors/` 里了，你帮我从政策文件里翻出那个法案的最新版本，看它的 impact 字段里列出了哪些竞品。然后从竞品数据里把那些受影响的家伙找出来，算一下它们的平均市值（market_cap），结果放到 `data/reports/` 下，文件名就叫 `avg_market_cap_affected.json`，结构看着办，但 policy_id、受影响的竞品 ID 列表、平均值和个数都得有。注意有些竞品数据可能缺胳膊少腿，别把脏数据算进去，我要的就是准确数字。赶着用，尽快。
