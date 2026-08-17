嘿，刚跑完两轮实验，手头有点急事。昨晚我手滑把 `data/experiments/` 里那个 `experiment_results.csv` 直接覆盖了旧数据，现在得赶紧把 `batch_A` 和 `batch_B` 这两批次的指标差异整理出来，一会儿汇报用。  

CSV 里混了不少乱七八糟的旧记录，还有些带 `#` 的注释行，你帮我筛干净，只对比这两个批次就行。每个组（group_id）在每批里只出现一次，直接算差值就好——把 `accuracy`、`latency_ms`、`cost_usd` 的变化量算出来，按 group_id 排好序，扔到 `ops/diff_record.json` 里。  

格式我随便写个例子：  
- 根对象里标记是哪两个批次对比。  
- 每个组一条记录，字段名清楚点，比如 `accuracy_diff` 之类的。  
- 数值保留原始精度，别四舍五入。  

搞快点，十分钟后要。
