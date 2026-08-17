Hey 管家助手，

周三下午客厅又热成蒸笼了！我翻了下 smart home 后台 —— `data/schedules.json` 里客厅 AC 的排班绝对撞车了。  
之前叫师傅调试时留了好几个旧调度没删，现在周三下午 14:00~16:00 之间至少有两个调度同时在抢空调控制权，搞得压缩机关了又开开了又关。

我已经把所有设备信息扔在 `data/devices.json` 里了，`data/schedules.json` 是调度表。  
请你帮我把周三当天，所有发生在 **Living Room** 的 AC 设备调度中，时间区间有重叠的那些调度 ID 揪出来。  
去重、只保留冲突的调度 ID，写到 `ops/conflict_schedules.json` 里，格式是一个纯 JSON 数组（比如 `["sched_01", "sched_03"]`）。  
别的多余东西一概不要，我只要冲突列表。

注意：只考虑 `active: true` 且 `day_of_week` 为 `Wednesday` 的调度，设备类型必须是 `ac`。  
谢谢！
