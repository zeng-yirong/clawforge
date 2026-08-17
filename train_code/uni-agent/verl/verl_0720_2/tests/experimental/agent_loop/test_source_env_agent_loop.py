# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
from types import SimpleNamespace

from verl.experimental.agent_loop.source_env_agent_loop import AgentData, AgentState, SourceEnvAgentLoop


def _agent_data(*, user_plan=None, next_step_index=0):
    return AgentData(
        messages=[{"role": "assistant", "content": "previous assistant response"}],
        image_data=None,
        video_data=None,
        metrics={},
        request_id="request-id",
        runtime=SimpleNamespace(),
        env_names=[],
        init_env={},
        user_plan=user_plan or [],
        next_step_index=next_step_index,
        validation_protocol="",
        task_id="task-id",
    )


def test_source_env_agent_turn_limit_is_global_across_plan_steps():
    loop = object.__new__(SourceEnvAgentLoop)
    loop.max_agent_turns = 2
    loop.response_length = 32

    agent_data = _agent_data(
        user_plan=[{"user_content": "first step"}, {"user_content": "second step"}],
        next_step_index=1,
    )
    agent_data.agent_turns = 2

    async def append_messages(agent_data, add_messages, *, mask_value):
        agent_data.messages.extend(add_messages)
        return True

    loop._append_messages_to_prompt = append_messages

    assert asyncio.run(loop._append_next_user_step(agent_data))
    assert agent_data.agent_turns == 2
    assert agent_data.next_step_index == 2

    state = asyncio.run(loop._handle_generating_state(agent_data, {}))

    assert state is AgentState.TERMINATED
    assert agent_data.status == "max_agent_turns_reached"
    assert agent_data.final_response == "previous assistant response"


def test_source_env_finishes_the_current_tool_round_without_a_per_step_limit():
    loop = object.__new__(SourceEnvAgentLoop)
    agent_data = _agent_data()
    agent_data.agent_turns = 7
    agent_data.pending_tool_calls = ["env['demo'].inspect()"]

    def execute_tool_calls(agent_data, tool_calls):
        agent_data.execution_trace.extend(tool_calls)
        return "tool feedback"

    async def append_messages(agent_data, add_messages, *, mask_value):
        agent_data.messages.extend(add_messages)
        return True

    loop._execute_tool_calls = execute_tool_calls
    loop._append_messages_to_prompt = append_messages

    state = asyncio.run(loop._handle_processing_tools_state(agent_data))

    assert state is AgentState.GENERATING
    assert agent_data.agent_turns == 7
    assert agent_data.execution_trace == ["env['demo'].inspect()"]


