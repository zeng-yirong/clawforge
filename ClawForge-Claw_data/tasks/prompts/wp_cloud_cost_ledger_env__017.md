Subject: Urgent – June cost spike on lakehouse-analytics  

Hey,  

I just got off a call with the finance team. Our June AWS bill hit $248K, and lakehouse-analytics alone jumped 60% vs. budget. Tara wants a breakdown by resource family by tomorrow.  

I dumped everything we have in `data/` – the resource ledger, cluster definitions, and the pricing catalogs from the last two months. Please figure out exactly what we’re paying for, per business cluster, using the June pricing catalog (the one that’s currently active).  

Drop the final report into `reports/monthly_cost_2026_06.json`. I need per-cluster totals plus a line-item breakdown per resource type – compute vs storage, vCPU vs GPU, block vs object – whatever the catalog covers.  

Don't include shared platform clusters; only business-facing workloads matter.  

One more thing – the resource ledger might have some stale or mis-tagged entries. Use your best judgment to ignore anything that doesn’t belong to a known business cluster.  

Thanks,  
Daniel Song  
Cloud FinOps Lead
