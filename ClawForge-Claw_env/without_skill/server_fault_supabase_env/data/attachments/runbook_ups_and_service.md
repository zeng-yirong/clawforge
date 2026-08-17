# UPS and Service Outage Runbook

Target categories for this scenario:

- `ups_outage`
- `service_down`

Expected handling:

- For `ups_outage`: confirm upstream power recovery, verify UPS condition, and validate dependent services after power is restored.
- For `service_down`: verify host health, restart the affected service, and validate readiness or health checks before closure.

Do not process unrelated categories such as `network_degradation` or watchlist-only replica lag tickets as if they were target remediation tickets.
