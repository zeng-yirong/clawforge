import sys
import json
import os
import pathlib

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # ---- 1. 检查目录结构 (10分) ----
    required_dirs = ["publish"]
    for d in required_dirs:
        dir_path = os.path.join(workspace, d)
        exists = os.path.isdir(dir_path)
        details.append({
            "item": f"Directory '{d}' exists",
            "score": 10 if exists else 0,
            "max_score": 10,
            "passed": exists,
            "reason": f"Directory '{d}' {'found' if exists else 'not found'}"
        })
        if exists:
            total_score += 10

    # ---- 2. 检查目标文件是否存在 (20分) ----
    target_file = os.path.join(workspace, "publish", "launch_post.txt")
    file_exists = os.path.isfile(target_file)
    details.append({
        "item": "File 'publish/launch_post.txt' exists",
        "score": 20 if file_exists else 0,
        "max_score": 20,
        "passed": file_exists,
        "reason": f"File {'found' if file_exists else 'not found'}"
    })
    if file_exists:
        total_score += 20

    # ---- 3. 文件内容精确匹配 (70分) ----
    content_score = 0
    if file_exists:
        with open(target_file, "r") as f:
            content = f.read()
        expected = (
            "Launch Date: 2025-08-15\n"
            "Mission: Orbit Insertion\n"
            "Payload: Comms Array\n"
            "\n"
            "This is the approved final brief. Use for all launch communications.\n"
        )
        if content == expected:
            content_score = 70
            reason = "Content exactly matches the correct attachment"
        else:
            # 尝试忽略尾部空行
            if content.rstrip("\n") == expected.rstrip("\n"):
                content_score = 60
                reason = "Content matches after stripping trailing newlines"
            else:
                content_score = 0
                reason = f"Content mismatch. Expected:\n{expected!r}\nGot:\n{content!r}"
    else:
        reason = "File not found, cannot check content"
        content_score = 0

    details.append({
        "item": "File content matches correct attachment",
        "score": content_score,
        "max_score": 70,
        "passed": content_score >= 60,
        "reason": reason
    })
    total_score += content_score

    # ---- 4. 检查是否有额外未要求的文件 (扣分项，最多扣10分) ----
    unexpected_files = []
    publish_dir = os.path.join(workspace, "publish")
    if os.path.isdir(publish_dir):
        for f in os.listdir(publish_dir):
            file_path = os.path.join(publish_dir, f)
            if os.path.isfile(file_path) and f != "launch_post.txt":
                unexpected_files.append(f)
    if unexpected_files:
        penalty = min(10, len(unexpected_files) * 5)
        penalty_reason = f"Unexpected files in publish/: {', '.join(unexpected_files)}"
        details.append({
            "item": "No unexpected files in publish/",
            "score": -penalty,
            "max_score": 0,
            "passed": False,
            "reason": penalty_reason
        })
        total_score -= penalty

    # 确保总分在0-100之间
    final_score = max(0, min(100, total_score))

    result = {
        "total_score": final_score,
        "details": details
    }
    return result

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
