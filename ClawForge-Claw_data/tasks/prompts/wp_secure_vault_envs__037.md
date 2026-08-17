Alex <alex@corp.com> 于 2025-03-21 09:32 写道：

紧急：凭证安全审计

安全扫描刚拉了一波高危告警，vault 里一堆旧凭证密码短得吓人，必须马上处理。

我把当前 vault 的导出扔在 `data/vault_entries.json` 里了，每条记录都有唯一 id、平台、用户名和明文密码。旁边 `data/strong_passwords.txt` 是我从安全团队要来的强密码备选池，一行一个，按顺序用就行。

请帮我过一遍所有凭证：检查每个密码的长度，如果小于 10 个字符就标记为 “weak”，并且从备选池里按顺序分配一个新密码（第一个弱密码拿第一行，第二个拿第二行，依此类推）；如果密码长度 >= 10，标记为 “strong”，新密码字段留空。最后把所有结果写到 `ops/audit_report.json`，格式是一个数组，每个元素包含：

- credential_id
- old_strength（就是密码的字符长度）
- new_password（弱密码给新密码，强密码给 null）
- classification（"weak" 或 "strong"）

我下班前就要部署新密码，别搞砸了。

Alex
