嘿，我是安全运维的小李。昨晚我们做了一次凭证库审计，发现了几个问题：重复的条目、分类混乱、还有一堆弱密码。我把导出的原始数据放到了 `data/raw_credentials.csv` 里，还有一份 `data/category_mapping.csv` 告诉你每个原始类别应该对应我们 vault schema 里的哪个正式类别（vault schema 在 `data/vault_schema.json`）。密码策略规定在 `policies/password_policy.json`。

我需要你帮我整理一份干净的凭证库，输出到 `vault/classified_credentials.json`。要求：合并重复（后来居上，即最后出现的记录覆盖之前相同 id 的记录），把 category 按照映射表填好，如果映射表里没有就填 `未分类`。然后对照密码策略检查每个密码是否弱（is_weak 字段 true/false）。最后按 id 从小到大排序。拜托了，尽快！
