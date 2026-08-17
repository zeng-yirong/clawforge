**主题：紧急 – 数据中心UPS故障，需快速定位关键工单**

Lena Park 刚才打来电话说 west4 机房的 UPS 彻底挂了，连带影响了 Billing API 和 Inference Worker。我从 incidents 目录下把工单池拖下来了，文件是 `incidents/incident_pool.json`。里面有些工单是旧的或者格式不对，我需要你帮我筛出所有 **ups_outage 类别 + critical 严重级别** 的工单，按 `opened_at` 时间从小到大排好，把 `incident_id` 和 `title` 摘出来，写到 `ops/urgent_ups_outages.json` 里（JSON 数组，每个元素只含 `incident_id` 和 `title`）。另外 `contacts.json` 里的人员信息回头可能要用，先留着不动。

注意：那个 JSON 文件里有些条目可能缺字段或类别写错了，丢掉它们，别让它们混进去。我要的是准确、干净的列表，十分钟后 NOC 要拿着它去分配抢修资源。辛苦！
