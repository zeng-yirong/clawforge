**主题: 紧急：给TechCorp联系人统一打标签**

嘿，

老板刚才拍桌子了——说我们跟TechCorp Industries的合作这么重要，CRM里居然没有统一标记他们。要求立刻把所有属于TechCorp的联系人打上“tech_partner”标签，方便后续筛选和关怀。

我把最新的公司信息、联系人列表和现有标签定义都放在 `data/` 下面了：
- `data/companies.json`（公司清单）
- `data/contacts.json`（联系人花名册）
- `data/tags/tag_definitions.json`（标签库）

注意：有些联系人可能已经被贴过“tech_partner”了，别再重复加，老板特别讨厌做无用功。

`ops/` 目录我已经建好了，你把需要打标签的结果整理成一个清单，文件名叫 `add_tags.json` 放在里面。每条记录写上联系人的ID和要添加的标签名就行，我拿到后直接批量导入。

辛苦尽快搞定，谢谢！

—— 市场部 小明
