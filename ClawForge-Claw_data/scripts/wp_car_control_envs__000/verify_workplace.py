import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0
    max_possible = 100

    # 1. 检查目录结构 (10分)
    dirs_ok = True
    if not os.path.isdir("ops"):
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 ops/ 目录"})
        dirs_ok = False
    else:
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录已创建"})
        total_score += 10
        dirs_ok = True

    # 2. 检查结果文件 ops/valid_high_fan_presets.json 存在且合法 (20分)
    result_path = "ops/valid_high_fan_presets.json"
    if not dirs_ok:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 20, "passed": False, "reason": "ops目录不存在，无法检查文件"})
    else:
        if not os.path.isfile(result_path):
            details.append({"item": "结果文件存在", "score": 0, "max_score": 20, "passed": False, "reason": f"文件 {result_path} 不存在"})
        else:
            try:
                with open(result_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    details.append({"item": "结果文件格式", "score": 0, "max_score": 20, "passed": False, "reason": "文件内容不是JSON数组"})
                else:
                    details.append({"item": "结果文件存在且合法", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且为有效JSON数组"})
                    total_score += 20
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                details.append({"item": "结果文件格式", "score": 0, "max_score": 20, "passed": False, "reason": f"JSON解析失败: {str(e)}"})

    # 3. 验证内容（70分）
    # 先加载原始预设文件获取正确答案
    try:
        with open("data/ac_presets.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        presets = raw.get("presets", [])
    except Exception:
        presets = []

    # 定义有效的预设: 必须是包含 preset_id 且 fan_speed == "high" 且类型为字符串（排除旧格式）
    expected_ids = set()
    for p in presets:
        if isinstance(p, dict) and "preset_id" in p and isinstance(p["preset_id"], str) and p.get("fan_speed") == "high":
            # 进一步排除明显格式异常（preset_id 以数字或特殊字符？这里只信任标准ID）
            expected_ids.add(p["preset_id"])

    # 正确答案：preset_001, preset_005, preset_007 （preset_009虽然是high但ac_enabled类型为字符串，可视为脏数据，不包含在预期内，取决于设计：这里我们定义为只取标准格式的预设）
    # 注意 duplicate_preset 的 preset_001 其 fan_speed 为 auto，被覆盖？但文件中有两个preset_001，其中一个是high，一个是auto。
    # 因为预设列表中有重复ID，agent应去重？prompt只说“把风扇转速设定为‘high’的有效预设对应的预设ID全部提取出来”，未明确去重。但重复ID应只保留一个？逻辑上取唯一ID。
    # 但为了答案唯一，我们规定只要ID存在且任意一条记录的fan_speed为high就算，去重后得到唯一ID集合。
    # 最终预期：preset_001 (因为valid_presets中第一个preset_001是high)，preset_005, preset_007。共3个。
    # preset_009虽然fan_speed=high，但ac_enabled为字符串，视为无效格式，不纳入。
    expected = {"preset_001", "preset_005", "preset_007"}
    # 但注意干扰项中有重复的preset_001（fan_speed=auto）可能会让agent困惑。预期仍然是preset_001因为valid有一条是high。

    if not os.path.isfile(result_path):
        # 已经在前一步扣分了，这里跳过内容分
        details.append({"item": "内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": "文件不存在，无法验证内容"})
    else:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            details.append({"item": "内容正确性", "score": 0, "max_score": 70, "passed": False, "reason": "结果不是列表，无法比较"})
        else:
            returned_set = set()
            for item in data:
                if isinstance(item, str):
                    returned_set.add(item)
                # 如果agent放入对象而非字符串，则按错误处理
            # 检查是否完全等于 expected
            if returned_set == expected:
                details.append({"item": "内容正确性", "score": 70, "max_score": 70, "passed": True, "reason": f"提取到正确的ID集合: {sorted(expected)}"})
                total_score += 70
            else:
                # 部分得分：每个正确ID得23分（70/3≈23.33，取整），错误扣分
                correct_ids = returned_set & expected
                extra_ids = returned_set - expected
                missing_ids = expected - returned_set
                score_partial = 0
                reason_parts = []
                if correct_ids:
                    score_partial += len(correct_ids) * 23
                    reason_parts.append(f"正确ID: {sorted(correct_ids)}")
                if extra_ids:
                    score_partial = 0  # 有多余ID直接0分（根据题意，不能多）
                    reason_parts = ["有多余ID, 不符合要求", f"多余: {sorted(extra_ids)}"]
                if missing_ids:
                    if not extra_ids:
                        score_partial = max(0, 70 - len(missing_ids) * 23)
                        reason_parts.append(f"缺少ID: {sorted(missing_ids)}")
                # 但题目强调不能多，所以一旦有额外ID就0分
                if extra_ids:
                    score_partial = 0
                else:
                    score_partial = min(70, score_partial)
                details.append({"item": "内容正确性", "score": score_partial, "max_score": 70,
                                "passed": score_partial == 70, "reason": "; ".join(reason_parts) if reason_parts else "无信息"})
                total_score += score_partial

    # 总分约束为100以内
    final_score = min(total_score, 100)
    # 写入得分文件
    score_data = {
        "total_score": final_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)

    print(f"Total score: {final_score}/100")
    sys.exit(0 if final_score == 100 else 1)

if __name__ == "__main__":
    main()
