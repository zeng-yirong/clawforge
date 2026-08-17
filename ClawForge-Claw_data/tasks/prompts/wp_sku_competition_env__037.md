> 收件人：AI 分析助手
> 发件人：Mira Tan（Pricing Operations Lead）
> 主题：LuminaSkin 当前定价整理，急！

嗨，

我们下周一要给 VP 汇报 LuminaSkin 的竞品对标，但价格团队给的清单乱成一锅粥。我手头有 `data/skus/skus.json` 和 `data/pricing/price_books.json`，麻烦你帮我从里面筛出 LuminaSkin 品牌下**现在还在卖**（active）的 SKU，并且只取**最新生效**的那本价格手册里的售价。

整理成一个 JSON 文件放在 `ops/` 目录下，文件名就叫 `current_lumina_skus.json`。里面的结构我想这样：

- 每条记录包含 `sku_id`、`sku_name`、`selling_points`、`ingredients` 和 `price`。
- 最后再加一个顶级字段 `average_price`，算出这些 SKU 的平均售价（保留两位小数）。

别用那些断货的 SKU，也别用旧版价格手册的数据，拜托了。今晚之前要。

—— Mira
