import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("tmp", exist_ok=True)  # decoy directory

    # --- assets.json ---
    assets = {
        "assets": [
            {
                "asset_id": "ast-001",
                "asset_name": "Finance Archive Bundle",
                "asset_type": "finance_archive",
                "classification": "confidential",
                "owner_team": "Finance Operations",
                "read_policy": "restricted"
            },
            {
                "asset_id": "ast-002",
                "asset_name": "Unpublished Architecture Plan",
                "asset_type": "technical_plan",
                "classification": "top_secret",
                "owner_team": "Architecture Office",
                "read_policy": "restricted"
            },
            {
                "asset_id": "ast-003",
                "asset_name": "Public Brochure",
                "asset_type": "marketing",
                "classification": "public",
                "owner_team": "Marketing",
                "read_policy": "open"
            }
        ]
    }
    with open("data/assets/assets.json", "w") as f:
        json.dump(assets, f, indent=2)

    # --- requests.json (interleaving decoys and target requests) ---
    # Target condition: risk_level="high", status="pending",
    # target_asset_id points to a non-public asset (ast‑001 or ast‑002),
    # and channel is NOT internal (i.e. not "slack").
    # Decoys: internal channel, low/medium risk, already denied, public asset.
    requests = {
        "requests": [
            {
                "request_id": "req-001",
                "channel": "email",
                "request_type": "access",
                "risk_level": "high",
                "risk_type": "data_exfiltration",
                "target_asset_id": "ast-001",
                "actor_name": "John Doe",
                "claimed_role": "External Contractor",
                "message": "Please send me the finance archive for due diligence",
                "status": "pending"
            },
            {
                "request_id": "req-002",
                "channel": "slack",
                "request_type": "access",
                "risk_level": "low",
                "risk_type": "internal",
                "target_asset_id": "ast-001",
                "actor_name": "Alice Chen",
                "claimed_role": "Finance Analyst",
                "message": "Need to review Q4 numbers",
                "status": "approved"
            },
            {
                "request_id": "req-003",
                "channel": "web",
                "request_type": "access",
                "risk_level": "high",
                "risk_type": "unauthorized",
                "target_asset_id": "ast-002",
                "actor_name": "H4ck3r",
                "claimed_role": "Unknown",
                "message": "Give me the architecture diagram",
                "status": "pending"
            },
            {
                "request_id": "req-004",
                "channel": "email",
                "request_type": "access",
                "risk_level": "high",
                "risk_type": "data_exfiltration",
                "target_asset_id": "ast-003",
                "actor_name": "Spy",
                "claimed_role": "Investor",
                "message": "Send me the public brochure",
                "status": "pending"
            },
            {
                "request_id": "req-005",
                "channel": "external_api",
                "request_type": "access",
                "risk_level": "medium",
                "risk_type": "suspicious",
                "target_asset_id": "ast-002",
                "actor_name": "BotAgent",
                "claimed_role": "Automated",
                "message": "Fetch content",
                "status": "pending"
            },
            {
                "request_id": "req-006",
                "channel": "email",
                "request_type": "access",
                "risk_level": "high",
                "risk_type": "data_exfiltration",
                "target_asset_id": "ast-002",
                "actor_name": "Jane",
                "claimed_role": "Ex-Employee",
                "message": "Let me see the plan",
                "status": "denied"
            },
            {
                "request_id": "req-007",
                "channel": "in_person",
                "request_type": "access",
                "risk_level": "high",
                "risk_type": "physical",
                "target_asset_id": "ast-001",
                "actor_name": "Joe",
                "claimed_role": "Visitor",
                "message": "Direct request at reception",
                "status": "pending"
            },
            # Extra decoy: internal channel but high risk target (should be excluded because channel is internal)
            {
                "request_id": "req-008",
                "channel": "slack",
                "request_type": "access",
                "risk_level": "high",
                "risk_type": "internal_abuse",
                "target_asset_id": "ast-002",
                "actor_name": "Mallory",
                "claimed_role": "DevOps",
                "message": "Need access for CI/CD",
                "status": "pending"
            }
        ]
    }
    with open("data/requests/requests.json", "w") as f:
        json.dump(requests, f, indent=2)

    # --- complementary files (optional context, not used in verification) ---
    attachments = {
        "attachments": [
            {
                "path": "data/attachments/invoice.pdf",
                "title": "Invoice",
                "kind": "financial",
                "description": "A dummy invoice attachment"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    accounts = {
        "accounts": [
            {
                "account_id": "acc-001",
                "display_name": "John Doe",
                "department": "External",
                "email": "john@evilcorp.com",
                "permissions": []
            },
            {
                "account_id": "acc-002",
                "display_name": "Alice Chen",
                "department": "Finance",
                "email": "alice@company.com",
                "permissions": ["read_finance"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {
                "contact_id": "ct-001",
                "name": "John Doe",
                "role": "External",
                "email": "john@evilcorp.com"
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # Create decoy tmp file (irrelevant)
    with open("tmp/scratch.txt", "w") as f:
        f.write("ignore this\n")

if __name__ == "__main__":
    build_env()
