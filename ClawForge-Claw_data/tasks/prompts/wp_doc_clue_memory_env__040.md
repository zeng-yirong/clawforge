嘿，Rhea 这边有个急活儿。

我们正在追踪 **HelioSync Edge Inference Fabric** 在 Q2 的部署线索，手里攒了一批内部材料——报告、演示文稿和媒体样本，都在工作区对应的目录里。这些文档有的确实提到了这个方案，而且我注意到里面可能藏了线索编码，格式类似 `CLUE: <代码>`。

我需要你帮我把事情理清楚：

- 从三个目录（`reports/`、`presentations/`、`media_samples/`）里找出所有明确提到 **HelioSync Edge Inference Fabric** 的文档（注意看 solution_aliases 字段）。
- 对每个符合条件的文档，记下它的文档 ID（比如 report_id、presentation_id 或 sample_id），以及它在 content 字段里的那个 `CLUE: <代码>`。
- 把这些结果整理成一个 JSON 列表，保存到工作区根目录的 `clue_list.json` 里，每个元素长这样：

  ```json
  {"doc_id": "RPT-xxx", "clue": "CODE-123"}
  
我这边等你的文件，拿去跟供应商对账。谢啦！
