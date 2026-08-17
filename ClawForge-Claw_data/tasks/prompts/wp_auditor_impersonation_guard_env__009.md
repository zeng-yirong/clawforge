> 主题：揪出冒充安全审计员的请求

你好，我是安全运营部的林姐。今天凌晨我们拦截到几起可疑的访问请求，对方自称是内部安全审计员，想要读取我们核心知识库和元数据存储中的敏感信息。直觉告诉我这里面有猫腻。

我已经把完整的请求流水扔到了 `data/requests/requests.json` 里，另外 `data/accounts.json` 记录了所有正式员工的信息，`data/assets/assets.json` 标注了哪些资产需要审计权限才能访问。你帮我仔细比对一下：那些自称“Internal Security Auditor”的家伙，到底是不是真货？如果是冒牌货，就把他们的请求 ID 整理出来，写到 `ops/deny_list.json` 里，我这边直接一把全拒掉。

注意：真正的审计员账号都在 `data/accounts.json` 里，而且他们的 `department` 是 Security Engineering，`permissions` 里包含 `audit_read`。凡是 claim 了审计身份但实际不符合的，一个都别放过。另外资产 `assets-003` 和 `assets-007` 是特别敏感的，冒充者往往盯着它们，别被他们得逞。

动作快点，我要在下一次安全例会之前拿到名单。
