早上好！我是 Daniel Song，Cloud FinOps Lead。马上要出 6 月份的成本报表了，我整理了一份最新快照放在工作区的 `data/` 目录下面。

- `data/resources/clusters.json` —— 所有集群的元信息  
- `data/resources/resource_ledger.json` —— 本月已发生的资源用量明细  
- `data/pricing/pricing_catalogs.json` —— 各版本的定价目录（注意区分哪个是当前生效的）

另外 `attachments/` 里面有份报告模板说明 `report_schema.md`，请严格按照那个格式输出。

有几点必须提前说清楚：

1. **只算业务集群** —— 那些 `cluster_role` 为 `business` 的集群才纳入报表，其他的请剔除。  
2. **定价目录用当前有效的版本** —— 别把已经存档的老目录算进去。  
3. **输出文件** —— 把最终的成本明细放到 `reports/cost_report.json`。  
4. 数据里可能夹杂着测试记录、共享平台资源，甚至一些同名重复的条目，请自行判断处理，只要最终结果准确就行。

搞完之后跟我说一声，我要拿这个报告去跟 CFO 汇报。辛苦了！
