**发件人:** Daniel Song <daniel.song@northstar.example.com>  
**收件人:** Cloud Cost Analyst Bot  
**主题:** 2026年6月业务集群成本汇总急需输出  

嗨，团队，  

我们上个月（2026年6月）的资源用量已经录入在 `data/resources/resource_ledger.json` 里了。财务部刚批准了新的定价目录，你可以在 `data/pricing/pricing_catalogs.json` 里找到它——请务必使用当前状态下标记为“active”的那个版本。  

我需要你把所有 **业务集群**（在 `data/resources/clusters.json` 里 `cluster_role` 是 `business` 的）的成本汇总出来，按集群为单位，输出到一份独立的报告里。报告放在 `reports/` 目录下，文件名叫 `2026-06_cost_summary.json`。  

报告中每个集群要包含：集群ID、集群名称，以及该集群的总成本（用两位小数表示，货币为美元）。计算成本时，根据资源分类和用量，对照定价目录中的单价完成。  

请确保你只关注业务集群，不要混入共享平台的数据。报告格式示例（仅示意结构）：  

[
  {
    "cluster_id": "...",
    "cluster_name": "...",
    "total_cost": 123.45
  }
]
数据都在工作区里了，有任何疑问先按照你的判断做，明天一早我需要这份报告开会。谢谢！  

Daniel
