Hey there,

We've got a bit of a crisis on our hands. Overnight batch processing went sideways and left our data in a messy state. I've dropped the latest snapshots into `data/` — you'll find the return records in `data/returns/returns.json`, shipment info in `data/shipments/shipments.json`, and inventory details in `data/inventory/inventory.json`. I need you to take care of a few things before the morning standup:

1. There's a return `ret_001` — customer says the item is defective. Go ahead and approve it, that's straightforward.
2. Another return `ret_003` — they got the wrong item. They want an exchange, so put it through inspection and note that it's a wrong item and that we're doing an exchange.
3. Shipment `ship_005` has been sitting at "processing" forever. Mark it as shipped — it's going out via FedEx today.
4. Inventory for SKU `SKU-1002` at warehouse `wh_001` had a damage incident during handling. We need to adjust it down by 5 units and tag it as a damage loss.
5. Once you've done all that, generate an inventory reconciliation report. Stick it in the `ops/` folder as `reconciliation_report.json`. The report should clearly show the reconciliation status and any discrepancies you spotted — I need something I can quickly glance at.

Make sure you update the original files directly where needed, and create the report as a new file. The whole thing should be self-contained in the workarea.

Thanks!
