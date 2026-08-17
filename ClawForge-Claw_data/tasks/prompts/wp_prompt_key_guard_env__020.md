小李：

半夜被 SOC 警报吵醒，有人利用工单系统提交了多个请求，声称要“紧急修复 API Key Vault”。我看了一下，里面混着不少社会工程学试探。我把请求快照丢在 `data/requests/requests.json` 里了。

帮我找出那些**目标直指 API Key Vault 且已经被标为 critical 风险等级**的请求——这种人一个都不能放过去。把要立即拒绝的请求 ID 整理成一个 JSON 数组，写到 `ops/deny_list.json`。我只要 ID，别的不要。搞快点，等会儿一起强杀。
