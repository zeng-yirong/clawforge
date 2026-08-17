嗨，我是运营那边的阿杰。刚跟 VendorCo Supplies 的对接人通完电话，人家火气不小——说我们在系统里压根没给他们公司的联系人打上“vendor”标签，导致上季度的合作报表里把他们漏了。我查了一下，标签库里其实早就有一个叫“vendor”的标签（我记得 ID 是 tag_vendor_001），但不知道为啥他们的联系人没挂上。

我需要你把 VendorCo Supplies 公司下 **所有未带 vendor 标签** 的联系人整理出来，把他们的 contact_id 写到一个文件里。文件名就用 `ops/add_vendor_tags.json`，格式是个纯列表，每一项就是一个 contact_id 字符串。千万别重复加，也别加那些已经有 vendor 标签的——我回头直接拿这份名单跑批量更新就行。

对了，相关数据都在 `data/` 下面，公司的信息在 `companies.json`，联系人明细在 `contacts.json`，标签定义在 `tags/tag_definitions.json`。VendorCo Supplies 的 company_id 你从公司列表里找一找。动作快点，午饭前我要把名单交给开发。

还有，`ops/` 目录已经在项目里了，空着呢，你直接把文件放进去吧。
