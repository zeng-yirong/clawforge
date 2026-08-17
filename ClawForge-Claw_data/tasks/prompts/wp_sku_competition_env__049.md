嘿，Mira 这边～刚跑完 Q2 定价审批，发现 LuminaSkin 和 DermVeil 几个 SKU 的新版价格（APAC-Q2-2026-LIVE）跟一季度存档（APAC-Q1-2026-ARCHIVE）比，跌得有点离谱。财务那边要求我们把降幅超过 20% 的全部拎出来，做成一个清单上报。

我手头的数据都放在 `data/` 下面了：
- `data/pricing/price_books.json` —— 两版价格书，老的是 archived，新的是 LIVE。
- `data/skus/skus.json` —— 所有 SKU 的详细信息，包括名称和所属品牌。
- `data/brands/brands.json` —— 品牌主数据，方便你确认 LuminaSkin 和 DermVeil 的品牌 ID。
- 另外 `data/attachments/price_drop_template.json` 里我丢了一个格式模板，你照着那个结构生成最终文件。

请把结果存到 `ops/price_drops_report.json`，注意只保留那两个品牌的 SKU，其他品牌别混进来。排序按降幅从大到小排，这样一眼就能看到最严重的。感谢！
