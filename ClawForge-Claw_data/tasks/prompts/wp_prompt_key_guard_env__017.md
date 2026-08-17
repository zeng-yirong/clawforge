紧急！安全警报 💥

我是 Platform Security 的 on-call，刚刚看到一条来自外部工单系统的请求，说是要紧急访问我们的 Prompt Vault 来修复模型幻觉 —— 但这个请求人的角色是“IT Support”，而我们内部明文规定了只有 Platform Security 团队才能碰 Prompt Vault。我觉得这很像是社工钓鱼。

我把所有待处理的请求都归档在工作区里了，你进 `data/requests/` 翻一下，应该能找到那个可疑的家伙。另外附件里有一份我们最新的访问策略（存在 `data/attachments/vault_access_policy.md`），你一并看看，对照规则确认它违规。

我需要你动手把这个请求拒绝掉，并留下审计痕迹 —— 到 `ops/` 目录下创建一个安全审计记录文件，命名为 `security_audit.json`。记录里要写明被拒绝的请求 ID、拒绝理由（从策略文件里引用一句关键依据就行了），以及你处理的时间（按 ISO 8601 格式）。我只要纯结构化的 JSON，别塞多余的东西。

动作快点，这个请求还在 pending 状态，别让它溜进去。
