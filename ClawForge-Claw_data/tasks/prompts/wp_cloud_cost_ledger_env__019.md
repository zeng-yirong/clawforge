From: Leah Kumar <leah.kumar@northstar.example.com>
To: FinOps Bot <finops-bot@northstar.example.com>
Subject: 6月成本报告——请使用最新定价目录重新核算

Hey Bot,

刚发现上个月的成本报告用了过期的定价目录，财务那边拒收了。我已经把最新的定价目录归档放到了 `data/pricing/` 下，注意别用那个标着 archive 的老版本。资源台账在 `data/resources/resource_ledger.json`，集群信息在 `data/resources/clusters.json`。

附件 `data/attachments/cost_accounting_rules.md` 里是我们通用的成本核算规则，你按那个来就行。

我需要你帮我生成一份 **每个业务（business）集群** 的月度成本明细，结果写到工作区根目录的 `monthly_cost_report.json`，格式你按规则里的 schema 来。另外，资源台账里可能有些脏数据（比如数量异常的条目），你处理的时候留意一下，别把异常数据算进去。

今晚要提交，尽快搞定！

--Leah
