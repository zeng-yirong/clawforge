#!/usr/bin/env python3
"""
验证 Agent 生成的 ops/missing_songs.json 是否正确。
检查项：
1. 缺失的 song_id 是否全部列出且不重复
2. 是否包含多余的 song_id
3. 文件格式是否合法 JSON 且为数组
4. 目录结构是否正确
"""
import json
import os
import sys

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 预期结果：所有存在于 playlists 但不在 songs 中的 song_id
    # 从环境构建的初始数据推断
    songs_path = os.path.join(workspace, "data", "songs", "songs.json")
    playlists_path = os.path.join(workspace, "data", "playlists", "playlists.json")
    result_path = os.path.join(workspace, "ops", "missing_songs.json")

    # 1. 检查目录结构
    max_dir = 5
    dir_ok = os.path.isdir(os.path.join(workspace, "ops"))
    if dir_ok:
        details.append({"item": "ops 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops 目录已创建"})
        total_score += 5
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops 目录不存在"})

    # 2. 检查结果文件是否存在且合法 JSON
    result_exists = os.path.isfile(result_path)
    if not result_exists:
        details.append({"item": "结果文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/missing_songs.json 不存在"})
        details.append({"item": "内容正确性", "score": 0, "max_score": 85, "passed": False, "reason": "文件不存在"})
        # write score
        score_data = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"总得分: {total_score}")
        return

    try:
        result = load_json(result_path)
    except Exception as e:
        details.append({"item": "结果文件可解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        details.append({"item": "内容正确性", "score": 0, "max_score": 85, "passed": False, "reason": "文件格式无效"})
        score_data = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"总得分: {total_score}")
        return

    # 3. 验证格式：必须是 JSON 数组
    if not isinstance(result, list):
        details.append({"item": "结果文件结构", "score": 0, "max_score": 10, "passed": False, "reason": "应为 JSON 数组"})
        details.append({"item": "内容正确性", "score": 0, "max_score": 85, "passed": False, "reason": "结构错误"})
        write_score(details, total_score, workspace)
        return

    details.append({"item": "结果文件格式正确", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 数组格式正确"})
    total_score += 10

    # 4. 计算真正的幽灵曲目
    try:
        songs_data = load_json(songs_path)
        playlists_data = load_json(playlists_path)
    except Exception as e:
        details.append({"item": "读取源数据", "score": 0, "max_score": 5, "passed": False, "reason": f"无法读取 songs/playlists: {e}"})
        write_score(details, total_score, workspace)
        return

    # valid song ids
    valid_ids = set(s["song_id"] for s in songs_data.get("songs", []))
    # all song ids from playlists
    all_playlist_ids = []
    for pl in playlists_data.get("playlists", []):
        all_playlist_ids.extend(pl.get("song_ids", []))
    # 幽灵曲目 = 所有歌单中的 song_id 不在 valid_ids 中的
    expected_missing = sorted(set(sid for sid in all_playlist_ids if sid not in valid_ids))

    # 去重后的 agent 结果
    agent_ids = sorted(set(result))
    # 检查是否每个元素是字符串
    if not all(isinstance(x, str) for x in agent_ids):
        details.append({"item": "元素类型", "score": 0, "max_score": 5, "passed": False, "reason": "数组元素必须为字符串"})
        write_score(details, total_score, workspace)
        return

    # 比较集合
    agent_set = set(agent_ids)
    expected_set = set(expected_missing)
    # 是否完全匹配
    if agent_set == expected_set:
        details.append({"item": "幽灵曲目集合完全正确", "score": 75, "max_score": 75, "passed": True, "reason": f"包含了所有 {len(expected_missing)} 个幽灵曲目且无多余"})
        total_score += 75
    else:
        # 算部分分
        missing_in_agent = expected_set - agent_set
        extra_in_agent = agent_set - expected_set
        correct = agent_set & expected_set
        # 按正确比例给分
        total_expected = len(expected_set) if expected_set else 1
        correct_count = len(correct)
        # 如果预期为空但agent有，扣分
        if len(expected_set) == 0:
            if len(agent_set) == 0:
                score_here = 75
            else:
                score_here = 0
        else:
            # 正确比例 = 正确数 / 预期总数，但最多75分
            ratio = correct_count / total_expected if total_expected > 0 else 0
            score_here = int(ratio * 75)
        details.append({"item": "幽灵曲目集合正确性", "score": score_here, "max_score": 75, "passed": score_here == 75, "reason": f"预期: {sorted(expected_set)}, 实际: {sorted(agent_set)}; 缺失: {missing_in_agent}, 多余: {extra_in_agent}"})
        total_score += score_here

    # 写入最终评分
    write_score(details, total_score, workspace)
    print(f"总得分: {total_score}")

def write_score(details, total_score, workspace):
    score_data = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
