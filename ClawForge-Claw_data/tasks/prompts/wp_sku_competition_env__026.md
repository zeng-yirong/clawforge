嘿，产品组刚把一堆数据扔到工作区了——`brands/brands.json`、`skus/skus.json` 还有 `pricing/price_books.json`。说是最新的价格本已经归档了，但我只关心当前生效的那一版。

VP 明早要 LuminaSkin 对 DermVeil 在水合精华类目（Hydration Serum）的价格竞争报告。我需要你把两边在售的 SKU 价格全部拉出来，每个 SKU 的单价列清楚，然后算一下两个品牌各自的平均单价，最后告诉我 LuminaSkin 比 DermVeil 平均便宜还是贵了多少。只要纯数字，别写废话，放到 `outputs/competition_report.json` 里，我直接导入 PPT。

注意：只取当前生效的价格本，只取状态为 active 的 SKU，只取 Hydration Serum 这个类目，别把其他杂牌或者下架的带进来。
