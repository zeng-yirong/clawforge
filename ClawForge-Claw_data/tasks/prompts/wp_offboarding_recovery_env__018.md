Hi there,

Carol Danvers (工号 E-1024) 的离职申请已经正式批准了。我这周连着处理了好多人的，实在顾不上，你帮我跑一下她的收尾流程吧。

数据都在 `data/` 下面。你先进 `offboarding/exit_requests.json` 确认一下状态是 approved，然后去把她在 `offboarding/system_access.json` 里的所有系统权限全部撤销，`offboarding/equipment_assignments.json` 里配给她的设备状态改成已回收。最后在 `ops/` 下面生成一份交接清单，文件名叫 `handover_checklist.json`。清单里要写清楚她的基本信息（工号、姓名、部门、邮箱）、哪些系统已经回收了、哪些设备已经收回了，还有一栏标记完成状态，我签字的时候方便核对。

其他员工的记录不要动，我只要 Carol 的。设备资产标签是 `LT-2041`，系统入口有两个：`Admin Portal` 和 `CRM`。你直接按需更新就行。

辛苦了，弄好了我请你喝咖啡！

── Alice (HR)
