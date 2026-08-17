**发件人:** Tara Ng <tara.ng@northstar.example.com>  
**收件人:** Cloud FinOps Team  
**主题:** 🔴 Q2 成本严重超支——需要你立刻出一份精确的月度成本报告

团队好，

刚收到财务预警，Q2 的云支出比预算高了将近 40%！我怀疑是某些集群的资源分配出了问题，或者我们用了过时的定价目录。现在需要你基于手头的数据给我一份 **准确的月度成本报告**，只针对 **业务集群**（business 角色），别把共享平台集群算进去。

数据都在工作区的 `data/` 下：
- 集群信息：`data/resources/clusters.json`
- 资源消耗明细：`data/resources/resource_ledger.json`
- 定价目录：`data/pricing/pricing_catalogs.json` —— 注意用 **当前生效的（active）** 版本，别用归档的。
- 附件文档 `data/attachments.json` 里引用了两份参考文件，其中有一份讲的是成本核算规则，另一份是报告的输出格式 schema，你务必先读一下再动手。

我这边已经有几笔明显有问题的记录，比如 `entry_id` 重复的脏数据，你在汇总时自己斟酌处理。另外，`shared-ops` 集群的消耗无论如何不要加进来。

最终报告请放到 `reports/` 目录下，文件名按附件里要求的来。我只认 JSON 格式，字段和结构必须和 schema 完全一致，别搞成 CSV 或纯文本。

辛苦今天下班前搞定，多谢！

Tara
