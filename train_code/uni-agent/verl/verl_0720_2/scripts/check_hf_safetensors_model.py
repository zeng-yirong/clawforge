#!/usr/bin/env python3
"""Validate a local Hugging Face model exported as safetensors.

The default checks deliberately avoid loading all model weights at once. They
validate each safetensors file, the optional sharded-weight index, model config,
tokenizer, and tensor names/shapes against a meta-initialized Transformers model.
Use ``--load-model`` for the slower, full ``from_pretrained`` verification.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import torch
from accelerate import init_empty_weights
from safetensors import safe_open
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForTokenClassification, AutoTokenizer

try:
    from transformers import AutoModelForImageTextToText
except ImportError:
    try:
        from transformers import AutoModelForVision2Seq as AutoModelForImageTextToText
    except ImportError:
        AutoModelForImageTextToText = None


DTYPE_BYTES = {
    "BOOL": 1,
    "U8": 1,
    "I8": 1,
    "I16": 2,
    "U16": 2,
    "I32": 4,
    "U32": 4,
    "F16": 2,
    "BF16": 2,
    "I64": 8,
    "U64": 8,
    "F32": 4,
    "F64": 8,
    "F8_E4M3FN": 1,
    "F8_E4M3FNUZ": 1,
    "F8_E5M2": 1,
    "F8_E5M2FNUZ": 1,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Hugging Face safetensors export.")
    parser.add_argument("--model-dir", required=True, type=Path, help="Merged Hugging Face model directory")
    parser.add_argument(
        "--load-model",
        action="store_true",
        help="Fully load the model with from_pretrained. Requires extra host RAM but is the strongest check.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Allow custom model/tokenizer code from this local model directory.",
    )
    return parser.parse_args()


def model_class_for_config(config: Any):
    architectures = list(getattr(config, "architectures", None) or [])
    architecture = architectures[0] if architectures else ""
    model_type = str(getattr(config, "model_type", "")).lower()

    if "ForTokenClassification" in architecture:
        return AutoModelForTokenClassification
    if "ForConditionalGeneration" in architecture or "vision" in model_type or "_vl" in model_type:
        if AutoModelForImageTextToText is None:
            raise RuntimeError("Installed Transformers does not expose a Vision2Seq/ImageTextToText AutoModel class.")
        return AutoModelForImageTextToText
    return AutoModelForCausalLM


def get_model_files(model_dir: Path) -> tuple[list[Path], dict[str, str] | None]:
    index_path = model_dir / "model.safetensors.index.json"
    if index_path.exists():
        with index_path.open(encoding="utf-8") as f:
            index = json.load(f)
        weight_map = index.get("weight_map")
        if not isinstance(weight_map, dict) or not weight_map:
            raise ValueError(f"Invalid or empty weight_map in {index_path}")
        filenames = sorted(set(weight_map.values()))
        files = [model_dir / filename for filename in filenames]
        absent = [str(path) for path in files if not path.is_file()]
        if absent:
            raise FileNotFoundError(f"Files referenced by {index_path} are missing: {absent}")
        return files, weight_map

    files = sorted(model_dir.glob("*.safetensors"))
    if not files:
        raise FileNotFoundError(f"No *.safetensors file and no model.safetensors.index.json found in {model_dir}")
    if len(files) != 1:
        raise ValueError(
            "Multiple safetensors files need model.safetensors.index.json so Transformers can load them: "
            f"{[path.name for path in files]}"
        )
    return files, None


def inspect_safetensors(files: list[Path]) -> tuple[dict[str, tuple[int, ...]], Counter, int]:
    tensor_shapes: dict[str, tuple[int, ...]] = {}
    dtypes: Counter = Counter()
    total_bytes = 0

    for path in files:
        with safe_open(str(path), framework="pt", device="cpu") as handle:
            keys = list(handle.keys())
            if not keys:
                raise ValueError(f"Safetensors file contains no tensors: {path}")
            for key in keys:
                if key in tensor_shapes:
                    raise ValueError(f"Duplicate tensor name across safetensors files: {key}")
                tensor_slice = handle.get_slice(key)
                shape = tuple(tensor_slice.get_shape())
                dtype = tensor_slice.get_dtype()
                tensor_shapes[key] = shape
                dtypes[dtype] += 1
                itemsize = DTYPE_BYTES.get(dtype)
                if itemsize is not None:
                    numel = 1
                    for dimension in shape:
                        numel *= dimension
                    total_bytes += numel * itemsize

    return tensor_shapes, dtypes, total_bytes


def allowed_tied_missing_keys(model: torch.nn.Module, observed_keys: set[str]) -> set[str]:
    """Return missing aliases intentionally removed by safe serialization.

    Transformers removes one member of a tied-weight group when saving a
    safetensors model. The names in ``_tied_weights_keys`` are regex patterns,
    hence they must not be compared as literal names.
    """

    patterns = list(getattr(model, "_tied_weights_keys", None) or [])
    return {
        key
        for key in model.state_dict().keys()
        if any(re.search(pattern, key) for pattern in patterns) and observed_keys
    }


def validate_against_meta_model(
    config: Any, tensor_shapes: dict[str, tuple[int, ...]], trust_remote_code: bool
) -> tuple[list[str], list[str], list[str]]:
    model_cls = model_class_for_config(config)
    with init_empty_weights():
        model = model_cls.from_config(config, trust_remote_code=trust_remote_code)
        if hasattr(model, "tie_weights"):
            model.tie_weights()
        expected_shapes = {name: tuple(tensor.shape) for name, tensor in model.state_dict().items()}
        allowed_missing = allowed_tied_missing_keys(model, set(tensor_shapes))

    observed_keys = set(tensor_shapes)
    expected_keys = set(expected_shapes)
    missing = sorted((expected_keys - observed_keys) - allowed_missing)
    unexpected = sorted(observed_keys - expected_keys)
    wrong_shape = sorted(
        name for name in observed_keys & expected_keys if tensor_shapes[name] != expected_shapes[name]
    )
    return missing, unexpected, wrong_shape


def main() -> None:
    args = parse_args()
    model_dir = args.model_dir.expanduser().resolve()
    if not model_dir.is_dir():
        raise FileNotFoundError(f"Model directory does not exist: {model_dir}")
    if not (model_dir / "config.json").is_file():
        raise FileNotFoundError(f"Missing config.json: {model_dir / 'config.json'}")

    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=args.trust_remote_code)
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=args.trust_remote_code)
    except Exception as exc:
        raise RuntimeError(f"Tokenizer cannot be loaded from {model_dir}: {exc}") from exc

    files, index_weight_map = get_model_files(model_dir)
    tensor_shapes, dtypes, total_tensor_bytes = inspect_safetensors(files)

    observed_keys = set(tensor_shapes)
    if index_weight_map is not None:
        index_keys = set(index_weight_map)
        if index_keys != observed_keys:
            missing_in_files = sorted(index_keys - observed_keys)
            missing_in_index = sorted(observed_keys - index_keys)
            raise RuntimeError(
                "Safetensors index does not match tensor files: "
                f"missing_in_files={missing_in_files[:10]}, missing_in_index={missing_in_index[:10]}"
            )

    missing, unexpected, wrong_shape = validate_against_meta_model(config, tensor_shapes, args.trust_remote_code)
    if missing or unexpected or wrong_shape:
        details = {
            "missing": missing[:20],
            "unexpected": unexpected[:20],
            "wrong_shape": wrong_shape[:20],
        }
        raise RuntimeError(f"Model weights do not match config: {json.dumps(details, ensure_ascii=False)}")

    if args.load_model:
        model_cls = model_class_for_config(config)
        loaded_model = model_cls.from_pretrained(
            model_dir,
            torch_dtype="auto",
            low_cpu_mem_usage=True,
            trust_remote_code=args.trust_remote_code,
        )
        loaded_model.eval()
        del loaded_model

    report = {
        "status": "passed",
        "model_dir": str(model_dir),
        "model_type": getattr(config, "model_type", None),
        "architectures": list(getattr(config, "architectures", None) or []),
        "safetensors_files": [path.name for path in files],
        "safetensors_file_count": len(files),
        "tensor_count": len(tensor_shapes),
        "tensor_dtypes": dict(sorted(dtypes.items())),
        "tensor_bytes": total_tensor_bytes,
        "tensor_gib": round(total_tensor_bytes / 1024**3, 3),
        "has_weight_index": index_weight_map is not None,
        "tokenizer_class": tokenizer.__class__.__name__,
        "full_transformers_load_checked": args.load_model,
    }
    report_path = model_dir / "merge_check.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Safetensors validation passed")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise


