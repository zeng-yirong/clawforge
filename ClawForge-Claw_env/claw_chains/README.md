# claw_chains — 工具链生成管线(claw 特色环境)

这是 `gen_chains/`(通用环境工具链方案)的 claw 版本。通用方案把每个环境的工具
当作可自由组合的散装函数,用 LLM 猜依赖建图再采样路径。claw 环境不同:agent 看到的
是**两层工具面**,且依赖关系可从代码确定性抽取,无需 LLM 猜测。

## 两层工具面

- **L1 scaffold 工具**:`read / write / edit / str_replace_editor / ls / find / grep /
  execute_bash / finish`,来自 `uni_agent.tools` registry,所有环境共享。
- **L2 环境 CLI 动词**:`list-customers / get-customer / generate-retention-email / ...`,
  解析自每个环境的 `cli.py`,**通过 `execute_bash` 调用**。trainer 隐藏命令
  (`prepare-rollout` / `reset-rollout`,即 `argparse.SUPPRESS`)会被剔除。

## 三个阶段

| 阶段 | 脚本 | 对应通用方案 | 产物 |
|---|---|---|---|
| A 抽取 | `extract_claw_tools.py` | `generate_graphs.py` | `claw_tool_env_docs/<env>.json` + `_scaffold_tools.json` |
| B 建图 | `build_claw_graph.py` | `build_graphs.py` | `claw_tool_graphs/<env>_tool_graph.json` |
| C 采样 | `sample_claw_chains.py` | notebook 路径采样 | `claw_chains_out/<env>.jsonl` |
| 旁路 | `gen_tool_env_docs.py` | `generate_graphs.py` 的 tool docs | `tool_env_docs/<env>.json`(函数工具格式) |
| 共用 | `llm_client.py` | `hm_aigc` 封装 | — |

## LLM 用在哪(对齐通用方案)

通用方案的 LLM 用在两处,claw 在**相同位置**用 LLM,以保证工具链可用性与多样性;
LLM 不可用(`hmwrangler` 缺失)时全部**优雅降级**为确定性输出,管线在任何环境都能跑:

1. **工具/参数描述生成**(`gen_tool_env_docs.py` 的 `_enrich_via_llm`)——对应通用方案的
   `_fill_env_docs_via_llm`。`cli.py` 没有 `help=` 文本的动词/参数,交给 LLM 写简洁描述;
   有 help 文本则直接用,无 LLM 时退化为模板描述。
2. **图的弱边生成**(`build_claw_graph.py` 的 `_llm_weak_edges`,`tier=llm_weak`)——对应
   通用方案的 `fetch_graph_code`。强边(dataflow/gold)已确定性建好,LLM 只补 0.2–0.3 的
   跨实体"合理后续"弱边,增加采样路径多样性。`--no-llm` 可关闭。

`llm_client.py` 封装与通用脚本一致的接口(`hm_aigc.aigc_managed`,`model_agent="yibu"`,
`deepseek-v4-flash`),`llm_json` / `llm_text` 在不可用时返回 None 触发降级。

## tool_env_docs 格式

`gen_tool_env_docs.py` 输出对齐 `30clawenv/tool_env_docs/*.json` 的函数工具格式:每个环境
一个 JSON 数组,**含 L1 scaffold 工具 + L2 CLI 动词**(L2 用 `action` 下划线名,对齐 evaluator),
每条 `{name, description, parameters:{type:"dict", properties, required}, response}`。
`_scaffold.json` 单独存共享的 L1 工具。

### A. 抽取(确定性,不依赖 LLM)
- L1:从 registry 取 scaffold 工具 schema(导入失败时退化为 stub)。
- L2:AST 解析 `cli.py` 的 `add_subparsers`/`add_parser`/`add_argument`,得到可见动词、
  参数(`required`/类型)、隐藏命令。支持**跟随 `_shared` CLI 工厂委派**
  (guard 环境的 verbs 来自 `_shared/security_guard_cli.py`)。
- 数据流信号:某动词 `--<entity>-id` 必填 → 找产出该 id 的 list/get 动词,建
  `produces_<entity>_id_for` 边(免猜)。
- 评测信号:解析 `evaluator.py` + `data/scenarios/*.json`,取 `required_actions`(gold
  序列)、anchor 字段(`target_*`/`expected_*`/`deny_*`)、打分维度。支持跟随 `_shared`
  evaluator 委派。

### B. 建图(两层异质 DiGraph,三档边)
- 节点 = L1 ∪ L2 可见动词;节点标 `layer`(scaffold/cli)、`role`(read/produce/guard)。
- 边三档,确定性优先:
  1. **dataflow**(weight 0.8)— 来自 cli.py 参数依赖。
  2. **gold**(weight 0.9)— 来自 evaluator 的 `required_actions` 顺序。
  3. **bridge**(0.3–0.6)— 规则生成的 L1↔L2 编织:`read(task)→任务动词→读动词→
     grep/find→produce 动词→write/edit→finish`。
- 不用 LLM 主导建图;如需扩跨实体弱边可后续加一层可选 LLM pass。

