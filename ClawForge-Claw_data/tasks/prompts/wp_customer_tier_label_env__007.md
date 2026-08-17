你好，我是市场部的 Sarah。我们目前的客户分层标签已经半年没更新了，很多高价值客户被当成普通客户对待，有些风险客户还在享受 VIP 待遇。运营团队刚刚制定了一套新的分层规则，我把它放在了 `ops/segmentation_rules.txt` 里，你按这个规则来。

最新的消费数据和活动数据在 `data/logs/` 目录下，请注意 `data/logs/` 里可能混有旧版或备份文件，请以 `consumption_logs.json` 和 `activity_logs.json` 为准。客户的档案在 `data/customers/customers.json`。

请根据规则为每个客户计算出新的分层标签（注意：是 **标签**，不是客户等级 `tier`），然后将 **需要更新标签** 的客户信息整理成一个文件 `ops/label_updates.json`。只要那些确实需要变更的客户，不需要更新的就不要写进去。辛苦了！
