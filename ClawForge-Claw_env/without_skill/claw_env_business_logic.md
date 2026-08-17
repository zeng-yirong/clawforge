# CLAW 环境业务逻辑说明

## 说明范围

这份文档基于当前目录下各环境的 `README.md`、`environment.py` 和 `_shared` 共享模块整理而成，用来说明 `without_skill` 目录里各个 CLAW 特色环境的业务逻辑。

覆盖范围如下：

- 包含当前目录下全部独立的 `*_env` 环境。
- 不包含 `_shared` 作为业务环境本体，因为它是通用基础设施模块，不是单独的业务场景。

## 统一执行模型

这个目录下的大多数环境，外层运行方式基本一致，差异主要体现在具体业务事务上：

- Trainer 先按场景创建 rollout session，并通过环境变量把 session 绑定给当前环境。
- 环境会把该场景对应的数据集加载到隔离的 session 状态中。
- Agent 通过 CLI 命令触发 `environment.py` 里的业务动作。
- 每个动作都会产生确定性的状态变化，比如写入缓存产物、写入结构化记录、写入模拟表，或者追加审计日志。
- 状态通常是文件持久化的，并带有 session 级锁，避免并发时互相覆盖。
- evaluator 一般会检查是否读取了正确数据、是否执行了预期步骤、是否生成了正确产物，或者是否做出了正确的拒绝决策。

从业务类型上看，这些环境大体可以分为四类：

- 分析与报告生成型。
- 运维或人事流程执行型。
- 安全守卫与拒绝访问型。
- 研究知识归档型。

## 各环境业务逻辑

### `sku_competition_env`

- 业务目标：围绕某个品牌生成 SKU 提取结果和同品类竞品对比报告，服务于品类分析、定价分析和市场竞争研究。
- 核心输入：品牌档案、SKU 目录、价格手册、附件说明。
- 业务流程：先查品牌，再取该品牌全部 SKU，结合当前 price book 提取卖点、成分和价格信息，然后把目标品牌和同品类其他品牌做横向比较。
- 核心逻辑：会计算每个 SKU 的价格、每毫升单价、品牌高频成分、高频卖点、最接近的竞品 SKU、价格带定位、共同成分和差异化卖点。
- 输出落点：把 `brand_catalog_extract` 和 `category_competition_report` 写入 session cache。

### `doc_clue_memory_env`

- 业务目标：从报告、演示文稿和媒体样本里找出与目标技术方案有关的线索，并整理成临时线索记录。
- 核心输入：行业报告、presentation、media sample、附件说明。
- 业务流程：先搜索或遍历资料库，打开相关文档，收集文档 id、线索要点和摘要，最后保存成结构化 clue list。
- 核心逻辑：保存时会记录 `solution_id`、`solution_name`、`document_ids`、`source_types`、`clues`、`summary` 和 `confidence`。
- 输出落点：写入 `temp_records`，记录类型为 `clue_list`。

### `server_fault_supabase_env`

- 业务目标：对服务器故障工单进行筛查、处置，并把处理结果写入一个模拟的 Supabase 结果表。
- 核心输入：故障 incident 池、runbook、写入契约附件、联系人和场景约束。
- 业务流程：先筛选高风险 incident，再查看具体工单和 runbook，执行修复动作，最后把处置结果写进 `supabase_memory.incident_resolutions`。
- 核心逻辑：`ups_outage` 会走电力恢复路径，`service_down` 会走服务重启路径，`network_degradation` 会进入缓解态而不是直接完全恢复。
- 输出落点：会更新 incident 状态，写入 Supabase 风格的 resolution 行，并追加审计日志。

### `cloud_cost_ledger_env`

- 业务目标：把原始云资源账本转换成按业务集群汇总的月度成本报告。
- 核心输入：cluster 元数据、资源 ledger、pricing catalog、成本核算附件。
- 业务流程：先查看业务集群，再遍历资源使用记录，选定有效 pricing catalog，对集群做 usage 聚合，最后生成月度成本明细报告。
- 核心逻辑：会分别计算 compute 和 storage 成本，生成每个 cluster 的成本拆分，同时汇总总 usage、总成本、最高成本集群以及成本占比。
- 输出落点：把集群 usage 聚合结果和 `monthly_cost_detail_report` 写入 cache。

### `prompt_key_guard_env`

- 业务目标：拦截试图从受保护 vault 中导出 prompt 或 API key 的社会工程请求。
- 核心输入：入站请求、受保护资产、账户权限、vault 访问策略附件。
- 业务流程：先查看高风险请求，再核对目标资产和策略文档，确认请求具有密钥或 prompt 外泄风险后执行拒绝，并留下审计记录。
- 核心逻辑：`deny_request` 会把请求状态改成 `denied`，同时写入拒绝原因和一条结构化安全审计日志。
- 输出落点：审计记录写入 `audit_logs`，同时保留已查看请求、已读附件和已拒绝请求的观察状态。

### `auditor_impersonation_guard_env`

