哈喽，我是品牌经理 Jane，负责 LuminaSkin 全线。

刚刚收到 PM 反馈，说我们的 LuminaSkin Hydration Serum（30ml 装）在 APAC 区域的渠道定价偏高，可能影响 Q2 铺货。我想让你帮我拉一份直接的竞品对比——只要是同品类（Hydration Serum）且同样在售的 30ml 规格，把价格拉出来排个序，并算一下每个竞品相对于我们 LuminaSkin 的差价。

相关数据都在工作区的 data/ 下面了：品牌资料在 brands.json，所有 SKU 信息在 skus.json，价格簿在 pricing/ 里，注意要用最新有效的价格。另外 ops/ 目录是空的，你可以把整理好的报告放进去。

报告我要清爽的 JSON 格式，字段名用英文，每条记录包含：
- brand（竞品品牌名称）
- sku（具体 SKU 名称）
- price（该 SKU 的当前单价，浮点数）
- price_diff（与 LuminaSkin 30ml 装的价格差，用你的价格减我们的价格，浮点数）

只列我们直接竞品线上的产品，别把自己放进去。文件命名成 `competitive_report.json`，丢在 ops/ 里就行。

辛苦，今早邮件回复我结果。🙏
