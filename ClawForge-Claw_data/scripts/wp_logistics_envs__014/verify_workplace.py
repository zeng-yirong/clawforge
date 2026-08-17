"""
Verify the agent's output for wp_logistics_envs__014.
Checks ops/actions.json for correct structure and values.
"""
import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    actions_path = os.path.join(workspace, "ops", "actions.json")

    total_score = 0
    details = []

    # 1. File existence (10 points)
    if not os.path.isfile(actions_path):
        details.append({
            "item": "File ops/actions.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 无法继续验证，直接输出结果
        score = 0
        write_score(workspace, score, details)
        return
    else:
        details.append({
            "item": "File ops/actions.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found"
        })
        total_score += 10

    # 2. JSON validity (10 points)
    try:
        with open(actions_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": str(e)
        })
        write_score(workspace, total_score, details)
        return

    # 3. Contains "operations" key which is a list (10 points)
    if not isinstance(data, dict) or "operations" not in data or not isinstance(data["operations"], list):
        details.append({
            "item": "Root object has 'operations' list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing or invalid 'operations' key"
        })
        write_score(workspace, total_score, details)
        return
    else:
        details.append({
            "item": "Root object has 'operations' list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found"
        })
        total_score += 10

    ops = data["operations"]

    # 4. Has exactly 5 operations (10 points)
    if len(ops) == 5:
        details.append({
            "item": "Number of operations is 5",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {len(ops)} operations"
        })
        total_score += 10
    else:
        details.append({
            "item": "Number of operations is 5",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found {len(ops)} operations, expected 5"
        })
        # Continue checking individual operations even if count wrong

    # Helper to find an operation by action name
    def find_op(action_name):
        for op in ops:
            if isinstance(op, dict) and op.get("action") == action_name:
                return op
        return None

    # 5. approve_return (12 points)
    op = find_op("approve_return")
    if op is None:
        details.append({
            "item": "approve_return operation",
            "score": 0,
            "max_score": 12,
            "passed": False,
            "reason": "Operation not found"
        })
    else:
        correct = True
        reasons = []
        if op.get("target") != "ret_001":
            correct = False
            reasons.append(f"target expected 'ret_001', got '{op.get('target')}'")
        if op.get("reason") != "defective":
            correct = False
            reasons.append(f"reason expected 'defective', got '{op.get('reason')}'")
        if op.get("status") != "approved":
            correct = False
            reasons.append(f"status expected 'approved', got '{op.get('status')}'")
        if correct:
            details.append({
                "item": "approve_return operation",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "All fields correct"
            })
            total_score += 12
        else:
            details.append({
                "item": "approve_return operation",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": "; ".join(reasons)
            })

    # 6. inspect_return (12 points)
    op = find_op("inspect_return")
    if op is None:
        details.append({
            "item": "inspect_return operation",
            "score": 0,
            "max_score": 12,
            "passed": False,
            "reason": "Operation not found"
        })
    else:
        correct = True
        reasons = []
        if op.get("target") != "ret_003":
            correct = False
            reasons.append(f"target expected 'ret_003', got '{op.get('target')}'")
        if op.get("issue") != "wrong item":
            correct = False
            reasons.append(f"issue expected 'wrong item', got '{op.get('issue')}'")
        if op.get("resolution") != "exchange":
            correct = False
            reasons.append(f"resolution expected 'exchange', got '{op.get('resolution')}'")
        if correct:
            details.append({
                "item": "inspect_return operation",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "All fields correct"
            })
            total_score += 12
        else:
            details.append({
                "item": "inspect_return operation",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": "; ".join(reasons)
            })

    # 7. update_shipment_status (12 points)
    op = find_op("update_shipment_status")
    if op is None:
        details.append({
            "item": "update_shipment_status operation",
            "score": 0,
            "max_score": 12,
            "passed": False,
            "reason": "Operation not found"
        })
    else:
        correct = True
        reasons = []
        if op.get("target") != "ship_005":
            correct = False
            reasons.append(f"target expected 'ship_005', got '{op.get('target')}'")
        if op.get("new_status") != "shipped":
            correct = False
            reasons.append(f"new_status expected 'shipped', got '{op.get('new_status')}'")
        if op.get("carrier") != "FedEx":
            correct = False
            reasons.append(f"carrier expected 'FedEx', got '{op.get('carrier')}'")
        if correct:
            details.append({
                "item": "update_shipment_status operation",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "All fields correct"
            })
            total_score += 12
        else:
            details.append({
                "item": "update_shipment_status operation",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": "; ".join(reasons)
            })

    # 8. adjust_inventory (12 points)
    op = find_op("adjust_inventory")
    if op is None:
        details.append({
            "item": "adjust_inventory operation",
            "score": 0,
            "max_score": 12,
            "passed": False,
            "reason": "Operation not found"
        })
    else:
        correct = True
        reasons = []
        if op.get("sku") != "SKU-1002":
            correct = False
            reasons.append(f"sku expected 'SKU-1002', got '{op.get('sku')}'")
        if op.get("warehouse") != "wh_001":
            correct = False
            reasons.append(f"warehouse expected 'wh_001', got '{op.get('warehouse')}'")
        if op.get("change") != -5:
            correct = False
            reasons.append(f"change expected -5, got '{op.get('change')}'")
        if op.get("type") != "damage":
            correct = False
            reasons.append(f"type expected 'damage', got '{op.get('type')}'")
        if correct:
            details.append({
                "item": "adjust_inventory operation",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "All fields correct"
            })
            total_score += 12
        else:
            details.append({
                "item": "adjust_inventory operation",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": "; ".join(reasons)
            })

    # 9. create_reconciliation_report (12 points)
    op = find_op("create_reconciliation_report")
    if op is None:
        details.append({
            "item": "create_reconciliation_report operation",
            "score": 0,
            "max_score": 12,
            "passed": False,
            "reason": "Operation not found"
        })
    else:
        correct = True
        reasons = []
        if op.get("type") != "inventory_reconciliation":
            correct = False
            reasons.append(f"type expected 'inventory_reconciliation', got '{op.get('type')}'")
        if op.get("status") != "balanced":
            correct = False
            reasons.append(f"status expected 'balanced', got '{op.get('status')}'")
        if op.get("discrepancy") != 0:
            correct = False
            reasons.append(f"discrepancy expected 0, got '{op.get('discrepancy')}'")
        if correct:
            details.append({
                "item": "create_reconciliation_report operation",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "All fields correct"
            })
            total_score += 12
        else:
            details.append({
                "item": "create_reconciliation_report operation",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": "; ".join(reasons)
            })

    # 10. No extraneous operations? 我们不扣分，但可以提示。
    # 确保总得分不超过100
    total_score = min(total_score, 100)
    write_score(workspace, total_score, details)

def write_score(workspace, score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    result = {
        "total_score": score,
        "details": details
    }
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
