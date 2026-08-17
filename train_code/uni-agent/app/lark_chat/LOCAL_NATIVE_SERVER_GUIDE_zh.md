# `local_native` 服务器部署指南（本地大模型）

本文面向这条部署路径：

- 运行环境：Linux 服务器 / 云主机 / 独立 VM
- Agent 模式：`app/lark_chat` 的 `local_native`
- 模型方式：本机自部署的大模型服务，提供 OpenAI-compatible `chat/completions` 接口
- 消息入口：Lark / Feishu Bot，通过 `lark-cli` 收消息和回消息

这条路径的核心特征是：

- 不使用 Docker 容器隔离
- Agent 会直接在宿主机 bash 上执行模型生成的命令
- 适合已经隔离好的专用服务器

不建议在个人办公电脑上直接使用 `local_native`。

---

## 1. 部署结构

`local_native` 的运行结构如下：

1. `python -m app.lark_chat.main` 在服务器上启动一个长期运行的进程
2. 该进程通过宿主机上的 `lark-cli` 监听 `im.message.receive_v1`
3. 收到消息后，Uni-Agent 在宿主机 bash 中调用工具
4. 模型请求发往你本机部署的大模型服务
5. 回复消息再通过同一个 `lark-cli` 发回 Lark / Feishu

注意事项：

- 这不是 HTTP webhook 服务，而是一个长期运行的监听进程
- 消息处理是串行的，共享一个 bash 会话
- 长期记忆和 transcript 都保存在服务器本地磁盘

---

## 2. 前提条件

开始前请确认以下条件已经满足：

- 服务器是 Linux，且有 `/usr/bin/env bash`
- Python >= 3.10
- 可以访问 GPU，或至少可以启动你自己的本地模型服务
- 已安装 `git`
- 已安装 `nodejs` 和 `npm`
- 已有可用的 Feishu / Lark 开发者应用
- Bot 已订阅事件 `im.message.receive_v1`
- 事件投递模式已设置为 WebSocket / long-link

建议先执行：

```bash
which bash
python3 --version
node --version
npm --version
git --version
```

如果 `which bash` 没有输出，不要继续使用 `local_native`。

---

## 3. 服务器目录约定

以下命令假设你把仓库放在：

```bash
/opt/uni-agent
```

如果你的实际目录不同，把后续命令中的路径替换掉即可。

建议使用专门用户运行，例如 `agent`：

```bash
sudo useradd -m -s /bin/bash agent || true
sudo mkdir -p /opt/uni-agent
sudo chown -R agent:agent /opt/uni-agent
```

后续命令默认在该用户下执行。

---

## 4. 安装系统依赖

以 Ubuntu 为例：

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-venv python3-pip \
  git curl tmux \
  nodejs npm
```

如果你使用其他发行版，请安装等价包。

`tmux` 不是必须，但强烈建议安装，方便长期挂后台。

---

## 5. 拉取代码并创建 Python 环境

```bash
cd /opt
git clone <YOUR_REPO_URL> uni-agent
cd /opt/uni-agent

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
```

如果代码已经存在，只需要：

```bash
cd /opt/uni-agent
source .venv/bin/activate
```

---

## 6. 安装 Uni-Agent 依赖

按仓库当前的安装方式执行：

```bash
cd /opt/uni-agent
source .venv/bin/activate

git submodule update --init --recursive
pip install --no-deps -e ./verl
pip install swe-rex loguru pydantic pydantic_settings aiohttp
```

`local_native` 额外依赖这些包：

```bash
pip install pexpect bashlex pyyaml tiktoken
```

可选校验：

```bash
python -c "import pexpect, bashlex, yaml, aiohttp; print('python deps ok')"
```

---

## 7. 启动本地大模型服务

你需要一个 OpenAI-compatible 接口，且模型本身支持工具调用。

仓库文档里给出的示例是 vLLM。以下是一个常见启动方式：

```bash
source /opt/uni-agent/.venv/bin/activate

CUDA_VISIBLE_DEVICES=0,1,2,3 \
vllm serve /data/models/Qwen3.6-35B-A3B \
  --served-model-name Qwen/Qwen3.6-35B-A3B \
  --tensor-parallel-size 4 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --port 8000
```

如果你是单卡服务器，可以改成：

```bash
CUDA_VISIBLE_DEVICES=0 \
vllm serve /data/models/Qwen3.6-35B-A3B \
  --served-model-name Qwen/Qwen3.6-35B-A3B \
  --tensor-parallel-size 1 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --port 8000
