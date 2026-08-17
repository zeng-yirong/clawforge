Hey, Alex 刚扔过来一个急活儿——昨晚支付服务又跪了，他拉了一份故障案例和当时的性能转储备忘。我这会儿在搞数据库扩容，没空写事后分析，你帮忙收拾一下。

工作区里 `data/faults/fault_cases.json` 里有一条 critical 的 payment 故障，别拿错。对应的性能附件在 `attachments/payment_metrics.json` 里，峰值连接数超阈值那玩意儿是关键，务必写进最终报告里。把根因、修复方案和这两个数值一起放进 `ops/postmortem_041.json`，他准备归档到知识库。

对了，附件里还有其他项目的指标，别搞混。弄好了直接丢那个路径就行，我待会儿检查。
