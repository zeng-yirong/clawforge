import json
import sys
import os
from pathlib import Path

def verify(workspace):
    ws = Path(workspace)
    details = []
    total_score = 0

    # ---- 1. ops/ directory exists (5) ----
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops/ directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Directory ops/ found."
        })
        total_score += 5
    else:
        details.append({
            "item": "ops/ directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Directory ops/ missing."
        })

    # ---- 2. recommendations.json exists (10) ----
    out_file = ops_dir / "recommendations.json"
    if out_file.is_file():
        details.append({
            "item": "recommendations.json file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at ops/recommendations.json."
        })
        total_score += 10
    else:
        details.append({
            "item": "recommendations.json file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # remaining checks impossible; return early with current score
        total = sum(d["score"] for d in details)
        with open(ws / "workplace_score.json", "w") as sf:
            json.dump({"total_score": total, "details": details}, sf)
        return

    # ---- 3. JSON is valid (10) ----
    try:
        data = json.loads(out_file.read_text())
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File parsed successfully."
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        total = sum(d["score"] for d in details)
        with open(ws / "workplace_score.json", "w") as sf:
            json.dump({"total_score": total, "details": details}, sf)
        return

    # ---- 4. Contains required top-level keys (10) ----
    required_keys = ["stocks", "avg_beat_pct"]
    missing = [k for k in required_keys if k not in data]
    if not missing:
        details.append({
            "item": "Required top-level keys present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Both 'stocks' and 'avg_beat_pct' found."
        })
        total_score += 10
    else:
        details.append({
            "item": "Required top-level keys present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing keys: {missing}"
        })

    # ---- 5. stocks is a list of exactly 2 items (10) ----
    stocks = data.get("stocks", [])
    if isinstance(stocks, list) and len(stocks) == 2:
        details.append({
            "item": "stocks list length is 2",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Exactly 2 stock entries found."
        })
        total_score += 10
    else:
        details.append({
            "item": "stocks list length is 2",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 2, got {len(stocks) if isinstance(stocks, list) else 'not a list'}"
        })

    # ---- 6. Ticker correctness (15) ----
    tickers_found = set(s.get("ticker") for s in stocks if isinstance(s, dict))
    expected_tickers = {"TECH", "NXTC"}
    if tickers_found == expected_tickers:
        details.append({
            "item": "Tickers contain exactly TECH and NXTC",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Correct ticker set."
        })
        total_score += 15
    else:
        extra = tickers_found - expected_tickers
        missing_t = expected_tickers - tickers_found
        details.append({
            "item": "Tickers contain exactly TECH and NXTC",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Extra: {extra}, Missing: {missing_t}"
        })

    # ---- 7. Each stock has required subfields and correct beat_pct (20 = 10 each) ----
    tech_ok = True
    nxtc_ok = True
    tech_item = None
    nxtc_item = None
    for s in stocks:
        if s.get("ticker") == "TECH":
            tech_item = s
        elif s.get("ticker") == "NXTC":
            nxtc_item = s

    # TECH
    if tech_item and all(k in tech_item for k in ("ticker","company_name","beat_pct","headline")):
        if tech_item["beat_pct"] == 8.5:
            details.append({
                "item": "TECH stock fields and beat_pct",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "TECH beat_pct = 8.5, required fields present."
            })
            total_score += 10
        else:
            details.append({
                "item": "TECH stock fields and beat_pct",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"beat_pct is {tech_item.get('beat_pct')}, expected 8.5"
            })
    else:
        details.append({
            "item": "TECH stock fields and beat_pct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing TECH entry or required subfields (ticker, company_name, beat_pct, headline)."
        })

    # NXTC
    if nxtc_item and all(k in nxtc_item for k in ("ticker","company_name","beat_pct","headline")):
        if nxtc_item["beat_pct"] == 12.0:
            details.append({
                "item": "NXTC stock fields and beat_pct",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "NXTC beat_pct = 12.0, required fields present."
            })
            total_score += 10
        else:
            details.append({
                "item": "NXTC stock fields and beat_pct",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"beat_pct is {nxtc_item.get('beat_pct')}, expected 12.0"
            })
    else:
        details.append({
            "item": "NXTC stock fields and beat_pct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing NXTC entry or required subfields (ticker, company_name, beat_pct, headline)."
        })

    # ---- 8. avg_beat_pct correct (15) ----
    expected_avg = 10.25
    avg = data.get("avg_beat_pct")
    if isinstance(avg, (int, float)) and abs(avg - expected_avg) < 1e-6:
        details.append({
            "item": "avg_beat_pct is 10.25",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Computed average = {avg}."
        })
        total_score += 15
    else:
        details.append({
            "item": "avg_beat_pct is 10.25",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"avg_beat_pct = {avg}, expected 10.25"
        })

    # ---- 9. Headline correctness (5) ----
    headline_ok = True
    # expected headlines
    expected_headlines = {
        "TECH": "TECH launches revolutionary AI chip",
        "NXTC": "NXTC partners with leading cloud provider"
    }
    for s in stocks:
        if s.get("ticker") in expected_headlines:
            if s.get("headline") != expected_headlines[s["ticker"]]:
                headline_ok = False
                break
    if headline_ok:
        details.append({
            "item": "Headlines match expected bullish news",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Both headlines match."
        })
        total_score += 5
    else:
        details.append({
            "item": "Headlines match expected bullish news",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "One or both headlines differ from expected."
        })

    # clamp total to 100
    total_score = min(total_score, 100)

    # write workplace_score.json
    score_file = ws / "workplace_score.json"
    with open(score_file, "w") as sf:
        json.dump({"total_score": total_score, "details": details}, sf, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
