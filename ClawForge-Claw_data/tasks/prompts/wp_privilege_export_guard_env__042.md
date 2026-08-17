嘿，安全审计组的同事，

凌晨的批量导出警报把我吵醒了。我们一个低权限账户（ID 在 `ops/config.json` 里）刚提交了好几个导出请求，我怀疑有些请求要的数据级别超出了它的权限范围。你知道规矩：不能让它把不该拿的客户、架构甚至密钥数据导走。

我把所有相关文件都扔到工作区了：
- `ops/config.json` 里有当前账户的 ID
- `data/accounts.json` 是账户权限清单，每个账户的 `permissions` 字段列出了它有权访问的数据类型和等级（比如 `customer_data:level2`）
- `data/assets/assets.json` 是资产目录，每个资产有个 `read_policy` 字段表示需要多少级权限才能导出
- `data/requests/requests.json` 是我刚拉下来的导出请求列表，你需要筛选出状态是“pending”且确实是当前账户发起的请求

请你立刻帮我审查一遍：找出所有“当前账户的权限不够看那个资产”的请求，把它们的 **request_id** 整理成一个 JSON 数组，写到 `ops/deny_list.json`。我只想要准确的 ID 列表，别拖泥带水。

这些数据里有可能混了旧备份或者不完整记录（比如 `data/backups/` 下面），你自己辨别，别用错了源。抓紧！
