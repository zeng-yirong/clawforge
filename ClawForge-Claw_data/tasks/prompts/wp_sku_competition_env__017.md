嘿，我刚拿到最新的 APAC 价格书和 SKU 清单，发现 LuminaSkin 的 Hydration Serum 系列定价有点古怪。我把相关的数据都放在 `data/` 目录下了——品牌目录、SKU 详情、两版价格书（一版是旧的归档，一版是当前 Q2 的）。另外还有几个竞品的资料混在里面，别弄混了。

麻烦你帮我理一下 LuminaSkin 和 DermVeil 在 Hydration Serum 这个品类下的价格情况。我需要一份简单的对比报告，放在 `ops/competition_report.json` 里。报告里要包含 LuminaSkin 所有活跃 SKU 的平均价格、DermVeil 所有活跃 SKU 的平均价格，以及它们的差值（LuminaSkin 减 DermVeil）。如果差值小于零，就在报告里标个 `"anomaly": true`，否则标 `false`。我只要这些数字，别加别的字段。

哦对了，别忘了只看当前生效的价格书（就是 `is_current` 为 `true` 的那本），别拿旧版本数据来算。SKU 也只挑状态是 `active` 的。其他杂七杂八的目录文件不用管，它们只是之前留下的草稿。
