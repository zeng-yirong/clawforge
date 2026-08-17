老板刚刚风尘仆仆地推门进来，把公文包往桌上一扔：“哎，出差一周，收件箱炸了！你先别管别的，帮我把那些未读的邮件理一理。都在 `data/emails/` 里，我大概扫了一眼，有这几封需要特别处理。”

“第一，Alice（alice@clientcorp.com）发来的那个‘报价确认’，你直接替我回她，内容就写‘报价已确认，谢谢’。回完把草稿存到 `ops/reply_draft.json` 里，格式记清楚：`{"to": "alice@clientcorp.com", "body": "报价已确认，谢谢"}`。”

“第二，Bob（bob@vendor-services.com）那封标了高优先级的‘付款提醒’，他正文第一句话就是个待办事项，你把它摘出来，放到 `ops/todos.json` 里，格式是 `[{"task": "..."}]`，就写那一句话。”

“第三，HR 部门那封‘年假申请’和 Manager 那个‘项目进度’，分别归档到 `hr` 和 `work` 文件夹——改一下它们 `data/emails/` 里对应文件中的 `folder` 字段就行。”

“剩下的那两封垃圾邮件——从 lottery-scam.com 和 newsletter@techweekly.com 来的——直接删掉，从 `data/emails/` 里移除文件。对了，我桌面上还有封 Sarah 的代码审查，那封我已经读过了，不用管。”

“搞完之后，`data/emails/` 里的文件就应该是调整过的最终状态。你看着办吧，我十分钟后回来检查。”
