import sys
import os
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops 目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops/ 目录存在" if dir_exists else "ops/ 目录不存在"
    })
    if dir_exists:
        total_score += 10

    # 2. 检查 night_drive_songs.json 文件是否存在
    result_path = os.path.join(workspace, "ops", "night_drive_songs.json")
    file_exists = os.path.isfile(result_path)
    details.append({
        "item": "night_drive_songs.json 文件存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "文件存在" if file_exists else "文件不存在"
    })
    if file_exists:
        total_score += 10
    else:
        # 后续检查无法进行，直接设置总分并输出
        total_score = sum(d["score"] for d in details)
        _write_score(total_score, details)
        return

    # 3. 解析 JSON 合法性
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        json_valid = True
        reason = "JSON 解析成功"
    except (json.JSONDecodeError, ValueError) as e:
        json_valid = False
        reason = f"JSON 解析失败: {e}"
    details.append({
        "item": "JSON 格式合法",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": reason
    })
    if json_valid:
        total_score += 10
    else:
        total_score = sum(d["score"] for d in details)
        _write_score(total_score, details)
        return

    # 4. 检查是否为列表
    is_list = isinstance(content, list)
    details.append({
        "item": "JSON 顶层为列表",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "顶层结构是列表" if is_list else f"顶层结构是 {type(content).__name__}"
    })
    if is_list:
        total_score += 10
    else:
        total_score = sum(d["score"] for d in details)
        _write_score(total_score, details)
        return

    # 5. 检查列表元素是否全是字符串（song_id）
    all_strings = all(isinstance(item, str) for item in content)
    details.append({
        "item": "列表元素均为字符串（歌曲ID）",
        "score": 10 if all_strings else 0,
        "max_score": 10,
        "passed": all_strings,
        "reason": "所有元素为字符串" if all_strings else "存在非字符串元素"
    })
    if all_strings:
        total_score += 10
    else:
        total_score = sum(d["score"] for d in details)
        _write_score(total_score, details)
        return

    # 6. 核心验证：内容是否与期望的唯一条目匹配
    # 期望结果（顺序无关）: ["S005", "S006", "S007"]
    expected = {"S005", "S006", "S007"}
    actual = set(content)
    if actual == expected:
        content_correct = True
        reason = f"歌曲ID集合完全匹配: {sorted(actual)}"
        score_item = 50
    elif actual < expected:
        # 缺少部分
        missing = expected - actual
        content_correct = False
        reason = f"缺少歌曲ID: {missing}"
        score_item = 0
    elif actual > expected:
        extra = actual - expected
        content_correct = False
        reason = f"包含多余歌曲ID: {extra}"
        score_item = 0
    else:
        # 大小一致但内容不同
        diff = expected.symmetric_difference(actual)
        content_correct = False
        reason = f"内容不匹配, 差异: {diff}"
        score_item = 0

    # 额外检查顺序：不强制要求顺序，但如果有多个结果且顺序不同不扣分（集合比较通过即可）
    # 但可以检查是否有重复? 集合已去重，但列表可能有重复。额外扣分？
    # 如果有重复元素（同一ID出现多次），视为多余，但集合已经处理。我们在集合比较后外加重复检查
    has_duplicates = len(content) != len(set(content))
    if has_duplicates and content_correct:
        # 虽然集合匹配，但有重复，扣分（比如扣20分，但为了保证分数合理，我们单独设一个检查项? 这里合并到reason）
        # 但为了简化，我们只通过集合比较，且不重复扣分。但最好在核心评分中加入重复检查。
        # 我们修改：在集合比较之前先检查重复，如果有重复则扣分。
        pass

    # 由于50分很大，我们可以拆分：内容正确30，无重复20。但为了简单，这里保持50分整体。
    # 但细粒度要求，我们增加一个子项：无重复ID
    # 在此检查无重复
    no_duplicates = len(content) == len(set(content))
    # 如果no_duplicates为False，则内容正确但有多余重复，扣掉重复分
    # 我们调整：正确的内容（集合匹配）赋值30分，无重复赋值20分
    total_remaining = 50
    if content_correct:
        score_base = 30
        reason_base = f"集合匹配, 包含 {sorted(actual)}"
    else:
        score_base = 0
        reason_base = reason
    if no_duplicates:
        score_dup = 20
        reason_dup = "无重复元素"
    else:
        score_dup = 0
        reason_dup = f"存在重复元素 (列表长度 {len(content)}, 集合长度 {len(set(content))})"
    total_content_score = score_base + score_dup
    content_reason = f"{reason_base}; {reason_dup}"
    details.append({
        "item": "核心内容验证：歌曲ID集合匹配且无重复",
        "score": total_content_score,
        "max_score": 50,
        "passed": content_correct and no_duplicates,
        "reason": content_reason
    })
    total_score += total_content_score

    _write_score(total_score, details)

def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Score written: total={total_score}")

if __name__ == "__main__":
    verify()
