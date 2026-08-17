Subject: Urgent: Automated Interview Scheduling Needed

Hi there,

Our recruitment pace is ramping up, and manually matching candidates to open positions is taking forever. I've prepared the latest hiring requirements in **data/jobs/jobs.json** and the updated candidate profiles in **data/candidates/current_candidates.json**. Please take a look and generate the interview invitations for all suitable matches—any candidate whose skill set fully covers the job's required skills should be scheduled.

To keep things consistent, please set the interview date to `2025-03-24` for all matches. Save the resulting schedule as **ops/interview_schedule.json**, with one entry per match including the `candidate_id`, `job_id`, and `interview_date`.

There's some old data lying around in `data/archive/`, but don't use that—only the current files matter.

Let me know if anything's missing.

Thanks,
Sarah
