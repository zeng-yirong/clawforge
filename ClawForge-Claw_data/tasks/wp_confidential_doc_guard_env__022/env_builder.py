import os
import json
import random

def build_env():
    # Ensure base directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("requests", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. accounts.json (optional, not used in task but provides context)
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "display_name": "Alice Wang", "department": "Architecture Office", "email": "alice@example.com", "permissions": ["read"]},
            {"account_id": "acc_002", "display_name": "Bob Li", "department": "Finance Operations", "email": "bob@example.com", "permissions": ["read", "write"]},
            {"account_id": "acc_003", "display_name": "Eve Zhou", "department": "Security", "email": "eve@example.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. assets.json – key assets, some confidential some public
    assets = {
        "assets": [
            {
                "asset_id": "ast_001",
                "asset_name": "Finance Archive Bundle",
                "asset_type": "finance_archive",
                "classification": "confidential",
                "owner_team": "Finance Operations",
                "read_policy": "restricted"
            },
            {
                "asset_id": "ast_002",
                "asset_name": "Unpublished Architecture Plan",
                "asset_type": "technical_plan",
                "classification": "confidential",
                "owner_team": "Architecture Office",
                "read_policy": "restricted"
            },
            {
                "asset_id": "ast_003",
                "asset_name": "Published Q3 Report",
                "asset_type": "finance_archive",
                "classification": "public",
                "owner_team": "Finance Operations",
                "read_policy": "open"
            },
            {
                "asset_id": "ast_004",
                "asset_name": "Legacy Network Diagram",
                "asset_type": "technical_plan",
                "classification": "public",
                "owner_team": "Architecture Office",
                "read_policy": "open"
            },
            {
                "asset_id": "ast_005",
                "asset_name": "Internal Meeting Notes",
                "asset_type": "document",
                "classification": "internal",
                "owner_team": "Engineering",
                "read_policy": "team"
            }
        ]
    }
    with open("data/assets/assets.json", "w") as f:
        json.dump(assets, f, indent=2)

    # 3. attachments.json (distractor)
    attachments = {
        "attachments": [
            {"path": "attachments/readme.txt", "title": "README", "kind": "text", "description": "Attachment placeholder"},
            {"path": "attachments/schema.pdf", "title": "Database Schema", "kind": "pdf", "description": "ER diagrams"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 4. contacts.json (distractor)
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Support Bot", "role": "service", "email": "bot@example.com"},
            {"contact_id": "c002", "name": "Jane Doe", "role": "analyst", "email": "jane@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 5. requests.json – the core data with distractors
    # We'll create 12 requests. Only 3 should be denied: REQ-002, REQ-007, REQ-011
    # Rules: risk_level=high, target asset classification=confidential, status=pending
    requests_list = []
    # Define a helper to create request dict
    def make_req(req_id, risk, target_asset, status, actor="unknown", channel="api", msg="Access attempt"):
        return {
            "request_id": req_id,
            "channel": channel,
            "request_type": "read",
            "risk_level": risk,
            "risk_type": "exfiltration" if risk == "high" else "normal",
            "target_asset_id": target_asset,
            "actor_name": actor,
            "claimed_role": "external",
            "message": msg,
            "status": status
        }

    # True positives (target confidential assets, high risk, pending)
    requests_list.append(make_req("REQ-002", "high", "ast_001", "pending", actor="MaliciousIP_1", msg="Attempt to access Finance Archive"))
    requests_list.append(make_req("REQ-007", "high", "ast_002", "pending", actor="MaliciousIP_2", msg="Attempt to access Architecture Plan"))
    # One more: different asset but same confidential
    requests_list.append(make_req("REQ-011", "high", "ast_001", "pending", actor="Suspicious_3", msg="Repeated access attempt"))

    # Distractors
    # Low risk, pending, confidential asset (should NOT deny because risk not high)
    requests_list.append(make_req("REQ-001", "low", "ast_001", "pending", actor="InternalAudit", msg="Scheduled audit"))
    # High risk, but asset is public (should not deny)
    requests_list.append(make_req("REQ-003", "high", "ast_003", "pending", actor="ScraperBot", msg="Query public report"))
    # High risk, confidential asset but already denied (status=denied, not pending)
    requests_list.append(make_req("REQ-004", "high", "ast_002", "denied", actor="OldThreat", msg="Previously blocked"))
    # Medium risk, confidential asset (not high)
    requests_list.append(make_req("REQ-005", "medium", "ast_002", "pending", actor="TestUser", msg="Test access"))
    # High risk, but asset not in list (ast_005 is internal, not confidential)
    requests_list.append(make_req("REQ-006", "high", "ast_005", "pending", actor="Curious_External", msg="Try internal notes"))
    # Low risk, public asset
    requests_list.append(make_req("REQ-008", "low", "ast_003", "pending", actor="NormalUser", msg="Lookup public data"))
    # High risk, confidential asset, but already completed (status=completed)
    requests_list.append(make_req("REQ-009", "high", "ast_001", "completed", actor="CompromisedAccount", msg="Already accessed"))
    # Medium risk, public asset
    requests_list.append(make_req("REQ-010", "medium", "ast_004", "pending", actor="Partner", msg="Review legacy diagram"))
    # One more distractor: duplicate request ID? No, make unique.
    # Add a request with missing target asset (should be ignored or cause error? we ignore)
    requests_list.append(make_req("REQ-012", "high", "ast_999", "pending", actor="Unknown", msg="Target non-existent"))

    # Shuffle to avoid order clues
    random.shuffle(requests_list)
    requests_data = {"requests": requests_list}
    with open("requests/requests.json", "w") as f:
        json.dump(requests_data, f, indent=2)

    # Create some unrelated files to add noise
    with open("ops/log.txt", "w") as f:
        f.write("Previous run logs...\n")
    with open("data/report.csv", "w") as f:
        f.write("id,value\n1,abc\n2,def\n")

if __name__ == "__main__":
    build_env()
