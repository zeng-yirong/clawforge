Hi,

新的一批员工下周就要入职了，但我的入职分配流程还卡在手动阶段😩。我把所有原始资料都扔在 `data/` 里了：

- 合同（`data/onboarding/contracts.json`）—— 有些已经签字（signed），有些还在走流程。
- 员工主账户（`data/accounts.json`）—— 有每个人的部门和邮箱。
- 权限包（`data/onboarding/permission_packs.json`）—— 根据部门划分了不同的系统访问组。
- 设备库存（`data/onboarding/equipment_inventory.json`）—— 标注了哪些设备是闲置可用的。

我需要你帮我做完以下几件事，把结果整齐放到工作区：

1. 找出所有已经签字的合同员工。
2. 根据他们的部门，从权限包里匹配对应的系统访问权限。
3. 从设备库存里挑一台闲置的设备分配给每个人（按姓名顺序挑就好，先到先得）。
4. 把每位员工的完整分配方案（叫什么、什么部门、分配了哪些系统、拿了哪台设备）汇总成一个文件，放到 `ops/onboarding_result.json`。
5. 给每位员工写一条简短的欢迎消息（至少包含“欢迎”和员工姓名），放到 `ops/slack_welcome_cache.json`。

拜托了，尽快搞定！有任何问题直接找我。

-- HR经理 张姐
