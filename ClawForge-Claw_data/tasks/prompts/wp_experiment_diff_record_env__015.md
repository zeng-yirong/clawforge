产品经理小张一大早就跑过来拍桌子：

“昨晚灰度上线的实验批次 batch_002，用户反馈说响应速度比 batch_001 那版慢了不少，但 accuracy 好像反而不及格？我让工程把两次实验的原始数据都 dump 出来了，就放在 `data/experiments/experiment_results.csv` 里。你帮我倒腾一下，把两个 batch 的每个分组在 accuracy、latency（毫秒）、cost（美元）上的变化值都算清楚，写成一个简明的差异记录，塞到 `ops/diff_record.json` 里。要准，别丢分组，也别塞无关批次进来。中午开会要用，赶紧的！”
