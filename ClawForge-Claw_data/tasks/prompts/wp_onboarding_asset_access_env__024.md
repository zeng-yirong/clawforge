Hey! 新来的 Zhang Wei 今天入职，他的合同已经签好了，就扔在 `data/onboarding/contracts.json` 里。我之前把权限包清单、设备库存都放在 `data/onboarding/` 下了，你先翻翻看。对了，公司邮箱规则是 firstname.lastname@company.com，别搞错。  

处理完了把完整的入职配置汇总到 `ops/onboarding_complete.json`，里面得把邮箱、分配的系统、设备标签和欢迎消息都塞进去。另外，欢迎消息也别落下，单独再写一份到 `slack_cache/onboarding_welcome.json`，我直接丢给 Slack 机器人发。  

别拖，下午五点前我要同步给 IT 和 HR。
