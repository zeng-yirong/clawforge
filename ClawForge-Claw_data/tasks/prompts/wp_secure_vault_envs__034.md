紧急求援！昨天晚上安全扫描发现我们的凭据库里有大量弱密码，我赶紧从备份里拖出了最新的快照放到 `vault/` 下了。具体情况：`vault/credentials.json` 里列出了所有员工凭据，但其中有些状态为 `inactive` 的历史记录不用管。密码策略在 `vault/password_policy.json`，分类信息在 `vault/categories.json`。为了快速修复，我提前准备了一个安全密码池 `vault/secure_passwords_pool.json`，里面按顺序存好了足够用的强密码。

我需要你帮忙做两件事：
1. 找出所有状态为 `active` 且密码不满足策略的凭据，按它们在原文件里出现的顺序，依次从密码池里取一个密码替换掉原来的弱密码，然后把完整的更新结果写到 `ops/updated_credentials.json`（保持原格式，只改密码字段）。
2. 对于剩下的所有 `active` 凭据（即密码本就合规的那些），检查它们对应的分类是否要求多因素认证（`requires_mfa` 字段），如果分类要求了MFA，则这个平台的自动填充功能可以启用；否则必须关闭。请为每个这样的凭据生成一条自动填充规则，规则包含平台名（`platform`）和是否启用（`enabled`），存成 JSON 数组放到 `ops/autofill_rules.json`。

我只要精确的结果，不要多也不要少。拜托了，明天安全大会要靠这些结案。
