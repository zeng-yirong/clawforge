主题：离职流程卡在 IT 环节，赶紧处理！

Hey，刚看到你在线。HR 那边催我了，说员工 **E-1024** 的离职流程已经批了三天，但 IT 这边啥都没动。

我翻了一下 `data/offboarding/` 下的几个档案：

-   系统访问权限还是开着的（Admin Portal 和 CRM 都能登陆），
-   公司配的笔记本（LT-2041）和显示器（BG-8821）也没还回来。

你现在帮我搞定三件事，然后给我一份交接清单，放到 `ops/handover_checklist.json`：

1.  把该员工在所有系统上的访问权限关掉——`data/offboarding/system_access.json` 里相应记录的状态改成已撤销。
2.  把那两件设备的记录状态改成已归还——`data/offboarding/equipment_assignments.json` 里改。
3.  生成一份完整的交接清单，里面要包含员工姓名、部门、撤销的访问系统列表、回收的设备列表，以及交接联系人信息。联系人信息从 `data/contacts.json` 里找，角色是 `handover` 的那个人。

**注意**：改数据之前，先把 `data/offboarding/` 下的三个 JSON 文件原封不动复制到 `backup/` 文件夹，以防万一。

其他员工的记录不要动，就管 E-1024 一个人的就行。搞完告诉我一声，我找 HR 确认。
