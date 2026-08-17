嘿，市场部刚发来紧急需求——Q2技术方案推广材料要定了，唯独“HelioSync Edge Inference Fabric”这条线的线索还不全。

我把几份原始数据都丢在 `data/` 底下了：报告、演示文稿、媒体样本的JSON都在各自子目录里。每个记录里有个 `solution_aliases` 字段，里面列出了该文档关联的方案别名。我需要你找出所有明确标记了“HelioSync Edge Inference Fabric”（完整短语，别把那些“HelioSync Lite”或“Edge Inference”之类的混进来）的文档。

每个匹配文档，记下它的文档ID、文档类型（report / presentation / media_sample）以及它的摘要（`summary` 字段）。把所有这些信息整理成一个清单，存到 `ops/clue_manifest.json`，格式你自己看着来，但要让我一眼能看出每个匹配文档是谁、是什么类型、大致说了啥。

别忘了 `ops/` 目录可能还没建，记得先创建。另外，我只要精确匹配上面那个全称，多一个少一个字母都不算。时间紧，赶紧跑一趟。
