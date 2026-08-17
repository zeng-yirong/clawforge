import os

def build_env():
    # 创建 docs 目录
    os.makedirs("docs", exist_ok=True)
    
    # 正确文档: proj-042_reproduction.md
    correct_content = """# Reproduction Ledger for proj-042
Author: Alice Zhang
Steps:
1. Install package version 2.1.0
2. Run command `example --flag`
3. Observe output contains "error code 0xDEAD"
"""
    with open("docs/proj-042_reproduction.md", "w") as f:
        f.write(correct_content)

    # 干扰项 1: 缺少作者字段，步骤只有两步
    decoy1 = """# Reproduction for proj-001
Steps:
1. Clone repo
2. Run `make test`
"""
    with open("docs/proj-001_readme.md", "w") as f:
        f.write(decoy1)

    # 干扰项 2: 作者不同，步骤顺序错乱
    decoy2 = """# Reproduction for proj-002
Author: Bob Smith
Steps:
- Run `npm install`
- Check log for "ERROR 503"
- Restart server
"""
    with open("docs/proj-002_readme.md", "w") as f:
        f.write(decoy2)

    # 干扰项 3: 纯测试文档，无步骤
    decoy3 = """# Test Document
This is just a placeholder.
"""
    with open("docs/test_doc.md", "w") as f:
        f.write(decoy3)

    # 创建空的 knowledge_base 目录
    os.makedirs("knowledge_base", exist_ok=True)

    # 额外干扰文件 (非 .md)
    with open("docs/extra.txt", "w") as f:
        f.write("Some random notes")

if __name__ == "__main__":
    build_env()
