嗨，我是 Mira Tan，Pricing Operations Lead。Q2 竞争分析报告马上就要截止了，但我从产品目录团队拿到的原始数据简直一塌糊涂！你能帮我理一理吗？

事情是这样的：我们聚焦 LuminaSkin 这个品牌，它主打的 Hydration Serum 系列是我们下季度定价策略的核心。我手头有 `data/skus/` 下的全部 SKU 清单，还有 `data/pricing/` 里的价格台账。但里面混了不少过期的、暂停销售的 SKU，还有别的品牌的数据。我只需要 LuminaSkin 目前在售（status 为 active）的 Hydration Serum SKU，并且必须是当前有效的定价（价格台账中 is_current 为 true 的那一版）。另外，每个 SKU 的 selling_points 前三个卖点也帮我摘出来吧。

整理好后，按 size_value 从小到大排好序，丢到 `outputs/competition_report.json` 里就行。格式你看着办，但要让我一眼能看清 SKU ID、品名、规格、包装数量、单价和核心卖点。拜托了，数据一定要准！

对了，`data/brands/` 里有品牌主文件可以交叉验证，别搞混了。加油！
