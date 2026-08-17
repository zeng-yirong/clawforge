Hey AI Agent,

刚刚新一批简历到了，我已经把候选人信息和职位要求整理好放在了 `data/` 下面。麻烦你帮我做一下初步匹配和面试安排。

具体要求是这样的：  
- 为每个 **活跃** 的职位（`status` 没写或者不是 `closed` 的）选一个最合适的候选人，匹配规则就看技能重合度（要求的技能和候选人的技能交集越多越好）。  
- 注意！有些候选人已经在 `data/existing_interviews.json` 里安排过面试了，别重复安排。  
- 有个职位标记了 `"urgent": true`，老板催得急，希望这个职位的面试能安排在 **明天**（当前日期在 `data/current_date.txt` 里）。其他职位安排在 **后天**。  
- 面试提醒默认提前 30 分钟。  

最后把安排结果写到 `ops/interview_schedule.json`，里面每个面试记录要写清楚：`candidate_id`、`job_id`、`scheduled_date`、`reminder_minutes_before`。谢谢！
