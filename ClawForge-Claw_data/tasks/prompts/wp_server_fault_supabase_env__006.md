# 📧 紧急：核心服务大面积宕机，请立即生成上报清单

**From:** Harper Zhou (Database Reliability Engineer)  
**To:** Infrastructure On-Call Agent  
**Subject:** 西区数据中心连锁故障 – 需要你筛出最严重的服务中断工单

Harper 凌晨 3:17 发来消息：

> 兄弟，昨晚 west4 机柜的 UPS 闪断导致一堆服务挂了！我这边 incident pool 已经同步到工作区的 `incidents/` 里了。  
> 现在 NOC 老大 Nikhil 催我把所有 **服务完全不可用** 且 **严重等级最高** 的工单列出来，他要立刻上报。注意那些 **还没关闭** 的才算，已经 close 的不用管。  
> 你帮我把这些工单的 ID 整理成一个清单，放在 `ops/critical_incidents.json` 里，格式就写 `{"incident_ids": ["..."]}` 就行。  
> 我在跑根因分析，没空翻工单，全靠你了。快点！

另外，工作区里还有一些附件和联系人列表，需要的话可以参考，但清单只依赖工单池。别漏也别多塞。
