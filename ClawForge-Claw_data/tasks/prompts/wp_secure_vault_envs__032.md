**主题：银行账户凭证安全审查**

Hey，

昨晚安全审计又扫出一堆糟心事。我们 vault 里的银行账户凭证，很多密码强度根本不够，昨晚差点出事。我早上已经把最新的安全策略更新到了 `vault/schema.json` 里，里面每个类别都有最低强度要求。

你帮我把 `vault/credentials/` 下所有属于“银行账户”类别（注意看 schema 里的 `name` 字段）且密码强度不达标的凭证都揪出来。步骤是这样：在 `vault/` 下建一个 `quarantined/` 文件夹，把那些有问题的凭证文件**移过去**（别留副本），然后在 `vault/` 根目录下生成一个 `quarantined_report.json`，里面一条一条列清楚：每个凭证的 `credential_id`、对应的 `service` 名称、以及为什么被隔离（比如“强度不足：实际 XX 分，要求至少 YY 分”）。报告格式你看着办，但字段必须包含 `credential_id`、`service`、`reason`。

搞完后回我一声，我马上跟安全组开会。别拖。

Cheers  
Jack
