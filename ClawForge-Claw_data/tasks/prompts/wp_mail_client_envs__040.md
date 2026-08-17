Hey AI, I'm back from vacation and my inbox is completely out of hand. My biggest client, Bob Vendor, sent a meeting confirmation for our project sync next Tuesday at 3pm. I need you to find that specific email among all the noise.

I dumped everything in the `data/emails/` folder – each email is a separate JSON file. Bob's email should be in there, but there are also spam, newsletters, and other clutter. Please read through them, pick the one that actually confirms the meeting, and extract:

- The exact meeting time  
- The meeting location  
- Any items I need to prepare  

Save these details into `ops/meeting_details.json` as a clean JSON object with three keys: `meeting_time`, `location`, and `preparation_items`. Make sure `preparation_items` is a list of strings.

Ignore everything else – I only care about the correct email from Bob. Thanks!
