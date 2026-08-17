Subject: 月底离职审计积压，需要你立刻处理

Hey，

HR 刚把本月最后一批批准的离职名单扔到 `data/offboarding/exit_requests.json` 里了。我手头还有三个紧急工单要跟，没空一条条对系统访问和设备。

你帮我把下面几件事跑完：

1. 系统访问记录在 `data/offboarding/system_access.json`，设备分配在 `data/offboarding/equipment_assignments.json`。请把名单上所有已经 **批准** 离职的人，他们的系统访问全部失效（状态标为 revoked），设备全部标记为已回收（状态标为 reclaimed）。

2. 然后汇总一份交接清单，放到 `handover_checklist.json` 里。清单里每个离职员工作为一个条目，包含他的 ID、姓名、被撤销了多少个系统、以及回收的设备资产标签。我回头要拿这份清单给下一任运维核对。

3. **注意**：只动那些 approval_status 为 approved 的人，其他人别碰，也别改错字段格式。

搞完发我一声，急。

——Sara (IT Ops Lead)
