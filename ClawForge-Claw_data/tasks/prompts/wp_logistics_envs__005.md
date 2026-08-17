# 👋 紧急：仓库凌晨处理请求

Hey，我是仓库值班主管小李。今晚压了一堆活儿，系统那边还没上线，只能靠你手动处理一下。我把原始数据都丢在工作区了，你帮我跑一遍。

**退货单**：`data/returns.json` 里有一批刚到的退货，状态都还是 `pending_review`。你帮我看看：
- 如果退货原因是“defective”，直接批准（状态改成 `approved`）。
- 如果原因是“wrong item”，标记为待检查（状态改成 `pending_inspection`）。
- 其他的先别管，等明天采购再定。

**发货单**：`data/shipments.json` 里有个货号 `ship_005` 的发货单，状态还卡在 `processing`，但实物已经交给 FedEx 了，帮我更新成 `shipped`。

**库存调整**：`data/inventory/inventory.json` 里 `warehouse wh_001` 的 `SKU-1002` 有 5 件在搬运时损坏了，把它从库存里扣掉（库存量减 5）。

最后，把上面所有操作的结果整理成一个 JSON 文件，放到 `ops/processing_result.json`。格式你看着办，但必须让我一眼能看出每个操作的对象、动作和结果。我明早核查要用，别整漏了。

哦对了，工作区里还有几个备份文件（`data/returns_backup.json`、`data/shipments_old.json`），那些是旧的，别管它们。
