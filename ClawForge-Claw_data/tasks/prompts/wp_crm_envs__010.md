# 邮件：紧急：OldClient Services 联系人清理

**发件人：** 运营部 <ops@crm.com>  
**收件人：** CRM 管理员 <admin@crm.com>  
**主题：** 紧急：OldClient Services 联系人清理  

Hi，  

我们刚刚确认 OldClient Services 已经终止合作，所有相关联系人需要立即标记为“流失客户”，移入 `inactive` 文件夹，并添加标签 `churn_risk`。标签定义目前还没有这个标签，你需要自己创建。  

相关数据都在 `data/` 目录下（`contacts.json`、`companies.json`、`tag_definitions.json` 等）。请你：  

- 更新这些联系人记录，确保他们被归类到 `inactive` 文件夹并带上 `churn_risk` 标签；  
- 在 `tag_definitions.json` 中添加 `churn_risk` 标签的定义（category 随意，你可以设成 `"status"`）；  
- 最后，生成一个简洁的报告文件 `ops/churn_report.json`，列出所有处理过的联系人的 `contact_id`、`full_name`、`email` 以及你执行的操作（比如 `"moved to inactive and tagged"`）。  

注意：公司名称是 **"OldClient Services"**，不要搞混。如有已 inactive 或已带标签的，也请确认无误，在报告中说明即可。  

请尽快处理，谢谢！  

-- 运营部  
