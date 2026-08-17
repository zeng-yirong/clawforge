import os
import json
from datetime import datetime, timezone

REF_DATE = "2025-04-01"
REF_DATETIME = datetime(2025, 4, 1, tzinfo=timezone.utc)

# Create ops directory with an old backup (interference)
os.makedirs("ops", exist_ok=True)
with open("ops/old_backup.json", "w") as f:
    json.dump({"note": "this is outdated"}, f)

# Category mapping
category_mapping = {
    "work email": "business_email",
    "banking": "banking",
    "shopping": "ecommerce",
    "social media": "social_media",
    "个人邮箱": "business_email",
    "company mail": "business_email"
}
with open("category_mapping.json", "w") as f:
    json.dump(category_mapping, f, indent=2)

# Password policy
policy = {
    "min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "require_special": True,
    "valid_date": REF_DATE
}
with open("vault_policy.json", "w") as f:
    json.dump(policy, f, indent=2)

# Create credentials CSV with interference
import csv
rows = [
    # id, username, password, category_raw, expiry_date, source
    # valid entries (should be kept)
    ("1", "alice", "A1b@Cdefghijk", "work email", "2025-04-10", "export_2025"),
    ("2", "bob", "X9y!Passw0rd", "company mail", "2025-05-01", "export_2025"),
    ("3", "charlie", "Z8@kLmnopqrst", "banking", "2025-06-15", "export_2025"),
    ("4", "dave", "Qw3#Rtyuiopl", "social media", "2025-07-20", "export_2025"),
    ("5", "eve", "M0n#KeyT?rd", "个人邮箱", "2025-04-05", "export_2025"),
    # expired entries (should be filtered)
    ("6", "frank", "Weak1@word", "work email", "2025-03-10", "export_legacy"),
    ("7", "grace", "ValidLongPass123!", "banking", "2025-02-28", "export_2024"),
    # weak password entries (should be filtered)
    ("8", "heidi", "short", "shopping", "2025-08-01", "export_2025"),
    ("9", "ivan", "12345678", "social media", "2025-04-15", "export_2025"),
    ("10", "judy", "NoSpecial12", "work email", "2025-04-20", "export_2025"),
    # duplicate of alice (different source, same username) - should be kept only once? Actually our rule says keep all valid and distinct; alice appears again with same password? Let's make it a different password but valid. To avoid confusion, we skip duplicates. Instead add one more valid entry.
    ("11", "karen", "P@ssw0rd!Long", "shopping", "2025-09-01", "export_2025"),
    # interference row with missing field
    ("12", "mike", "", "work email", "2025-04-10", "broken_export"),
]

# Ensure no duplicates and valid entries count
# Actually karen's password: 'P@ssw0rd!Long' length 12, has uppercase, lowercase, digit, special ( `@` and `!` ) -> valid. Category 'shopping' maps to 'ecommerce'. So we have 6 valid entries now? Let's check: alice,bob,charlie,dave,eve,karen = 6. 
# But we need unique mapping? We'll keep it. The expected vault should contain exactly 6 entries.
# However karen's expiry is 2025-09-01, valid.

with open("credentials_dump.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "username", "password", "category_raw", "expiry_date", "source"])
    writer.writerows(rows)

# Also write a notes file as interference
with open("README.txt", "w") as f:
    f.write("This directory contains credential export and policies.\n")
