import sys
import os
import json
import csv
import math

def load_json(ws, path):
    full = os.path.join(ws, path)
    if not os.path.isfile(full):
        return None
    with open(full, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查必备目录结构 (10分)
    required_dirs = ["data/customers", "data/logs", "data/news", "cache"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 2.5
    if dir_score == 10:
        passed = True
        reason = "所有必需目录存在"
    else:
        passed = False
        reason = f"缺少某些目录，得分{dir_score}/10"
    details.append({"item": "directory_structure", "score": dir_score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += dir_score

    # 2. 检查 source 数据文件合法性 (10分)
    src_files = ["data/customers/customers.json", "data/logs/activity_logs.json", "data/news/news_samples.json"]
    src_score = 0
    for f in src_files:
        data = load_json(workspace, f)
        if data is not None:
            src_score += 10/3
    src_score = round(src_score, 2)
    if src_score == 10:
        passed = True
        reason = "所有源数据文件可解析"
    else:
        passed = False
        reason = f"部分源文件缺失或损坏，得分{src_score}/10"
    details.append({"item": "source_data_validity", "score": src_score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += src_score

    # 3. 检查产物文件 cache/retention_emails.json 存在且合法 (10分)
    prod = load_json(workspace, "cache/retention_emails.json")
    prod_valid_score = 0
    if prod is not None:
        if isinstance(prod, list) and len(prod) > 0:
            prod_valid_score = 10
            passed = True
            reason = "产物存在且为合法JSON数组"
        else:
            passed = False
            reason = "产物不是非空数组"
    else:
        passed = False
        reason = "产物文件不存在"
    details.append({"item": "product_existence", "score": prod_valid_score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += prod_valid_score

    if prod_valid_score < 10:
        # 如果产物无效，后续无法评分，直接输出
        final = {"total_score": int(total_score), "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final, indent=2))
        return

    # 4. 验证产物内容：必须包含且只包含客户C001和C002，每个客户一条记录 (30分)
    content_score = 0
    expected_ids = {"C001", "C002"}
    actual_ids = set()
    errors = []
    for item in prod:
        if not isinstance(item, dict):
            errors.append("存在非字典元素")
            continue
        cid = item.get("customer_id")
        if cid is None:
            errors.append("缺少customer_id")
        else:
            actual_ids.add(cid)
    # 检查覆盖
    if actual_ids == expected_ids:
        content_score += 20
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = ""
        if missing:
            reason += f"缺少客户: {missing}; "
        if extra:
            reason += f"多余客户: {extra}; "
        errors.append(reason)
    # 检查每个记录必要字段
    required_fields = ["customer_id", "customer_name", "industry", "news_id", "subject", "body"]
    field_ok = True
    for item in prod:
        for field in required_fields:
            if field not in item:
                field_ok = False
                errors.append(f"记录中缺少字段 {field}")
                break
    if field_ok:
        content_score += 10
    else:
        content_score += 0
    if errors:
        passed = False
        reason = "; ".join(errors)
    else:
        passed = True
        reason = "产物包含正确客户且字段完整"
    details.append({"item": "product_content_correctness", "score": content_score, "max_score": 30, "passed": passed, "reason": reason})
    total_score += content_score

    # 5. 验证引用的新闻ID准确 (20分)
    news_score = 0
    # 根据客户行业和新闻pain_point确定正确映射
    correct_map = {
        "C001": "N001",  # fintech -> N001 (pain_point)
        "C002": "N003"   # retail -> N003 (pain_point)
    }
    news_errors = []
    for item in prod:
        cid = item.get("customer_id")
        nid = item.get("news_id")
        expected_nid = correct_map.get(cid)
        if cid in expected_ids and nid == expected_nid:
            news_score += 10  # 每个正确10分，共20
        elif cid in expected_ids:
            news_errors.append(f"{cid} 引用了 {nid}，期望 {expected_nid}")
    if news_errors:
        passed = False
        reason = "; ".join(news_errors)
    else:
        passed = True
        reason = "所有高危客户引用了正确的行业痛点新闻"
    details.append({"item": "news_mapping_accuracy", "score": news_score, "max_score": 20, "passed": passed, "reason": reason})
    total_score += news_score

    # 6. 验证主题格式与正文完整性 (10分)
    subject_score = 0
    for item in prod:
        subject = item.get("subject", "")
        cname = item.get("customer_name", "")
        expected_subject = f"Retention Offer for {cname}"
        if subject == expected_subject:
            subject_score += 5  # 每条记录5分，共10分
        body = item.get("body", "")
        if isinstance(body, str) and len(body) > 20:
            subject_score += 5  # 正文有长度即可
    if subject_score == 10:
        passed = True
        reason = "主题格式正确，正文完整"
    else:
        passed = False
        reason = f"主题或正文不符合要求，得分{subject_score}/10"
    details.append({"item": "email_format", "score": subject_score, "max_score": 10, "passed": passed, "reason": reason})
    total_score += subject_score

    # 7. 检查是否有多余的无效记录 (5分)
    extra_penalty = 0
    if len(prod) > 2:
        extra_penalty = 5  # 扣分
    if extra_penalty:
        passed = False
        reason = f"存在{len(prod)-2}条多余记录"
    else:
        passed = True
        reason = "记录数量正确"
    details.append({"item": "no_extra_records", "score": max(0, 5 - extra_penalty), "max_score": 5, "passed": passed, "reason": reason})
    total_score += max(0, 5 - extra_penalty)

    # 8. 检查是否将低风险客户（C003, C004, C005）错误包含 (5分)
    bad_ids = {"C003", "C004", "C005"}
    bad_found = actual_ids & bad_ids
    if bad_found:
        passed = False
        reason = f"错误包含不应出现的客户: {bad_found}"
        score = 0
    else:
        passed = True
        reason = "未包含干扰客户"
        score = 5
    details.append({"item": "exclude_low_risk", "score": score, "max_score": 5, "passed": passed, "reason": reason})
    total_score += score

    # 最终分数四舍五入整数
    final_score = int(round(min(total_score, 100)))
    final = {"total_score": final_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    print(json.dumps(final, indent=2))

if __name__ == "__main__":
    main()
