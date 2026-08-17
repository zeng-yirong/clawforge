"""
Verifier for Business Markdown Report Task
Checks that agent produced reports/business_report.md with correct period and totals.
"""
import sys
import os
import re
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # Pre-computed expected values from env_builder (sum of 2024-Q1 rows)
    expected_period = "2024-Q1"
    expected_customer = 42 + 315 + 11          # 368
    expected_product = 1280 + 47 + 5           # 1332
    expected_ops = int(99.7 + 89 + 1.2)        # 189.9 integer? We'll compare as float but use rounding? Actually we need exact. Since csv stores "99.7" as string, sum is 189.9. Let's compute as float and compare with tolerance? Better to keep as float and exact. But the sum in Python will be 99.7+89+1.2 = 189.9, which is a float. Agent will likely sum as int? Actually metric_value in csv are mixed: 99.7 is float, 89 int, 1.2 float. Agent might read and sum, resulting 189.9. We need to decide: we expect float sum. But verifier should compare exactly? Since floats may have representation issues, we'll compare using math.isclose or allow small epsilon. We'll use decimal for exactness? Simpler: compute the expected sum as decimal (189.9) and compare with tolerance 1e-9. Or we can force all values to be integers in env_builder to avoid float issues. Let's change env_builder to make ops values all integers. E.g., server_uptime = 997 (representing 99.7%), avg_response_time = 12 (representing 1.2s). But the prompt doesn't specify scale; better keep as integers. I'll modify env_builder to use integers for ops too: server_uptime 997, incidents_resolved 89, avg_response_time 12 -> sum = 1098. Then expected_ops = 1098. That's cleaner. However, I already wrote env_builder with floats. Let's adjust now in this output. To keep consistency, I'll rewrite env_builder with integers for ops. (We are generating all files now, so we can fix.)
    # Actually, we must ensure that the numbers used in verifier match env_builder exactly. Let's recompute: 
    # customer: 42+315+11 = 368
    # product: 1280+47+5 = 1332
    # ops: we need integers. Let's set server_uptime=997, incidents=89, avg_response_time=12 => 1098.
    # So modify env_builder accordingly.
    
    # We'll define expected values here (hardcoded).
    EXPECTED_PERIOD = "2024-Q1"
    EXPECTED_CUSTOMER = 368
    EXPECTED_PRODUCT = 1332
    EXPECTED_OPS = 1098

    # 1. Check reports/ directory exists (10 pts)
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        results.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found"})
        total_score += 10
    else:
        results.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found"})

    # 2. Check business_report.md exists (10 pts)
    report_path = os.path.join(reports_dir, "business_report.md") if os.path.isdir(reports_dir) else os.path.join(workspace, "reports", "business_report.md")
    if os.path.isfile(report_path):
        results.append({"item": "business_report.md exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        results.append({"item": "business_report.md exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Cannot continue further
        finalize(workspace, total_score, results)
        return

    # 3. Parse content and validate format (10 pts)
    with open(report_path, "r") as f:
        content = f.read()

    # Expected pattern
    pattern = r"# Business Report\s*\*\*Period\*\*:\s*(\S+)\s*\*\*Total Customer Metrics\*\*:\s*(\d+)\s*\*\*Total Product Metrics\*\*:\s*(\d+)\s*\*\*Total Ops Metrics\*\*:\s*(\d+)"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        period = match.group(1)
        customer_val = int(match.group(2))
        product_val = int(match.group(3))
        ops_val = int(match.group(4))
        results.append({"item": "report format valid", "score": 10, "max_score": 10, "passed": True, "reason": "Pattern matched"})
        total_score += 10
    else:
        results.append({"item": "report format valid", "score": 0, "max_score": 10, "passed": False, "reason": "Could not extract required fields"})
        finalize(workspace, total_score, results)
        return

    # 4. Check Period (10 pts)
    if period == EXPECTED_PERIOD:
        results.append({"item": "Period correct", "score": 10, "max_score": 10, "passed": True, "reason": f"Period is {EXPECTED_PERIOD}"})
        total_score += 10
    else:
        results.append({"item": "Period correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {EXPECTED_PERIOD}, got {period}"})

    # 5. Check Customer total (20 pts)
    if customer_val == EXPECTED_CUSTOMER:
        results.append({"item": "Customer total correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Value is {EXPECTED_CUSTOMER}"})
        total_score += 20
    else:
        results.append({"item": "Customer total correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {EXPECTED_CUSTOMER}, got {customer_val}"})

    # 6. Check Product total (20 pts)
    if product_val == EXPECTED_PRODUCT:
        results.append({"item": "Product total correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Value is {EXPECTED_PRODUCT}"})
        total_score += 20
    else:
        results.append({"item": "Product total correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {EXPECTED_PRODUCT}, got {product_val}"})

    # 7. Check Ops total (20 pts)
    if ops_val == EXPECTED_OPS:
        results.append({"item": "Ops total correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Value is {EXPECTED_OPS}"})
        total_score += 20
    else:
        results.append({"item": "Ops total correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {EXPECTED_OPS}, got {ops_val}"})

    finalize(workspace, total_score, results)

def finalize(workspace, total_score, results):
    # Cap at 100
    total_score = min(total_score, 100)
    output = {
        "total_score": total_score,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