```

如果你不是用 vLLM，只要满足这几个要求即可：

- 有 OpenAI-compatible `/v1/chat/completions`
- 支持工具调用
- 能稳定处理长上下文

启动后先做自检：

```bash
curl http://127.0.0.1:8000/v1/models
```

如果这里不通，Agent 不要继续启动。

建议把模型服务单独放到一个 `tmux` 会话中：

```bash
tmux new -s model
```

然后在 `tmux` 里运行 vLLM。退出但不关闭会话：

```bash
Ctrl+b d
```

重新进入：

```bash
tmux attach -t model
```

---

## 8. 配置 Feishu / Lark 开发者后台

在 Feishu / Lark 开发者后台确认以下项目：

- 应用已创建
- Bot 已启用
- 已订阅 `im.message.receive_v1`
- 事件接收方式为 WebSocket / long-link
- 需要测试的用户或群聊可以向该 Bot 发消息

本地代码不负责替你创建这些平台配置。

---

## 9. 安装并授权 `lark-cli`

在服务器上执行：

```bash
npm install -g @larksuite/cli
lark-cli --version
```

初始化和授权：

```bash
lark-cli config init --new
lark-cli auth login
lark-cli auth status
```

说明：

- `auth login` 走的是设备码 / OAuth 流程
- 即使服务器没有桌面环境，也可以在终端里看到登录地址和授权码
- 你可以在自己的浏览器里完成授权

授权完成后，务必确认：

```bash
lark-cli auth status
```

如果这一步失败，后续启动时会卡在获取 bot `open_id` 阶段。

---

## 10. 准备运行目录

建议先手动创建所有运行目录：

```bash
mkdir -p ~/.uni-agent/app/lark_chat/memory/notes
mkdir -p ~/.uni-agent/app/lark_chat/transcripts
mkdir -p ~/.agents/skills
mkdir -p ~/.uni-agent/bin
```

说明：

- `memory/`：长期记忆目录
- `transcripts/`：每个聊天的消息历史
- `skills/`：可选技能目录
- `~/.uni-agent/bin`：`local_native` 安装工具脚本的目录

---

## 11. 创建服务器专用配置文件

不要直接改仓库自带的参考配置，建议复制一份：

```bash
cd /opt/uni-agent
cp app/lark_chat/config.local_native.yaml app/lark_chat/config.server.local_native.yaml
```

编辑配置：

```bash
nano app/lark_chat/config.server.local_native.yaml
```

推荐配置如下：

```yaml
deployment:
  type: local_native
  startup_timeout: 60.0
  tool_install_dir: ~/.uni-agent/bin

memory_dir: ~/.uni-agent/app/lark_chat/memory

model:
  base_url: http://127.0.0.1:8000/v1
  name: Qwen/Qwen3.6-35B-A3B
  api_key: EMPTY
  sampling_params:
    temperature: 1.0
    top_p: 0.95
    presence_penalty: 1.5
    top_k: 20
    repetition_penalty: 1.0

tools:
  - execute_bash
  - lark-cli
  - str_replace_editor
  - finish

skills_dir: ~/.agents/skills
transcripts_dir: ~/.uni-agent/app/lark_chat/transcripts

agent:
  action_timeout: 60
  max_steps_per_turn: 20
  history_max_tokens: 128000
  history_target_tokens: 32000
```

需要重点检查的是：

- `deployment.type` 必须是 `local_native`
- `model.base_url` 必须指向你的本地模型服务
- `model.name` 必须和模型服务暴露出来的模型名一致
- `tool_install_dir` 必须是可写目录

如果你的模型服务需要鉴权，不想把密钥写进 YAML，可以用环境变量：

```bash
export API_KEY="your-real-api-key"
```

配置里 `model.api_key` 可以保留为 `EMPTY`，或者改成 `null`。

---

## 12. 启动前自检

正式启动前执行以下检查：

### 12.1 检查 bash

```bash
/usr/bin/env bash -lc 'echo bash_ok'
```

### 12.2 检查模型接口

```bash
curl http://127.0.0.1:8000/v1/models
```

### 12.3 检查 `lark-cli`

```bash
which lark-cli
lark-cli auth status
```

### 12.4 检查 Python 依赖

```bash
cd /opt/uni-agent
source .venv/bin/activate
python -c "import pexpect, bashlex, yaml; print('runtime deps ok')"
```

四项都成功再启动 Agent。

---

## 13. 启动 `local_native` Agent

前台启动方式：

```bash
cd /opt/uni-agent
source .venv/bin/activate
python -m app.lark_chat.main --config app/lark_chat/config.server.local_native.yaml
```

如果启动成功，你会看到类似阶段：

1. `Resolving bot open_id via Lark Open API...`
2. `Starting sandbox env...`
3. `Installing tools + skills...`
4. `Wiring model client...`
5. `Starting Lark event listener...`
6. `Entering chat loop...`

出现第 6 步后，就可以在 Lark / Feishu 里给 Bot 发消息了。

---

## 14. 推荐后台运行方式

### 方案 A：`tmux`

最实用，推荐优先使用。

创建会话：

```bash
tmux new -s lark-agent
```

在会话中运行：

```bash
cd /opt/uni-agent
source .venv/bin/activate
python -m app.lark_chat.main --config app/lark_chat/config.server.local_native.yaml
```

脱离会话：

```bash
Ctrl+b d
```

重新进入：

```bash
tmux attach -t lark-agent
```

查看现有会话：

```bash
tmux ls
```

### 方案 B：`nohup`

如果你不想用 `tmux`：

```bash
cd /opt/uni-agent
source .venv/bin/activate
nohup python -m app.lark_chat.main --config app/lark_chat/config.server.local_native.yaml \
  > /opt/uni-agent/lark_chat.out 2>&1 &
