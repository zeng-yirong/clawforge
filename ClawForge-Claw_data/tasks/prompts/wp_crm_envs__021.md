嘿，Emma 刚发来一条紧急消息：

“刚接到客户投诉，说我们几个重要商务客户的生日提醒根本没发出去。我怀疑是数据那边出问题了——有些人的生日信息不全，或者格式乱七八糟，还有的提醒已经存在但我们没检查出来。

你帮我把 data/contacts.json 里那些 folder 是 business 的客户过一遍：
1. 看看他们的 birthday 字段有没有写对（标准格式是 YYYY-MM-DD，其他人填的啥破玩意儿你也看看）。
2. 再去 data/reminders/ 里翻翻现有的提醒列表，已经有生日提醒的就别重复搞了。
3. 把那些真正需要新建生日提醒的 business 客户挑出来，每条记录写上 contact_id、full_name、birthday（原样保留）和 suggested_reminder_date（生日前3天，同样 YYYY-MM-DD 格式）。
4. 整理成一个 JSON 列表，放进 ops/birthday_reminders_to_create.json。

搞定后回我一声，我直接拿去 sync 给客服系统。动作快点！”
