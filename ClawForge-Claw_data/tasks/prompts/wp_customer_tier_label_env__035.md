我是客户运营部的张经理。我们最近更新了客户分层标准，但系统还没同步，我需要你根据最新的数据重新评估所有客户的标签。

事情是这样的：老板让我把客户重新划分为三个等级——VIP、Premium和Standard。规则是这样的：季度消费超过1万美元，并且最近30天内有活跃记录的，算VIP；季度消费超过5千美元，并且最近60天内有活跃记录的，算Premium；其他的都算Standard。不过要注意，那些风险等级标记为“high”的客户先不处理，他们的标签就用他们当前labels字段里的第一个标签。

另外，运营部那边给了我一个手动覆盖列表，放在`ops/overrides.txt`里，里面有些客户需要强制打上某个标签，这个优先级最高，你按那个来。

数据我都准备好了：
- 客户主数据在 `data/customers/customers.json`
- 最新季度消费数据在 `data/logs/consumption_logs.json`
- 最近活跃数据在 `data/logs/activity_logs.json`
- 覆盖列表在 `ops/overrides.txt`

你帮我把所有客户的最新标签都算出来，整理成一个文件，叫 `ops/customer_tier_label_update.json`，里面每个客户都要有customer_id、new_label和reason（说明为什么是这个标签）。弄好了直接放在那里就行，我待会儿拿去导入。

拜托了，今天下班前要交给老板！
