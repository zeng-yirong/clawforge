嘿，总算找到你了。财务那边刚扔过来一个紧急工单，说六月份的云账单出了大问题——retail-core 集群的成本比上个月翻了一倍，但运营那边咬定资源没扩容，定价也没涨。我翻了翻出账明细，感觉是账本里的用量汇总和定价版本对不上号。

我把所有原始数据都丢在工作区了：

- `data/resources/clusters.json` —— 集群清单，retail-core 的 cluster_id 你查一下。
- `data/resources/resource_ledger.json` —— 六月的资源用量流水，每个条目都带着 cluster_id、resource_family、quantity 和 billing_model。
- `data/pricing/pricing_catalogs.json` —— 定价目录，注意只有 `active` 状态的版本才是有效的，千万别用那个三月份的归档版。
- `data/attachments.json` —— 里面有个附件 `report_schema.md`，是财务要求的成本报告格式，你生成报告前务必先看一遍它的字段说明。

我的要求很简单：把 retail-core 集群六月所有资源的成本算出来，按照 `report_schema.md` 规定的结构写进根目录的 `cost_report.json`。只用 active 的定价，按 resource_family 逐项算，最后汇总一个总成本，币种和月份别漏了。别碰其他集群的数据，也别自己编造字段。搞完了告诉我一声就行。

时间紧，你直接动手吧。
