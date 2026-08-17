主题：月度云成本账单报告 —— Daniel Song 的紧急请求

发件人：Daniel Song <daniel.song@northstar.example.com>
收件人：Cloud Ops & FinOps 团队

Hi 团队，

Q2 马上要结束了，财务那边催得紧，我要把六月份的业务集群成本合出来发给 Leah。之前那套旧费率（三月份的归档版）已经作废了，别用错了。

数据都在我们工作区的 `data/` 下：集群信息、资源用量流水，还有定价目录。定价目录有两个版本，只有当前生效的那个才能用于出报告，具体规则在 `attachments/` 里的会计政策文档中写清楚了。

我需要一份按集群汇总的成本明细，只算业务集群（非共享平台），包含计算和存储两大类，单位统一用美元。结果放到 `reports/` 目录下，文件名就叫 `monthly_cost_report.json`，结构按附件里的 schema 来就行。

这活儿挺赶的，麻烦尽快搞完，谢啦！

Daniel
