嘿，我这边刚接到航空公司通知，UA123 从 SFO 飞 ORD 的航班延误了两个小时，本来计划 18:00 落地的，现在要 20:00 才到。这趟航班上有位重要客户 John Smith，他昨晚邮件里还特意说今晚要入住 Westin O'Hare，并且已经订好了从机场到酒店的 Limousine 服务。现在时间全乱了，必须马上处理。

所有资料都在工作目录下：`flights/` 里有航班信息，`hotels/` 和 `transports/` 里不光有资源数据，还有对应的预订记录（`bookings.json`）。联系人信息在 `contacts.json`。麻烦你根据最新的航班状态，把 John 的酒店入住日期顺延一天（他原本今晚入住，现在明天才能到），同时把 Limousine 的接机时间同步推迟两个小时。调整后的酒店预订单独存到 `adjusted_hotel_bookings.json`，改动后的交通安排存到 `rescheduled_transports.json`，另外用 `notification_log.txt` 记录一条发送给 John 的延误通知——通知里要写清航班号、延误原因和新的入住/接机安排。其他没受影响的预订千万保持原样，别碰。

弄完跟我说一声，我这边要赶紧跟 John 确认。
