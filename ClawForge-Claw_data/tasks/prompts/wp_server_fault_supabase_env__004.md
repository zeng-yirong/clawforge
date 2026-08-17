> **From:** DBA On‑Call (Harper Zhou)  
> **To:** SRE Bot  
> **Subject:** Edge‑Cluster A12 —— 长事务锁死

兄弟，edge‑cluster‑a12 的 PG 又卡死了，所有写操作全堵在行锁上。  
我把它的 PostgreSQL 日志拖下来了，就在 `logs/postgresql.log` 里。你帮我翻翻，找那个跑了快一个钟头的长事务，它屁股底下压着一堆行锁不撒手。  

把这个事务 ID 给我抠出来，写到 `ops/kill_target.json`，格式就 `{"transaction_id": "..."}`，我拿到就直接 `pg_terminate_backend`。  

⚠️ 注意：`logs/archive/` 下的是旧日志，别管它们。我只要当前最新的那个文件里的结果。谢了！
