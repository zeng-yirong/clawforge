Hey team,

Mira here. We're smack in the middle of the Q2 pricing review for LuminaSkin, and I need a clean snapshot fast. I've dumped the latest price books into `ops/pricing/` – you'll find the live version marked as current. The product SKU master lives in `data/skus/`. 

Could you pull together a list of every LuminaSkin SKU that has a live price in the current book? I need each entry to show the SKU ID, its display name, and the unit price. Sort them by unit price descending – highest first, lowest last. Drop the result as a JSON array in `ops/lumina_pricing_snapshot.json`.

That's it. I'll grab it from there. Thanks!

Mira Tan
Pricing Operations Lead
