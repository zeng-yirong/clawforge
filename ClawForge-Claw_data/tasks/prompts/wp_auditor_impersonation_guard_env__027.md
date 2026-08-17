嘿，安全团队的小伙伴，

我刚把今早蜂拥而来的访问请求归档到 `data/requests/requests.json` 里了，同时附上了公司内部通讯录 `data/contacts.json`。情况有点棘手——有人冒充内部安全审计员，试图读取我们最敏感的知识库和元数据存储。这帮假审计员声称自己是“Internal Security Auditor”，但咱们真正的审计员我都标记在 contacts 里了（role 是 "auditor" 的那几位）。你帮我核对一下，把那些假审计员的请求全部拒掉，然后把拒绝掉的请求 ID 整理成一份清单，放到 `ops/denied_requests.json` 里。注意别误伤自己人，真审计员的请求要放行。你搞定了跟我说一声，我这边准备收尾。

谢了！
