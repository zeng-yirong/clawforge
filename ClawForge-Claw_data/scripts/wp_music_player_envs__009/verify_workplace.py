import json
import os
import sys
from pathlib import Path

# 工作区路径
workspace = sys.argv[1] if len(sys.argv) > 1 else "."
workspace = Path(workspace)

# 结果分数结构
score_details = []
total_score = 0
max_total = 100

def check(condition, item_name, max_score, reason_if_fail):
    """单项检查，通过得满分，否则得0分"""
    if condition:
        score_details.append({
            "item": item_name,
            "score": max_score,
            "max_score": max_score,
            "passed": True,
            "reason": "符合要求"
        })
        return max_score
    else:
        score_details.append({
            "item": item_name,
            "score": 0,
            "max_score": max_score,
            "passed": False,
            "reason": reason_if_fail
        })
        return 0

# ---------- 1. 检查 report.json 是否存在 (10分) ----------
report_path = workspace / "report.json"
score = check(report_path.exists(), "结果文件 report.json 存在", 10, "report.json 未找到")
total_score += score

if not report_path.exists():
    # 如果不存在，后续检查跳过
    pass
else:
    # ---------- 2. 检查 JSON 合法性 (10分) ----------
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        json_valid = True
    except (json.JSONDecodeError, Exception):
        json_valid = False
    score = check(json_valid, "report.json 是合法 JSON", 10, "JSON 解析失败")
    total_score += score

    if json_valid:
        # ---------- 3. 检查数据结构 (20分) ----------
        # 必须是一个对象，包含 "songs" 列表和 "total_duration" 数值
        struct_ok = isinstance(report_data, dict) and "songs" in report_data and "total_duration" in report_data
        if struct_ok:
            songs_list = report_data["songs"]
            total_duration = report_data["total_duration"]
            struct_ok = isinstance(songs_list, list) and len(songs_list) > 0 and isinstance(total_duration, (int, float))
        score = check(struct_ok, "report.json 结构正确 (songs列表 + total_duration)", 20,
                      "缺少 songs 或 total_duration 字段，或类型错误")
        total_score += score

        if struct_ok:
            # ---------- 4. 检查每首歌字段 (10分) ----------
            # 每条记录必须有 song_id 和 duration 且为字符串和数字
            field_ok = all(
                isinstance(s, dict) and "song_id" in s and "duration" in s and
                isinstance(s["song_id"], str) and isinstance(s["duration"], (int, float))
                for s in songs_list
            )
            score = check(field_ok, "每条歌曲包含 song_id (str) 和 duration (int/float)", 10,
                          "存在字段缺失或类型错误")
            total_score += score

            # ---------- 5. 检查歌曲数量 (15分) ----------
            # 真实答案：播放列表“夜驾驶”中有5首英文歌（S100~S104），所以长度应为5
            # 干扰：注意播放列表包含5首英文+3首中文，但Agent应该只筛选英文歌
            expected_song_ids = {"S100", "S101", "S102", "S103", "S104"}
            actual_song_ids = {s["song_id"] for s in songs_list}
            count_correct = (len(songs_list) == 5) and (actual_song_ids == expected_song_ids)
            score = check(count_correct, "歌曲数量正确且song_id集合匹配", 15,
                          f"实际歌曲ID集合: {actual_song_ids}, 期望: {expected_song_ids}")
            total_score += score

            # ---------- 6. 检查总时长计算 (20分) ----------
            # 从环境构建的歌曲数据中，这5首英文歌的duration需要精确匹配
            # 我们需要从原数据中读取真实时长。注意env_builder里随机加了0~10，所以必须读取data/songs/songs.json
            real_songs_path = workspace / "data" / "songs" / "songs.json"
            if real_songs_path.exists():
                with open(real_songs_path, "r", encoding="utf-8") as f:
                    all_songs_data = json.load(f)["songs"]
                song_id_to_duration = {s["song_id"]: s["duration"] for s in all_songs_data}
                expected_total = sum(song_id_to_duration[sid] for sid in expected_song_ids if sid in song_id_to_duration)
            else:
                expected_total = 0  # 如果源数据不存在，则无法验证

            total_duration_ok = (abs(total_duration - expected_total) < 0.01)
            score = check(total_duration_ok, "total_duration 计算准确", 20,
                          f"实际total_duration={total_duration}, 期望={expected_total}")
            total_score += score

            # ---------- 7. 检查是否混入中文歌 (15分) ----------
            # 通过读取源数据检查每首歌的language，确保没有中文歌进入结果
            if real_songs_path.exists():
                # 重新加载以避免变量污染
                with open(real_songs_path, "r", encoding="utf-8") as f:
                    all_songs_data = json.load(f)["songs"]
                song_id_to_lang = {s["song_id"]: s["language"] for s in all_songs_data}
                no_chinese = all(song_id_to_lang.get(s["song_id"], "中文") == "英文" for s in songs_list)
                score = check(no_chinese, "结果中没有中文歌", 15,
                              "存在language不是'英文'的歌曲")
                total_score += score
            else:
                # 如果源数据不存在，视为无法验证，扣分
                score = check(False, "结果中没有中文歌（源数据缺失）", 15, "无法验证源数据")
                total_score += score

# 写入结果
total_score = min(total_score, 100)  # 防止溢出
result = {
    "total_score": total_score,
    "details": score_details
}
score_path = workspace / "workplace_score.json"
with open(score_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Verification complete. Total score: {total_score}")
