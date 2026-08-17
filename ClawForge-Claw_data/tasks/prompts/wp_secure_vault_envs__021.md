Hey Team,

总算把旧 vault 的导出拿到了，里面简直一团糟。分类字段要么空着，要么填错，还有些凭据压根没归类。我现在得赶紧搭好新系统，所以需要你帮我整理一下这些凭据，并设好自动填充规则。

具体文件都在工作目录里：
- `vault_export.json` 是原始凭据清单，每条记录都有 id、平台、用户名、密码和当前分类（可能是 null 或错的）。
- `vault_schema.json` 里定义了四个正式分类（工作邮箱、电商平台、社交媒体、银行账户），以及每个分类的策略（优先级、是否强制 MFA 等）。
- `mapping.json` 是一个平台关键词到分类的映射参考，你可以用它来辅助判断每个凭据该归属哪个分类。

请按以下两点搞定：
1. 对每一条凭据，根据平台信息和映射，给它分配正确的分类（必须是 schema 中定义的四种之一），然后把结果按原结构（但分类字段用正确的值）写到 `classified_vault.json`。
2. 为每个分类生成一条自动填充规则，规则内容参照 schema 中该分类的 `priority` 和 `requires_mfa`。规则格式为每条一个对象，包含 `category`（分类名称）、`fill_username`（true）、`fill_password`（true）、`requires_mfa`（从 schema 取）、`priority`（从 schema 取）。所有规则放到 `autofill_rules.json` 里（列表形式）。

注意：`mapping.json` 只作为线索，最终分类要以 schema 中的名称为准；请不要引入不在 schema 中的分类。

时间很紧，辛苦你了！有问题随时找我。

—— Ada
