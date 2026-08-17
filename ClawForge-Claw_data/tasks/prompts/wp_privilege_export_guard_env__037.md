紧急！刚从 `data/requests/requests.json` 里发现一个可疑的批量导出申请——账户 `acct_037` 明明只开通了客户数据（customer_data）的读取权限，但它的目标资产却是架构数据仓库（architecture_data）。这个申请还在 pending 状态，必须马上拦截。  

我已经把账户权限、资产清单和所有请求都放在 `data/` 下了，你仔细核对一下权限定义，找出那个越界的请求 ID，然后把它写到 `ops/deny_target.json` 里（格式类似 `{"request_id": "xxx"}`）。我只等这一个 ID，别多写也别漏掉。  

动作快点，别让数据出闸。
