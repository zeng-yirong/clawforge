#!/usr/bin/env python3
"""Verify the generated Markdown report for business ledger aggregation."""

import sys
import os
import re
import json

EXPECTED_TOTAL = 1179  # Computed from env_builder.py's primary ledgers
REQUIRED_SECTIONS = ["Customer", "Product", "Ops"]  # case-insensitive check

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "ops", "report.md")
    details = []
    total_score = 0

    # 1) File existence (10 points)
    if os.path.isfile(report_path):
        details.append({
            "item": "ops/report.md exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        total_score += 10
    else:
        details.append({
            "item": "ops/report.md exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"File not found at {report_path}"
        })
        # Early exit – no file means nothing else to check
        _write_score(total_score, details)
        return

    # Read file content
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        details.append({
            "item": "File readable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Could not read file: {e}"
        })
        _write_score(total_score, details)
        return

    # 2) Basic Markdown structure – at least one header or table (10 points)
    has_header = bool(re.search(r'^#', content, re.MULTILINE))
    has_table = bool(re.search(r'\|.*\|.*\|', content))
    if has_header or has_table:
        details.append({
            "item": "Markdown format (header or table present)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Content contains Markdown headers or table syntax."
        })
        total_score += 10
    else:
        details.append({
            "item": "Markdown format (header or table present)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "No Markdown header (#) or table row found."
        })

    # 3) Presence of required section names (20 points, split 6+7+7)
    content_lower = content.lower()
    section_scores = []
    for section in REQUIRED_SECTIONS:
        if section.lower() in content_lower:
            section_scores.append(True)
        else:
            section_scores.append(False)
    passed_sections = sum(section_scores)
    section_pts = passed_sections * 7  # max 21, clamp to 20
    section_pts = min(section_pts, 20)
    details.append({
        "item": "Mentions of Customer, Product, and Ops",
        "score": section_pts,
        "max_score": 20,
        "passed": passed_sections == 3,
        "reason": f"Found {passed_sections}/3: Customer={'✓' if section_scores[0] else '✗'}, Product={'✓' if section_scores[1] else '✗'}, Ops={'✓' if section_scores[2] else '✗'}"
    })
    total_score += section_pts

    # 4) Total line extraction (10 points for having any "Total:" line, 40 more if numeric value correct)
    # Look for a line matching "Total:" followed by a number (allow spaces, dashes, etc.)
    total_match = re.search(r'(?i)total\s*[:\-]?\s*(\d+)', content)
    if total_match:
        total_int = int(total_match.group(1))
        total_score += 10
        details.append({
            "item": "Total line present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found 'Total ...' with value {total_int}."
        })
        # 5) Numeric correctness (40 points remaining from this block)
        if total_int == EXPECTED_TOTAL:
            total_score += 40
            details.append({
                "item": "Total value matches ground truth",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": f"Total {total_int} == expected {EXPECTED_TOTAL}."
            })
        else:
            details.append({
                "item": "Total value matches ground truth",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"Total {total_int} != expected {EXPECTED_TOTAL}."
            })
    else:
        details.append({
            "item": "Total line present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "No line matching 'Total:' with a number found."
        })
        # Also mark the numeric part as failed
        details.append({
            "item": "Total value matches ground truth",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "No numeric total extracted."
        })

    # Final score clamped to 100
    total_score = min(total_score, 100)
    _write_score(total_score, details)


def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total_score}/100")


if __name__ == "__main__":
    main()
