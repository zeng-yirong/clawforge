Hi team,

We just wrapped up the second experiment batch (batch_002) and need to compare it against the baseline (batch_001). I've dumped the raw results into `data/experiments/experiment_results.csv` — there are some stray batches and a few messy rows in there, so you'll need to clean it up.

For each group (A, B, C) I need the delta of three metrics: accuracy, latency (in milliseconds), and cost (in USD). Just the difference between batch_002 and batch_001. Please put the final comparison report in `ops/diff_record.json`. Ignore everything else.

Thanks!
