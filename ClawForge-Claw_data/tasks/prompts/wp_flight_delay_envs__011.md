Subject: Urgent – Flight UA123 Delay Impact

Hi there,

We've got a ripple effect from UA123 (SFO → ORD) coming in late by 2 hours. I've dropped all the raw data in `data/` – flight details, hotel stays, transport pickups, and our contact list. There's also a standard notification template sitting in `data/templates/` we normally use for these situations.

I need you to figure out which existing bookings are tangled with this delayed flight (hint: they're linked by flight ID) and adjust them accordingly. For the hotel, shift the check-in and check-out by one day. For the transport, push the pickup time back by the exact delay. Then, using the template, craft the notifications for the affected traveler.

Please gather everything into the `ops/` folder: a summary of the changes (call it `adjustments.json`) and the list of notifications (`notifications.json`). Make sure the format is clean and unambiguous – we'll feed it straight into our downstream systems.

Thanks for handling this quickly!

Best,
The Travel Ops Crew
