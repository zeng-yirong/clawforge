import sys, os, json, pathlib

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. ops/ directory exists (10 points)
    ops_dir = pathlib.Path(workspace) / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # 2. signals.json exists (10 points)
    signals_path = ops_dir / "signals.json"
    if signals_path.is_file():
        details.append({"item": "signals.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present"})
        total_score += 10
    else:
        details.append({"item": "signals.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # if file missing, we can still check other items but they'll mostly fail; we'll return early
        total_score = 0
        details.append({"item": "comprehensive structure", "score": 0, "max_score": 80, "passed": False, "reason": "missing signals.json, cannot continue"})
        _write_score(total_score, details)
        return

    # 3. Valid JSON (10 points)
    try:
        with open(signals_path) as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "parsed successfully"})
        total_score += 10
    except (json.JSONDecodeError, IOError) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {e}"})
        _write_score(total_score, details)
        return

    # 4. Contains exactly three keys (5 points)
    expected_keys = {"reports", "presentations", "media_samples"}
    actual_keys = set(data.keys())
    if actual_keys == expected_keys:
        details.append({"item": "top-level keys", "score": 5, "max_score": 5, "passed": True, "reason": "keys are correct"})
        total_score += 5
    else:
        details.append({"item": "top-level keys", "score": 0, "max_score": 5, "passed": False, "reason": f"expected {expected_keys}, got {actual_keys}"})

    # 5. reports category content (30 points)
    reports_correct = 0
    reports_max = 30
    expected_reports = [
        {"id": "rpt-004", "clue": "Comparison of edge AI platforms."}
    ]
    actual_reports = data.get("reports", [])
    if len(actual_reports) == 1 and isinstance(actual_reports, list):
        reports_correct += 10  # length correct
        if actual_reports[0].get("id") == expected_reports[0]["id"]:
            reports_correct += 10
        if actual_reports[0].get("clue") == expected_reports[0]["clue"]:
            reports_correct += 10
        if set(actual_reports[0].keys()) == {"id", "clue"}:
            reports_correct += 5  # bonus - extra credit, but we already have max 30 -> cap
            # cap at 30
            if reports_correct > 30:
                reports_correct = 30
    else:
        reports_correct = 0
    details.append({"item": "reports content", "score": reports_correct, "max_score": reports_max, "passed": reports_correct == reports_max, "reason": f"got {reports_correct}/{reports_max}"})
    total_score += reports_correct

    # 6. presentations category content (30 points)
    presentations_correct = 0
    presentations_max = 30
    expected_presentations = [
        {"id": "prs-003", "clue": "HelioSync Edge Inference Fabric enables real-time video analytics at the edge. deployment plan included."}
    ]
    actual_presentations = data.get("presentations", [])
    if len(actual_presentations) == 1 and isinstance(actual_presentations, list):
        presentations_correct += 10
        if actual_presentations[0].get("id") == expected_presentations[0]["id"]:
            presentations_correct += 10
        if actual_presentations[0].get("clue") == expected_presentations[0]["clue"]:
            presentations_correct += 10
        if set(actual_presentations[0].keys()) == {"id", "clue"}:
            presentations_correct = min(presentations_correct + 5, 30)
    details.append({"item": "presentations content", "score": presentations_correct, "max_score": presentations_max, "passed": presentations_correct == presentations_max, "reason": f"got {presentations_correct}/{presentations_max}"})
    total_score += presentations_correct

    # 7. media_samples category content (30 points)
    media_correct = 0
    media_max = 30
    expected_media = [
        {"id": "med-004", "clue": "Podcast discussion on deploying HelioSync Edge Inference Fabric in manufacturing environments. Key takeaway: reduced latency and real-time control."}
    ]
    actual_media = data.get("media_samples", [])
    if len(actual_media) == 1 and isinstance(actual_media, list):
        media_correct += 10
        if actual_media[0].get("id") == expected_media[0]["id"]:
            media_correct += 10
        if actual_media[0].get("clue") == expected_media[0]["clue"]:
            media_correct += 10
        if set(actual_media[0].keys()) == {"id", "clue"}:
            media_correct = min(media_correct + 5, 30)
    details.append({"item": "media_samples content", "score": media_correct, "max_score": media_max, "passed": media_correct == media_max, "reason": f"got {media_correct}/{media_max}"})
    total_score += media_correct

    # 8. No extra fields in any entry (5 points) – already partly covered, but check all
    extra_fields_penalty = 0
    for cat in ["reports", "presentations", "media_samples"]:
        for entry in data.get(cat, []):
            if set(entry.keys()) != {"id", "clue"}:
                extra_fields_penalty = 1
                break
    if extra_fields_penalty == 0 and actual_keys == expected_keys:
        details.append({"item": "no extra fields in entries", "score": 5, "max_score": 5, "passed": True, "reason": "all entries have only id and clue"})
        total_score += 5
    else:
        details.append({"item": "no extra fields in entries", "score": 0, "max_score": 5, "passed": False, "reason": "found extra fields or unexpected keys"})

    # 9. Bonus: exactly the two missing categories (we already count) but we need to ensure no extra categories
    # Already covered in key check.

    # Cap total at 100
    total_score = min(total_score, 100)
    _write_score(total_score, details)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
