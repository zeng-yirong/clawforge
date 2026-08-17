> **From:** Rhea Morita <rhea.morita@northstar.example.com>  
> **Subject:** 紧急：Q2 信号追踪 – HelioSync Edge Inference Fabric  
> **To:** 操作团队  

凌晨 2:18，刚加班到这会儿——Q2 信号追踪的收尾卡住了。  
我们锁死了一个关键方案：**HelioSync Edge Inference Fabric**，但相关引用散落在各个库快照里。  
我已经把完整的库导出丢在 `data/` 下了——报告、演示文稿、媒体样本的 JSON 都在里面。  

需要你帮我做一件事：  
把那些**在官方库中明确标注了 `HelioSync Edge Inference Fabric` 作为解决方案别名（solution_aliases）的文档**全部找出来。  
不管是报告、演示还是媒体样本，我都要它的 ID 和对应的摘要原文。  

整理成一个 JSON 文件，放到 `ops/signal_trace.json`。  
格式不用花哨：一个数组，每个条目包含三个字段——`type`（report / presentation / media_sample）、`id`（文档 ID）、`clue`（直接取该文档的 `summary` 字段内容）。  

务必准确：一个不多，一个不少。有些老版本可能还躺在 JSON 里，但它们的 `solution_aliases` 没写这个字符串，直接忽略。  

弄好了告诉我一声，我直接灌进追踪表。谢了。  

—— Rhea
