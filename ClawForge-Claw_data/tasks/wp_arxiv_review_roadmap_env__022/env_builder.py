import json
import os

def build_env():
    # 创建目录
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    
    # 创建干扰附件清单（文件本身为空占位）
    attachments = [
        {"path": "attachments/mobilenet_supp.pdf", "title": "MobileNet supplement", "kind": "pdf", "description": "Supplemental material for MobileNet"},
        {"path": "attachments/efficientnet_figures.png", "title": "EfficientNet figures", "kind": "image", "description": "Architecture diagrams"}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)
    for att in attachments:
        open(att["path"], "w").close()
    
    # 主论文数据（包含目标方向与干扰）
    papers = [
        # 目标方向：efficient_vision
        {"paper_id": "P001", "title": "MobileNetV3", "direction": "efficient_vision", "year": 2019,
         "keywords": ["efficient", "mobile"], "abstract": "A lightweight model for mobile vision.", "citation_ids": []},
        {"paper_id": "P002", "title": "EfficientNetV2", "direction": "efficient_vision", "year": 2021,
         "keywords": ["scaling", "efficient"], "abstract": "Improved scaling of CNNs.", "citation_ids": ["P001"]},
        {"paper_id": "P003", "title": "ConvNeXt", "direction": "efficient_vision", "year": 2022,
         "keywords": ["modern", "convolution"], "abstract": "A modernized ConvNet.", "citation_ids": ["P002"]},
        {"paper_id": "P004", "title": "RepVGG", "direction": "efficient_vision", "year": 2021,
         "keywords": ["reparametrization", "VGG"], "abstract": "Making VGG-style nets great again.", "citation_ids": ["P001", "P003"]},
        {"paper_id": "P005", "title": "EdgeNeXt", "direction": "efficient_vision", "year": 2023,
         "keywords": ["edge", "transformer"], "abstract": "Efficient edge transformer.", "citation_ids": ["P004"]},
        # 干扰方向：tool_augmented_reasoning
        {"paper_id": "T001", "title": "Toolformer", "direction": "tool_augmented_reasoning", "year": 2023,
         "keywords": ["tool", "language model"], "abstract": "Language models that learn to use tools.", "citation_ids": []},
        {"paper_id": "T002", "title": "Gorilla", "direction": "tool_augmented_reasoning", "year": 2022,
         "keywords": ["API", "LLM"], "abstract": "API call generation.", "citation_ids": ["T001"]},
        # 干扰：方向字符串不精确
        {"paper_id": "P006", "title": "FakeNet", "direction": "efficient vision", "year": 2022,
         "keywords": ["fake"], "abstract": "Not real.", "citation_ids": []},
        {"paper_id": "P007", "title": "FasterNet", "direction": "Efficient_Vision", "year": 2023,
         "keywords": ["fast"], "abstract": "Also not real.", "citation_ids": []}
    ]
    with open("data/papers/papers.json", "w") as f:
        json.dump({"papers": papers}, f, indent=2)

if __name__ == "__main__":
    build_env()
