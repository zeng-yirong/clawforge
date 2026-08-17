> **收件人**：安全值班工程师  
> **发件人**：IT运维-张姐  
> **紧急程度**：高  

小张，上周安全团队内部审计发现我们的凭证存储乱成一锅粥！  
旧的凭证库里 **data/credential_store.json** 里混了一堆无效记录和分类错误的条目，  
而新来的专家已经定下了标准的分类方案（见 **data/vault_schema.json**），  
autofill 规则也是一片空白，导致用户每次都要手动填密码，怨声载道。  

你的任务：  
1. 把旧的凭证库清洗一遍，只保留**字段完整且分类名称能对应到标准分类**的记录。  
2. 根据标准分类，给每条有效记录**分配正确的 category_id**，同时算一下每条密码的强度分——  
   规则很简单：每 1 个字符长度计 4 分，每个数字额外加 5 分，每个大写字母额外加 3 分。  
3. 把清洗、分类、算好强度后的结果整理成一个新文件 **classified_credentials.json**。  
4. 为每个标准分类设置一条 autofill 规则，生成 **autofill_rules.json**，  
   规则里填上对应的 URL 模式（`https://*.example.com/<分类英文名>`）和需要自动填充的字段  
   （所有分类都需要 `username` 和 `password` 两个字段）。分类的英文名就在 schema 的 `name` 字段里，  
   把中文名翻译成拼音？不用，schema 里已经附带了英文名 `name_en`，直接用那个。  

注意：  
- 无效记录（比如缺少 `id`、`username`、`platform`、`category_name`、`password` 任意一个字段的）直接丢弃，不要留痕迹。  
- 分类名称必须**完全匹配** schema 中 `name` 字段（注意大小写和空格），匹配不上的记录也视为无效。  
- 密码强度分算出来直接保留两位小数存入 `password_strength` 字段。  
- autofill 规则中字段列表用 `["username", "password"]`，URL 模式用 `https://*.example.com/<分类的 name_en>`，  
  其中 `<分类的 name_en>` 替换为实际值，例如 `https://*.example.com/work_email`。  

弄完后把两个结果文件放在工作区根目录下就行，我这边要直接导入新系统。  
辛苦！  
