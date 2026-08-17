Hey team,

I just finished running two back-to-back experiments – `exp_v1` and `exp_v2`.  
I dumped the raw results into `data/experiments/experiment_results.csv`, but it's a bit of a mess:  
there are rows from older batches, some duplicates, and a few incomplete entries.  

Could you please clean that up and produce a **diff record** for me?  
I want to see, for each experimental group that exists in **both** batches, how the three core metrics changed:  
accuracy, latency (ms), and cost (USD).  

Put the result in `ops/experiment_diff.json` – I'll use it in the review meeting later.  

Thanks,  
Alice
