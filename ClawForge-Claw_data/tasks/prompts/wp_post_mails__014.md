嘿，我是产品发布经理Ray。我们明天就要正式上线 **Aurora X1** 了，但我发现几个月前的预热帖还挂在社交媒体上，要是用户看到旧内容会出大乱子。我把所有相关材料都塞到工作区了，你帮我清理一下。

邮件都在 `data/emails/` 里，其中有一封是最终批准的发布简报——它被标记为 `approved`，重要性是 `high`。那封邮件带有一个JSON附件（放在 `data/attachments/` 下），里面包含了产品的 `product_id` 和正式上线日期 `launch_date`。

拿到这两个值后，去翻 `data/social/` 下的所有帖子。我需要你把那些 **帖子ID包含这个 `product_id`**，并且 **发布时间早于 `launch_date`** 的帖子全部揪出来。把它们的 `post_id` 列成一个数组，写到 `ops/pre_launch_posts.json` 里，格式就只是一个数组，比如 `["post_001", "post_002"]`。

只做这一件事，别多掺和。我等着你的结果去删帖。
