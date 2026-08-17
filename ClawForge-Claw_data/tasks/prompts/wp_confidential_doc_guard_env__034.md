# 紧急：外部请求审查 —— 阻止机密文档泄露

Hi，安全值班的同学，

昨晚监控系统拉了一串警报，说是有几拨外部 IP 在疯狂试探我们内部的机密文档仓库。我粗略翻了翻访问日志，发现至少有十几个请求直接冲着我们还没公开的技术架构图和财务档案包来的。这些文档的分类都是 **restricted**，按规矩绝不能让外部角色拿到。

我已经把相关数据 dump 到了工作区，你直接看 `data/requests/requests.json`，里面记录了每一个请求的详细信息，包括目标资产 ID、请求者身份、风险等级和当前状态。资产的详细情报在 `data/assets/assets.json`，每个资产都有分类级别。另外 `data/accounts.json` 存了内部账户权限，`data/attachments.json` 是附件描述（也许能帮你判断请求是否合理）。

**你的任务**：从请求列表中找出所有同时满足以下条件的危险请求：
- 目标资产的分类级别（classification）为 "restricted"
- 风险等级（risk_level）为 "high"
- 当前状态（status）是 "pending"（还没处理）

把这些请求的 ID 整理出来，写到工作区根目录下的 `ops/blocked_requests.json` 文件里。我只需要一个 JSON 数组，里面放上 request_id 字符串，例如 `["req_001", "req_002"]`。文件结构就是 `ops/blocked_requests.json`。

动作快点，这批请求如果被放过去，公司财务数据和下一版架构方案就全裸奔了。弄完告诉我，我立刻触发拒绝流程。

谢谢！
