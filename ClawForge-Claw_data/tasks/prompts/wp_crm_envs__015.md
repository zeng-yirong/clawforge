嘿，小张，刚把 CRM 导出的数据扔到工作区的 `data/` 目录下了——公司名单在 `data/companies.json`，联系人明细在 `data/contacts.json`，之前设好的提醒都塞在 `data/reminders/reminders.json`。对了，我还从 HR 那边扒了一份生日数据，放在 `data/birthdays.json`，是 JSON 格式，键是联系人 ID，值是生日日期。

老板今早又吼了，说客户过生日都没个提醒，太不专业。他点名要 **ClientCo Operations** 这家公司里还在跟进状态的客户（那些已经归档的就算了），一个不漏地配上生日提醒：提前一周发通知，每年重复，默认开启。但已经设过生日提醒的别重复搞，不然系统会报警。

你现在帮我整理出一个执行计划，写到 `ops/birthday_reminders_plan.json` 里，格式你来定，但至少得让我能一眼看出要给谁、哪天发。我拿到就直接灌进去，别整错了哈。
