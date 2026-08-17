Subject: [URGENT] Payment service crash – need postmortem ASAP

Hey,

Another meltdown in the payment service at 2 AM. I've already collected the relevant data – head to `data/faults/fault_cases.json` and find the critical one that's directly breaking payments. Its attachments live under `data/attachments/` and include the stack trace, call chain, and a repair note.

Please digest them and write a concise postmortem report into `ops/postmortem.json`. I need the fault ID, the root cause, the exact call chain, and the suggested fix – just the essentials so the on-call team can act fast. Don't overcomplicate it, make sure the report is clean and ready to be handed off.

Thanks,
Mia
