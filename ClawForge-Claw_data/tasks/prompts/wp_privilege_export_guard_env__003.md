**主题：紧急 – 批量导出越权审查**

刚接到审计警报，凌晨有一波批量导出请求可能越权访问敏感资产。我把相关数据都丢在工作区了：

- `data/accounts.json` – 各账号及其权限
- `data/assets/assets.json` – 资产清单，每项都标注了读取所需的权限级别
- `data/requests/requests.json` – 今天凌晨积压的导出请求

你帮我快速过一遍，找出那些“发起人没有对应资产读取权限”的越权请求。把结果整理成一个 JSON 列表，每一条写明 `request_id` 和 `actor_name`，保存到 `ops/breach_deny.json`。注意，别把正常请求拖进去，也别漏掉任何一个越权的。我这边等你的阻断列表，赶紧！
