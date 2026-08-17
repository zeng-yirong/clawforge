**发件人：** Alina Bose (Category Director)  
**收件人：** 产品分析助手  
**主题：** 紧急！LuminaSkin 新定价已生效，立刻出竞争报告

Hi 团队，

APAC Q2 的定价刚刚更新了，我手头有最新的价格本和 SKU 快照，全扔在 `data/pricing/` 和 `data/skus/` 里了。但历史遗留问题一堆——上一轮同事留了不少脏数据，两个版本的价格本混在一起，SKU 表里还有重复的 discontinued 记录。我需要你只盯着 **LuminaSkin** 这个品牌，用 **最新的有效价格本**（注意是 `is_current: true` 的那个），找出所有 **状态为 active** 的 SKU，把每个 SKU 的名称、当前价格、卖点和成分都列清楚。

另外，请给我一个整体分析：总共多少个活跃 SKU、平均价格、价格区间（最低–最高）。把这些内容打包成一个 JSON 文件放到 `ops/competitive_report.json`，我准备直接用这个报告去跟供应商砍价。报告编号记作 `CMP-APAC-LuminaSkin-020`，别忘了。

数据路径都已在工作区内，你顺着找就行。拜托了，今天下午就要！
