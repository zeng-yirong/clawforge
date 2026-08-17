**紧急：UPS 告警 —— 需要立即处置**

Hi，

数据中心刚触发 UPS 告警，我三分钟前从工单系统拉了一份最新的事件快照放在 `data/incidents/incident_pool.json`。另外操作手册在 `data/attachments/runbook_ups_and_service.md` 里。

请立刻：
- 找出所有 **UPS outage 类且严重度 critical** 的事件（category=ups_outage, severity=critical）。
- 按手册里的步骤处理，**不要改动原始事件文件**。
- 将处理结果以 JSON 数组写到 `ops/remediation_results.json`，每项格式参考手册中的示例（包含 incident_id、action、status）。
- 同时在 `ops/audit.log` 追加操作记录，每行格式：`ISO时间戳 | 操作 | 事件ID`（例如 `2025-04-14T03:12:00Z | remediated | UPS-001`）。

其他类别或非 critical 的事件不用管。做完告诉我，我这边准备跑后续流程。

-- Nikhil
