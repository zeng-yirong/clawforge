哎，老板今天一大早就把我堵在走廊里，非要那份“竞争情报闪电战”报告。上周我不是让你关注欧盟那个数字市场法案的落地影响吗？法务那边已经把受影响的竞品名单筛出来了，就在 `data/policies/` 里面，标了 affected_competitors 字段的那个就是。

我反复看了几遍，DataFlow AI 那家伙最近花钱如流水，但获客效率一直没公开。我怀疑他们用户获取成本已经崩了。你帮我干两件事：

1. 把 DataFlow AI（就是那个 competitor_id 为 comp_002 的倒霉蛋）旗下所有用户的平均 acquisition_cost 算出来。
2. 再翻一翻 CloudMajor（competitor_id = comp_001）的用户数据，做个同样的平均值，然后算算 DataFlow AI 比 CloudMajor 便宜还是贵了，差了多少百分比（用 (DataFlow平均 - CloudMajor平均) / CloudMajor平均 * 100 算，保留两位小数）。

结果存到 `ops/report.json`，格式你给我看着办，但至少得包含 competitor_id、avg_cost、avg_cost_other 和 cost_difference_percent 这四个字段。哦对了，`data/users/` 里有些用户数据可能缺胳膊少腿（比如 cost 字段写了不明文字或者直接缺失），你处理的时候悠着点，别把脏数据当真。

文件都在工作区里，拖干净了快点给我回话！
