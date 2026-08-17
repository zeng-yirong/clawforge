import os
import json
from datetime import datetime, timedelta

def build_env():
    # --- docs 目录 ---
    os.makedirs("docs", exist_ok=True)
    doc_content = """# Reproducing segfault in v3.2.1

## Steps
1. Run the application with the test input from `tests/input.dat`.
2. Observe the crash log in `logs/` directory.
3. Find the **latest** crash log (filename format `crash_YYYYMMDD.log`).
4. Extract the `error_id` value from the last line of that log.
5. The extracted ID is the key to report.

**Note:** Only the log with the newest date contains the correct error_id.
"""
    with open("docs/segfault_v3.2.1.md", "w") as f:
        f.write(doc_content)
    # 干扰文档
    with open("docs/feature-x.md", "w") as f:
        f.write("This is a feature doc, not relevant.")
    with open("docs/README.md", "w") as f:
        f.write("Project documentation root.")

    # --- logs 目录 ---
    os.makedirs("logs", exist_ok=True)
    # 生成多个日志，日期不同，只有最新的有正确 error_id
    today = datetime.now()
    for offset, err_id in [(10, "deadbeef"), (5, "cafebabe"), (2, "feedface"), (0, "a1b2c3d4")]:
        date_str = (today - timedelta(days=offset)).strftime("%Y%m%d")
        filename = f"crash_{date_str}.log"
        content = f"""[INFO] Application started
[ERROR] Segmentation fault at 0x{err_id}
Traceback (most recent call last):
  File "main.py", line 42, in run
    crash()
error_id = {err_id}
"""
        with open(f"logs/{filename}", "w") as f:
            f.write(content)
    # 干扰非crash日志
    with open("logs/debug.log", "w") as f:
        f.write("[DEBUG] Nothing important.\n")

    # --- knowledge 目录 ---
    os.makedirs("knowledge", exist_ok=True)
    known = {
        "known_issues": [
            {"id": "K001", "description": "Old segfault in v3.1.0"}
        ]
    }
    with open("knowledge/known_issues.json", "w") as f:
        json.dump(known, f)

    # --- reproductions 目录（空，等待 agent 创建产物） ---
    os.makedirs("reproductions", exist_ok=True)

    # 正确答案写在一个隐藏文件里，方便 verify 脚本读取
    correct_answer = "a1b2c3d4"
    os.makedirs(".meta", exist_ok=True)
    with open(".meta/correct_error_id.txt", "w") as f:
        f.write(correct_answer)

if __name__ == "__main__":
    build_env()
