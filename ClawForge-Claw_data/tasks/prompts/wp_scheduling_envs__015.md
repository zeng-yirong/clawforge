主题：客厅空调下午不工作

嗨，我家客厅的空调最近下午总是罢工。我看了下调度配置，发现 `data/schedules/living_room_ac_schedule.json` 里面控制用的插头好像不对劲。你帮我对一下 `data/devices/devices.json` 里空调的电源插头设置，看看调度里用的插头和空调实际绑定的插头是不是不一致。如果是，把应该使用的那个插头的ID写到 `ops/issue_device.json` 里，格式为 `{"suspect_plug_id": "..."}`。谢啦！
