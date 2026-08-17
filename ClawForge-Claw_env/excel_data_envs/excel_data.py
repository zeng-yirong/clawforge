from __future__ import annotations

from typing import Any


def read_raw_data(session: dict[str, Any], data_id: str) -> dict[str, Any]:
    raw_data = session["raw_data"].get(data_id)
    if not raw_data:
        return {
            "success": False,
            "error": f"Raw data not found: {data_id}"
        }
    columns = list(raw_data[0].keys()) if raw_data else []
    return {
        "success": True,
        "data_id": data_id,
        "columns": columns,
        "row_count": len(raw_data)
    }


def list_raw_data(session: dict[str, Any]) -> dict[str, Any]:
    raw_data = session.get("raw_data", {})
    return {
        "success": True,
        "data_ids": list(raw_data.keys()),
        "total_datasets": len(raw_data)
    }


def deduplicate_data(session: dict[str, Any], data_id: str, key_column: str = "transaction_id") -> dict[str, Any]:
    raw_data = session["raw_data"].get(data_id)
    if not raw_data:
        return {
            "success": False,
            "error": f"Raw data not found: {data_id}"
        }

    seen_keys: set[str] = set()
    deduplicated = []
    duplicates_removed = 0

    for row in raw_data:
        key = row.get(key_column, "")
        if key and key not in seen_keys:
            seen_keys.add(key)
            deduplicated.append(dict(row))
        else:
            duplicates_removed += 1

    columns = list(raw_data[0].keys()) if raw_data else []

    session["cleaned_data"] = {
        "data_id": data_id,
        "key_column": key_column,
        "original_count": len(raw_data),
        "deduplicated_count": len(deduplicated),
        "duplicates_removed": duplicates_removed,
        "columns": columns,
        "rows": deduplicated
    }

    return {
        "success": True,
        "original_count": len(raw_data),
        "deduplicated_count": len(deduplicated),
        "duplicates_removed": duplicates_removed
    }


def fill_missing_customers(session: dict[str, Any], data_id: str) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "Run deduplication first"
        }

    cleaned = session["cleaned_data"]
    if cleaned["data_id"] != data_id:
        return {
            "success": False,
            "error": f"Data ID mismatch: expected {cleaned['data_id']}, got {data_id}"
        }

    customer_map: dict[str, dict[str, str]] = {}
    rows_filled = 0

    for row in cleaned["rows"]:
        cust_id = str(row.get("customer_id", "")).strip()
        cust_name = str(row.get("customer_name", "")).strip()

        if cust_id and cust_name:
            customer_map[cust_id] = {"id": cust_id, "name": cust_name}

    for row in cleaned["rows"]:
        cust_id = str(row.get("customer_id", "")).strip()
        cust_name = str(row.get("customer_name", "")).strip()

        if not cust_id or not cust_name:
            for map_id, map_info in customer_map.items():
                if map_info["name"] == cust_name or map_id == cust_id:
                    if not row.get("customer_id"):
                        row["customer_id"] = map_info["id"]
                        rows_filled += 1
                    if not row.get("customer_name"):
                        row["customer_name"] = map_info["name"]
                        rows_filled += 1
                    break

    return {
        "success": True,
        "rows_filled": rows_filled,
        "customer_map_size": len(customer_map)
    }


def get_cleaned_data(session: dict[str, Any]) -> dict[str, Any]:
    if "cleaned_data" not in session:
        return {
            "success": False,
            "error": "No cleaned data available. Run deduplication first."
        }

    cleaned = session["cleaned_data"]
    return {
        "success": True,
        "data_id": cleaned["data_id"],
        "columns": cleaned["columns"],
        "row_count": cleaned["deduplicated_count"],
        "rows": cleaned["rows"]
    }


def get_data_summary(session: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "raw_data": {},
        "cleaned_data": None
    }

    raw_data = session.get("raw_data", {})
    for data_id, data in raw_data.items():
        columns = list(data[0].keys()) if data else []
        summary["raw_data"][data_id] = {
            "columns": columns,
            "row_count": len(data)
        }

    if "cleaned_data" in session:
        cleaned = session["cleaned_data"]
        summary["cleaned_data"] = {
            "data_id": cleaned["data_id"],
            "original_count": cleaned["original_count"],
            "deduplicated_count": cleaned["deduplicated_count"],
            "duplicates_removed": cleaned["duplicates_removed"]
        }

    return {
        "success": True,
        "summary": summary
    }
