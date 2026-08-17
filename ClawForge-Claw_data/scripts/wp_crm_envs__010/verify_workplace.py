import sys
import json
import os

def verify(workspace):
    details = []
    total_score = 0

    # 1. directory structure (10 pts)
    ops_dir = os.path.join(workspace, "ops")
    report_file = os.path.join(ops_dir, "churn_report.json")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
        if os.path.isfile(report_file):
            details.append({"item": "churn_report.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "file found"})
            total_score += 5
        else:
            details.append({"item": "churn_report.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "file missing"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ not found"})
        details.append({"item": "churn_report.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops missing"})

    # 2. JSON validity (10 pts)
    try:
        with open(report_file, 'r') as f:
            report = json.load(f)
        details.append({"item": "churn_report.json valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": "parse ok"})
        total_score += 5
    except Exception as e:
        details.append({"item": "churn_report.json valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": str(e)})
        report = None

    contacts_file = os.path.join(workspace, "data/contacts.json")
    try:
        with open(contacts_file, 'r') as f:
            contacts_data = json.load(f)
        details.append({"item": "contacts.json valid JSON", "score": 2.5, "max_score": 2.5, "passed": True, "reason": "parse ok"})
        total_score += 2.5
    except Exception as e:
        details.append({"item": "contacts.json valid JSON", "score": 0, "max_score": 2.5, "passed": False, "reason": str(e)})
        contacts_data = None

    tags_file = os.path.join(workspace, "data/tag_definitions.json")
    try:
        with open(tags_file, 'r') as f:
            tags_data = json.load(f)
        details.append({"item": "tag_definitions.json valid JSON", "score": 2.5, "max_score": 2.5, "passed": True, "reason": "parse ok"})
        total_score += 2.5
    except Exception as e:
        details.append({"item": "tag_definitions.json valid JSON", "score": 0, "max_score": 2.5, "passed": False, "reason": str(e)})
        tags_data = None

    # 3. report content (30 pts)
    target_ids = ["ct_101", "ct_102", "ct_103", "ct_104", "ct_105"]
    if report is not None and isinstance(report, list):
        report_ids = [item.get("contact_id") for item in report if isinstance(item, dict)]
        missing = set(target_ids) - set(report_ids)
        extra = set(report_ids) - set(target_ids)
        if not missing and not extra:
            report_score = 30
        elif not missing and extra:
            report_score = 20
        elif missing and not extra:
            report_score = 10
        else:
            report_score = 0
        details.append({"item": "Report contains correct contacts", "score": report_score, "max_score": 30, "passed": report_score == 30, "reason": f"missing {missing} extra {extra}"})
        total_score += report_score
    else:
        details.append({"item": "Report contains correct contacts", "score": 0, "max_score": 30, "passed": False, "reason": "report not valid list"})

    # 4. contact modifications (40 pts – 8 per contact)
    if contacts_data is not None and "contacts" in contacts_data:
        contact_map = {c["contact_id"]: c for c in contacts_data["contacts"] if "contact_id" in c}
        for cid in target_ids:
            contact = contact_map.get(cid)
            if contact is None:
                details.append({"item": f"Contact {cid} exists", "score": 0, "max_score": 8, "passed": False, "reason": "missing"})
                continue
            folder_ok = contact.get("folder") == "inactive"
            tags = contact.get("tags", [])
            tags_ok = "churn_risk" in tags
            sub = 0
            if folder_ok:
                sub += 4
            if tags_ok:
                sub += 4
            details.append({"item": f"Contact {cid} folder inactive & tags churn_risk", "score": sub, "max_score": 8, "passed": sub == 8, "reason": f"folder={contact.get('folder')}, tags={tags}"})
            total_score += sub
    else:
        details.append({"item": "Contact modifications", "score": 0, "max_score": 40, "passed": False, "reason": "contacts.json invalid"})

    # 5. tag definition (10 pts)
    if tags_data is not None and "tag_definitions" in tags_data:
        churn_tags = [t for t in tags_data["tag_definitions"] if t.get("name") == "churn_risk"]
        if churn_tags:
            cat = churn_tags[0].get("category")
            tag_score = 10 if cat is not None else 5
            details.append({"item": "churn_risk tag definition exists", "score": tag_score, "max_score": 10, "passed": tag_score == 10, "reason": f"category={cat}"})
            total_score += tag_score
        else:
            details.append({"item": "churn_risk tag definition exists", "score": 0, "max_score": 10, "passed": False, "reason": "not found"})
    else:
        details.append({"item": "churn_risk tag definition", "score": 0, "max_score": 10, "passed": False, "reason": "tag_definitions.json invalid"})

    # write result
    total_score = round(total_score)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to workplace_score.json: {total_score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
