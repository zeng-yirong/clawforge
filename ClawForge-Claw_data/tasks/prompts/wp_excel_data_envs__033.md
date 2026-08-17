Subject: 紧急：销售数据清洗和汇总

嘿，数据分析师！

我刚从系统导出销售数据，放在 `sales_raw.csv` 里了，还有客户信息表 `accounts.csv` 在同一个目录下。数据乱成一团：有重复的行，有些客户名缺失，有些销售额空白。我需要你帮我整理一下，生成一个清理后的数据文件 `cleaned_data.csv`，然后按区域（region）汇总一下每个区域的总销售额和平均订单金额，结果放到 `region_summary.json` 里。要求 JSON 的键是区域名，每个区域对应一个对象，里面有 `total_revenue` 和 `average_order` 两个字段。

注意：缺失的客户名可以从 `accounts.csv` 里根据 customer_id 查找补齐；缺失的销售额直接填 0 就行。重复的行只保留一条。其他字段保持原样。

我需要两个文件：`cleaned_data.csv` 和 `region_summary.json`。别整其他花哨的，就这些。搞定了回我邮件。

多谢！
