# CompeteTrack Environment

竞争情报追踪环境，用于AI训练和评估，专注于追踪竞品市场表现、监管政策变化及用户获取情况。

## 功能特性

- **竞品追踪**: 监控竞品市场表现、财务数据、产品线动态
- **政策监控**: 追踪全球监管政策变化及其对业务的影响
- **用户获取分析**: 分析用户获取渠道、转化漏斗、用户群组表现
- **报告生成**: 自动生成竞争格局、监管摘要、用户获取分析报告
- **告警管理**: 创建和确认重要竞品或政策变化的告警

## 安装

```bash
pip install -e .
```

## 快速开始

```bash
# 列出可用场景
python -m compete_track_envs.cli list-scenarios

# 创建会话
python -m compete_track_envs.cli prepare-rollout --session-id my-session

# 查看任务
python -m compete_track_envs.cli task

# 执行操作
python -m compete_track_envs.cli list-competitors
python -m compete_track_envs.cli list-policies
python -m compete_track_envs.cli list-users
```

## 核心模块

| 模块 | 说明 |
|------|------|
| `environment.py` | 主环境类，协调所有操作 |
| `repository.py` | 数据访问层 |
| `store.py` | 会话状态管理 |
| `evaluator.py` | 评估逻辑 |
| `competitors.py` | 竞品业务逻辑 |
| `policies.py` | 政策业务逻辑 |
| `users.py` | 用户业务逻辑 |
| `reports.py` | 报告生成逻辑 |
| `cli.py` | 命令行接口 |

## 数据结构

```
compete_track_envs/
├── data/
│   ├── competitors/     # 竞品数据 (JSON)
│   ├── policies/        # 政策数据 (JSON)
│   ├── users/           # 用户数据 (JSON)
│   ├── scenarios/       # 场景定义 (JSON)
│   ├── accounts.json    # 账户配置
│   └── contacts.json    # 联系人配置
└── .compete_track_state/  # 会话状态存储
```

## 并行Rollout

由于每个会话独立存储在文件系统中，可以并行运行多个会话：

```bash
# 并行创建多个会话
python -m compete_track_envs.cli prepare-rollout --session-id rollout-1 &
python -m compete_track_envs.cli prepare-rollout --session-id rollout-2 &
python -m compete_track_envs.cli prepare-rollout --session-id rollout-3 &

# 并行执行任务
export COMPETE_TRACK_SESSION_ID=rollout-1
python -m compete_track_envs.cli list-competitors &
```

## License

MIT
