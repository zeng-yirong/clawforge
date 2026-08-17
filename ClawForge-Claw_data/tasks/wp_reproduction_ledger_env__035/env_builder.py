import os, json, random

def build_env():
    # 创建目录结构
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 创建 accounts.json（干扰项）
    accounts = [
        {"account_id": "a01", "display_name": "Zhang San", "department": "Research", "email": "zhangsan@example.com", "permissions": ["read", "write"]},
        {"account_id": "a02", "display_name": "Li Si", "department": "Engineering", "email": "lisi@example.com", "permissions": ["read"]},
        {"account_id": "a03", "display_name": "Wang Wu", "department": "Research", "email": "wangwu@example.com", "permissions": ["admin"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts, "wrapper": "accounts", "key": "account_id"}, f)

    # 2. 创建 contacts.json（干扰项）
    contacts = [
        {"contact_id": "c01", "name": "Alice", "role": "PM", "email": "alice@example.com"},
        {"contact_id": "c02", "name": "Bob", "role": "Dev", "email": "bob@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts, "wrapper": "contacts", "key": "contact_id"}, f)

    # 3. 创建 project_docs.json（索引）
    # 精心设计：有效文档5个，总steps=35；干扰项：路径无效、reproducible false、格式缺失、steps负数等
    docs = []
    # 有效文档（reproducible true， steps正整数，文件存在）
    valid = [
        ("doc001", "P001", "Setup Environment", "docs/setup_env.md", True, 7),
        ("doc002", "P001", "Run Unit Tests", "docs/unit_tests.md", True, 5),
        ("doc003", "P002", "Integration Test", "docs/integration.md", True, 12),
        ("doc004", "P002", "Performance Benchmark", "docs/benchmark.md", True, 8),
        ("doc005", "P003", "Cleanup Script", "docs/cleanup.md", True, 3),
        # 干扰：reproducible false
        ("doc006", "P003", "Legacy Process", "docs/legacy.md", False, 10),
        # 干扰：path 不存在
        ("doc007", "P001", "Missing File", "docs/missing.md", True, 4),
        # 干扰：steps 为负数
        ("doc008", "P002", "Negative Steps", "docs/negative.md", True, -2),
        # 干扰：steps 缺失（元数据不全）
        ("doc009", "P003", "No Steps", "docs/no_steps.md", True, None),  # 会生成不含steps的文件
    ]
    for doc_id, proj_id, title, path, reproducible, steps in valid:
        entry = {
            "doc_id": doc_id,
            "project_id": proj_id,
            "title": title,
            "path": path,
            "reproducible": reproducible
        }
        if steps is not None:
            entry["steps"] = steps
        docs.append(entry)

    # 额外添加一个干扰项：path路径有特殊字符，文件存在但元数据不合规（steps非整数）
    # 为了避免歧义，我们不在索引中添加，而是直接在docs/下放一个无索引文件？索引中不存在，所以不会被读取，不影响。
    # 但为了增加挑战，可以在索引中添加一个path指向一个文件，其元数据中steps不是整数（如字符串"?"）
    docs.append({
        "doc_id": "doc010",
        "project_id": "P004",
        "title": "Strange Steps",
        "path": "docs/strange.md",
        "reproducible": True,
        "steps": 99  # 索引里写99，但实际文件元数据中steps是字符串"?"
    })
    # 注意：实际文件内容会覆盖索引中的steps，但Agent应该根据文件元数据为准，而不是索引中的steps字段。
    # 索引中的steps只是干扰。

    with open("data/projects/project_docs.json", "w") as f:
        json.dump({"project_docs": docs, "wrapper": "project_docs", "key": "doc_id"}, f)

    # 4. 生成实际的文档文件（Markdown）
    # 有效文件
    file_defs = [
        ("docs/setup_env.md", True, 7, "# Setup\n1. Install dependencies\n2. Configure\n3. Verify\n"),
        ("docs/unit_tests.md", True, 5, "# Unit Tests\n1. Run pytest\n2. Check coverage\n3. Generate report\n"),
        ("docs/integration.md", True, 12, "# Integration\n1. Deploy test server\n2. Run API tests\n3. Check database\n4. Cleanup\n"),
        ("docs/benchmark.md", True, 8, "# Benchmark\n1. Load test data\n2. Execute queries\n3. Record metrics\n"),
        ("docs/cleanup.md", True, 3, "# Cleanup\n1. Remove temp files\n2. Reset environment\n"),
        # 干扰：reproducible false 但文件存在
        ("docs/legacy.md", False, 10, "# Legacy\n1. Manual step A\n2. Manual step B\n"),
        # 干扰：路径不存在——我们就不创建文件
        # 干扰：steps负数的文件
        ("docs/negative.md", True, -2, "# Negative\n1. Step one\n2. Step two\n"),
        # 干扰：steps缺失（没有steps字段）
        ("docs/no_steps.md", True, None, "# No Steps\n1. Do something\n"),
        # 干扰：索引中doc010对应的文件，其元数据steps是字符串
        ("docs/strange.md", True, "?", "# Strange\n1. Step one\n"),
    ]
    for path, reproducible, steps, content in file_defs:
        # 构建front matter
        meta = {}
        meta["reproducible"] = str(reproducible).lower()  # 注意字符串
        if steps is not None:
            # 对于doc010，steps是字符串"?"，直接写入
            meta["steps"] = steps
        # 注意：对于no_steps.md，我们不写steps字段
        lines = ["---"]
        for k, v in meta.items():
            lines.append(f"{k}: {v}")
        lines.append("---")
        lines.append(content)
        with open(path, "w") as f:
            f.write("\n".join(lines))

    # 确保missing.md不创建
    # 额外创建一些无关文件以增加迷惑
    with open("docs/extra_notes.txt", "w") as f:
        f.write("This is not a doc.")
    with open("ops/old_result.json", "w") as f:
        f.write("{\"score\": 0}")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
