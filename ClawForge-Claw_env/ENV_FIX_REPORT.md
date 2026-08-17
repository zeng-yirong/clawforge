# claw_envs 环境修复报告

更新时间：2026-06-14

## 范围说明

本次按 `C:\work\uni-agent\claw_envs\claw_env_recipe.md` 对 `claw_envs` 下生成环境逐个检查，并修复了“明确不合格”的环境实现与并发测试。

`post_mails` 是参考环境，本次未做代码修改，只用于对照和最终验证。

## 已修复环境与修复点

### 1. `car_control_envs`

- 修复 `ac.py` 顶部 `from __future__ annotations` 语法错误，恢复 CLI 可运行性。
- 修复 `cli.py` 帮助输出，隐藏 trainer 专用命令与 `--session-id`。
- 修复 `repository.py` 的 `get_scenario()`，当文件名与 `scenario_id` 不一致时也能按 `scenario_id` 找到场景文件。

### 2. `car_navi_envs`

- 修复 `cli.py` 帮助输出，隐藏 `prepare-rollout`、`reset-rollout`、`evaluate` 和 `--session-id`。

### 3. `compete_track_envs`

- 在 `__init__.py` 中导出 `CompeteTrackEnvironment`，修复包级导入。
- 修复 `concurrency_test.py` 使用错误用户 ID `usr_001` 的问题，改为真实数据中的 `user_001`。
- 修复共享会话并发测试的动作计数期望，使其与环境真实“只记录写动作”的模型一致。
- 为 `store.py` 的原子写入改为唯一临时文件名，避免 Windows 下多进程写同一会话时冲突。
- 为 `store.py` 增加 `save_session_unlocked()`，并在 `environment.py` 的加锁写路径中使用，避免“已持锁时再次走无锁覆盖写”导致的竞争。

### 4. `excel_data_envs`

- 删除 `cli.py` 中重复注册的 `get-chart-details` 子命令。

### 5. `expense_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer/session plumbing。
- 修复 `concurrency_test.py` 中残留的未定义 `ExpenseRepository` 引用。
- 修复并发测试场景 ID，改为真实存在的 `expense_analysis_001`。

### 6. `finance_envs`

- 在 `__init__.py` 中导出 `FinanceEnvironment`。
- 修复 `concurrency_test.py` 的包导入。
- 修复并发测试对旧 API 的调用：
  - `screen_stocks(... analyst_rating=...)` 改为 `min_analyst_rating`
  - `create_earnings_summary` 改为传 `tickers`
  - `provide_recommendations` 改为传 `tickers`
  - `create_brief` 的 `investment_rationale`、`risks`、`key_metrics` 改为环境实际要求的数据结构
  - `submit_brief` 使用真实返回的 `brief_result["data"]["brief_id"]`
- 将共享会话竞争测试改为执行真实会写入状态的动作，而不是只读接口。
- 为 `store.py` 的原子写入改为唯一临时文件名，降低多进程写入冲突风险。

### 7. `flight_delay_envs`

- 在 `__init__.py` 中导出 `FlightDelayEnvironment`。
- 修复 `concurrency_test.py` 的包导入。
- 修复并发测试中错误的航班 ID `flight_001`，改为真实存在的 `flight_ua123`。
- 将共享会话竞争测试改为执行会写入状态的 `check_flight_status` / `update_flight_status`。
- 修复评分字段兼容，支持 `score` 回退。
- 为 `store.py` 的原子写入改为唯一临时文件名。

### 8. `itinerary_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer 命令与 `--session-id`。

### 9. `mail_client_envs`

- 修复 `repository.py` 附件路径拼接问题，避免 `attachments/attachments/...` 重复路径。

### 10. `music_player_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer/session plumbing。
- 修复 `concurrency_test.py` 的导入和仓储引用问题。

### 11. `scheduling_envs`

- 修复 `environment.py`、`tasks.py`、`concurrency_test.py` 的旧式导入路径。
- 为 `reset()` 生成更稳妥的唯一 session id，避免高并发下碰撞。
- 在 `store.py` 中增加 `save_session_unlocked()`，并在 `environment.py` 的持锁写路径中使用。
- 修复 `execute_action()` 的持锁读改写流程，确保共享会话竞争时状态更新串行化。
- 修复 `session_summary()`，补充 `total_actions`。
- 修复 `concurrency_test.py` 中缺失的 `device_type` 参数，避免读取动作被环境判为参数缺失。
- 为 `store.py` 的原子写入改为唯一临时文件名。

### 12. `secure_vault_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer/session plumbing。

### 13. `security_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer 命令与 `--session-id`。
- 修复 `cli.py`、`environment.py`、`concurrency_test.py` 的旧式导入路径。
- 将 `store.py` 替换为目录化 session store：
  - `<state_root>/<session_id>/session.json`
  - `<state_root>/<session_id>/.lock`
  - session id 校验
  - 原子写
