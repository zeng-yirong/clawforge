Hi team,

I just ran the morning health check and a bunch of sensors are stuck in `critical` status — but I know some of those have already been marked as resolved in our incident tracker. I'm swamped with other fires right now, so I need your help to sort this out.

You'll find everything you need in the workspace:

- `data/accounts.json` — lists all our accounts and their associated sensors  
- `data/sensors/sensors.json` — current sensor readings and statuses  
- `data/locations/locations.json` — where each sensor lives (probably not needed but here for reference)  
- `raw_logs/incidents.csv` — a log of incidents we've handled, with a status column showing whether an incident is `resolved` or `open`

What I need: a clean list of **sensors that are currently `critical` and have NOT been resolved** in the incident log. Please group them by the account they belong to. The result should go into `ops/active_critical.json` as a JSON object where each key is an account ID and the value is an array of sensor IDs that satisfy the condition.

For example (just a sketch, not the real answer):  
{
  "acme": ["SENSOR_X"],
  "beta": ["SENSOR_Y", "SENSOR_Z"]
}
Thanks — try to get this to me as soon as you can.
