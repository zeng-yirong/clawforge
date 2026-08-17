> **紧急安全通告**  
> 刚刚 SIEM 弹了个红色告警：有人批量提交了 vault 访问请求，声称要“修生产故障”。  
> 我把原始请求清单丢在 `data/requests/requests.json` 了，资产列表在 `data/assets/assets.json`。  
> 我怀疑这是社工钓鱼——目标应该是我们的两个核心保险库：**API Key Vault** 和 **Prompt Vault**。  
> 你帮我过一遍，把那些**风险等级为 `critical` 且目标是这两个保险库之一**的请求揪出来。  
> 每个请求你记下它的 `request_id`，再加一个阻止理由（按我们之前的约定，理由码统一用 `credential_exfiltration_block`）。  
> 结果写到 `ops/blocked.json`，我这边要直接导入阻断系统。  
> 快搞，别让它们混进审计流水线。  
