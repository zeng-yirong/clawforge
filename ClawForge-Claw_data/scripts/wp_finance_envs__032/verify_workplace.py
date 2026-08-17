import sys, os, json, re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_max = 100

# ---------- 1. Output file existence (10) ----------
max1 = 10
brief_path = os.path.join(workspace, "ops", "tech_brief.json")
if os.path.isfile(brief_path):
    score_details.append({"item": "Output file ops/tech_brief.json exists", "score": max1, "max_score": max1, "passed": True, "reason": "File found"})
else:
    score_details.append({"item": "Output file ops/tech_brief.json exists", "score": 0, "max_score": max1, "passed": False, "reason": "File missing"})
    # if file missing, can't check further content, write score and exit
    total_score = 0
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# ---------- 2. File is valid JSON (10) ----------
max2 = 10
try:
    with open(brief_path, "r") as f:
        data = json.load(f)
    score_details.append({"item": "tech_brief.json is valid JSON", "score": max2, "max_score": max2, "passed": True, "reason": "Parsed OK"})
except Exception as e:
    score_details.append({"item": "tech_brief.json is valid JSON", "score": 0, "max_score": max2, "passed": False, "reason": f"Invalid JSON: {e}"})
    total_score = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# ---------- 3. Required fields present (30) ----------
max3 = 30
required_fields = ["recommendation", "reasons", "risks", "ticker"]
missing_fields = [f for f in required_fields if f not in data]
if not missing_fields and isinstance(data.get("reasons"), list) and isinstance(data.get("risks"), list):
    score_details.append({"item": "Required fields (recommendation, ticker, reasons, risks) present and correctly typed", "score": max3, "max_score": max3, "passed": True, "reason": "All fields present"})
else:
    reasons = "Missing fields: " + ", ".join(missing_fields) if missing_fields else "Types incorrect (reasons/risks must be lists)"
    score_details.append({"item": "Required fields present and typed correct", "score": 0, "max_score": max3, "passed": False, "reason": reasons})

# ---------- 4. Recommendation correctness (40) ----------
max4 = 40
ticker = data.get("ticker", "")
recommendation = data.get("recommendation", "")

# Load environment data to verify
try:
    with open(os.path.join(workspace, "data", "news.json")) as f:
        news_data = json.load(f)
    with open(os.path.join(workspace, "data", "earnings.json")) as f:
        earnings_data = json.load(f)
except Exception as e:
    score_details.append({"item": "Recommendation correctness", "score": 0, "max_score": max4, "passed": False, "reason": f"Cannot read data files: {e}"})
    total_score = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f)
    sys.exit(0)

# Collect latest Q2 2026 eps_beat_pct for TECH and NXTC
target_tickers = ["TECH", "NXTC"]
eps_beat = {}
for t in target_tickers:
    q2 = [e for e in earnings_data if e["ticker"] == t and e["quarter"] == "Q2 2026"]
    if q2:
        eps_beat[t] = q2[0]["eps_beat_pct"]
    else:
        eps_beat[t] = -1

# Find bullish news for tech stocks (sentiment="bullish" and related_tickers includes TECH or NXTC)
tech_news_count = {}
for n in news_data:
    for t in target_tickers:
        if t in n.get("related_tickers", []) and n.get("sentiment") == "bullish":
            tech_news_count[t] = tech_news_count.get(t, 0) + 1

# Ground truth: TECH has higher EPS beat (15.27) and at least 2 bullish news
true_ticker = "TECH"
true_reason_eps = "15.27% EPS beat"
true_reason_news = "bullish partnership and earnings news"

passed_recommendation = False
reason_eps_found = False
reason_news_found = False

# Check if ticker == "TECH"
if ticker == true_ticker:
    passed_recommendation = True

# Check reasons contain EPS beat percentage and mention news
if isinstance(data.get("reasons"), list):
    for r in data["reasons"]:
        r_str = str(r)
        # Check for EPS beat number between 15 and 16 (allow formatting)
        if re.search(r'1[4-6]\.?\d*\s*%', r_str):
            reason_eps_found = True
        # Check for reference to partnership or earnings news
        if re.search(r'partner|earnings|record|cloud', r_str, re.IGNORECASE):
            reason_news_found = True

score4 = 0
# Sub-scores: ticker=20, eps reason=10, news reason=10
if passed_recommendation:
    score4 += 20
if reason_eps_found:
    score4 += 10
if reason_news_found:
    score4 += 10

reason4_parts = []
if not passed_recommendation:
    reason4_parts.append(f"Expected ticker TECH, got {ticker}")
if not reason_eps_found:
    reason4_parts.append("Missing EPS beat percentage (≈15.27%) in reasons")
if not reason_news_found:
    reason4_parts.append("Missing reference to bullish news (partnership/earnings) in reasons")

score_details.append({"item": "Recommendation correctness", "score": score4, "max_score": max4, "passed": score4 == max4, "reason": "; ".join(reason4_parts) if reason4_parts else "Ticker and reasons correct"})

# ---------- 5. Risks present (10) ----------
max5 = 10
if isinstance(data.get("risks"), list) and len(data["risks"]) >= 1:
    score_details.append({"item": "At least one risk listed", "score": max5, "max_score": max5, "passed": True, "reason": f"Risks count = {len(data['risks'])}"})
else:
    score_details.append({"item": "At least one risk listed", "score": 0, "max_score": max5, "passed": False, "reason": "Risks missing or empty"})

# ---------- Total ----------
total_score = sum(d["score"] for d in score_details)
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": score_details}, f)
