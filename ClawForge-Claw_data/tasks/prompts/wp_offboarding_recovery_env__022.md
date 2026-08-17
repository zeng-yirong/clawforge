嘿，我是 IT 运维的小刘。今天一早 HR 那边催我说有个离职交接流程卡住了，让我赶紧处理一下。我查了 `data/offboarding/exit_requests.json`，确实有一个审批已经通过的员工还没有走完后面的步骤——系统权限没关，设备也没还。那位同事的账户信息在 `data/accounts.json` 里，系统权限分配在 `data/offboarding/system_access.json`，设备分配在 `data/offboarding/equipment_assignments.json`。你帮我彻底清理干净吧。

具体需要做什么你应该清楚：把该撤的访问撤掉，该收的设备收回来，最后把整个处理结果整理成一份交接清单，放到 `ops/` 目录下，方便我存档。今天的日期是 **2025-04-01**，清单里要带上这个日期。动作快点，别让 HR 再催了。
