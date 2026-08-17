Subject: Urgent: JFK → LHR flight booking for Friday's board meeting

Hi there,

Our Sales Director, Emily, needs to fly from JFK to LHR on June 15th, business class. Her budget is $2,200 all-in (including any platform fees). I've dumped all the raw flight data into `raw_flights/`, along with the latest platform specs in `data/platforms/` and our corporate travel policies in `data/policies/`. Also, there's a `current_date.txt` in the root so you know today's date.

We only use active platforms, and the policy we're on is the latest version (hint: the one with version "2.0" in `data/policies/`). Emily's account ID is `acme-001` – you'll find her company details in `data/accounts.json` if needed.

Please dig through the mess, apply the current policy, and pick the cheapest flight that ticks all the boxes. Once you've found it, write a short summary to `ops/booking_candidate.json` with the flight's ID, the platform, the total cost (base price + transaction fee + service fee), the policy version used, whether it meets policy, and whether it needs approval (since Emily's budget is tight, I want to know if we have to get an approval before booking).

No time for back-and-forth – just the JSON file, please.

Thanks,
Smith
Travel Desk
