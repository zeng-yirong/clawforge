嗨，我是运营部的 Sam。Bob Smith（bob.smith@company.com）明天正式入职，合同已经签了。我需要你帮他跑完入职准备流程，所有原始数据都在工作区里。

- 请从 `data/accounts.json` 里找到他的部门信息和对应权限配置标识。
- 然后去 `onboarding/permission_packs.json` 拉出他部门该有的系统权限列表。
- 再扫一眼 `onboarding/equipment_inventory.json`，给他分配一台可用的笔记本电脑（别拿台式机或平板）。
- 最后，把所有信息整理成一个 `onboarding_profile.json`，放在工作区根目录。里面要有员工姓名、邮箱、部门、分配的系统权限列表、设备编号，状态写 `onboarding_complete`。

不清楚的字段名你看着办，但别漏了东西。搞完喊我一声就行。
