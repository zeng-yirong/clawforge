# 合成 CLI 训练环境的方法

本文说明如何继续合成与 `claw_envs/post_mails` 结构相同的新训练环境。

重点不是机械复制 `post_mails`，而是复用它背后的环境架构：

- session 由 trainer 持有和管理
- agent 只看得到任务相关命令
- 不可变数据放文件里，可变状态落到文件态 session
- 评测过程可确定、可复现
- 能安全支持并发 rollout

后续合成新环境时，可以把 `claw_envs/post_mails` 当作参考实现，再配合本文的方法来做。

---

## 设计目标

用于 RL 训练的合成环境，建议至少满足以下六个约束：

1. 环境应该更像真实工作流，而不是一个玩具函数调用题。
2. 环境只暴露 agent 真正应该使用的任务面，不暴露训练基础设施细节。
3. 环境要能支持大量并发 rollout，且不会出现共享状态污染。
4. 任务数据要可落盘、可检查、可持续扩展。
5. reward 应该能从 session 状态中确定性地计算出来。
6. 环境应该易于 reset、replay，以及做压力测试。

---

## 推荐的包结构

每个环境建议作为一个独立 Python 包，放在 `claw_envs/<env_name>/` 下。

```text
claw_envs/
  <env_name>/
    __init__.py
    cli.py
    environment.py
    evaluator.py
    repository.py
    store.py
    README.md
    SKILL.md
    concurrency_test.py
    data/
      scenarios/
      attachments/
      emails/
      social/
      accounts.json
      contacts.json
```

如果任务跨多个业务域，可以继续拆一些小模块，例如：

- `mail.py`
- `social.py`
- `tickets.py`
- `crm.py`
- `calendar.py`

这些模块负责承载领域内的状态变更和查询逻辑。`environment.py` 只做编排，不要把所有业务规则都塞进去。

### 快速起步模板

如果要新建一个环境，最快的做法通常是：

1. 复制 `claw_envs/post_mails/` 到 `claw_envs/<env_name>/`
2. 删除原来场景专用的数据文件
3. 只有当任务形态真的变化很大时，再去重命名领域模块
4. 替换数据模型、评测规则和 CLI 动词
5. 尽量保留 session store 和隐藏 rollout 生命周期的模式

如果新任务仍然属于“多 artifact 检索 -> 基于依据执行公开动作”这一类，组件边界通常可以基本不改。

---

## 各组件职责说明

### `data/`

`data/` 用来存不可变的世界数据。在 `post_mails` 里，这部分包括：

- 账号画像
- 联系人
- 邮件
- 公开帖子
- 附件
- 场景定义

设计原则：

- `data/` 里的内容都是“创作期数据”
- rollout 过程中不要修改 `data/`

这样环境数据就会非常容易 diff、扩展和审阅。

推荐拆分方式：

- `accounts.json`：工作账号、操作人画像或品牌人格
- `contacts.json`：任务世界里出现的人或组织
- `scenarios/*.json`：任务 prompt、实体 id、当前时间、评分规则
- 领域文件，例如 `emails/*.json`、`tickets/*.json`、`threads/*.json`
- `attachments/*.md` 或 `.txt`：agent 可能需要阅读的长文本材料

### `repository.py`

`repository.py` 是不可变数据访问层。

它应该负责：

- 解析 `data_root`
- 读取 JSON 或文本文件
- 暴露清晰的 helper 方法，例如 `load_email(email_id)`
- 对外隐藏真实文件布局

不要把 session 的可变逻辑写进 `repository.py`。

### `store.py`

`store.py` 是可变 session 状态层。

在 `post_mails` 中，每个 rollout session 的存储位置是：

```text
<state_root>/<session_id>/session.json
```

对应的锁文件是：

```text
<state_root>/<session_id>/.lock
```

`store.py` 建议提供这些能力：

- session id 校验
- session 路径帮助函数
- JSON 原子写入
- 锁获取与释放
- `load_session`
- `save_session`
- `create_session`

这是环境能安全支持并行 rollout 的关键之一。

### `environment.py`

`environment.py` 是环境服务层。

它负责：

- 创建和重置 session
- 编排多个领域模块
- 记录动作日志
- 生成确定性的事件时间戳
- 生成 session 摘要
- 提供 reward 入口

环境本身不需要知道 trainer 如何调度 rollout，但它必须提供合适的 primitive，使 trainer 能做到“一个 sample 绑定一个 session”。

### 领域模块，例如 `mail.py` 和 `social.py`

这些模块应实现具体任务里的领域操作，例如：

- 列表查询与过滤
- 标记为已读
- 发布帖子
- 追加回复
- 校验平台要求字段

它们应尽量保持窄而清晰：输入一个 session，返回结构化结果。不要在这里做 CLI 解析，也不要在这里做文件锁。

