嘿，我是李昂，HR 基础设施组的。今天下午就要发一批明天入职的同事的 welcome 包，但流程卡住了。

我手动检查了一下合同和库存，发现一堆问题：有几个合同还没签，有的人的公司邮箱已经被先来的实习生占用了，还有设备清单里好多笔记本都标了“损坏”或者“已分配”。时间太紧，我顾不上一个一个排查了。

我把所有原始数据丢到工作区了：
- `data/onboarding/contracts.json` —— 新员工合同，每份都带着他们自选的设备类型（asset_type）
- `data/accounts.json` —— 公司已有账号，避免邮箱冲突
- `data/onboarding/equipment_inventory.json` —— 设备库存表
- `data/onboarding/permission_packs.json` —— 不同部门的系统权限包

要求很简单：**只处理那些合同已经签署、邮箱没有被占用、并且库存里有可用设备的员工**。为这些人走完入职流程，然后在 `onboarding/processed_onboarding.json` 里留下一份报告，把成功和失败的都列清楚。

辛苦你搞定，我等着把这个报告直接发给 IT 和行政去执行。别漏掉任何细节。
