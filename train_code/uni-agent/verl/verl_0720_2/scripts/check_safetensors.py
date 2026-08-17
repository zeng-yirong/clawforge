#!/usr/bin/env python3
"""Quick integrity check for a Hugging Face safetensors export."""

import json
import sys
from pathlib import Path

from safetensors import safe_open


if len(sys.argv) != 2:
    raise SystemExit(f"Usage: {Path(sys.argv[0]).name} <merged_hf_dir>")

model_dir = Path(sys.argv[1]).expanduser()
if not (model_dir / "config.json").is_file():
    raise SystemExit(f"Missing config.json: {model_dir}")

files = sorted(model_dir.glob("*.safetensors"))
if not files:
    raise SystemExit(f"No safetensors files found: {model_dir}")

tensor_names = set()
for file in files:
    with safe_open(str(file), framework="pt", device="cpu") as handle:
        names = set(handle.keys())
        if tensor_names & names:
            raise SystemExit(f"Duplicate tensor names: {file}")
        tensor_names.update(names)

index = model_dir / "model.safetensors.index.json"
if len(files) > 1 and not index.is_file():
    raise SystemExit(f"Missing shard index: {index}")
if index.is_file():
    with index.open(encoding="utf-8") as f:
        weight_map = json.load(f).get("weight_map", {})
    if not isinstance(weight_map, dict) or set(weight_map) != tensor_names or any(
        not (model_dir / name).is_file() for name in weight_map.values()
    ):
        raise SystemExit(f"Invalid safetensors index: {index}")

print(f"OK: {len(files)} safetensors file(s), {len(tensor_names)} tensors: {model_dir}")


