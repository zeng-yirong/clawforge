Hey, quick one. A new flight booking landed in our `new_bookings/` folder this morning – someone submitted a business-class trip for next week. Before we can confirm, we need to double-check it against the current corporate travel policy. The policy files are in `data/policies/` – make sure you use the most up-to-date version. Also grab the company account info from `data/accounts.json`.

If the booking requires approval (you'll know when you read the policy), please generate an approval request file inside `ops/`. The file should contain the exact booking ID, the total cost (base + taxes + fees – just the number from the booking record), the relevant account ID, and who should approve it. I need the answer clean and ready – just the one file, no extra fluff.

Don't touch anything in `data/platforms/` – that's just for reference. Focus on the booking record and the policy. Let me know when it's done. Thanks!
