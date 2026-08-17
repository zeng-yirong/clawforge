import os
import sys
import json
import re
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace).resolve()

    details = []
    total_score = 0

    # ---------- 1. Directory and file existence (10 points) ----------
    outputs_dir = ws / "outputs"
    review_path = outputs_dir / "review.md"
    roadmap_path = outputs_dir / "roadmap.mmd"

    exist_dir = outputs_dir.is_dir()
    details.append({
        "item": "outputs directory exists",
        "score": 5 if exist_dir else 0,
        "max_score": 5,
        "passed": exist_dir,
        "reason": "Directory outputs/ found." if exist_dir else "Directory outputs/ missing."
    })
    total_score += details[-1]["score"]

    exist_review = review_path.is_file()
    details.append({
        "item": "review.md exists",
        "score": 3 if exist_review else 0,
        "max_score": 3,
        "passed": exist_review,
        "reason": "File outputs/review.md found." if exist_review else "File outputs/review.md missing."
    })
    total_score += details[-1]["score"]

    exist_roadmap = roadmap_path.is_file()
    details.append({
        "item": "roadmap.mmd exists",
        "score": 2 if exist_roadmap else 0,
        "max_score": 2,
        "passed": exist_roadmap,
        "reason": "File outputs/roadmap.mmd found." if exist_roadmap else "File outputs/roadmap.mmd missing."
    })
    total_score += details[-1]["score"]

    # If any core file missing, skip further parsing
    if not (exist_review and exist_roadmap):
        details.append({
            "item": "Further checks skipped due to missing files",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "One or both expected output files not present."
        })
        _write_score(ws, total_score, details)
        return

    # ---------- 2. Format legality (10 points) ----------
    # Parse review.md
    with open(review_path, "r") as f:
        review_lines = f.readlines()

    review_items = []
    for line in review_lines:
        line = line.strip()
        m = re.match(r'^-\s+([^:]+):\s*(.*)', line)
        if m:
            review_items.append((m.group(1).strip(), m.group(2).strip()))

    review_ok = len(review_items) > 0
    details.append({
        "item": "review.md parseable bullet points",
        "score": 5 if review_ok else 0,
        "max_score": 5,
        "passed": review_ok,
        "reason": f"Found {len(review_items)} bullet points." if review_ok else "No valid bullet points found (expected '- PAPER_ID: Title')."
    })
    total_score += details[-1]["score"]

    # Parse roadmap.mmd – extract timeline rows inside ```mermaid block
    with open(roadmap_path, "r") as f:
        roadmap_text = f.read()

    timeline_rows = []
    in_mermaid = False
    for line in roadmap_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```mermaid"):
            in_mermaid = True
            continue
        if stripped.startswith("```") and in_mermaid:
            in_mermaid = False
            continue
        if in_mermaid:
            m = re.match(r'^(\d{4})\s*:\s*([^:]+)\s*:\s*(.*)', stripped)
            if m:
                year = int(m.group(1))
                pid = m.group(2).strip()
                title = m.group(3).strip()
                timeline_rows.append((year, pid, title))

    roadmap_ok = len(timeline_rows) > 0
    details.append({
        "item": "roadmap.mmd parseable timeline rows",
        "score": 5 if roadmap_ok else 0,
        "max_score": 5,
        "passed": roadmap_ok,
        "reason": f"Found {len(timeline_rows)} timeline rows." if roadmap_ok else "No valid timeline rows found (expected 'YEAR : PAPER_ID : Title' inside code block)."
    })
    total_score += details[-1]["score"]

    # If parse failed, skip further checks
    if not (review_ok and roadmap_ok):
        details.append({
            "item": "Further checks skipped due to parse failure",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "Could not extract structured data from both files."
        })
        _write_score(ws, total_score, details)
        return

    # ---------- 3. Correct paper inclusion (40 points: 20 review + 20 roadmap) ----------
    expected_papers = {
        "ev01": {"year": 2020, "title": "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks"},
        "ev02": {"year": 2020, "title": "EfficientDet: Scalable and Efficient Object Detection"},
        "ev03": {"year": 2021, "title": "MobileNetV3: Searching for MobileNetV3"},
        "ev04": {"year": 2022, "title": "ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design"},
        "ev05": {"year": 2023, "title": "EfficientFormer: Vision Transformers at MobileNet Speed"}
    }
    expected_ids = set(expected_papers.keys())

    # Review IDs
    review_ids = set(pid for pid, _ in review_items)
    correct_in_review = expected_ids & review_ids
    review_score = len(correct_in_review) * 4  # 4 per paper, max 20
    details.append({
        "item": "correct papers in review.md",
        "score": review_score,
        "max_score": 20,
        "passed": review_score == 20,
        "reason": f"Found {len(correct_in_review)} out of {len(expected_ids)} expected IDs in review."
    })
    total_score += review_score

    # Roadmap IDs
    roadmap_ids = set(pid for _, pid, _ in timeline_rows)
    correct_in_roadmap = expected_ids & roadmap_ids
    roadmap_correct_score = len(correct_in_roadmap) * 4
    details.append({
        "item": "correct papers in roadmap.mmd",
        "score": roadmap_correct_score,
        "max_score": 20,
        "passed": roadmap_correct_score == 20,
        "reason": f"Found {len(correct_in_roadmap)} out of {len(expected_ids)} expected IDs in roadmap."
    })
    total_score += roadmap_correct_score

    # ---------- 4. No extra (dirty) papers (20 points: 10 review + 10 roadmap) ----------
    allowed_ids = expected_ids  # only these should appear
    # Review extras
    review_extra = review_ids - allowed_ids
    review_extra_penalty = min(10, len(review_extra) * 5)
    details.append({
        "item": "no extra papers in review.md",
        "score": 10 - review_extra_penalty,
        "max_score": 10,
        "passed": len(review_extra) == 0,
        "reason": f"Extra IDs found: {review_extra}" if review_extra else "No extra IDs."
    })
    total_score += details[-1]["score"]

    # Roadmap extras
    roadmap_extra = roadmap_ids - allowed_ids
    roadmap_extra_penalty = min(10, len(roadmap_extra) * 5)
    details.append({
        "item": "no extra papers in roadmap.mmd",
        "score": 10 - roadmap_extra_penalty,
        "max_score": 10,
        "passed": len(roadmap_extra) == 0,
        "reason": f"Extra IDs found: {roadmap_extra}" if roadmap_extra else "No extra IDs."
    })
    total_score += details[-1]["score"]

    # ---------- 5. Year ordering & correctness (20 points: 10 order + 10 per-year match) ----------
    # Order: timeline_rows should be sorted by year ascending
    sorted_rows = sorted(timeline_rows, key=lambda x: (x[0], x[1]))  # year then ID
    order_ok = timeline_rows == sorted_rows
    details.append({
        "item": "roadmap rows sorted by year ascending",
        "score": 10 if order_ok else 0,
        "max_score": 10,
        "passed": order_ok,
        "reason": "Rows are in correct chronological order." if order_ok else "Rows are NOT in year-ascending order."
    })
    total_score += details[-1]["score"]

    # Year per paper
    year_match_score = 0
    for pid, expected_info in expected_papers.items():
        # find the entry in timeline_rows
        expected_year = expected_info["year"]
        matches = [(y, p) for y, p, t in timeline_rows if p == pid]
        if len(matches) == 1 and matches[0][0] == expected_year:
            year_match_score += 2
    details.append({
        "item": "year correctness for each paper in roadmap",
        "score": year_match_score,
        "max_score": 10,
        "passed": year_match_score == 10,
        "reason": f"Matched {year_match_score // 2} out of {len(expected_ids)} papers' years."
    })
    total_score += year_match_score

    # ---------- Write final score ----------
    _write_score(ws, total_score, details)

def _write_score(workspace, total_score, details):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = workspace / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
