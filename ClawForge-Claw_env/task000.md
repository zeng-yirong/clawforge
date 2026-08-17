我是市场部的急活儿！刚准备发 NovaOS 2.0 的官方公告，结果收件箱炸了——全是营销垃圾、旧版本会议记录、还有几封自称“审批通过”的邮件。我分不清哪个才是真的最新批准版。

你听好：
- 去 `data/emails/` 里翻，标签带 “approved” 且重要性标 “high” 的，挑时间最新的那封。那里面写着我们 boss 最后敲定的启动消息和几条核心事实（launch_message 和 key_facts）。
- 拿到后，立刻在 `data/social/` 里找需要回复的帖子（`needs_response: true`），但小心！有些帖子标签里带着 “spam”，那些别理，boss 说了直接忽略。
- 用那个最新brief里的内容干活：  
  1. 在 Reddit 和 X 上各发一篇官方启动帖，内容就用 brief 里的 launch_message。  
  2. 对每条需要回复的帖子，用 brief 里 boss 亲笔写的回复（approved_replies 里对应 post_id 的那句）去回复。  
- 所有成果扔到 `ops/` 目录下：  
  - `launch_posts.json`：里面要有 reddit 和 x 两个对象，每个对象至少带 `platform` 和 `content` 字段。  
  - `response_draft.json`：一个数组，每个元素包含 `post_id` 和 `reply_content`。  

我只认那封最新的 approved 邮件，别的别碰。搞快点，今晚就要上线！
