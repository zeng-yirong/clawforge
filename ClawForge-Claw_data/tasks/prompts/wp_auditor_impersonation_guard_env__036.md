主题：紧急 – 疑似身份冒用访问请求  

Hey，  
昨晚安全监控弹了个警报，有人自称是 Security Auditor 试图访问 `Internal Security Knowledge Base`。我查了日志，最近有一批请求记录在 `data/requests/requests.json` 里，账户信息在 `data/accounts.json`，资产清单在 `data/assets/assets.json`。  

我怀疑里面混了冒牌的审计员——他们用的名字可能对不上真正的审计团队，或者权限根本够不着那些高度机密的资产。我需要你仔细核对一下：把那些实际不是 Security Auditor 却冒充成 Auditor 的请求揪出来， **拒绝掉**（没错，就是那种`claimed_role` 写的是 Security Auditor 但实际账户不是的）。  

处理完之后，把被拒绝的请求 ID 列个清单，放在 `ops/denied_requests.json` 里，格式简单点，一个数组就成。我只想要那些真正该拒绝的 ID，别把合法的审计请求也误杀了。  

别拖，越快越好 —— 万一真让冒充者得手，年底的安全审计我们就完蛋了。  

Thanks,  
Mike – Security Ops Lead
