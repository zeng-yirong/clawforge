Hey, this is urgent. We had a critical deadlock in **payment-service** around 03:12 this morning – fault ID `f-001`. The whole order pipeline froze for 2 minutes.

I've dumped what we have:
- The fault record with stack trace and call chain is in `data/faults/fault_cases.json`
- The slow query logs from that window are sitting in `logs/slow_queries.log`
- Also there's an error dump in `logs/` that you can ignore.

I've already eyeballed the stack – it's definitely a transaction blocking itself. I need you to dig through the logs, find the exact transaction ID of the deadlocked query (the one that belongs to payment-service), and write it into `ops/kill_target.json`. I need the file ready so the on-call engineer can copy the ID and kill it immediately.

Format: just a simple JSON object like `{"transaction_id": "the_id"}`. Nothing else. Only the one that actually caused the deadlock.

Thanks! Get it done fast.
