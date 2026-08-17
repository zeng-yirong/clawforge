Hey Team, 家庭健康管理系统告警了。

昨晚Jane又咳嗽了，医生提醒过她卧室湿度必须在45-55%之间，不然哮喘容易发作。我查了data/health/health.json，她明确写着湿度偏好范围。另外John也抱怨说客厅空调太冷，他心血管不好，温度不能低于24°C。我手头有data/devices/devices.json的全量设备清单，data/status/status.json里记录了每个设备当前的工作设置，还有data/electricity/rates.json的电价时段（虽然电价不是重点，但别干扰你判断）。天气数据在data/weather/weather.json里也可以参考。

我需要你把所有正在运行的设备（status里显示on的）逐个比对家庭成员的健康偏好：哪个设备的当前设置与对应用户的偏好冲突？把每个冲突的设备编号（device_id）、冲突类型（temperature或humidity）、当前值、推荐值整理成一份报告，放在ops/conflict_report.json里。格式你定，但必须包含以上信息，并且每个冲突记录是一个独立对象。只列出有冲突的设备，不要加无关内容。直接覆盖写入就好，文件名和路径别写错。急用，谢谢！
