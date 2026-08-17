import os
import json

def build_env():
    # --- helper to write JSON ---
    def write_json(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    # --- accounts ---
    accounts = [
        {"account_id": "acc_001", "display_name": "Dev Mehra", "department": "Archive Ops", "email": "dev.mehra@northstar.example.com", "permissions": ["read", "write"], "default_region": "us-east", "voice": ["en"]},
        {"account_id": "acc_002", "display_name": "Keiko Han", "department": "Market Intelligence", "email": "keiko.han@northstar.example.com", "permissions": ["read"], "default_region": "eu-west", "voice": ["ja", "en"]},
        {"account_id": "acc_003", "display_name": "Rhea Morita", "department": "Signal Research", "email": "rhea.morita@northstar.example.com", "permissions": ["read", "admin"], "default_region": "ap-southeast", "voice": ["en"]}
    ]
    write_json("data/accounts.json", {"accounts": accounts})

    # --- contacts (same as schema, but also in separate file) ---
    contacts = [
        {"contact_id": "cnt_001", "name": "Dev Mehra", "role": "Archive Operations", "email": "dev.mehra@northstar.example.com"},
        {"contact_id": "cnt_002", "name": "Keiko Han", "role": "Market Intelligence Partner", "email": "keiko.han@northstar.example.com"},
        {"contact_id": "cnt_003", "name": "Rhea Morita", "role": "Signal Research Lead", "email": "rhea.morita@northstar.example.com"}
    ]
    write_json("data/contacts.json", {"contacts": contacts})

    # --- attachments ---
    # Create the solution_matching_notes.md with clues for multiple solutions.
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/solution_matching_notes.md", "w") as f:
        f.write(r"""# Solution Matching Notes

## HelioSync Edge Inference Fabric (target)
- Clue 1: Latency under 5ms at edge
- Clue 2: Supports ONNX Runtime 1.17+
- Clue 3: Native ARM NEON acceleration
- Clue 4: Integrated with Kubeless v2.3

## AeroMind Drone Core (distractor)
- Clue A: Flight endurance >45 min
- Clue B: Obstacle avoidance SDK 3.2
- Clue C: Weight <250g

## QuantumSafe Encryption Suite (distractor)
- Clue α: NIST PQC finalist integration
- Clue β: 256-bit key length minimum
- Clue γ: Hardware TPM 2.0 binding
""")
    with open("data/attachments/temp_record_guidelines.md", "w") as f:
        f.write("# Temporary Record Guidelines\n\nUse this schema for clue lists:\n- type (string): report|presentation|media_sample\n- document_id (string)\n- clues (array of strings)\n")

    # --- reports ---
    reports = [
        {
            "report_id": "rpt_101",
            "title": "Edge AI Market Outlook 2026",
            "sector": "industrial_ai",
            "published_at": "2026-03-15",
            "tags": ["edge", "inference", "market"],
            "summary": "HelioSync Edge Inference Fabric gains traction in manufacturing.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Full content ..."
        },
        {
            "report_id": "rpt_102",
            "title": "Logistics Robotics Tech Radar",
            "sector": "logistics_ai",
            "published_at": "2026-04-01",
            "tags": ["robotics", "warehouse", "edge"],
            "summary": "Comparison of edge inference solutions including HelioSync.",
            "solution_aliases": ["HelioSync Edge Inference Fabric", "AeroMind Drone Core"],
            "content": "Full content ..."
        },
        {
            "report_id": "rpt_103",
            "title": "QuantumSafe Encryption for IoT",
            "sector": "industrial_ai",
            "published_at": "2026-02-20",
            "tags": ["encryption", "quantum", "iot"],
            "summary": "Post-quantum cryptography on constrained devices.",
            "solution_aliases": ["QuantumSafe Encryption Suite"],
            "content": "Full content ..."
        }
    ]
    write_json("data/reports/reports.json", {"reports": reports})

    # --- presentations ---
    presentations = [
        {
            "presentation_id": "pres_201",
            "title": "HelioSync Deployment Patterns",
            "owner": "partner_marketing",
            "updated_at": "2026-03-28",
            "tags": ["edge", "helio", "deployment"],
            "summary": "Best practices for rolling out HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "deck_notes": "Slide deck with architecture diagrams."
        },
        {
            "presentation_id": "pres_202",
            "title": "AeroMind Drone Core Flight Control",
            "owner": "research_design",
            "updated_at": "2026-01-10",
            "tags": ["drone", "flight", "control"],
            "summary": "AeroMind SDK updates for autonomous navigation.",
            "solution_aliases": ["AeroMind Drone Core"],
            "deck_notes": "Technical overview."
        },
        {
            "presentation_id": "pres_203",
            "title": "QuantumSafe Key Exchange Demo",
            "owner": "strategy_team",
            "updated_at": "2026-04-05",
            "tags": ["quantum", "encryption", "demo"],
            "summary": "Live demo of QuantumSafe handshake.",
            "solution_aliases": ["QuantumSafe Encryption Suite"],
            "deck_notes": "Not relevant to HelioSync."
        }
    ]
    write_json("data/presentations/presentations.json", {"presentations": presentations})

    # --- media_samples ---
    media_samples = [
        {
            "sample_id": "media_301",
            "title": "Edge Inference Fabric Launch Webinar",
            "channel": "keynote_transcript",
            "captured_at": "2026-03-20T14:00:00Z",
            "tags": ["webinar", "launch", "helio"],
            "summary": "CEO unveils HelioSync Edge Inference Fabric.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Transcript ..."
        },
        {
            "sample_id": "media_302",
            "title": "Tech Talk: Accelerating Inference with ARM NEON",
            "channel": "podcast_transcript",
            "captured_at": "2026-03-22T10:30:00Z",
            "tags": ["tech", "arm", "edge"],
            "summary": "Deep dive on HelioSync's NEON acceleration.",
            "solution_aliases": ["HelioSync Edge Inference Fabric"],
            "content": "Transcript ..."
        },
        {
            "sample_id": "media_303",
            "title": "AeroMind Drone Core Pre-launch",
            "channel": "editorial_draft",
            "captured_at": "2026-02-14T08:00:00Z",
            "tags": ["drone", "prelaunch"],
            "summary": "AeroMind sneak peek for partners.",
            "solution_aliases": ["AeroMind Drone Core"],
            "content": "Draft article ..."
        }
    ]
    write_json("data/media_samples/media_samples.json", {"media_samples": media_samples})

    # --- additional distractor: an old media sample with same solution but duplicate?  add a second HelioSync but with same ID? No, unique.
    # Already 2 HelioSync media samples (301,302) – good.

    # --- make sure ops/ doesn't exist yet (agent will create)
    # All done

if __name__ == "__main__":
    build_env()
