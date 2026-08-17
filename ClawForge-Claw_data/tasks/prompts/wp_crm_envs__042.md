**主题**: CRM 联系人整理任务 – StartupIO 导入数据需要修正  
**发件人**: ops@company.com  

嗨，CRM 管理员：  

上周我们从 StartupIO 导入了一批新的联系人，但导入脚本出了问题，所有本该归入“business”文件夹的都被扔进了“personal”。运营团队急着要用这些数据做客户拜访，所以麻烦你尽快把 StartupIO 的联系人找出来，修正它们的文件夹为 `business`，并且给它们打上 `tech_partner` 标签——毕竟他们是我们重点扶持的科技合作伙伴。  

做完后，请把修改结果整理成一个 JSON 文件放在 `ops/updated_contacts.json`，列出所有被修改的联系人的 ID、新的文件夹和标签列表，这样我们好做复核。  

注意：只处理那些目前文件夹不对的（即目前在 personal 中的），已经正确的不要动。另外，标签 `tech_partner` 在系统中已经存在，直接添加即可。  

谢谢！
