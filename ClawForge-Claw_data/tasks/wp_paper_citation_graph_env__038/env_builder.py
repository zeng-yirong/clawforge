import os
import json

def build_env():
    # 创建 papers 目录
    os.makedirs("papers", exist_ok=True)
    
    # 有效论文数据
    papers_valid = [
        {
            "paper_id": "p001",
            "title": "Deep Learning for NLP",
            "year": 2020,
            "citation_ids": ["p002", "p003"]
        },
        {
            "paper_id": "p002",
            "title": "Attention Is All You Need",
            "year": 2017,
            "citation_ids": ["p004"]
        },
        {
            "paper_id": "p003",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "year": 2018,
            "citation_ids": ["p001", "p004"]
        },
        {
            "paper_id": "p004",
            "title": "Transformer-XL",
            "year": 2019,
            "citation_ids": ["p002"]
        },
        {
            "paper_id": "p005",
            "title": "GPT-3",
            "year": 2020,
            "citation_ids": ["p001", "p003", "p006"]  # p006 不存在，但保留为合法边？应该视为无效引用？题目设计：只保留论文ID在有效集合中的边。所以 p006 的边应被忽略
        }
    ]
    # 写有效文件
    for paper in papers_valid:
        fname = f"papers/{paper['paper_id']}.json"
        with open(fname, "w") as f:
            json.dump(paper, f)
    
    # ----- 干扰项 -----
    # 1. 自引用 (paper_id="p010" 引用自身)
    self_ref = {
        "paper_id": "p010",
        "title": "Self Citation Madness",
        "year": 2021,
        "citation_ids": ["p010", "p002"]
    }
    with open("papers/p010.json", "w") as f:
        json.dump(self_ref, f)
    
    # 2. 格式错误文件（非 JSON）
    with open("papers/corrupt.txt", "w") as f:
        f.write("this is not json")
    
    # 3. 缺少 citation_ids 字段
    no_cite = {
        "paper_id": "p020",
        "title": "Missing Citation Field",
        "year": 2022
    }
    with open("papers/p020.json", "w") as f:
        json.dump(no_cite, f)
    
    # 4. 重复文件（内容与 p001 相同但文件名不同）
    dup = {
        "paper_id": "p001",
        "title": "Deep Learning for NLP",
        "year": 2020,
        "citation_ids": ["p002", "p003"]
    }
    with open("papers/dup_p001.json", "w") as f:
        json.dump(dup, f)
    
    # 5. 旧版本（p003 的旧版，但 citation_ids 不同，应忽略，因为 paper_id 重复？按 paper_id 去重，保留后出现的？这里设计为旧版内容，但 paper_id 相同，应只保留一个。我们将 dup 视为同一 paper_id，但内容一致，所以不影响。更巧妙：p003 的旧版文件名为 p003_old.json，但内容中 paper_id 仍为 p003，而且 citation_ids 不同。但实际上 agent 读取所有文件后，按 paper_id 合并或取最后？为了唯一答案，我们让旧版文件的 paper_id 写成 p003_old，这样不会冲突，但干扰。或者让旧版文件与 p003 的 paper_id 相同，但内容不同。为了简单，我让旧版文件的 paper_id 为 p003_old，标题暗示旧版。
    old_version = {
        "paper_id": "p003_old",
        "title": "BERT (Old Version)",
        "year": 2017,
        "citation_ids": ["p001"]
    }
    with open("papers/old_p003.json", "w") as f:
        json.dump(old_version, f)
    
    # 添加一个隐藏的目录或无关文件
    os.makedirs("logs", exist_ok=True)
    with open("logs/readme.txt", "w") as f:
        f.write("irrelevant")
    
    # 创建 output 目录（验证时会检查是否存在文件）
    os.makedirs("output", exist_ok=True)

if __name__ == "__main__":
    build_env()
