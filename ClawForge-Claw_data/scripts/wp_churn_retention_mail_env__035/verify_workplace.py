import json
import os
import sys

def collect_strings(obj):
    """递归收集所有字符串值"""
    strings = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings.extend(collect_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            strings.extend(collect_strings(item))
    return strings

def verify(workspace):
    details = []
    cache_path = os.path.join(workspace, "ops", "retention_cache.json")

    # 1. 文件存在性 (10分)
    if not os.path.exists(cache_path):
        details.append({
            "item": "缓存文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/retention_cache.json 不存在"
        })
    else:
        details.append({
            "item": "缓存文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })

        # 2. JSON 合法性 (10分)
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "JSON 合法",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "合法 JSON"
            })

            strings = collect_strings(data)

            # 3. 包含正确客户名称 LedgerFlow (25分)
            if "LedgerFlow" in strings:
                details.append({
                    "item": "包含正确客户名称",
                    "score": 25,
                    "max_score": 25,
                    "passed": True,
                    "reason": "找到客户名称 LedgerFlow"
                })
            else:
                details.append({
                    "item": "包含正确客户名称",
                    "score": 0,
                    "max_score": 25,
                    "passed": False,
                    "reason": "未找到客户名称 LedgerFlow"
                })

            # 4. 包含正确新闻标题 (25分)
            headline = "Fintech Growth Surges: New Opportunities for 2025"
            if headline in strings:
                details.append({
                    "item": "包含正确新闻标题",
                    "score": 25,
                    "max_score": 25,
                    "passed": True,
                    "reason": "找到新闻标题"
                })
            else:
                details.append({
                    "item": "包含正确新闻标题",
                    "score": 0,
                    "max_score": 25,
                    "passed": False,
                    "reason": "未找到新闻标题"
                })

            # 5. 邮件以 "Dear LedgerFlow" 开头 (30分)
            found_greeting = any("Dear LedgerFlow" in s or "Dear LedgerFlow," in s for s in strings)
            if found_greeting:
                details.append({
                    "item": "邮件以 Dear 开头包含客户名",
                    "score": 30,
                    "max_score": 30,
                    "passed": True,
                    "reason": "找到问候语 'Dear LedgerFlow'"
                })
            else:
                details.append({
                    "item": "邮件以 Dear 开头包含客户名",
                    "score": 0,
                    "max_score": 30,
                    "passed": False,
                    "reason": "未找到问候语 'Dear LedgerFlow'"
                })

        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "JSON 合法",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON 解析失败: {str(e)}"
            })
            # 后续项无法判断
            for item_name, max_s in [("包含正确客户名称", 25), ("包含正确新闻标题", 25), ("邮件以 Dear 开头包含客户名", 30)]:
                details.append({
                    "item": item_name,
                    "score": 0,
                    "max_score": max_s,
                    "passed": False,
                    "reason": "文件非合法 JSON"
                })

    total_score = sum(d["score"] for d in details)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
