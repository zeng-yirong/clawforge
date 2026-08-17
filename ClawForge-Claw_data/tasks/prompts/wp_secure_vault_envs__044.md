Hi Agent,

最近公司内部有几次异常登录警告，安全团队怀疑是部分账号的密码太弱，被暴力破解了。我导出了一份最新的 vault 凭据快照（`vault_export.json`），旁边还有我们刚刚更新的密码策略（`policy.json`）。你帮我两个忙：

1. 对照策略，把那些不符合要求的弱密码条目筛出来，把它们的 ID 整理到 `ops/security_audit.json` 的 `weak_password_ids` 列表里。
2. 我发现有些凭据的分类标签可能放错了——比如某个工作邮箱被标成了电商平台。你根据 `site` 的域名判断一下它应该属于哪类（工作邮箱、电商平台、社交媒体、银行账户），把归类有误的条目 ID 放到同一个文件的 `misclassified_ids` 列表里。

注意：目录 `vault_records/backup/` 里是一些旧版本数据，别混淆了。结果放到 `ops/security_audit.json`，我直接拿去给安全团队复查。辛苦！
