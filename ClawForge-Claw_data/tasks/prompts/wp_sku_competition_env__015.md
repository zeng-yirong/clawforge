**主题：紧急！LuminaSkin 价目表价格不一致**

发件人: Mira Tan (Pricing Operations Lead) <mira.tan@northstar.example.com>  
收件人: 你  

Hi，

我们刚收到 LuminaSkin 品牌方发来的最新定价通知（我已放在 `data/attachments/current_pricebook_notice.md`），但今天核对时发现我们系统中生效的 APAC Q2 2026 价目表（LIVE 版）里，有好几个 SKU 的价格跟通知对不上。财务那边下周就要报送成本数据，必须今天内把差异清单整理好。

请你：
- 读取通知文件，提取里面列出的所有 SKU 及其建议的 **Correct Price**。
- 从当前价目表（LIVE 版）中找出这些 SKU **当前生效的价格**，逐一比对。
- 凡是不一致的，都记录到一个 JSON 文件里，放到 `ops/price_discrepancies.json`。  
  每个条目包含 `sku_id`（字符串）和 `correct_price`（浮点数），直接用通知里的价格。  
  我只想看到真正需要修正的 SKU，不要出现多余条目。

拜托了，今天必须搞定！

— Mira
