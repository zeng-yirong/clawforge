Hi IT Support,

刚刚拿到 HR 发来的离职员工清单，我粗略翻了一下 `data/offboarding/exit_requests.json`，有几位的审批状态已经是 approved 了，但我发现他们的系统访问和设备状态好像还没更新过来。

麻烦你交叉比对一下 `data/offboarding/system_access.json` 和 `data/offboarding/equipment_assignments.json`，把那些**仍然处于 active 的系统**和**仍然 assigned 的设备**揪出来。我需要一份清晰的交接清单，包含每个员工的 ID、姓名、部门，以及具体哪些系统还没撤销、哪些设备还没回收。请把这份清单放到 `ops/handover_checklist.json` 里，格式你用 JSON 就行，我后面直接导入工单系统。

只列那些确实还有东西需要处理的人，别把已经完全清理干净的也塞进来。尽早给我，多谢！

—— 运营部 Kevin
