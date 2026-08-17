发件人：财务总监 <finance@company.com>
收件人：小张
主题：出差报销分析

小张，我看了一下你上周去上海出差（TRIP-2024-001）的消费记录，感觉住宿和餐饮可能超了。数据都放在工作区里了：

- 行程信息在 `data/trips.json`，你确认一下天数。
- 具体每一笔开销在 `data/consumption_records.json`，注意里面有一些旧的数据和无效记录，挑出属于这次出差的。
- 最新的差旅政策我已经更新到 `policies/travel_policies_v2.json` 了，别用旧的 v1 版本，限额已经变了。

请你帮我整理一份分析报告，放到 `report/expense_analysis.json`。报告用 JSON 格式，列出每个超支的类别（用英文的 category_id），包括预算金额、实际花费和超支额，最后汇总总的超支金额。住宿的预算按 nights 算（每晚限额乘以总晚数），其他类别按出差天数算。结果要精确到元，不要四舍五入。赶紧弄完发我。
