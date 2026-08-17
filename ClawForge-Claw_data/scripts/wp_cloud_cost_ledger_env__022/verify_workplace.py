import sys, os, json, math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
report_path = os.path.join(workspace, "ops", "cost_report.json")
scores = []
total_score = 0

# 1. File exists
if os.path.exists(report_path):
    scores.append({"item": "report file exists", "score": 5, "max_score": 5, "passed": True, "reason": ""})
    total_score += 5
else:
    scores.append({"item": "report file exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})

if os.path.exists(report_path):
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
        scores.append({"item": "report is valid JSON", "score": 5, "max_score": 5, "passed": True, "reason": ""})
        total_score += 5
    except json.JSONDecodeError as e:
        scores.append({"item": "report is valid JSON", "score": 0, "max_score": 5, "passed": False, "reason": f"JSON decode error: {e}"})
        report = None
else:
    report = None

if report is not None:
    # 2. Check required fields
    required_fields = ['report_month', 'clusters', 'total_cost']
    missing = [f for f in required_fields if f not in report]
    if missing:
        scores.append({"item": "report contains required fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
    else:
        scores.append({"item": "report contains required fields", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total_score += 10

        # 3. report_month
        if report.get('report_month') == '2026-06':
            scores.append({"item": "report_month is correct", "score": 10, "max_score": 10, "passed": True, "reason": ""})
            total_score += 10
        else:
            scores.append({"item": "report_month is correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected '2026-06', got {report.get('report_month')}"})

        # 4. clusters array
        clusters = report.get('clusters', [])
        expected_ids = ['ads-ranking', 'lakehouse-analytics']
        if isinstance(clusters, list) and len(clusters) == 2:
            ids = [c.get('cluster_id') for c in clusters]
            if sorted(ids) == sorted(expected_ids):
                scores.append({"item": "clusters list contains exactly the two requested clusters", "score": 10, "max_score": 10, "passed": True, "reason": ""})
                total_score += 10
            else:
                scores.append({"item": "clusters list contains exactly the two requested clusters", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_ids}, got {ids}"})
        else:
            scores.append({"item": "clusters list contains exactly the two requested clusters", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected list of 2, got {clusters}"})

        # 5. Compute expected costs from original data
        ledger_path = os.path.join(workspace, "data", "resources", "resource_ledger.json")
        pricing_path = os.path.join(workspace, "data", "pricing", "pricing_catalogs.json")
        expected_ads_cost = 0.0
        expected_lakehouse_cost = 0.0

        if os.path.exists(ledger_path) and os.path.exists(pricing_path):
            with open(ledger_path) as f:
                ledger = json.load(f)
            with open(pricing_path) as f:
                catalogs = json.load(f)

            # Find active catalog for June 2026
            active_catalog = None
            for cat in catalogs:
                if cat.get('status') == 'active' and cat.get('billing_month') == '2026-06':
                    active_catalog = cat
                    break
            if active_catalog:
                rates = active_catalog.get('rates', [])
                rate_map = {}
                for r in rates:
                    key = (r['resource_family'], r['metric_code'])
                    rate_map[key] = r['price']

                # Aggregate quantities per cluster for June
                cluster_quantities = {'ads-ranking': {}, 'lakehouse-analytics': {}}
                for entry in ledger:
                    cid = entry.get('cluster_id')
                    if cid not in cluster_quantities:
                        continue
                    if entry.get('billing_month') != '2026-06':
                        continue
                    rf = entry['resource_family']
                    mc = entry['metric_code']
                    qty = entry['quantity']
                    key = (rf, mc)
                    key_val = cluster_quantities[cid]
                    key_val[key] = key_val.get(key, 0) + qty

                for cid, quants in cluster_quantities.items():
                    cost = 0.0
                    for key, qty in quants.items():
                        if key in rate_map:
                            cost += qty * rate_map[key]
                    if cid == 'ads-ranking':
                        expected_ads_cost = cost
                    elif cid == 'lakehouse-analytics':
                        expected_lakehouse_cost = cost

        expected_total = expected_ads_cost + expected_lakehouse_cost
        tolerance = 1e-6

        # Per cluster cost check
        for cl in clusters:
            cid = cl.get('cluster_id')
            cost = cl.get('cost', 0)
            if cid == 'ads-ranking':
                if abs(cost - expected_ads_cost) < tolerance:
                    scores.append({"item": f"cost for {cid} is correct", "score": 10, "max_score": 10, "passed": True, "reason": ""})
                    total_score += 10
                else:
                    scores.append({"item": f"cost for {cid} is correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_ads_cost}, got {cost}"})
            elif cid == 'lakehouse-analytics':
                if abs(cost - expected_lakehouse_cost) < tolerance:
                    scores.append({"item": f"cost for {cid} is correct", "score": 10, "max_score": 10, "passed": True, "reason": ""})
                    total_score += 10
                else:
                    scores.append({"item": f"cost for {cid} is correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_lakehouse_cost}, got {cost}"})

        # Total cost check
        if abs(report.get('total_cost', 0) - expected_total) < tolerance:
            scores.append({"item": "total_cost is correct", "score": 20, "max_score": 20, "passed": True, "reason": ""})
            total_score += 20
        else:
            scores.append({"item": "total_cost is correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_total}, got {report.get('total_cost')}"})

        # No extra clusters
        extra = [c for c in clusters if c.get('cluster_id') not in expected_ids]
        if not extra:
            scores.append({"item": "no extra clusters", "score": 10, "max_score": 10, "passed": True, "reason": ""})
            total_score += 10
        else:
            scores.append({"item": "no extra clusters", "score": 0, "max_score": 10, "passed": False, "reason": f"Found extra clusters: {extra}"})

# Ensure total_score does not exceed 100
total_score = min(total_score, 100)

result = {"total_score": total_score, "details": scores}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