### `evaluator.py`

`evaluator.py` 负责根据最终 session 状态和 scenario 元数据计算 reward。

一个好的 evaluator 应该是：

- 确定性的
- 可检查的
- 基于明确场景事实驱动
- 在需要时对同义表达有一定鲁棒性
- 能惩罚过时信息和禁止性 claim

除非动作顺序在语义上真的重要，否则不要把评测写成对某种具体命令调用顺序的脆弱依赖。

### `cli.py`

`cli.py` 是 agent 面向的接口层。

对于这种模式，CLI 建议分成两类命令：

1. 对 trainer 隐式可用、对 agent 隐藏的命令，例如 `prepare-rollout` 和 `reset-rollout`
2. agent 的任务命令，例如 `task`、`list-*`、`read-*`、`publish-*`、`reply-*`、`session-summary`

agent 可见命令不应要求传 `--session-id`。
session 的绑定应该由 trainer 在 rollout 启动前通过环境变量注入。

### `concurrency_test.py`

这个脚本用于验证 session 隔离和加锁机制在高并发下是否正确。

之所以把它独立于正常 CLI，是因为：

- 它是给环境开发者用的，不是给 agent 用的
- 它可以直接走 Python API
- 它应该输出机器可读报告

### `README.md`

`README.md` 主要解释：

- 环境任务是什么
- session 模型是什么
- trainer 如何 bootstrap
- agent 能看到哪些命令
- 如何运行并发压力测试

### `SKILL.md`

`SKILL.md` 不是开发者文档，而是给运行在该环境里的 agent 的工作流说明。

它要尽量简短，只保留：

- 应该优先用哪些工具
- 哪些环境命令最重要
- 高层工作流
- 最重要的行为约束

---

## 最核心的架构规则：不要让 agent 管理 session

这是从 `post_mails` 提炼出来的最重要设计规则。

agent 的任务是解决业务问题，而不是管理 rollout 基础设施。
因此：

- 一个 rollout sample 对应一个 session id
- session 由 trainer 创建或重置
- trainer 把 session 绑定注入到 rollout 进程
- agent 执行命令时不应该看到 `--session-id`

这样可以避免一类常见问题：模型学会操纵 session plumbing，或者把训练基础设施细节泄露进 prompt。

### 隐藏的 trainer 命令

建议使用隐藏命令管理 rollout 生命周期，例如：

- `prepare-rollout`
- `reset-rollout`

CLI 可以为了兼容性保留 `create-session` 这类旧别名，但不要让这些命令出现在 agent 的帮助信息里。

### 必需的环境变量绑定

在 `post_mails` 里，trainer 会注入：

- `POST_MAILS_SESSION_ID`
- `POST_MAILS_STATE_ROOT`
- `POST_MAILS_SCENARIO_ID`

后续新环境建议沿用同样的命名模式，例如：

- `MY_ENV_SESSION_ID`
- `MY_ENV_STATE_ROOT`
- `MY_ENV_SCENARIO_ID`

### 推荐流程

```text
trainer -> prepare-rollout -> 拿到 bindings
trainer -> 用这些 bindings 启动 rollout 进程
agent -> 调用 task/list/read/publish/reply 等命令
trainer -> 如有需要调用 reset-rollout
trainer -> 调用 evaluate_session() 或读取最终 reward
```

---

## 数据合成方法

构建新环境时，建议先从“世界模型”开始，而不是先写代码。

### 1. 先定义真实工作流

优先选择满足以下条件的工作流：

- 目标明确
- 中间过程有可观察 artifact
- 最终有对外可见动作
- 存在有意义的失败路径

好的例子：

- 找到最新批准的 incident 响应说明并发布状态更新
- 阅读 CRM 记录并做正确的跟进动作
- 处理 vendor 邮件并发布采购决策
- 审查 support ticket 并输出有优先级的升级摘要

应避免那种本质上只是“查一个隐藏标签”的任务。

### 2. 定义 gold facts

先明确列出 agent 被允许使用的标准事实，例如：

- 发布时间
- 支持的功能
- 不支持的功能
- 已批准的对外表述
- 必须出现的 disclaimer
- 哪些公开线程必须回复

这份 gold facts 清单会同时决定 scenario 内容和 evaluator 规则。

### 3. 加入 stale facts 和 distractors

一个像样的环境不能只有一份完美真相，还需要加入“看起来合理但其实不该用”的信息。

对每个 gold fact，都可以考虑是否加入：

- 旧版本草稿
- 冲突性 rumor
- 部分正确但已过时的 artifact
- 语义相近但不具权威性的噪声消息

目的不是随机刁难 agent，而是迫使它识别“最新批准来源”。

### 4. 把事实分散到多个 artifact

不要把所有信息都放在一个完美文件里。

