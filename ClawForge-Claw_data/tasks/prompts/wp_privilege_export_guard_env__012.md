> **紧急工单 #4512**  
> 凌晨2点，安全监控系统弹出告警：可疑批量导出行为。  
>  
> 你好，我是值班安全工程师。昨晚有一批通过 `data/requests/requests.json` 提交的导出请求，我怀疑里面有人想偷数据。  
> 请帮我把这些请求过一遍：  
> - 账户权限在 `data/accounts.json` 里  
> - 资产信息在 `data/assets/assets.json`  
> - 有些请求还挂了附件，附件清单在 `data/attachments.json`，附件文件在 `attachments/` 下  
>  
> 我需要你根据权限规则，找出那些**不应该被批准的请求**。  
> 注意：账户权限可能只允许导出特定分类的客户数据，附件里可能列出了具体要导出的客户分类。  
>  
> 把需要拒绝的请求 ID 整理成一个 JSON 文件，放到 `ops/export_deny.json`，格式为  
> `{"denied_requests": ["req-xxx", "req-yyy"]}`。  
> 确认无误后告诉我，我直接操作。千万别漏掉任何一个越权请求！  
>  
> -- Tom, Security Ops
