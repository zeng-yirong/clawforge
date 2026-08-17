嘿，刚处理完一个线上死锁故障，手忙脚乱的。故障编号是 F037，服务调用链卡住了，堆栈里全是 `LockAcquisitionException`。我把当时现场抓的日志丢在 `attachments/` 下了，你翻翻看，然后帮我把事后分析归档到 `ops/` 下。格式嘛，就按我们团队一贯的 JSON 来：故障 ID、根因、涉及的表、关键事务 ID、怎么修的。别漏了关键细节，尤其是那个惹事的事务 ID —— 得从日志里扒出来。我等着归档入库。

操作时注意 `data/faults/fault_cases.json` 里有案例清单，附件索引在 `data/attachments.json`。其他目录里的东西可能是旧版本，别搞混。
