嘿，我这边刚接手一批旧凭证，数据在 `data/credential_dump.csv` 里，但看着头大。有人乱分类，有些密码弱得跟纸糊的一样，还有些废弃记录混在里面没清理。旁边 `data/vault_schema.json` 是咱们当前的分类标准，`ops/password_policy.json` 是我让安全组定好的新策略，顺便还搁了几个备选强密码，你直接拿去用。

我需要你帮我把这堆烂摊子收拾干净：那些明显该扔的（比如状态标了“retired”的）就别留着了，连必要字段都缺的（比如没平台信息的）也当垃圾丢掉。剩下的记录，你看看谁的密码强度不到80，给它换上一个够硬的密码——就从 `ops/password_policy.json` 里的备选列表按顺序拿。分类如果跟平台对不上号也得掰正（平台 `example.com` 对应工作邮箱，`shop.com` 和 `store.com` 是电商，`bank.com` 是银行，`social.io` 是社交媒体）。最后把洗好的凭证存到 `ops/cleaned_credentials.json`，再根据每个平台做个自动填充规则扔到 `ops/autofill_rules.json`。

就这些，搞完告诉我一声，我直接推上去。