### C. 采样(围绕 gold 骨架 + 数据流可达)
claw 的两条硬约束,通用采样器没有:
1. **gold 覆盖**:每条链必须覆盖该 scenario 的 `required_actions`,否则注定低分、无训练
   价值。所以以 gold 序列为骨架,在间隙插入 scaffold 操作和可选读动词,生成"带噪声但
   仍正确"的链。
2. **数据流可达**:带 `--<entity>-id` 的动词,前驱必须先出现该 id 的产出动词;静态未找到
   producer 时退化为名字匹配的读动词注入,仍无法解析则标 `dataflow_ok=false`(供审查,
   不静默丢弃)。

## 用法

```bash
cd claw_envs/claw_chains
python extract_claw_tools.py                      # 全部 39 个环境(含/不含 skill)
python build_claw_graph.py
python sample_claw_chains.py --n 8 --seed 0       # 确定性采样

# 单环境
python extract_claw_tools.py --env post_mails
python build_claw_graph.py   --env post_mails
python sample_claw_chains.py --env post_mails --n 12
```

## 通用覆盖

- **不含 skill** 环境(`without_skill/*`)与**含 skill** 顶层环境(`post_mails` 等)同一套
  脚本处理;`has_skill_md` 字段贯穿三个阶段,便于把"有无 skill"作为独立训练条件区分。
- env-var 绑定兼容两种风格:显式常量(`CHURN_..._SESSION_ID = "..."`)与工厂 kwarg
  (`session_env_var="..."`)。

## 下游

`claw_chains_out/<env>.jsonl` 的每条链 = `{env_name, scenario_id, has_skill_md,
gold_actions, chain:[{layer, op, call}], dataflow_ok}`,作为后续**种子 scenario 派生 +
真跑自校验 + persona 规模化**阶段的输入。注意 claw 数据**不内嵌** `init_env` /
`validation_protocol`(与通用 `example.jsonl` 不同):状态由文件态 session 提供,reward 由
环境既有的确定性 `evaluate_session()` 在 rollout 后现算。

## 初始环境状态生成(descriptor → 核心态 → 复杂化)

claw 环境的"初始状态" = `data/` 目录里的实体记录集合;scenario 通过 **id 池**
(`email_ids`/`customer_ids`)和 **anchor 键**(`target_customer_id`/`required_*`)引用这些
记录。早期 Stage B 让 LLM 盲猜 `data_fragments`,字段/类型常出错。现拆成三步,**evaluator.py
始终原样复用,绝不重写**:

| 步骤 | 脚本 | 产物 |
|---|---|---|
| 0 描述 | `gen_env_descriptors.py` | `env_descriptors/<env>.json` |
| B 核心态 | `gen_claw_seed_tasks.py`(改造 Stage B) | `claw_seed_tasks/seed_tasks_<env>.jsonl` |
| C 复杂化 | `complicate_env_state.py` | `claw_seed_tasks_complicated/seed_tasks_<env>.jsonl` |
| 自校验 | `selfcheck_complicated.py` | 临时 rollout + evaluator 现算 |

- **descriptor**:确定性扫描每个 data 文件,推断 kind(per_record / collection /
  markdown_attachment / csv)、字段名/类型、低基数短串 `enum`(datetime/长文本标 `free_text`)、
  记录主键;再读 scenarios 把 id 池/anchor 键映射到它们引用的文件(`points_to`,一个
  `customer_id` 可同时落在 `customers.json` + `logs/*.json`)。LLM 仅为字段补一句 `desc`,
  不可用时退化模板。结构由代码保证准确。
- **核心态**:Stage B 把 descriptor 的 file schema + `points_to` 喂 LLM,要求产出的
  `data_fragments` 严格按字段 schema、含全部 required、enum 取合法值,且 id 在多文件间一致。
  产物标 `state_stage:"core"`。无 LLM 时退化为复用 base scenario。
- **复杂化**:克隆现有合法记录(env 真实数据 + 核心态 fragment 的**冻结快照**,避免克隆克隆),
  改主键为诱饵 id、轻改 1-2 字段(near-dup / stale / decoy / noise)。诱饵 id 只进 scenario
  的 **id 池**(逼 agent 辨别),**绝不进 anchor 键**;anchor 引用的记录列入 `protected_ids`
  从不改动。每条带 `complication_log` 便于审查。`--noise-per-pool`/`--seed` 可调可复现。
- **自校验**:把复杂化态物化进 env 的临时拷贝,`prepare-rollout`(证明诱饵记录可 hydrate =
  schema 合法)+ 直接调 builtin evaluator(证明 anchor 未被破坏)。CLI 无 `--data-root` 覆盖、
  scenario 无 `scenario_id`、evaluator 非模块级函数的环境会**优雅 SKIP**(复杂化仍照常应用)。

用法:
```bash
python gen_env_descriptors.py                     # 全部;或 --env <env> / --no-llm
python gen_claw_seed_tasks.py --max-chains 2      # 核心态
python complicate_env_state.py --seed 0           # 复杂化
python selfcheck_complicated.py --env post_mails  # 单环境自校验
```