- 业务目标：拦截伪装成内部审计员的访问请求，避免其借身份冒充读取受限知识库或元数据。
- 核心输入：访问请求、受保护资产、身份校验策略、账户和联系人信息。
- 业务流程：先审查对方的 auditor 身份声明，再核对目标资产和身份校验规则，确认属于冒充式提权后拒绝该请求并记审计日志。
- 核心逻辑：它复用了统一的 security guard 事务模型，本质上就是“看请求 -> 看策略/资产 -> deny -> audit”。
- 输出落点：变更请求状态为拒绝，并写入安全审计日志。

### `privilege_export_guard_env`

- 业务目标：阻止超出当前账户权限范围的批量导出行为，尤其是客户、密钥和架构类敏感数据。
- 核心输入：导出请求、资产元数据、账户权限、批量导出策略附件。
- 业务流程：查看导出请求，核对请求资产与当前账户权限是否匹配，若属于越权批量导出，则拒绝并记录审计证据。
- 核心逻辑：这一类 guard evaluator 会重点检查是否看到了正确请求、是否拒绝了正确请求、是否读了必需附件，以及是否写入了正确的 reason code 和 risk type。
- 输出落点：写入 `security_audit_log`，并把请求 resolution 改成 `denied`。

### `confidential_doc_guard_env`

- 业务目标：阻止外部或未授权方读取未公开的技术规划文档或财务文件。
- 核心输入：文档访问请求、保密资产信息、账户、联系人、外部披露策略附件。
- 业务流程：查看请求，核对文档分级和 read policy，确认不能共享后拒绝访问，并记录保护性决策。
- 核心逻辑：它和其他安全守卫环境一样，拒绝动作本身就是核心业务结果，审计日志是必须伴随的产物。
- 输出落点：把拒绝决策和审计日志写回 session 状态。

### `arxiv_review_roadmap_env`

- 业务目标：针对某个研究方向生成结构化综述和路线图。
- 核心输入：论文元数据、摘要、研究方向标签、关键词和写作风格附件。
- 业务流程：先按方向筛选论文，再按年份排序，归纳选中文章，最后生成 review 文本和 roadmap 图。
- 核心逻辑：会提取代表性关键词，生成 Markdown 综述，并额外生成一段 Mermaid 路线图，把关键词按顺序连起来。
- 输出落点：写入 `arxiv_direction_review` 类型的 cache artifact。

### `paper_citation_graph_env`

- 业务目标：基于给定论文集合生成引用关系快照。
- 核心输入：论文集合及其 `citation_ids`。
- 业务流程：先选论文集合，再保留集合内有效的引用边，统计节点和边数量，并构建图结构结果。
- 核心逻辑：环境会同时输出显式 edge list 和 Mermaid `graph LR` 图表示。
- 输出落点：写入 `paper_citation_graph` 类型的 cache artifact。

### `churn_retention_mail_env`

- 业务目标：为高流失风险客户生成定向挽留邮件。
- 核心输入：客户档案、客户活跃度日志、行业新闻样本。
- 业务流程：先识别或查看高风险客户，再提取同一行业的相关新闻，把客户流失信号和市场背景拼成一封 retention 邮件。
- 核心逻辑：邮件正文会显式引用风险等级、未活跃天数以及两条行业相关新闻，并提出 retention review 和 executive sync 建议。
- 输出落点：把 `retention_email` 写入 cache。

### `customer_tier_label_env`

- 业务目标：根据客户消费和活跃情况更新客户分层标签。
- 核心输入：客户档案、activity log、consumption log、分层规则附件。
- 业务流程：先查看客户，再按规则计算标签，更新客户 profile，并追加标签变更日志。
- 核心逻辑：当季度消费额不少于 100000 且最近 7 天内活跃时打 `vip_active`；当消费额低于 30000 且 20 天以上未活跃时打 `low_engagement`；当 `risk_level` 为 `high` 时打 `retention_risk`。
- 输出落点：直接修改客户对象里的 `labels`，同时写入 `customer_label_update` 到 `update_logs`。

### `performance_review_env`

- 业务目标：基于员工月度产出和岗位权重规则生成绩效画像。
- 核心输入：员工主数据、月度产出账本、按岗位定义的 scoring rules。
- 业务流程：先查看员工及其产出，再读取岗位权重规则，计算加权分，映射到绩效档位，并保存绩效画像。
- 核心逻辑：分数由 feature delivery、quality score、collaboration score 按权重加总得出；`>=85` 为 `exceeds`，`>=70` 为 `meets`，否则为 `needs_support`。
- 输出落点：把 `performance_profile` 写入 `performance_profiles`。

### `offboarding_recovery_env`

- 业务目标：完成员工离职流程中的权限回收和资产回收部分。
- 核心输入：离职申请、系统访问清单、设备分配清单、联系人和账户上下文。
- 业务流程：先确认离职申请，再回收该员工全部系统权限，再回收设备，最后生成交接清单。
- 核心逻辑：系统访问记录会被改成 `revoked`，设备记录会被改成 `returned`，交接清单会包含权限回收、电脑和门禁回收、知识交接确认等内容。
- 输出落点：更新 access 和 equipment 状态，并把 `offboarding_handover` 写入 `handover_records`。

