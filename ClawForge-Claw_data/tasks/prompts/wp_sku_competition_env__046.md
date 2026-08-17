> **发件人**: Mira Tan (mira.tan@northstar.example.com)  
> **收件人**: Agent  
> **主题**: 紧急：LuminaSkin 价格书数据乱了，帮我理一份竞品对照

Hey agent,

我们刚收到亚太区Q2的定价调整通知，但手头的数据一团糟。QA组的Jonas发现 `pricing/price_books.json` 里混着好几个版本，还有一堆已经归档的老数据。我现在必须拿到 LuminaSkin 品牌所有还在卖的产品的当前价格，才能跟渠道商谈新折扣。

具体需求是这样的：

- 品牌范围：只关注 LuminaSkin。其他品牌（AquaPulse、DermVeil 那些）的暂时别看，别混进来。
- 产品状态：只有 `status` 为 “active” 的 SKU 才算在售，那些 discontinued、pending 的不要。
- 价格来源：用当前生效的价格书。在 `price_books.json` 里面，我指的是 `is_current` 为 `true` 的那一本。注意，里面可能有多个 `status` 但只有 `approved` 且当前的才算数。别拿归档版。
- 每条 SKU 需要记录：sku_id, sku_name, 当前价格（从价格书 entries 里对应 sku_id 找 price）、卖点（只取前两个）、成分（只取前三个）。
- 最后把所有结果汇总成一个 JSON 文件，放到 `ops/competitor_report.json` 里。文件结构你自己组织，但要清晰可读，我这边要一键导入到 BI 工具。

另外，仓库里还有一些过期附件和旧备份，别被它们干扰。我只需要干净的数据。辛苦你整理好，今晚我要发给 Alina。

Thanks,
Mira
