Hey Amy here from the warehouse floor. System’s gone haywire – I’ve dumped the latest snapshots into the workspace so you can sort out a few urgent actions.

Look at the returns files – some customers marked "defective", those should go straight to refund. Others said "wrong item", those need inspection then exchange. On the shipping side, there’s a FedEx shipment still stuck "in_transit" – please flip it to "shipped". Also, check the stock – SKU‑1002 at wh_001 had 5 units water‑damaged; we need to write those off as damage in the system.

Please compile everything into an action plan and save it as `ops/action_plan.json`. Use a JSON array of objects, each with `action` (e.g., `"approve_return"`), `target` (the ID, like `"ret_001"`), and `params` (any additional details such as `{"resolution": "refund_approved"}`). Thanks – I’ll run with it directly.