建议分布到：

- 邮箱内容
- 附件
- 公开线程
- FAQ 或说明文档
- persona 元数据

这样 agent 才需要做检索、核实和 grounding，更像真实工作。

### 5. 设计一条高效的正确路径

环境中最好存在一条清晰、合理、可执行的标准解法，例如：

1. 读取任务说明
2. 用 “approved” 等关键词搜索 inbox
3. 打开最可能的最新 brief
4. 阅读相关 FAQ 或 guardrails
5. 查看需要响应的公开线程
6. 发布官方内容
7. 基于批准事实进行回复

evaluator 可以允许替代路径，但环境本身应该有一条明显的“专业路径”。

### 6. 设计有意义的失败路径

例如：

- 在阅读批准 brief 之前就发布内容
- 使用旧草稿里的日期
- 声称不支持的功能
- 在官方公告前就去公开回复
- 忽略关键附件

这些失败路径应该在 `evaluator.py` 中被显式体现出来。

---

## Session 状态设计

建议把 session 设计成一个可以被加载、修改、保存、评测的 JSON 快照，而不是依赖外部长期运行服务。

### 推荐的 session payload 结构

```json
{
  "session_id": "<generated by trainer>",
  "scenario_id": "<scenario id>",
  "created_at": "<iso timestamp>",
  "meta": {
    "base_time": "<scenario time>",
    "action_index": 0
  },
  "workspace_account": {},
  "domain_a": {},
  "domain_b": {},
  "actions": []
}
```

### 为什么要保留 `actions` 日志

动作日志非常有价值，可用于：

- reward 计算
- 轨迹调试
- 顺序校验
- 分析失败 rollout 的行为

每条 action 建议至少包含：

- `action_index`
- `timestamp`
- `action_type`
- `details`

### 为什么要用确定性时间戳

不要直接用真实墙钟时间给动作打点。
应该用“场景时间 + action_index”的方式来推导。

好处：

- rollout 可复现
- 测试稳定
- 顺序相关评测更确定

---

## CLI 设计方法

CLI 应该表达任务面，而不是代码内部结构。

### 合理的 agent 可见命令

优先使用与真实任务一致的动词，例如：

- `task`
- `list-*`
- `read-*`
- `view-*`
- `publish-*`
- `reply-*`
- `approve-*`
- `dispatch-*`
- `session-summary`

### 不合理的 agent 可见命令

应避免暴露内部实现细节，例如：

- `load-json`
- `inspect-state`
- `dump-scenario`
- `set-session`
- `read-evaluator-rules`

### 输出格式

统一返回结构化 JSON，例如：

- `status`
- `data`

如果环境本身知道结构，就不要逼 agent 去解析一大段原始文本。

### 错误处理

对于基础设施错误，必要时要映射成更安全的任务侧错误信息。

例如：

- 没有 rollout 绑定 -> 提示 trainer 先 prepare session
- 锁超时 -> 提示调用方重试

不要把无关的基础设施细节暴露给 agent。

---

## Trainer 集成模式

这套架构本身就是为 rollout 系统集成准备的。

### Trainer 必须负责的事情

trainer 需要：

1. 调用 `prepare-rollout`
2. 获取返回的 bindings
3. 把这些 bindings 注入到 rollout 进程
4. 让 agent 通过 CLI 和环境交互
5. 在结束后通过 Python 环境或 wrapper 收集 reward

### 一个 trainer bootstrap 例子

```python
import json
import os
import subprocess

result = subprocess.run(
    [
        "python",
        "-m",
        "claw_envs.post_mails.cli",
        "prepare-rollout",
        "--scenario-id",
        "orbital_launch",
        "--show-bindings",
    ],
    check=True,
    capture_output=True,
    text=True,
)

payload = json.loads(result.stdout)
bindings = payload["data"]["bindings"]
rollout_env = {**os.environ, **bindings}
```

之后 trainer 就可以在 `rollout_env` 中运行 agent 可见命令。

### 为什么这里更适合 CLI-first

对于训练任务而言，CLI-first 通常优于共享 Flask 服务，因为它：

- 不需要固定端口
- 不依赖共享内存全局状态
- 减少服务启动竞争
- 让 session 生命周期更明确
- 更适合 many-worker rollout

只有当任务本身就是强网络服务形态，并且值得承担额外工程复杂度时，才建议改成 HTTP 服务。

---

## 如何编写 Evaluator

如果 evaluator 写得随意，它通常会成为最脆弱的部分。

### 优先从 scenario metadata 出发

尽量把这些信息写到 scenario 配置中：

- 必须阅读的附件
- 必须响应的公开线程
- 允许的 claims
- 禁止的 claims
- 要求的动作顺序

这样后续扩 scenario 会比把一堆特殊 case 硬编码在 Python 里更容易维护。

