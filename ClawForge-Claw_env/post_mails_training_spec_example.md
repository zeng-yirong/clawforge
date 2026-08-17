# post_mails 训练数据说明示例

## 结论

需要。

如果你要给 `claw_envs` 生成训练数据，那么每个环境最好也补齐与普通 agentic 环境相同层级的 3 类信息：

1. `env_des`：环境描述
2. `state_des`：初始状态描述
3. `tools`：环境内 agent 可调用函数说明

但是 `claw_envs` 不能完全照搬普通环境的写法，核心差异有两点：

1. `claw_envs` 通常是 trainer 持有 session，agent 侧不应该显式暴露 `session_id` 参数。
2. 训练数据里应该只描述 agent 真正可见、可调用的工具，不要把 trainer-only 或 hidden rollout 命令混进去。

对 `post_mails` 来说，适合暴露给训练数据的内容就是：

- 环境目标与业务背景
- 会话初始状态的精确结构
- 邮件与社交平台上的只读/写入型工具

不建议直接暴露给 agent 的内容包括：

- `prepare-rollout`
- `reset-rollout`
- trainer 侧评测入口

---

## post_mails 示例

下面给出一个与普通 agentic 环境风格一致、但适配 `claw_envs` 的 `post_mails` 说明模板。

```python
{
    "env_des": "This is the communications environment, named 'post_mails'. It simulates an internal launch-communications workflow where the agent must inspect a noisy company inbox, read approved launch materials, publish official messages to social platforms, and reply to selected public discussions using only approved facts.",
    "state_des": "Based on the instructions below, synthesize a complex and realistic initial state for the Post Mails environment.\n\n1. Goals and Format Requirements\nGoal: Synthesize a state dictionary representing the initial running state of one isolated post_mails session.\n\nImportant Session Constraint: In the real claw environment, the trainer owns the session lifecycle. The agent does not need to provide session_id as a tool argument, but the synthesized state must still contain the internally tracked session_id field.\n\nRequired Root Keys: The state dictionary must include all of the following keys, and their formats and types must strictly adhere to the definitions:\n\n\"session_id\": str (Unique identifier of the current environment session)\n\n\"scenario_id\": str (Identifier of the loaded scenario)\n\n\"created_at\": str (ISO-8601 timestamp of when the session was created)\n\n\"meta\": dict (Session metadata)\n- \"base_time\": str (ISO-8601 base timestamp used for deterministic event timing)\n- \"action_index\": int (Monotonic counter for action ordering)\n\n\"workspace_account\": dict (The official company account the agent is operating for)\n- Recommended fields: \"account_id\": str, \"name\": str, \"email\": str, \"team\": str, \"x_handle\": str or None, \"reddit_handle\": str or None\n\n\"mail\": dict (Mailbox state)\n- \"emails\": list[dict] (List of hydrated email records)\n\nEmail Dictionary Structure: Each email dictionary in \"mail\"[\"emails\"] should contain realistic fields consistent with the environment data model. Recommended required fields are:\n- \"email_id\": str\n- \"subject\": str\n- \"folder\": str\n- \"body\": str\n- \"sender\": dict with keys: \"contact_id\", \"name\", \"email\", \"role\", \"team\"\n- \"to\": list[str]\n- \"cc\": list[str]\n- \"received_at\": str\n- \"read\": bool\n- \"opened_at\": str or None\n- \"attachments\": list[dict]\n\nAttachment Dictionary Structure: Each attachment dictionary should contain:\n- \"attachment_id\": str\n- \"filename\": str\n- \"content\": str\n- \"read\": bool\n- \"read_at\": str or None\n\n\"social\": dict (Public platform state)\n- \"seed_posts\": list[dict] (Pre-existing public posts and threads the agent may review)\n- \"agent_posts\": list[dict] (Posts published by the agent during the session)\n- \"agent_replies\": list[dict] (Replies published by the agent during the session)\n\nSocial Post Dictionary Structure: Each seed or agent-authored post should contain realistic fields such as:\n- \"post_id\": str\n- \"platform\": str (For example: \"x\" or \"reddit\")\n- \"author\": str\n- \"author_handle\": str or None\n- \"content\": str\n- \"title\": str or None\n- \"community\": str or None\n- \"created_at\": str\n- \"needs_response\": bool\n- \"created_by_agent\": bool\n\nReply Dictionary Structure: Each reply dictionary should contain realistic fields such as:\n- \"reply_id\": str\n- \"post_id\": str\n- \"platform\": str\n- \"author\": str\n- \"content\": str\n- \"created_at\": str\n- \"created_by_agent\": bool\n\n\"actions\": list[dict] (Deterministic action log for the session)\n- Each action record should contain realistic fields such as: \"action_id\": str, \"type\": str, \"target_id\": str or None, \"created_at\": str, \"payload\": dict\n\nInitialization Guidance:\n- For a typical initial state, \"agent_posts\", \"agent_replies\", and \"actions\" should start empty.\n- Most emails should start unread unless the scenario explicitly requires otherwise.\n- Most attachments should start unread unless the scenario explicitly requires otherwise.\n- The mailbox and public social posts should contain enough noise, ambiguity, and cross-references to require multi-step reasoning.\n- Facts that are safe to publish should be derivable from approved emails and attachments, while unapproved rumors may appear in social posts.\n\nOutput Format Requirement (The LLM must provide the result in a Python/JSON compatible format):\n\n```python\n{\n    \"session_id\": \"session_orbital_launch_001\",\n    \"scenario_id\": \"orbital_launch\",\n    \"created_at\": \"2026-06-15T09:00:00Z\",\n    \"meta\": {\n        \"base_time\": \"2026-06-15T09:00:00Z\",\n        \"action_index\": 0,\n    },\n    \"workspace_account\": {},\n    \"mail\": {\n        \"emails\": [],\n    },\n    \"social\": {\n        \"seed_posts\": [],\n        \"agent_posts\": [],\n        \"agent_replies\": [],\n    },\n    \"actions\": [],\n}\n```",
    "tools": [
        {
            "name": "list_scenarios",
            "description": "List the available training scenarios in the post_mails environment. This is optional for agent use if the scenario is already pre-bound by the trainer.",
            "parameters": {
                "type": "dict",
                "properties": {},
                "required": []
            },
            "response": {
                "type": "dict",
                "properties": {
                    "scenarios": {
                        "type": "array",
                        "description": "List of available scenario summaries."
                    }
                }
            }
        },
        {
            "name": "get_task",
            "description": "Get the current task brief for the active post_mails session, including the scenario prompt and workspace account context.",
            "parameters": {
                "type": "dict",
                "properties": {},
                "required": []
            },
            "response": {
                "type": "dict",
                "properties": {
                    "scenario_id": {
                        "type": "string",
                        "description": "Identifier of the active scenario."
                    },
                    "title": {
                        "type": "string",
                        "description": "Short title of the scenario task."
                    },
                    "task_prompt": {
                        "type": "string",
                        "description": "Detailed task instructions for the agent."
                    },
                    "workspace_account": {
                        "type": "dict",
                        "description": "Official company account context used by the agent."
                    },
                    "unread_email_count": {
                        "type": "integer",
                        "description": "Current number of unread emails."
                    }
                }
            }
        },
        {
            "name": "list_emails",
            "description": "List emails in the mailbox, optionally filtering by query, unread status, folder, or count limit.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Free-text query applied to email content and metadata.",
                        "default": ""
                    },
                    "unread_only": {
                        "type": "boolean",
                        "description": "Whether to return only unread emails.",
                        "default": false
                    },
                    "folder": {
                        "type": "string",
                        "description": "Optional folder filter such as inbox or sent."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional maximum number of emails to return."
                    }
                },
                "required": []
            },
            "response": {
                "type": "dict",
                "properties": {
                    "emails": {
                        "type": "array",
                        "description": "List of email summary dictionaries."
                    }
                }
            }
        },
        {
            "name": "read_email",
            "description": "Open a specific email, returning its full content and marking it as read in the session state.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Identifier of the email to open."
                    }
                },
                "required": [
                    "email_id"
                ]
            },
            "response": {
                "type": "dict",
                "properties": {
                    "email": {
                        "type": "dict",
                        "description": "Full hydrated email record, including sender and attachments."
                    }
                }
            }
        },
        {
            "name": "read_attachment",
            "description": "Open a specific attachment, returning its content and marking it as read in the session state.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "attachment_id": {
                        "type": "string",
                        "description": "Identifier of the attachment to open."
                    }
                },
                "required": [
                    "attachment_id"
                ]
            },
            "response": {
                "type": "dict",
                "properties": {
                    "attachment": {
                        "type": "dict",
                        "description": "Attachment metadata and full text content."
                    }
                }
            }
        },
        {
            "name": "list_posts",
            "description": "List public social posts visible to the agent, optionally filtered by query, platform, response need, or result limit.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Free-text query for social posts.",
                        "default": ""
                    },
                    "platform": {
                        "type": "string",
                        "description": "Optional platform filter such as x or reddit."
                    },
                    "needs_response_only": {
                        "type": "boolean",
                        "description": "Whether to return only posts that need an official reply.",
                        "default": false
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional maximum number of posts to return."
                    }
                },
                "required": []
            },
            "response": {
                "type": "dict",
                "properties": {
                    "posts": {
                        "type": "array",
                        "description": "List of public post summary dictionaries."
                    }
                }
            }
        },
        {
            "name": "view_post",
            "description": "View the full details of a public post or thread before deciding whether to respond.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Identifier of the post to inspect."
                    }
                },
                "required": [
                    "post_id"
                ]
            },
            "response": {
                "type": "dict",
                "properties": {
                    "post": {
                        "type": "dict",
                        "description": "Full post or thread detail."
                    }
                }
            }
        },
        {
            "name": "publish_post",
            "description": "Publish an official company post to a supported social platform using approved information only.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "platform": {
                        "type": "string",
                        "description": "Target platform, such as x or reddit."
                    },
                    "content": {
                        "type": "string",
                        "description": "Main text content of the post."
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title, typically used for reddit posts."
                    },
                    "community": {
                        "type": "string",
                        "description": "Optional community or subreddit target."
                    },
                    "author": {
                        "type": "string",
                        "description": "Optional override author display name."
                    }
                },
                "required": [
                    "platform",
                    "content"
                ]
            },
            "response": {
                "type": "dict",
                "properties": {
                    "post": {
                        "type": "dict",
                        "description": "Created post record that is appended to the session state."
                    }
                }
            }
        },
        {
            "name": "reply_to_post",
            "description": "Reply to a specific public post using only approved and scenario-consistent facts.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Identifier of the target post."
                    },
                    "content": {
                        "type": "string",
                        "description": "Reply content to publish."
                    },
                    "author": {
                        "type": "string",
                        "description": "Optional override author display name."
                    }
                },
                "required": [
                    "post_id",
                    "content"
                ]
            },
            "response": {
                "type": "dict",
                "properties": {
                    "reply": {
                        "type": "dict",
                        "description": "Created reply record that is appended to the session state."
                    }
                }
            }
        },
        {
            "name": "session_summary",
            "description": "Return a compact summary of the current session progress, including unread mail and posting activity.",
            "parameters": {
                "type": "dict",
                "properties": {},
                "required": []
            },
            "response": {
                "type": "dict",
                "properties": {
                    "unread_email_count": {
                        "type": "integer",
                        "description": "Number of unread emails remaining."
                    },
                    "attachments_read": {
                        "type": "integer",
                        "description": "Number of attachments already opened."
                    },
                    "agent_post_count": {
                        "type": "integer",
                        "description": "Number of agent-authored posts."
                    },
                    "agent_reply_count": {
                        "type": "integer",
                        "description": "Number of agent-authored replies."
                    },
                    "action_count": {
                        "type": "integer",
                        "description": "Number of actions recorded in the session log."
                    }
                }
            }
        }
    ]
}
```

---

## 建议你后续统一补充的字段规范

如果你准备给 `claw_envs` 批量生成训练数据，建议每个环境都统一按下面的思路组织：

1. `env_des`
   明确环境是什么、业务目标是什么、agent 在里面扮演什么角色。

2. `state_des`
   不只写“有什么字段”，还要写：
   - 必须包含哪些根键
   - 每个键的类型
   - 嵌套对象结构
   - 初始状态下哪些字段通常为空
   - 哪些字段会被工具调用修改

3. `tools`
   每个工具都写清楚：
   - `name`
   - `description`
   - `parameters`
   - `response`

4. agent 可见边界
   对 `claw_envs` 特别重要。训练数据里最好只保留 agent 真正能操作的接口，不要把 trainer 内部命令、评测入口、session 管理细节直接暴露进去。

---

## 对 post_mails 的一句话结论

`post_mails` 需要与普通 agentic 环境同类的训练描述信息，但要额外强调它是 trainer-owned session 模型，因此：

- 状态里保留 `session_id`
- 工具参数里通常不要让 agent 显式传 `session_id`
- 只描述 agent-facing 的读邮件、读附件、看帖子、发帖、回帖、查看摘要等能力

