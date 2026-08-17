Alex（市场总监）发来一条紧急消息：

“凌晨的活跃度报告看得我头皮发麻 —— 有好几个客户明显在流失边缘。IT 把客户资料放在 `data/customers/customers.json` 里，最近的活动日志在 `logs/activity_logs.json`。另外，`news/news_samples.json` 是我们订阅的行业新闻，有按行业分类的。我只需要你处理一件事：

找出真正有高风险且活跃度快速下降的客户（别把那些只是偶尔不活跃或者风险低的混进来），从新闻里找一条能给他们信心的 news（注意要用 opportunity 调性的，别用 pain_point 吓到他们）。就针对那个最紧急的客户，写一份保留邮件草稿。

邮件草稿要包含客户ID、客户名称、邮件主题和正文，还有你引用的那条新闻的 ID 和标题，方便我后续查证。最终保存为一个 JSON 文件到 `cache/retention_emails.json`。

快点搞定，我上午要发给销售团队。”
