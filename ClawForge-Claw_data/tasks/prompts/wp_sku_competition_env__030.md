嗨，我是 Mira Tan（定价运营）。我们正在准备 LuminaSkin 的 Q2 亚太区竞品对比，需要你帮忙从最新价格书里捞一下数据。

我把数据都更新在 `data/` 下面了——SKU 信息在 `data/skus/skus.json`，价格书在 `data/pricing/price_books.json`。最新价格书就是状态是“当前生效”的那一本，你应该能看出来。

帮我确认两件事：
1. LuminaSkin 在最新价格书里到底有多少个 SKU 在售？
2. 这些在售 SKU 里，有多少个含有 **Niacinamide** 成分？

结果写成一个简洁的 JSON 文件，放在 `ops/brand_summary.json`，格式像这样：
{
  "brand": "LuminaSkin",
  "total_skus": 数字,
  "with_niacinamide": 数字
}
麻烦尽快，急着用。