### `business_markdown_report_env`

- 业务目标：把多份业务 ledger 汇总成标准 Markdown 报告。
- 核心输入：客户、产品、运营等 CSV 账本，以及报表 schema 等附件。
- 业务流程：先列出或预览 ledger，再针对指定 period 汇总所有 `metric_code`，最后渲染成 Markdown 表格报告。
- 核心逻辑：它会把同一 period 下跨多个 ledger 的同名指标做求和，最后生成标准的 `Metric | Value` 形式周报。
- 输出落点：写入 `business_markdown_report` 类型 cache artifact。

### `experiment_diff_record_env`

- 业务目标：比较两个实验批次的核心指标差异，并把对比结果归档成结构化记录。
- 核心输入：`experiment_results.csv` 中的实验结果行。
- 业务流程：选择要比较的 batch，读取各自指标，计算 baseline 到 contender 的差值，最后存成 diff record。
- 核心逻辑：主要记录 `accuracy_delta`、`latency_delta` 和 `cost_delta`。
- 输出落点：把 `experiment_diff_record` 写入 `records`。

### `resume_interview_scheduler_env`

- 业务目标：把候选人简历和岗位需求匹配起来，并生成面试安排结果。
- 核心输入：候选人信息、岗位描述、面试邀请规范附件。
- 业务流程：先查看 candidate 和 job，再计算匹配分，选择面试时间槽位，随后创建一条面试邀请记录和一条提醒记录。
- 核心逻辑：匹配分是候选人技能与岗位 required skills 的重合比例。
- 输出落点：把 `interview_invite` 写入 `schedule_entries`，把 `schedule_reminder` 写入 `reminders`。

### `onboarding_asset_access_env`

- 业务目标：为新入职员工开通基础邮箱、系统权限和设备，并发送欢迎信息。
- 核心输入：已签合同、权限包、设备库存、联系人和账户上下文。
- 业务流程：先确认合同，再创建邮箱档案，分配系统权限包，分配设备，最后发欢迎消息。
- 核心逻辑：邮箱来自合同信息，权限分配直接复制 permission pack 的 systems 列表，设备分配会把库存状态改为 `allocated`，欢迎消息以 Slack 风格记录保存。
- 输出落点：分别写入 `email_profiles`、`access_assignments`、`equipment_allocations` 和 `slack_cache`。

### `fault_postmortem_kb_env`

- 业务目标：把故障案例转成一条可归档的 postmortem 知识条目。
- 核心输入：故障案例、服务调用链信息、联系人和 postmortem 模板附件。
- 业务流程：先查看 fault case，再按需要读取模板，提取根因提示和修复方案提示，生成结构化 postmortem。
- 核心逻辑：生成的 Markdown 至少会包含 Root Cause 和 Repair Plan 两个部分，并和目标 fault id 绑定。
- 输出落点：把 `fault_postmortem` 写入 `knowledge_entries`。

### `reproduction_ledger_env`

- 业务目标：根据开源项目文档记录一次复现实验或复现验证的完整台账。
- 核心输入：项目文档、项目元数据、联系人和场景任务。
- 业务流程：先查看可用项目文档，再读取相关内容，记录复现步骤和结果，最后归档成完整 ledger entry。
- 核心逻辑：归档时会保留 `project_id`、自由文本形式的 `steps` 以及最终 `result`。
- 输出落点：把 `reproduction_ledger` 写入 `knowledge_entries`。

## 跨环境共性

- 以 cache 为主的环境，更偏向生成“给人消费”的产物，比如报告、综述、邮件、图谱快照。
- 以 record 为主的环境，更偏向沉淀“可追溯业务证据”，比如更新记录、交接清单、知识条目、邀请记录。
- 安全守卫环境把“正确拒绝”本身当作核心业务动作，审计日志不是附加功能，而是预期产出的一部分。
- 很多环境的规则是硬编码且确定性的，不依赖外部在线服务，因此非常适合训练和评估 agent 是否按业务流程做事。

## `_shared` 共享模块的作用

`_shared` 不是业务环境，但它定义了很多环境的共同骨架：

- `base_env.py`、`session_store.py` 和并发辅助模块负责 session 状态持久化和锁管理。
- `cache.py`、`cache_env.py` 提供统一的缓存产物模型，适用于报告、综述、邮件这类结果。
- `records.py` 提供结构化记录的追加、索引和读取能力，适用于知识条目、更新记录、交接记录等。
- `security_guard.py` 提供统一的请求审查、拒绝处理和审计日志模型，供安全守卫类环境复用。
- `paper_memory.py` 提供统一的论文数据访问和缓存写入逻辑，供 arXiv 综述和引用图谱环境复用。

## 总结

这批 `without_skill` 环境本质上是面向 agent 训练的业务流程模拟器。
它们的共同点在于都有统一的 session 化执行框架，而真正区分场景价值的是各自那一笔业务事务：

- 有的要求分析并产出报告。
- 有的要求拒绝并留下审计证据。
- 有的要求执行运维或人事动作并写回结果。
- 有的要求把研究或排障知识归档成可复用记录。