```

查看日志：

```bash
tail -f /opt/uni-agent/lark_chat.out
```

不建议优先用 `nohup`，因为排障体验不如 `tmux`。

---

## 15. 测试流程

建议按下面顺序联调：

1. 先只启动模型服务，确认 `/v1/models` 可访问
2. 再确认 `lark-cli auth status` 正常
3. 启动 `app.lark_chat.main`
4. 用你的 Lark / Feishu 账号给 Bot 发一条简单消息
5. 观察终端输出中是否出现 step / tool / exit 信息

测试消息可以先发：

```text
你好，回复一句“联调成功”
```

如果 Bot 能回这句话，说明整条链路已经通了。

---

## 16. 数据和状态文件位置

默认情况下，重要文件位于：

```text
~/.uni-agent/app/lark_chat/memory/
~/.uni-agent/app/lark_chat/transcripts/
~/.agents/skills/
~/.uni-agent/bin/
```

含义如下：

- `memory/`：模型维护的长期记忆
- `transcripts/`：按 `chat_id` 持久化的消息记录
- `skills/`：技能包目录
- `bin/`：工具安装目录

备份时，至少保留：

- `~/.uni-agent/app/lark_chat/memory/`
- `~/.uni-agent/app/lark_chat/transcripts/`

---

## 17. 常见问题

### 17.1 `lark-cli: command not found`

重新安装：

```bash
npm install -g @larksuite/cli
```

确认全局 npm bin 在 `PATH` 中：

```bash
which lark-cli
npm root -g
```

### 17.2 启动时卡在 `Resolving bot open_id`

优先检查：

```bash
lark-cli auth status
```

然后检查：

- 开发者后台应用是否可用
- Bot 是否启用
- 当前认证身份是否对应正确应用

### 17.3 启动时模型请求失败

先检查：

```bash
curl http://127.0.0.1:8000/v1/models
```

如果不通，先修复模型服务，不要先怀疑 Agent。

### 17.4 收不到消息

检查：

- `im.message.receive_v1` 是否已订阅
- 事件接收方式是否为 WebSocket / long-link
- 测试用户是否能真正给该 Bot 发消息

### 17.5 工具安装失败

检查 `tool_install_dir` 是否可写：

```bash
ls -ld ~/.uni-agent/bin
touch ~/.uni-agent/bin/.write_test
rm ~/.uni-agent/bin/.write_test
```

### 17.6 服务器重启后状态丢失

确认你没有把 `memory_dir` 和 `transcripts_dir` 指到临时目录。

推荐始终使用：

```text
~/.uni-agent/app/lark_chat/memory
~/.uni-agent/app/lark_chat/transcripts
```

---

## 18. 一份最短可执行清单

如果你已经具备：

- Linux 服务器
- 本地模型服务
- 可用的 Lark / Feishu Bot

那么最短命令流如下：

```bash
cd /opt/uni-agent

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip setuptools wheel
git submodule update --init --recursive
pip install --no-deps -e ./verl
pip install swe-rex loguru pydantic pydantic_settings aiohttp pexpect bashlex pyyaml tiktoken

npm install -g @larksuite/cli
lark-cli config init --new
lark-cli auth login
lark-cli auth status

mkdir -p ~/.uni-agent/app/lark_chat/memory/notes
mkdir -p ~/.uni-agent/app/lark_chat/transcripts
mkdir -p ~/.agents/skills
mkdir -p ~/.uni-agent/bin

cp app/lark_chat/config.local_native.yaml app/lark_chat/config.server.local_native.yaml
python -m app.lark_chat.main --config app/lark_chat/config.server.local_native.yaml
```

在启动最后一步之前，请先把配置文件中的 `model.base_url` 和 `model.name` 改成你自己的模型服务。

---

## 19. 建议的运维方式

生产或长期测试环境建议这样分离：

- `tmux` 会话 1：本地模型服务
- `tmux` 会话 2：`app.lark_chat.main`

这样排障最简单，也最容易分别重启。

如果后续你要做更稳定的托管，可以再把这两个进程拆成 `systemd` 服务，但第一次联调阶段不建议一开始就上 `systemd`。