- 去掉 `sessions_meta.json` 并发写入带来的竞争点，消除多进程 `PermissionError`。
- 修复 `environment.py` 的 metrics 统计逻辑，使不返回 `success` 字段但成功写入的领域函数也能正确累计 `doors_locked`、`emergency_calls_made` 等指标。
- 修复共享会话竞争测试的动作计数期望，使其与真实记录动作数一致。

### 14. `sensor_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer/session plumbing。
- 修复 `cli.py` 内部报告子命令重复注册问题。
- 修复 `cli.py`、`environment.py`、`concurrency_test.py` 的旧式导入路径。
- 为 `reset()` 生成更稳妥的唯一 session id，避免高并发下碰撞。
- 在 `store.py` 中增加 `save_session_unlocked()`，并在环境持锁写路径中使用。
- 修复共享竞争测试，使 worker 正确绑定到共享 session。
- 修复 `environment.py` 的动作计数逻辑：对于领域函数通过向 `actions` 追加记录来表示写入的情况，也会正确增加 `total_actions`。
- 修复 `session_summary()`，补充 `reports_generated`。
- 为 `store.py` 的原子写入改为唯一临时文件名。

### 15. `smart_home_envs`

- 在 `__init__.py` 中导出 `SmartHomeEnvironment`。
- 修复 `concurrency_test.py` 的包导入。
- 修复并发测试调用旧方法名：
  - `get_recommended_temperature` 改为 `calculate_recommended_temperature`
  - `check_cost_saving` 改为 `check_cost_saving_opportunity`
- 修复评分字段兼容，支持 `total_score` 回退。
- 修复共享会话动作计数期望，使其与环境“每次设备调整写两条动作记录”的真实模型一致。
- 为 `store.py` 的原子写入改为唯一临时文件名。

### 16. `travel_policy_envs`

- 修复 `cli.py` 帮助输出，隐藏 trainer/session plumbing。
- 将 `store.py` 替换为目录化 session store：
  - `<state_root>/<session_id>/session.json`
  - `<state_root>/<session_id>/.lock`
  - session id 校验
  - 原子写
  - `meta.base_time` / `meta.action_index`
- 修复 `environment.py` 的 `session_summary(session_id: str | None = None)` 和 `evaluate_session(session_id: str | None = None)`，适配外部并发测试调用方式。
- 修复 `concurrency_test.py` 对旧 API 的调用：
  - `compare_platform_prices` 不再传 `platform_id`
  - `validate_booking_against_policy` 使用 `estimated_cost`、`cabin_class`、`advance_booking_days`
  - `get_policy_approval_chain` 使用 `estimated_cost`
  - `initiate_approval_request` 传真实 `booking_details`、`approver_email`、`justification`
  - `create_booking` 使用真实签名 `platform_id/platform_name/flight_details/total_cost`
- 修复评分字段兼容，支持 `total_score` 回退。
- 为 `store.py` 增加 `record_action_unlocked()`，并让 `environment.py` 内的审批/预订变更动作在同一 session 锁中完成“状态变更 + action 记录”，消除多进程共享会话下的隐藏竞争。
- 为 `store.py` 的原子写入改为唯一临时文件名。

## 统一修复类别

本次修复主要集中在以下几类：

- agent CLI 暴露了 trainer 命令或 `--session-id`
- 并发测试仍调用旧 API / 错误数据 ID / 错误评分字段
- session store 不满足目录化、原子写、锁文件、session id 校验要求
- 持锁写路径仍调用非持锁保存函数，导致共享会话竞争时存在覆盖写风险
- Windows 下固定 `session.json.tmp` 临时文件名导致多进程 `PermissionError`

## 验证结果

### 1. 语法与编译

- 已对 `claw_envs/**/*.py` 全量执行 `py_compile`
- 结果：通过

### 2. CLI 帮助输出泄漏检查

已检查以下环境的 `--help` 输出：

- `car_control_envs`
- `car_navi_envs`
- `expense_envs`
- `itinerary_envs`
- `music_player_envs`
- `secure_vault_envs`
- `security_envs`
- `sensor_envs`
- `travel_policy_envs`

检查项：

- `prepare-rollout`
- `reset-rollout`
- `--session-id`
- `==SUPPRESS==`

结果：未发现泄漏。

### 3. 并发测试

以下环境已通过并发测试：

- `car_control_envs`
- `car_navi_envs`
- `compete_track_envs`
- `crm_envs`
- `excel_data_envs`
- `expense_envs`
- `finance_envs`
- `flight_delay_envs`
- `itinerary_envs`
- `logistics_envs`
- `mail_client_envs`
- `music_player_envs`
- `scheduling_envs`
- `secure_vault_envs`
- `security_envs`
- `sensor_envs`
- `smart_home_envs`
- `travel_policy_envs`

补充说明：

- `post_mails` 仅做参考验证，未修改，验证通过。

## 结论

本次检查中识别出的明确不合格环境已经完成修复，并通过了相应的编译、CLI 泄漏检查和并发验证。
