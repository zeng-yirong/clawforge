早上好！新同事 Xiao Ming 明天就要入职了。合约我已经签好放在 `data/onboarding/contracts.json` 里，状态是 signed 的那个就是他。麻烦你帮我把剩下的入职流程跑一遍：

1. 给他创建公司邮箱（按照 firstname.lastname@acme.com 的格式）；
2. 根据他的部门，从 `data/onboarding/permission_packs.json` 里找到对应的权限包，把那些系统访问权限给他；
3. 再从 `data/onboarding/equipment_inventory.json` 里挑一台可用的笔记本分配给他；
4. 最后在 Slack 上发条欢迎消息，内容就写 “Welcome {姓名}! You have been granted access to {系统列表}.”

所有操作的结果汇总到一个文件里，方便以后审计。你就放在工作区 `ops/` 目录下，文件名就叫 `onboarding_summary.json`。内容把每一步的结果都记清楚——员工 ID、姓名、创建的邮箱、分配的权限、分配的设备、还有欢迎消息的内容。格式你自己定，但信息要完整，我一个字段都不能少。谢谢！
