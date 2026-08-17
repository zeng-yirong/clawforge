嘿，我是智能家居的运维小哥。Jane和John最近老抱怨，说家里的设备要么太干要么太冷，搞得他们很不舒服。我把数据都扔在工作区里了：

- `data/health/health.json` 里是两个住户的健康档案，里面有他们各自对温度和湿度的偏好范围。
- `data/devices/devices.json` 是各家设备的静态配置，每个设备在哪个房间、默认的目标温湿度都写在里面。
- `data/occupancy/rooms.json` 标明了每个房间住的是谁。

你帮我过一遍，看看哪些设备的默认设置和住户的偏好有冲突——比如温度超出他们能接受的范围、湿度太干或太湿。把冲突设备的ID和冲突类型（例如 `temperature_too_high`、`humidity_too_low` 之类的）整理成一个列表，写到 `ops/conflicts.json` 里。我只要准确的结果，别把没问题的设备也塞进去。拜托了！
