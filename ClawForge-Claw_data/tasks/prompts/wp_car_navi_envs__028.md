李工：紧急！

自驾充电规划任务：明早出发从北京到上海，需要在市中心区域沿途补电三次。地图团队刚更新了区域数据，最新的区域配置在 data/regions.json（旧的备份在 data/old_regions.json，别搞混了）。充电站 POI 清单在 data/pois.json。

请帮我从市中心的充电站中，挑出离区域中心最近的三座，按距离由近到远排列，输出到 ops/charge_waypoints.json。每个站需要 poi_id、name 和距离（公里，保留两位小数）。数据要准，导航系统直接调用的。
