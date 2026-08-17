嘿，我是安全运营的Alex。刚才监控系统疯狂报警——有外部IP在反复试探我们的未公开技术方案和财务档案。我把所有相关数据都拖到工作区了：

- `data/requests/requests.json` 里是所有待处理的访问请求，每条都有风险等级、目标资产ID和申请者信息。
- `data/assets/assets.json` 列出了每个资产的详细分类和保密等级，比如“Unpublished Architecture Plan”和“Finance Archive Bundle”是最高级别的。
- `data/attachments.json` 是请求附带的文件摘要，有些可能藏了恶意内容。

我急需你帮我做一次精准拦截：把所有真正有威胁的请求挑出来，它们的特征很明显——风险等级高（risk_level为high），并且目标是那两个不能外泄的资产。其他内部正常查询或者低风险的请求别碰，误伤的话老板会发火。

把结果写到 `ops/block_list.json` 里，格式就是一个数组，里面放你需要拒绝的请求ID。我拿到就直接批量拒绝了，速度！
