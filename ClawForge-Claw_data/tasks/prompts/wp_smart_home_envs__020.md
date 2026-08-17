主题：家里的电费暴涨，Jane 又咳嗽了！帮忙分析一下

Hi 智能管家，

最近两个月电费翻了一倍，而且 Jane 的呼吸道问题又严重了，医生说她很可能对室内温湿度敏感。我把所有相关数据都整理好放在 `data/` 目录下了：

- 设备清单和当前运行状态：`data/devices/devices.json` 和 `data/devices/status.json`
- 分时电价表：`data/electricity/rates.json`
- 家庭成员健康档案：`data/health/health.json`
- 今天的天气快照：`data/weather/weather.json`

你帮我仔细看看这些问题：

1. 哪些设备目前开启，并且它的设定值（温度或湿度）跟 Jane 的健康需求有冲突？需要明确指出冲突原因和具体调整建议。
2. 哪些设备正在高峰电价时段运行？对于这些设备，除了健康必要的之外，给出省电建议。

请你把分析结果整理成一个报告，放在 `analysis/` 目录下，文件名就叫 `optimization_report.json`。报告里要有两个列表，一个叫 `health_conflicts`，一个叫 `rate_conflicts`，每条记录都要包含设备ID `device_id`、问题描述 `issue` 和你的具体建议 `suggestion`。建议里要给出明确的数字调整值（比如温度调到几度、湿度调到几度），我拿到手就能直接操作。拜托了！
