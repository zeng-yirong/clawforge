嘿，AI，帮我把销售部的邮箱整理一下。我昨天手动读了一些邮件，标了标签，但没来得及处理后续。现在积压的邮件都在 `emails/` 目录下，每个邮件是个 JSON 文件，参考 `accounts.json` 和 `contacts.json` 里的信息来做判断。

我的习惯是：
- 所有已读的 newsletter 和 spam 直接归档，留着占地方。
- 客户 Alice 发来的邮件还没回过的（也就是 hasn_read 是 false 的那些），帮我写个简洁的回复草稿，语气客气点，就说“收到，我们会尽快处理，谢谢”。
- 另外，Sarah 发来的邮件，如果标题或正文里带 “urgent” 或 “bug” 字样的，给她记个 TODO 项，描述具体是什么事。

处理完把结果放到 `ops/` 目录下：
- `ops/archive.json`：列出所有需要归档的邮件 ID，用 JSON 数组。
- `ops/replies.json`：一个对象，key 是邮件 ID，value 是回复内容（纯文本）。
- `ops/todos.json`：一个数组，每个 TODO 要包含邮件 ID 和简短描述。

我下班前要检查，别弄错了。
