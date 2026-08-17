Subject: Urgent Interview Scheduling – Senior Data Engineer

Hi Agent,

I’m the recruiting lead, and we’re in a crunch. The hiring manager for the **Senior Data Engineer** position just told me we need to finalize interviews by end of day. We’ve got candidate profiles and job postings sitting in `data/`. Could you please review the candidates and the open job we’re focusing on (title says "Senior Data Engineer"), then prepare a clean interview schedule?

Here’s what I need:

- Look through the candidates in `data/candidates/candidates.json`. Each candidate has skills listed.
- Check the job description in `data/jobs/jobs.json` for the Senior Data Engineer role – it lists the required skills.
- Only schedule interviews for candidates whose skills **completely cover** the required skills for that job. No partial matches, we need the full set.
- Arrange interviews on the **next two working days** from today (assume today is Monday 2025-03-10). Each interview slot is 30 minutes (no breaks needed). Start the first interview at 09:00 on the first day, and continue back-to-back. If all fit on day one, leave day two empty.
- Save the schedule as `ops/interviews.json`. The file should be a JSON array of objects, each object containing:
  - `candidate_id`
  - `job_id`
  - `interview_date` (YYYY-MM-DD)
  - `interview_time` (HH:MM, 24h format)

Please make sure there are no duplicates, no irrelevant candidates, and no extra fields. Just what I asked for.

Thanks! Deadline is tight.

– Recruiting Ops
