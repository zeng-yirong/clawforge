嘿，R&D情报组的任务又来啦。Q2的HelioSync Edge Inference Fabric方案客户兴趣暴涨，但我们的线索散落在不同文档库里，而且里面混了不少旧版本和无关内容，让你帮我整理一下。

具体是这样的：我在`reports/`、`presentations/`、`media_samples/`三个文件夹里各有一个JSON文件，分别存了这段时间的产品报告、演示文稿和媒体样本的元数据。每个文档都有个`solution_aliases`字段，列出它关联的方案别名。我需要你把所有**明确标注了“HelioSync Edge Inference Fabric”**（注意是全名，不是“HelioSync Edge”也不是“Inference Fabric”单独出现）的文档挑出来，每个文档记下它的ID（字段名叫`report_id`、`presentation_id`或`sample_id`）和一段简短摘要（`summary`字段），合并成一个`clue_list.json`放在工作区根目录。格式就用一个JSON数组，每个元素包含`id`和`summary`两个字段。

千万别把那些只沾点边但型号不对的混进来，比如旧版“HelioSync Edge”或者别的什么“Fabric”方案。我只要**精确匹配**的那几个。弄好之后直接放根目录，我今晚需要拿去给客户看。谢啦！
