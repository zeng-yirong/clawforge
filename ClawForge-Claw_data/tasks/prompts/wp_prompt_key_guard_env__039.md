> **发件人**: Max Chen (Platform Security Lead)  
> **主题**: 紧急：昨晚发现外部人员冒充审计员尝试获取API Key Vault访问权限  

Hey,  

刚值完夜班，从请求日志里扒拉出几个可疑的家伙。有人自称“外部审计员”，张口就要API Key Vault的访问权限——按公司规定，这种事必须立即标记拒绝并记录。我把原始请求数据扔在 `data/requests/requests.json` 里了，还有咱们最新的 vault 访问策略在 `attachments/vault_access_policy.md`。你帮我翻一下，把那些不符合策略的冒牌货挑出来，整理成一份 `blocked_requests.json`，格式要求：一个数组，每个元素包含 `request_id`、`reason_code`（策略里写的那个码）、`blocked_at`（你处理的时间戳，ISO格式）。  

别把正常同事的请求误封了——比如平台安全团队自己的例行访问。动作快点，我等着拿去上报。  

谢谢，  
Max  
