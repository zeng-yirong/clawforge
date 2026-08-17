"""Shared LLM client for the claw_chains pipeline.

Mirrors the call interface used by the generic ``gen_chains``/``gen_seed_tasks``
scripts (``hmwrangler.hm_aigc.aigc_managed`` with ``model_agent='yibu'`` and a
``deepseek-v4-flash`` model) so this pipeline runs against the same managed
endpoint when available.

It degrades gracefully: if ``hmwrangler`` cannot be imported (e.g. running
outside the training venv), ``llm_json`` / ``llm_text`` return ``None`` and the
callers fall back to deterministic output. This keeps the whole pipeline
runnable everywhere while still using the LLM wherever the generic pipeline does
once the dependency is present.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("llm_client")

MAX_RETRIES = 3
DEFAULT_MODEL = "deepseek-v4-flash"
SUB_ACCOUNT = "一步_教育办公_侯宇泰_0601-2"

# Make the repo root importable so ``hmwrangler_init`` (which registers the
# managed client) can be found, matching the generic scripts' sys.path tweak.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_AVAILABLE: Optional[bool] = None


def llm_available() -> bool:
    """Return True if the managed LLM client can be imported."""
    global _AVAILABLE
    if _AVAILABLE is not None:
        return _AVAILABLE
    try:
        import hmwrangler_init  # noqa: F401
        from hmwrangler import hm_aigc  # noqa: F401
        _AVAILABLE = True
    except Exception as exc:
        log.warning("LLM unavailable (%s); pipeline will use deterministic fallback", exc)
        _AVAILABLE = False
    return _AVAILABLE


def _call(prompt: str, model: str, temperature: float, json_mode: bool) -> Optional[str]:
    if not llm_available():
        return None
    from hmwrangler import hm_aigc

    req_data: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "stream": False,
    }
    if json_mode:
        req_data["response_format"] = {"type": "json_object"}

    for attempt in range(MAX_RETRIES):
        try:
            result = hm_aigc.aigc_managed(
                model_agent="yibu",
                req_data=req_data,
                sub_account_name=SUB_ACCOUNT,
                model=model,
                timeout=600,
            )
            return result["choices"][0]["message"]["content"]
        except Exception as exc:
            log.warning("LLM attempt %d/%d failed: %s", attempt + 1, MAX_RETRIES, exc)
    return None


def llm_text(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.3) -> Optional[str]:
    """Return raw text completion, or None on unavailability/failure."""
    out = _call(prompt, model, temperature, json_mode=False)
    if out is None:
        return None
    return re.sub(r"^```(?:\w+)?\s*|```\s*$", "", out.strip(), flags=re.MULTILINE).strip()


def llm_json(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.3) -> Optional[dict]:
    """Return a parsed JSON object completion, or None on failure."""
    out = _call(prompt, model, temperature, json_mode=True)
    if out is None:
        return None
    out = out.strip()
    if out.startswith("```"):
        out = re.sub(r"^```(?:json)?|```$", "", out, flags=re.MULTILINE).strip()
    try:
        return json.loads(out)
    except Exception as exc:
        log.warning("LLM JSON parse failed: %s", exc)
        return None
