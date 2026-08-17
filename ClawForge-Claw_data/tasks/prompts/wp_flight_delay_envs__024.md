Subject: Urgent – Flight delay adjustments needed  

Hi there,  

We had a sync issue last night – **UA123** ended up delayed by 2 hours, but the hotel and transport teams never got the memo. I've pulled a snapshot of the current data into `data/`. You'll find flights, hotel bookings, and transport bookings in their respective JSON files.  

Could you please go through the data and figure out which bookings are actually affected?  
- Only consider bookings with `"status": "confirmed"`.  
- Only act on delays longer than 60 minutes (the short 10‑minute stuff can stay as is).  

For each affected booking, calculate the new time (original time + delay) and compile everything into a single JSON file at **`ops/adjustments.json`**.  
I need it structured with two keys: `transport_adjustments` and `hotel_adjustments`. Under each key, put an array of objects – each object must have `id` (the booking ID) and `new_time` (the adjusted datetime in ISO 8601 format).  

Keep it clean, no fluff. I'll send these directly to the ops team.  

Thanks,  
Jane
