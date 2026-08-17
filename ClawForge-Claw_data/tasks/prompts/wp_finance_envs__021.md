**主题：紧急：Q2财报筛选——科技股连续超预期**

Hi，

今天是7月15号，Q2财报季刚收尾。我需要你帮忙从工作区的数据中找出那些“真金不怕火炼”的科技股：连续两个季度（Q1和Q2）营收和每股收益都超预期（beat），并且近期（一周内）有正面新闻的股票。

具体数据在 `data/` 目录下：
- `data/stocks.json`
- `data/earnings/earnings.json`
- `data/news/news.json`

请把符合条件的股票代码和公司名称汇总成一个 JSON 数组，放到 `ops/recommended_stocks.json`。格式就像这样：
[{"ticker": "...", "company_name": "..."}]
我们只关注科技板块（sector 为 Technology）。时间紧，麻烦尽快处理，谢谢！
