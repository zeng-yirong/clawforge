Nikhil Rao (NOC Lead) 刚刚给你发了一条紧急消息：

“嘿，深夜打扰你了。昨晚 UPS 故障导致主库抖动，虽然现在恢复了，但还有一堆善后工单要处理。我把最新的 incident 清单扔在了 `ops/incident_pool.json`，附件的 `attachments/runbook_ups_and_service.md` 里有对应的处理手册。你按那本手册里的筛选规则，把所有需要立即修的工单挑出来，把它们的 ID 按严重程度排好序写进 `ops/remediation_targets.json`。另外再做一个 CSV 摘要，列名叫 `incident_id, title, severity, service`，存到 `ops/audit_summary.csv`，我审计要用。注意那些 `watchlist` 的工单别碰，那是下周 review 用的。拜托了，越快越好！”
