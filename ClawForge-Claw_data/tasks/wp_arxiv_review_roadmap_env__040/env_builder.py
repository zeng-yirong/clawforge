import os
import json
import shutil

def build_env():
    # 确保工作区干净
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("reviews"):
        shutil.rmtree("reviews")
    if os.path.exists("old_dump"):
        shutil.rmtree("old_dump")

    # 创建目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("old_dump", exist_ok=True)

    # 干扰：旧数据目录里放一个无关的 JSON
    old_papers = {
        "wrapper": "papers",
        "papers": [
            {"paper_id": "old001", "title": "Ancient CNN", "direction": "efficient_vision", "year": 1998, "keywords": ["cnn"], "abstract": "", "citation_ids": []}
        ]
    }
    with open("old_dump/old_papers.json", "w") as f:
        json.dump(old_papers, f)

    # 干扰：附件中有无关文件
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": []}, f)

    # 正式论文数据
    papers = {
        "wrapper": "papers",
        "papers": [
            # Efficient Vision 方向（共6篇，年份各不相同）
            {"paper_id": "ev003", "title": "SqueezeNet", "direction": "efficient_vision", "year": 2016, "keywords": ["lightweight"], "abstract": "A small CNN architecture...", "citation_ids": []},
            {"paper_id": "ev001", "title": "MobileNetV1", "direction": "efficient_vision", "year": 2017, "keywords": ["depthwise"], "abstract": "Depthwise separable convolutions...", "citation_ids": []},
            {"paper_id": "ev005", "title": "ShuffleNet", "direction": "efficient_vision", "year": 2018, "keywords": ["channel shuffle"], "abstract": "Group convolution and channel shuffle...", "citation_ids": []},
            {"paper_id": "ev002", "title": "EfficientNet", "direction": "efficient_vision", "year": 2019, "keywords": ["compound scaling"], "abstract": "Systematic scaling of depth, width, resolution...", "citation_ids": []},
            {"paper_id": "ev004", "title": "GhostNet", "direction": "efficient_vision", "year": 2020, "keywords": ["ghost module"], "abstract": "Generate more features from cheap operations...", "citation_ids": []},
            {"paper_id": "ev006", "title": "MobileNetV3", "direction": "efficient_vision", "year": 2021, "keywords": ["NAS", "squeeze-and-excitation"], "abstract": "Neural architecture search for mobile...", "citation_ids": []},
            # 其他方向（干扰）
            {"paper_id": "ta001", "title": "ReAct", "direction": "tool_augmented_reasoning", "year": 2022, "keywords": ["reasoning"], "abstract": "Synergizing reasoning and acting...", "citation_ids": []},
            {"paper_id": "ta002", "title": "Toolformer", "direction": "tool_augmented_reasoning", "year": 2023, "keywords": ["tool usage"], "abstract": "Language model can learn to use tools...", "citation_ids": []},
            {"paper_id": "ta003", "title": "ART", "direction": "tool_augmented_reasoning", "year": 2023, "keywords": ["automated reasoning"], "abstract": "Auto-regressive tool...", "citation_ids": []},
            # 无关方向（进一步干扰）
            {"paper_id": "oth001", "title": "PointNet", "direction": "3d_vision", "year": 2017, "keywords": ["point cloud"], "abstract": "Deep learning on point sets...", "citation_ids": []}
        ]
    }
    with open("data/papers/papers.json", "w") as f:
        json.dump(papers, f, indent=2)

    # 创建一个空目录 reviews 作为预期输出位置（agent 需要自己创建，这里不创建）
    # 但为了干扰，可以在别处放一些已有的 review 文件
    if not os.path.exists("reviews"):
        pass  # 让 agent 自己创建

if __name__ == "__main__":
    build_env()
