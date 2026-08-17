**Subject:** Urgent: Q3 end-of-month reconciliation tasks  

Hey ops team,  

I've just pulled the latest snapshots into the `data/` directory – you'll find returns, shipments, inventory, and the physical count log from the floor. We have a handful of loose ends that need to be tied before close-of-business today.  

- **Return RET-001:** Customer called in, says the item arrived defective. I've already approved the refund on our side – please make sure it's marked approved in our local tracking and note the reason.  
- **Return RET-003:** Another customer claims we sent the wrong item and wants an exchange. Go inspect it, document that it's the wrong item and we're proceeding with an exchange.  
- **Shipment SHIP-005:** That FedEx package we shipped last week? Still showing "processing" in our records. Update its status to shipped and note the carrier.  
- **Inventory:** Warehouse wh_001 found 5 units of SKU-1002 damaged beyond repair. Write them off from stock – record the adjustment and the reason.  
- **Reconciliation:** Finally, I need an inventory reconciliation report. Use the physical count log under `data/inventory/physical_count.json` and compare it against our system inventory. Flag any discrepancies you find.  

Please compile all these resolutions into a single JSON file `ops/task_resolutions.json`. Use a `tasks` array where each entry has a `type` (e.g., "approve_return", "inspect_return", "update_shipment", "adjust_inventory", "reconciliation_report") and a `details` object with the relevant info. Keep it clean – I'll forward it straight to the auditors.  

Thanks,  
Boss
