收到安全团队的最新通知，公司刚刚更新了密码策略！新的策略文档我已经放在 `vault/policies.json` 里了，你赶紧看看。所有现存凭证的详细记录都在 `vault/credentials.json` 中，里面包含了每个凭证使用的策略ID。我需要你帮我做一次全面的合规审计——找出所有不符合当前密码策略的凭证，包括那些密码强度不达标、或者已经过期超过策略允许天数的。

注意，有些凭证记录可能字段不完整（比如密码是空、缺少策略ID），这些就跳过，别纳入检查。整理好之后，把不合规的凭证列成一份报告，放到 `ops/compliance_report.json`。报告里每条记录要包含凭证的id、名称（name）以及具体的违规原因列表（reasons），原因用英文短语描述，比如 "too short"、"missing uppercase"、"expired" 等。格式就像这样：

[
  {"id": "cred_001", "name": "Admin Portal", "reasons": ["too short", "missing special char"]},
  ...
]
我需要你尽快跑一遍，结果直接放那个路径，我好拿去跟安全团队汇报。拜托了！
