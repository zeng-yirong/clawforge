Hey, this is Sarah from IT Operations. HR just pushed the latest offboarding list to `data/offboarding/exit_requests.json`. I need you to action the approved departures today.

The system access records live in `data/offboarding/system_access.json` and equipment assignments are in `data/offboarding/equipment_assignments.json`. For every employee whose approval_status is "approved", please:

- Revoke all their system access (set the status to "REVOKED").
- Reclaim all their assigned equipment (set the status to "RECLAIMED").

Once done, create a handover checklist at `handover_checklist.json` summarizing what was completed. The checklist should list each processed employee's ID, name, how many systems were revoked, how many equipment items were reclaimed, and a completion timestamp.

Ignore any requests that aren't approved, and don't touch any other files. Thanks for keeping the offboarding pipeline clean!
