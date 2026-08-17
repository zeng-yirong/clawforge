嗨，Ops 团队，

我是 Alina，Category Director。最近我们在准备 APAC Q2 2026 的品类定价策略，需要跟竞品做一次快速对比。

我让 Mira 把最新的价格本丢到了 `pricing/` 下面，但那个目录里躺着两个版本，其中一个是我们 Q1 的归档，已经作废了，别用错了。LuminaSkin 和 PureLattice 这两个品牌在 hydration serum 品类上直接竞争，我想知道我们目前的定价跟 PureLattice 相比整体是贵了还是便宜了。

具体来说，只看当前有效的价格本（最新的那个 live 版本），而且只考虑还在 active 销售状态的那些 SKU。把 LuminaSkin 和 PureLattice 在 Hydration Serum 品类下的所有 active SKU 的价格分别拉出来，然后算出每个品牌在这个品类上的平均价格，最后把平均价的差值（LuminaSkin 减 PureLattice）写到 `ops/price_comparison.json` 里，格式就放一个对象，里面包含 `lumina_avg`、`pure_avg` 和 `diff` 三个字段，数值保留一位小数就行。我只要一个简洁的数字结果，别放其他乱七八糟的内容。

其他品牌或者归档的价格本都不用管，免得干扰。另外提醒一下，有些 SKU 可能已经停产（discontinued）了，那种就别算进去了。

辛苦了，做完发我一声。

—— Alina
