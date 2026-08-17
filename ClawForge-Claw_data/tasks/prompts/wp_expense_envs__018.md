> 财务经理老王的紧急留言：
> 
> 小王，系统突然崩了，报销流程卡在半路。我手动把这次出差（TRIP-018）的相关文件拖出来了，就放在工作区的这几个目录里：
> - `trip_info.json` —— 出差基本信息
> - `policy_db/travel_policies.json` —— 公司等级差旅政策
> - `consumption/consumption_records.json` —— 这次出差的所有消费记录（可能有其他 trip 的干扰项，注意筛选）
> 
> 另外 `raw_logs/` 底下是系统崩之前的日志，不用管它。
> 
> 张总（senior 级别）刚从北京出差回来，住了2晚，呆了3天。我赶着审批，你帮我算算哪些费用类别超预算了。**只要把超标的单项列出来**，按下面格式放到 `ops/report.json`：
> ```json
> {
>   "trip_id": "TRIP-018",
>   "overspend_items": [
>     {
>       "category": "（中文类别名）",
>       "actual_total": 实际汇总金额,
>       "budget_total": 预算金额,
>       "overspend": 超出金额
>     }
>   ]
> }
> 
> 
> 注意：政策里每天有预算的类别（住宿、餐饮、出租车等）要乘以天数算总预算；机票这类一次性预算直接使用。还有，只看有收据（receipt=true）的记录就行。拜托了，搞快点！
