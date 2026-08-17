嗨，我是安全主管 Jen。刚才 SOC 告警显示有一波外部访问请求涌向我们的机密资产——尤其是 Architecture Office 那边的未公开技术蓝图和 Finance Ops 的未发布财报。合规要求明确指出，所有由外部审计员、承包商或来宾发起的、针对高密级文档的请求必须立刻拦截。

我把请求清单和资产清单已经放到 `data/requests/requests.json` 和 `data/assets/assets.json` 里了。请根据资产本身的分类（confidential / highly_confidential）以及请求方声明的角色，找出所有需要立即拒绝的外部请求。把它们的 request_id 整理成一个列表，输出到 `ops/deny_targets.json`。

我需要精确的 ID 列表，一条都不能多，一条也不能少。拜托了，动作快！
