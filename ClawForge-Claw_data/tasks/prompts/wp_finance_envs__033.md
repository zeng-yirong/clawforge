嘿，我是 Sarah Chen，分析组的。刚才从数据库拉了下 Q2 的财报快照，放在 `data/earnings/earnings.json` 里。我正赶一份给投资委员会的绩效摘要，需要你搭把手。

帮我筛一下：哪些标的的 Q2 财报里，**营收和每股收益都超预期（revenue_beat 和 eps_beat 都是 true）**？按营收超预期的幅度（revenue_beat_pct）从高到低排个序，把前五个最亮眼的挑出来，记到 `ops/top_performers.json` 里。格式是 JSON 数组，每个元素就两个字段：`ticker` 和 `revenue_beat_pct`。别搞混了，我只要 Q2 的数据，旧的、没超预期的统统跳过。

拜托了，今晚之前我要把这份表发出去。
