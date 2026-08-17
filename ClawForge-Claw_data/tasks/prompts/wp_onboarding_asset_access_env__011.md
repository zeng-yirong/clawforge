你好！我是人事部的 Lisa。新员工 Sarah Johnson 的入职流程卡在中间了——她的合同我们已经签好，但后续的邮箱开通、系统权限分配、设备发放全都没动。技术那边催得急，说再不给权限下周就上不了班了。

我把手头的资料都放在工作区里了，你帮我翻一下：
- 合同文件在 `data/onboarding/contracts.json`，她的合同状态应该是“active”，而且还没有处理过（注意别拿已经弄过的）。
- 系统权限包的定义在 `data/onboarding/permission_packs.json`，合同里会注明需要哪个包。
- 设备库存清单在 `data/onboarding/equipment_inventory.json`，合同里写了给她分配的资产标签，你得确认那台设备目前是“available”状态，别给了已经发出去的。
- 她的个人账户信息（姓名、邮箱等）也在 `data/accounts.json` 里，你顺便核对一下。

帮我整理一个完整的入职摘要文件，放在工作区根目录下，命名为 `onboarding_summary.json`。里面至少得包含：她的员工ID、姓名、邮箱、需要开通的系统列表（从权限包解析出来）、分配给她的设备资产标签。我拿到这个文件就可以直接走下一步流程了。多谢！
