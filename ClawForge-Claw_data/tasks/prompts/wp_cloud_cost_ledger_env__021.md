Hey, it's Daniel from FinOps. Last month’s cost report was a nightmare – the CFO flagged duplicate clusters, wrong pricing, and even storage sneaking into the compute line. I need you to re-generate a clean monthly cost detail for **June 2026**.  

Only pull the **business clusters** – that's ads-ranking, lakehouse-analytics, and retail-core. Leave shared-ops out; it's shared platform and not part of our business cost allocation.  

Focus purely on **compute** resources: vCPU and memory (GiB). No storage, no GPU, nothing else.  

Use the **approved** pricing – you’ll find the live catalog tagged `2026.06-live`. Make sure you’re grabbing the one that’s marked as approved for reporting. The new accounting rules are in the attachments – give them a read; they changed the calculation method last week.  

Drop the final output into `report/cost_detail_202606.json`. I’ll pick it up from there. Make it accurate – I don’t want another Fire Drill with the CFO.  

Cheers,  
Daniel
