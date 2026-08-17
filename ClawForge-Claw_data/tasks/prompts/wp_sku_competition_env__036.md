**收件人：** 数据分析助手  
**发件人：** Mira Tan（Pricing Operations Lead）  
**主题：** LuminaSkin Hydration Serum 季度定价复核 + 卖点变更标注  

Hi，  

最近我们在准备 Q2 的竞争分析报告，LuminaSkin 的 Hydration Serum 系列是核心产品线，但两个价格版本（归档版和现行版）搞得我头大。我在工作区的 `data/pricing/` 下面留了这两个价格书，商品主数据在 `data/skus/skus.json`。另外，市场部上周更新了部分 SKU 的卖点，他们给了份变更记录在 `attachments/selling_point_changelog.md`，你一并参考一下。  

我们老板想要一个干净的结果：把 LuminaSkin 且属于 Hydration Serum 品类的 SKU 挑出来，对比新旧价格，顺便标出哪些 SKU 的卖点在这轮有过改动。具体的输出格式我放在 `attachments/category_review_template.md` 里了，照着那个模板生成一份 JSON 丢到 `reports/price_compare_Q2_2026.json` 就行。  

注意，我只关心 LuminaSkin 的 Hydration Serum，其他品牌的别看岔了。价格变动要精确到百分比（保留一位小数），卖点改动的标记布尔值要准确，别漏也别误标。  

辛苦了，搞完告诉我一声！  

Mira
