嗨，运维小能手！

新员工 Alex Johnson 今天入职 Engineering 部门，合同（`data/onboarding/contracts.json`）已经签好了。但别高兴太早——我这边一堆现成的权限包（`data/onboarding/permission_packs.json`）和设备库存（`data/onboarding/equipment_inventory.json`）需要你帮忙配上。

具体来说，我需要你：

*   **创建公司邮箱**：公司邮箱统一用 `名字.姓氏@company.com`，比如 Alex 的就是 `alex.johnson@company.com`。把邮箱配置整理成一个 JSON 文件放到 `output/email_profile.json`，里面至少包含 `email`、`display_name`、`department` 这几个字段。
*   **分配系统访问权限**：合同里已经注明了该用什么权限包（`permission_pack_id`），你从权限包清单里把对应的系统列表拿出来，给 Alex 配上。把分配结果写到 `output/system_access.json`，至少包括 `employee_id`、`pack_id` 和 `systems`。
*   **分配设备**：Alex 需要一台笔记本电脑（`asset_type` 为 `laptop`），库存里找一台状态为 `available` 的，分配给 Alex。分配信息记到 `output/equipment_allocation.json`，至少包括 `asset_tag`、`asset_type` 和 `assigned_to`。
*   **发送欢迎消息**：辛苦再写一条欢迎消息，存到 `output/welcome_message.json`，内容至少要有 `recipient`（员工邮箱）和 `message`（一段欢迎语，提一下他的名字和部门）。

这些都是新人入职的标准操作，别出岔子哦。搞定了告诉我一声，我这边流程就走下一步了。