### 把检索奖励和动作奖励拆开

一个实用的模式是分别打多个维度的分，例如：

- retrieval / reading score
- 输出正确性分数
- reply 质量分数
- order / workflow 分数
- forbidden-claim penalty

最后再聚合成 `overall_score`。

这种设计的调试信号远好于单一 pass/fail。

### 显式惩罚 shortcut 行为

如果你希望 agent 学到的是 grounded 行为，就不要只看最终文本质量，还要明确惩罚：

- 使用过时来源
- 跳过前置阅读步骤
- 声称不支持内容
- 过早进行公开回复

否则模型会学到“猜答案”，而不是走环境希望的工作流。

---

## 并发与压力验证

如果环境是拿来做 RL 训练的，那么并发验证不是可选项，而是必选项。

### 应该测什么

至少要覆盖两类压力测试：

1. 多个独立 session 并行运行
2. 多个 worker 竞争同一个共享 session

第一类验证是否存在 session 污染。
第二类验证锁和 save 流程是否真的正确。

### 应该断言什么

最少要检查：

- 没有 worker crash
- 最终 action 数量与预期完全一致
- 最终 post / reply 数量与预期完全一致
- 合法行为下 reward 保持稳定

### 为什么要保留单独脚本

这样可以在大规模训练前单独运行，比如放到 CI 或本地 smoke test 中。

`post_mails` 的 `concurrency_test.py` 就是专门做这件事的。

---

## 测试策略

对于一个新环境，至少应该补这些测试：

### 1. Session 隔离测试

从同一个 scenario 创建两个 session。
修改其中一个。
断言另一个没有变化。

### 2. Happy-path evaluator 测试

执行标准正确流程，断言最终分数足够高，最好是满分。

### 3. Failure-path evaluator 测试

发布过时或禁止性内容，断言分数被惩罚。

### 4. CLI binding 测试

断言：

- agent 帮助信息里看不到隐藏 rollout 命令
- 没有 trainer binding 时 agent 命令会明确失败
- `prepare-rollout` 之后，不传 `--session-id` 也能正常执行 agent 命令

这些测试都不大，但它们守住了 environment 和 trainer 之间最重要的契约。

---

## 推荐的实现顺序

合成一个新环境时，建议按这个顺序来：

1. 定义任务和 gold facts 清单
2. 先写 `data/` 下的不可变数据
3. 实现 `repository.py`
4. 定义 session JSON 结构
5. 实现带原子写入与加锁的 `store.py`
6. 实现领域模块
7. 实现 `environment.py`
8. 实现 `evaluator.py`
9. 实现带隐藏 trainer 生命周期命令的 `cli.py`
10. 加单元测试
11. 加并发压力脚本
12. 补 `README.md` 和 `SKILL.md`

不要从 CLI 开始写。应该先把世界数据和 session 模型想清楚。

### 一个更实用的三天开发节奏

```text
day 1:
  - 定义 scenario 和 gold facts
  - 写数据文件
  - 打通 repository.py 和 session payload

day 2:
  - 实现领域动作
  - 实现 evaluator.py
  - 实现 CLI 命令

day 3:
  - 补测试
  - 补 concurrency_test.py
  - 补 README.md 和 SKILL.md
  - 跑压力验证
```

这种节奏可以避免 CLI 提前长出来，但数据和 reward 模型还没稳定。

---

## 常见错误

继续按这个模式造环境时，尽量避免以下错误：

- 让 agent 自己管理 `session_id`
- 把 rollout 状态存在模块级全局变量里
- 让 reward 逻辑直接依赖 CLI 解析
- 把可变状态重新写回 `data/`
- 在 session 日志里使用真实墙钟时间
- 在普通帮助信息中暴露隐藏 trainer 命令
- 把所有逻辑都堆到一个超大的 `environment.py`
- 因为 isolated 测试通过了，就跳过 contention 测试
- 只评分最终文本，不检查前置阅读是否完成

---

## 最小检查清单

在认为一个新环境已经可用之前，至少确认下面这些都成立：

- agent 可以只通过 agent 可见的 CLI 命令完成任务
- trainer 可以为每个 rollout sample 创建独立 session
- `session_id` 不会出现在 agent 工作流里
- 不可变世界数据都落在 `data/` 文件中
- 可变 rollout 状态是文件态、且有锁保护
- evaluator 是确定性的，并由 scenario 驱动
- 环境具备 session 隔离测试
- 环境至少有一个并发压力测试
- `README.md` 解释了 trainer bootstrap 和 agent 命令
- `SKILL.md` 用简短方式说明了 agent 工作流，记得用英文描述

如果一个新环境满足这份检查清单，那么它在结构上就已经和 `post_mails` 对齐，通常可以安全接入训练。
