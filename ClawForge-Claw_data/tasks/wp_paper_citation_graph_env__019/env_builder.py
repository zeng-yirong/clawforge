import os, json, shutil

def build_env():
    # 清理并创建基础目录
    for d in ["data/papers", "cache", "notes"]:
        os.makedirs(d, exist_ok=True)
    
    # 干扰文件 —— 非论文数据
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)
    with open("notes/draft.txt", "w") as f:
        f.write("This is a draft note.\n")
    
    # 核心论文数据
    papers = [
        {
            "paper_id": "paper1",
            "title": "Attention Is All You Need",
            "year": 2017,
            "citation_ids": ["paper2", "paper3", "nonexistent"]
        },
        {
            "paper_id": "paper2",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "year": 2018,
            "citation_ids": ["paper1"]
        },
        {
            "paper_id": "paper3",
            "title": "Improving Language Understanding by Generative Pre-Training",
            "year": 2018,
            "citation_ids": ["paper1", "paper2"]
        },
        {
            "paper_id": "paper4",
            "title": "Deep Residual Learning for Image Recognition",
            "year": 2015,
            "citation_ids": ["paper5"]
        },
        {
            "paper_id": "paper5",
            "title": "Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context",
            "year": 2017,
            "citation_ids": ["paper1", "paper5"]
        }
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

    # 额外干扰：另一个目录下的旧版论文数据
    with open("data/papers/old_papers.json", "w") as f:
        json.dump({"papers": [{"paper_id": "fake1", "citation_ids": []}]}, f)

if __name__ == "__main__":
    build_env()
