Hey team, Alice here — I need to schedule a business trip from JFK to LHR on June 15, 2026. Business class, just me.  

The latest company travel policy is in the `policies/` directory — use the most recent version, and note that the policy has a strict vendor preference: only vendors explicitly listed in the policy's `preferred_vendors` are acceptable for booking.  

My account details are in `accounts.json` — budget and approvers are there.  

All available flight platforms are stored in `platforms/`. Each platform file contains its flights. Compare them, but only consider platforms with `is_active: true` and flights that match the route, date, and cabin class.  

I need the **cheapest** flight that meets the policy rules. If the price exceeds the policy's `requires_approval_above` threshold, flag it for approval — include that flag in the final output.  

Save the booking request as `ops/booking_request.json`. The file should clearly show the chosen flight ID, the platform, the price, and whether approval is needed.  

Thanks!
