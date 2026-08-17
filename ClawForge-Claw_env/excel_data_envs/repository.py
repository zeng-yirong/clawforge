from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class DatasetRepository:
    def __init__(self, data_root: str | Path | None = None):
        base_root = Path(data_root) if data_root is not None else Path(__file__).parent / "data"
        self.data_root = base_root.resolve()
        self.raw_data_dir = self.data_root / "raw_data"
        self.scenario_dir = self.data_root / "scenarios"
        self.accounts_file = self.data_root / "accounts.csv"

    def load_accounts(self) -> dict[str, dict[str, Any]]:
        rows = _load_csv(self.accounts_file)
        return {item["account_id"]: item for item in rows}

    def load_raw_data(self, data_id: str) -> list[dict[str, Any]]:
        return _load_csv(self.raw_data_dir / f"{data_id}.csv")

    def load_scenario(self, scenario_id: str) -> dict[str, Any]:
        import json
        path = self.scenario_dir / f"{scenario_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def list_scenarios(self) -> list[dict[str, Any]]:
        import json
        return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(self.scenario_dir.glob("*.json"))]

    def read_data_summary(self) -> dict[str, Any]:
        raw_files = list(self.raw_data_dir.glob("*.csv"))
        return {
            "data_files_count": len(raw_files),
            "data_files": [f.stem for f in raw_files]
        }
