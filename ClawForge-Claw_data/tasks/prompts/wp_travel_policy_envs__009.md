Hi there,

Our quarterly sales team trip is coming up, and I’m drowning in spreadsheets. I pulled all the flight offers from our three booking platforms into `raw_data/flight_offers.csv`, but it’s a mess – some rows are garbled, some are duplicates, and some don’t even match our corporate travel policy. 

I also saved the latest policy snapshot as `raw_data/policy.json` and our account info in `raw_data/account.json`. The rules say we can only book economy or premium economy cabins, and the total cost per booking must not exceed the policy’s `max_cost_per_booking`. Also, we have a travel budget but I’ll handle that part – just focus on the flight itself.

Could you go through the offers, clean out any invalid entries (wrong cabin class, missing required fields, duplicate records), then apply the policy filter, and finally pick the **single cheapest eligible flight**? 

Please put your answer in a file called `outputs/best_booking.json` with the following fields:
- flight_id: string
- platform: string
- cabin_class: string
- price: number (as a plain number, not string)

I need it as soon as possible so I can submit the approval request. Thanks a lot!

Best,
Jamie
