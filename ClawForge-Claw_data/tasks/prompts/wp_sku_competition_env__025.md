嗨，我是运营部的小王。刚才从产品线那边转来一个急活儿：LuminaSkin 要赶在 Q2 促销前更新竞品定价对比表，但系统里历史版本乱成一锅粥，我这边只有同事留下的几个半成品文件，丢在 `data/` 下了。

我手头有：
- `data/skus/skus.json`：所有品牌的 SKU 清单，LuminaSkin 的也在里面。
- `data/pricing/price_books.json`：价格本，有旧的 APAC-Q1 归档版和最新的 APAC-Q2-LIVE 版。注意，最新的那个才是我们当前生效的，千万别搞混了。
- 还有 `data/brands/brands.json`，不过 LuminaSkin 的品牌信息你应该用不上，主要是拿 SKU 和价格。

帮我把 LuminaSkin 在售 SKU 的当前价格全部提取出来，汇总一下整个品牌的定价情况——比如总价是多少，平均每个 SKU 多少钱。最后把这些结果整理成一份简洁的 JSON 文件，放到 `reports/lumina_skin_pricing_summary.json` 里。我只需要纯数字，不要带货币单位，也不要别的废话。

对了，`reports/` 目录还不存在，你顺手建一下就行。辛苦啦！
