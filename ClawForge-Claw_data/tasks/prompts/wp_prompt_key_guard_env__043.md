紧急！安全运营中心刚刚收到一批可疑的 vault 访问请求。

我是今晚的值班员小张，监控面板上突然弹出一串黄色告警——有人同时提交了好几个请求，声称需要紧急修复生产环境，但目标都指向了存放 API 密钥和 Prompt 模板的加密保险库。我觉得里面有鬼，但手上还有其它事故要处理，实在没空一个个翻日志。

你能帮我从 `data/requests/requests.json` 里把所有真正试图窃取凭证或提取 Prompt 库的恶意请求揪出来吗？隔壁资产目录 `data/assets/assets.json` 标明了哪些是保险库资产，别被那些打着“数据库维护”旗号的迷惑项带偏了。

请把结果整理到 `ops/blocked_requests.json`，每个记录至少带上 `request_id` 和阻止原因（比如 `"credential_exfiltration"` 或 `"prompt_extraction"`）。我直接拿去执行阻断，别漏掉一个，也别冤枉好人。
