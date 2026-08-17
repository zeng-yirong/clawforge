主题：紧急 VP 伦敦出差机票预订

Hi 助手，

VP 下周一要去伦敦参加峰会，需要一张商务舱机票。我刚从各平台拉来了报价单，放在 `data/offers/` 下面，每个平台一个子文件夹，里面是 JSON 格式的航班详情。公司最新的差旅政策文件在 `data/policies/current_policy.json`，你直接用它。

帮我从这些报价中筛出完全符合政策的航班，然后按价格从低到高排序，把最便宜那个写到 `ops/best_option.json`。格式记得带 flight_id、platform、price、cabin_class 这几个字段，方便我直接提审批。

哦对了，有的平台已经停运了，报价单里能看到 `platform_is_active` 字段，别用它们的。先谢啦！
