Hey 数据分析师，季度末要更新客户分层标签了。最新的消费数据在 `logs/consumption_logs.json`，活动日志在 `logs/activity_logs.json`，都是 JSON 格式的。注意里面混了些旧版本或重复的记录，你清洗的时候留个心眼。

规则很简单：
*   季度消费 ≥ 10,000 美金的客户：
    *   如果最近 30 天内有活跃（last_active_days ≤ 30），打标签 **VIP活跃**
    *   否则打 **VIP沉睡**
*   季度消费 < 10,000 美金的客户：
    *   如果最近 30 天内有活跃，打标签 **普通活跃**
    *   否则打 **普通沉睡**

帮我算一下每个客户的最终标签，输出到 `outputs/customer_tier_labels.json`，里面放一个数组，每个元素包含 `customer_id` 和 `new_label` 两个字段。别漏了人，也别加无关的数据。谢啦！
