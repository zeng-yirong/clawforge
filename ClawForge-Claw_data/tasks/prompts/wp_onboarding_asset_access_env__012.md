Hey there,  

Alice Wang is starting in Engineering today and I'm already drowning in the messy onboarding data. I've dumped the contract database (`contracts.json`), the permission pack reference (`permission_packs.json`), and the equipment inventory (`equipment_inventory.json`) into the workspace.  

The contract file is a bit of a mess – there are old entries, cancelled ones, and even someone else with the same name. I need you to find the one active contract for Alice, figure out which department she's in, then look up the correct permission pack for that department. Also, from the inventory, grab an available laptop (asset type `laptop`) – there should be exactly one that's free.  

Please put together a single JSON file at `ops/onboarding_plan.json` with:  
- her name  
- her email  
- the list of systems she needs access to  
- the asset tag of that laptop  

I'll pass it straight to IT to run the actual provisioning. Need it asap – thanks!  

— HR
