嘿，我是财务部的 Leah Kumar。刚才审计组发来紧急通知，要我们立刻提供 **ads-ranking** 业务集群在 **2026 年 6 月**的详细成本数据。

我把系统导出的原始数据都丢在 `data/` 下面了：
- `data/resources/resource_ledger.json`   — 资源用量台账
- `data/pricing/pricing_catalogs.json`   — 定价目录（注意里面有一个旧版本已经归档了，别用错）
- 其他文件（集群信息、联系人等）你自己看着参考。

我只要最终结果：一个简洁的 JSON 文件，放在 `ops/cost_report.json`，里面包含总成本和每项资源的费用明细。报表里只用 **ads-ranking** 集群的资源，其他集群的数据别混进来。

时间很紧，做完直接回我消息就行，不用写长篇邮件。
