嘿，帮我处理一下今天的离职单据。

我刚把离职请求的快照丢到了 `data/offboarding/exit_requests.json` 里，里面是今天要走的几个人。但系统权限和设备分配表还在那边挂着，没来得及清。你顺着这张表，把所有已经批了（approval_status 是 “approved”）的人挨个过一遍：

1. 先看 `data/offboarding/system_access.json` —— 每个人的系统访问权限都还在 “active” 状态，必须全部撤销掉，一个系统都不能漏。
2. 再看 `data/offboarding/equipment_assignments.json` —— 每个人名下的设备如果还是 “assigned”，就去回收掉，变成 “returned”。
3. 最后把每一步的操作结果整理成一份交接清单，放到 `ops/handover_checklist.json` 里。清单里要写清楚：每个员工都撤销了哪些系统、回收了哪些设备，还有完成的日期。

数据路径都在工作区根目录下，别跑偏了。做完告诉我就行。

哦对了，那些还没批或者已经拒了的你别碰，只处理已批准的。谢谢！
