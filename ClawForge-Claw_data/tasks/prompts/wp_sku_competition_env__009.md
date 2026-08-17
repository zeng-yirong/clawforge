嘿，数据分析师，我是 Mira。LuminaSkin 刚调了价，我需要确认他们的 Hydration Serum 系列现在到底什么价格，再和 AquaPulse 的同类产品拉个对比。我把最新的产品目录丢到 `data/` 文件夹里了，价格手册也都在里面。那个 live 的手册才是当前生效的，别搞混了——archived 的版本已经过期了，不用管。另外，停产（discontinued）的 SKU 就别列出来了，只看还在售的。

帮我把 LuminaSkin 和 AquaPulse 两个品牌下，所有 Hydration Serum 类别里 active 状态的 SKU 都找出来，从最新价格手册里拿到它们的当前价格（两位小数）。然后生成一份 JSON 报告，放到 `reports/` 目录下，文件名就叫 `competitor_report.json`。报告里需要包含两个列表：`lumina_skus` 和 `aqua_skus`，每个元素包含 `sku_id`、`sku_name`、`current_price`（数字，两位小数）。再帮我算一下两个品牌的平均价格，分别存为 `lumina_avg_price` 和 `aqua_avg_price`，最后算出平均价的差值 `avg_price_diff = lumina_avg_price - aqua_avg_price`。这些字段一个都不能少。结果要精确到小数点后两位。辛苦你了！

——Mira Tan, Pricing Operations Lead
