嘿，Jane 的健康警报又响了！今天早上她心率监测器报警，昨晚她一直咳嗽，我猜是卧室太干加上今天温度飙到35度，她那哮喘和高血压肯定受不了。我这边已经拉到了最新的天气、电价和用户档案，都在 `data/` 下面。设备清单在 `data/devices/devices.json`，电价表在 `data/electricity/rates.json`，健康和用户数据在 `data/health/health.json`，当前天气在 `data/weather/weather.json`。

我需要你帮我生成一份智能控制建议，让系统自动执行。格式就按 John 上次给我的那个模板：一个 JSON 文件，包含一个 `recommendations` 数组，每个元素是一个对象，有 `device_id`（字符串）、`action`（必须用 `"turn_on"`、`"turn_off"` 或 `"adjust"`）、`target`（如果 action 是 adjust 则给出数值，其他情况可以省略或设为 null）。注意把家里所有设备都列进去（包括智能插头），别漏了。输出保存到 `ops/control_recommendations.json`。

简单来说：Jane 需要舒适的环境，但今天电价是高峰，我们得在健康和电费之间找平衡。我相信你能搞定！
