嗨，我是HR的Lena。新员工Emma Chen（工号EMP_007）下周一入职，合同应该已经在`data/onboarding/contracts.json`里签过了。我手头事情太多，你帮我把她的入职流程跑一遍吧。

她分在Engineering部门，你根据部门给她开好系统权限，权限包可以在`data/onboarding/permission_packs.json`里查。再找一台可用的笔记本分配给她，库存清单在`data/onboarding/equipment_inventory.json`。最后在Slack欢迎频道#welcome发条消息，格式你定，但得包含她的邮箱、能访问的系统列表和分配的设备。

我习惯把每个步骤的结果单独存到`output/`文件夹下：
- 邮箱配置文件 → `email_profile.json`
- 系统访问记录 → `system_access.json`
- 设备分配记录 → `equipment_allocation.json`
- 欢迎消息 → `welcome_message.json`

所有字段按业务常识填，别漏东西。搞定后跟我说一声就行。
