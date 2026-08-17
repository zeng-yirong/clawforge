Hey, this is Tina from HR. We’ve got a mess on our hands – the candidate database is a dumpster fire. I pulled the latest dumps into `data/` but there's old backups in `data/backup/` and some entries have garbage skill lists (empty strings, nulls). I need you to do cleanup and match our open positions against the valid candidates.

Here are the open jobs (in `data/jobs/jobs.json`) and the candidates (`data/candidates/candidates.json`). For each job, find the candidate whose skills best match the required skills – I want whichever has the most overlapping skills. If there’s a tie, pick the one with the smallest candidate ID. Skip any candidate whose skills list is junk (empty or contains only whitespace/null). Also skip jobs that can’t find any qualified candidate.

Once you have the matches, schedule an interview for each one. Use a single consistent interviewer – I’ll be using `Dr. Smith` from Engineering. Set the first interview at `2025-06-01T10:00:00Z` and space them one hour apart. All interviews are in `Room 101`, status `confirmed`. Then create a separate reminder for each interview, firing 15 minutes before the interview time.

Put the finished schedule and reminders into `ops/`. Name the schedule file `scheduled_interviews.json` and the reminders file `reminders.json`. I need them clean, no extra fluff – just the records.

Make sure you don’t accidentally include the dirty candidates or the old backup data. I trust you to get it right. Let me know if you have questions.
