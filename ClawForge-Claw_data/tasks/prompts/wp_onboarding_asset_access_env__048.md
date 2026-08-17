嘿，我是IT支持小李。刚收到HR的消息，新员工 Emily Chen 已经签了合同，明天就入职了。我需要你帮我把她的入职流程跑完：先给她创建公司邮箱（格式：名.姓@ourcompany.com），然后根据她的部门（Engineering）分配对应的系统权限，再从设备库中挑一台可用的笔记本电脑分配给她，最后在Slack模拟缓存里记录一条欢迎消息。

所有原始数据都在 `data/` 目录下：合同在 `data/onboarding/contracts.json`，设备清单在 `data/onboarding/equipment_inventory.json`，权限包在 `data/onboarding/permission_packs.json`。注意只能处理已经签署的合同（status 为 signed），其他状态的合同别碰。

请把最终的结果汇总成一个 JSON 文件放到 `ops/onboarding_summary.json`，这样我就能快速审核了。谢谢！
