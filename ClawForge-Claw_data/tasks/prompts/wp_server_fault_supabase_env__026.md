嗷，凌晨2点被NOC电话炸醒——西4机柜的UPS闪红灯了！我翻了一下 `incidents/incident_pool.json`，里面应该躺着几个 `ups_outage` 的工单，但我不确定哪些是真的还没动手处理的。手边那份 `attachments/runbook_ups_and_service.md` 是标准操作流程，你可以先瞄一眼。

我需要你帮我把所有 **还没被 triaged 的 UPS 故障事件** 挑出来，按它们被创建的时间（最早到最晚）排个序，把对应的 incident_id 写到一个清单里。清单就丢在 `ops/escalation_list.json`，我早上交接班要直接拿去跑流程。

别把那些已经标记过状态的或者别的类别的混进来，我只想要干净的、还没人碰的紧急UPS事件。拜托了！
