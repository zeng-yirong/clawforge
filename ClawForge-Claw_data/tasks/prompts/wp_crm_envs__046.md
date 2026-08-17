嘿，CRM管理员，销售团队刚刚开完会，说我们很多技术行业的商务联系人还躺在“personal”文件夹里，标签也乱七八糟。他们下周有个定向活动，需要把这些人统一归到“business”文件夹，并打上“tech_client”标签，方便营销组批量操作。

公司信息都在 `data/companies.json` 里，联系人数据在 `data/contacts.json`。你按规则改好之后，把完整的联系人列表写到 `ops/updated_contacts.json`，我直接拿去覆盖生产库。注意别动其他字段，也不要漏掉任何应该改的人——那些已经是business文件夹但标签不对的也得补上。

弄完告诉我一声，我们赶紧推进。
