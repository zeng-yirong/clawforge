Hey there,

I’m Alice from Engineering Hiring. We’re trying to fill a **Senior Data Engineer** position urgently, and I’ve dumped all the messy candidate data into `data/candidates/candidates.json`. The job specs are in `data/jobs/jobs.json` – look for the one that matches the title above.

I need you to:

- Go through the candidate records. Some folks submitted multiple times with different skill sets – I only care about the **latest version** of each candidate (the most recent `added_at`).
- Find the candidate whose skills exactly cover **Python**, **SQL**, and **Airflow** (no more, no less – just those three). If multiple candidates have the exact same skill set, pick the one with the earliest `added_at` so we prioritize early applicants.
- From `data/contacts.json`, grab the person whose role is **Hiring Manager** – that’ll be the interviewer.
- Set up the interview for **next Tuesday at 10:00 AM** (that’s 2025-03-25 10:00). Use room 401 as the location.
- Then create a reminder for me (my email is `alice@company.com`, you can find me in `data/accounts.json`) to fire **one hour before** the interview.

Save the results as:
- `ops/interviews.json` – the full interview record.
- `ops/reminders.json` – the reminder configuration.

I need these files ready before I head to the meeting in 20 minutes. Make sure you clean up any duplicates and only keep the valid candidate.

Cheers,
Alice
