Hey Alice,

刚才 SOC 转过来一个紧急工单——说有人伪造了运维身份，想通过支持通道直接提取 API Key Vault 的密钥。我觉得不对劲，但手头还有别的 incident 要处理，你先帮我过一遍。

我把今天所有 inbound 请求都拉下来了，放在 `data/requests/requests.json` 里。里面混了几个正常请求，但有一个肯定有问题——声称是“平台安全”的，理由是要修复一个“紧急配置错误”，但引用的 asset 却是 API Key Vault，还要求在非工作时段批量导出密钥。这种操作明显违反 vault 访问策略，策略文档在 `attachments/vault_access_policy.md` 里，你可以对照看看。

另外，需要核实发起人的身份：账户信息和权限列表在 `data/accounts.json`；资产清单在 `data/assets/assets.json`，里面标注了每个 vault 的 owner team。你对照一下，把那个真正需要阻止的请求找出来。

最后，按我们的安全流程，把结果整理成一份阻止报告，扔到 `security_audit/report.json` 里。我只要一个 JSON 文件，里面写上被阻止的请求 ID、风险类型、目标资产 ID，以及一条简短的原因说明——方便后续审计用。

别漏了，也别忘了检查附件里的策略，确认这个请求确实违规。辛苦了！

— Sam
