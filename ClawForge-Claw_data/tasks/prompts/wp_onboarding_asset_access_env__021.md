嗨，IT 运维的同学，

今天下午要入职一位新同事，但是 HR 那边跑完合同流程后，剩下最后的入职配置卡住了。他们给了我一份数据包，就在工作区里：

- `data/accounts.json` 里是所有员工的账号信息
- `data/contacts.json` 是组织通讯录
- `data/onboarding/contracts.json` 是已经跑完的合同，状态标记为 "signed" 的才需要走后续流程
- `data/onboarding/equipment_inventory.json` 是设备库存表
- `data/onboarding/permission_packs.json` 是权限包定义

我检查了一下，发现 `outputs/` 文件夹里有一些老员工的入职包，但新员工的还缺。我需要你帮我生成一个完整的入职汇总文件，放在 `outputs/onboarding_bundle.json` 里。

具体来说，这位新员工是合同中状态为 "signed" 但还没有对应入职包的那个。你需要从合同里找出她的信息，然后：

- 根据 `accounts.json` 里的账号信息，创建一个正式的邮箱档案（假设邮箱就是她合同里那个，显示名用账户里的 display_name，部门也用账户里的）。
- 根据合同里她所属的权限包编号，从 `permission_packs.json` 里拉出要分配给她的系统清单（每个系统一条记录，格式为 `{"system": "系统名", "permission": "权限"}`）。
- 从 `equipment_inventory.json` 里挑一台状态为 "available" 的笔记本设备分配给她（分配后把状态改成 "assigned" 并记录到她名下）。
- 最后写一条简短的 Slack 欢迎消息，频道写 `#general`，内容按公司传统写 `"欢迎 {她的名字} 加入 {部门}！"`。

所有信息汇总到 `outputs/onboarding_bundle.json`，结构你看着办，只要清晰可读就行。麻烦尽快处理，谢谢！
