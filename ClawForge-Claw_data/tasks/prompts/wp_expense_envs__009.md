# 差旅报销核对请求

**发件人:** 财务部 老李 <laoli@company.com>  
**收件人:** 你 <assistant@company.com>  
**主题:** 小张（工号10086）北京出差报销审核

小张上周去北京出差3天，回来交了一堆报销单，我按senior级别的新政策（在 `data/travel_policy_senior.json`）对了一下，总觉得有几项超了。他的实际消费记录我已经整理好放在 `consumption/records.json` 里了，你帮我跑一下对比，把**所有超支的项目**挑出来，按超支金额从高到低排，如果超支金额一样就按实际花费从高到低排，写到 `ops/overbudget.json` 里。

每条记录我只要这几个信息：  
- record_id  
- category  
- amount（实际花销）  
- budget（该项目的预算额度）  
- overspend（超支金额）

住宿预算按每晚限额乘以住宿天数算，其他类按每天限额乘以出差天数算。我手头还有别的事，拜托你了！

---

**备注：** 小张的差旅编号是 `trip-2025-001`，别跟别人的混了。
