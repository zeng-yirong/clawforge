嘿，我是研究团队的小张。最近我们在整理项目 Alpha 的再现账本，方便后续复现验证。我把所有项目的文档都按索引放在了 `data/projects/project_docs.json` 里，实际的文档内容散落在 `docs/` 目录下。

你帮我看看：从项目 Alpha 的文档里，找出最新且有效的再现步骤说明，把里面记录的 commit 哈希和版本号摘出来。然后直接在 `archive/` 目录下创建一个 `reproduction_ledger.json`，格式就像 `{"project": "project-alpha", "commit_hash": "...", "version": "..."}` 这样，我好直接归档到知识库里。

注意一下，有些文档可能是废弃的（名字里带着 `_deprecated`）或者内容不完整，你别拿错了。我要的是真正有效的那个。

弄好之后跟我说一声就行，谢谢！
