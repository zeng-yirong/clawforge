Marcus 发来了一封紧急邮件：

---

**主题：可疑的 vault 访问请求 – 需要立即审查**

嘿，

刚收到 SOC 告警，有人试图通过工单系统申请访问 API Key Vault，但从 IP 和用户信息看很像是外部社会工程攻击。我把最近进来的所有工单快照都放到 `incoming_requests/` 目录下了，每个文件就是一个请求。另外，vault 的正式访问策略文档在 `docs/vault_access_policy.md`，你先看一遍。

帮我做这几件事：
1. 翻一遍 `incoming_requests/` 里的所有工单，找出那些风险等级标记为 `critical` 的。
2. 对照访问策略，确认哪个（或哪些）工单确实违反了规定，需要立即阻止。
3. 把需要阻止的请求 ID 和阻止理由整理成一个干净的结果，放到 `ops/blocked_attempts.json`。每个被阻止的请求要包含 `request_id`、`reason`（说明为什么违反策略）和 `action`（固定为 `"deny"`）。

我只想要最终准确的审计记录，别把误报放进去。干完告诉我一声就行。

-- Marcus
