嘿，我是HR的Ella。刚才发现张三（员工ID是E003）的离职流程居然漏掉了！他的离职申请在 `data/offboarding/exit_requests.json` 里早就批了，但我核对时发现他的系统访问（`data/offboarding/system_access.json`）和设备（`data/offboarding/equipment_assignments.json`）都还是**active**和**assigned**状态，根本没回收。

你能不能帮我处理一下：把他的系统访问关掉、设备收回来？最后把整个交接的总结写到一个清单文件里，放到 `ops/handover_checklist.json` 中。我打算直接拿去归档，所以内容要完整、清楚。我这边等着，拜托了！
