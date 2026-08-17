from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OpenAIBackend:
    api_base: str
    api_key: str
    model: str
    timeout: float
    max_workers: int


@dataclass(frozen=True)
class OpenAISamplingParams:
    temperature: float
    top_p: float
    max_tokens: int
    seed: int | None = None


def build_llm(args: argparse.Namespace) -> Any:
    backend = getattr(args, "backend", "local")
    if backend == "openai":
        api_base = (args.api_base or "http://127.0.0.1:8000/v1").rstrip("/")
        model = args.served_model_name or args.model
        return OpenAIBackend(
            api_base=api_base,
            api_key=args.api_key or "dummy_key",
            model=model,
            timeout=float(args.api_timeout),
            max_workers=max(1, int(getattr(args, "api_max_workers", 0) or getattr(args, "agent_batch_size", 1))),
        )

    from vllm import LLM

    llm_kwargs: dict[str, Any] = {
        "model": args.model,
        "tokenizer": args.tokenizer or args.model,
        "tensor_parallel_size": args.tensor_parallel_size,
        "dtype": args.dtype,
        "max_model_len": args.max_model_len,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "trust_remote_code": args.trust_remote_code,
        "enforce_eager": args.enforce_eager,
        "enable_prefix_caching": args.enable_prefix_caching,
    }
    if args.max_num_batched_tokens is not None:
        llm_kwargs["max_num_batched_tokens"] = args.max_num_batched_tokens
    if args.max_num_seqs is not None:
        llm_kwargs["max_num_seqs"] = args.max_num_seqs
    if args.seed is not None:
        llm_kwargs["seed"] = args.seed
    return LLM(**llm_kwargs)


def build_sampling_params(args: argparse.Namespace) -> Any:
    backend = getattr(args, "backend", "local")
    if backend == "openai":
        return OpenAISamplingParams(
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
            seed=args.seed,
        )

    from vllm import SamplingParams

    return SamplingParams(
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        max_tokens=args.max_tokens,
        skip_special_tokens=True,
    )


def load_tokenizer(args: argparse.Namespace) -> Any:
    backend = getattr(args, "backend", "local")
    if backend == "openai":
        return None

    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(
        args.tokenizer or args.model,
        trust_remote_code=args.trust_remote_code,
    )


def apply_chat_template(tokenizer: Any, messages: list[dict[str, str]], *, enable_thinking: bool) -> str:
    kwargs = {"tokenize": False, "add_generation_prompt": True}
    try:
        return tokenizer.apply_chat_template(messages, enable_thinking=enable_thinking, **kwargs)
    except TypeError as exc:
        message = str(exc)
        if "enable_thinking" not in message and "unexpected" not in message:
            raise
        return tokenizer.apply_chat_template(messages, **kwargs)


def generate_reply(
    *,
    llm: Any,
    tokenizer: Any,
    sampling_params: Any,
    messages: list[dict[str, str]],
    enable_thinking: bool,
) -> str:
    replies = generate_replies(
        llm=llm,
        tokenizer=tokenizer,
        sampling_params=sampling_params,
        message_batches=[messages],
        enable_thinking=enable_thinking,
    )
    return replies[0] if replies else ""


def generate_replies(
    *,
    llm: Any,
    tokenizer: Any,
    sampling_params: Any,
    message_batches: list[list[dict[str, str]]],
    enable_thinking: bool,
) -> list[str]:
    if isinstance(llm, OpenAIBackend):
        return generate_openai_replies(
            backend=llm,
            sampling_params=sampling_params,
            message_batches=message_batches,
            enable_thinking=enable_thinking,
        )

    prompts = [
        apply_chat_template(tokenizer, messages, enable_thinking=enable_thinking)
        for messages in message_batches
    ]
    request_outputs = llm.generate(prompts, sampling_params, use_tqdm=False)
    replies: list[str] = []
    for request_output in request_outputs:
        if not request_output.outputs:
            replies.append("")
            continue
        replies.append(request_output.outputs[0].text.strip())
    return replies


def generate_openai_replies(
    *,
    backend: OpenAIBackend,
    sampling_params: OpenAISamplingParams,
    message_batches: list[list[dict[str, str]]],
    enable_thinking: bool,
) -> list[str]:
    if not message_batches:
        return []
    if len(message_batches) == 1:
        return [chat_completion(backend, sampling_params, message_batches[0], enable_thinking=enable_thinking)]

    max_workers = min(backend.max_workers, len(message_batches))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                chat_completion,
                backend,
                sampling_params,
                messages,
                enable_thinking=enable_thinking,
            )
            for messages in message_batches
        ]
        return [future.result() for future in futures]


def chat_completion(
    backend: OpenAIBackend,
    sampling_params: OpenAISamplingParams,
    messages: list[dict[str, str]],
    *,
    enable_thinking: bool,
) -> str:
    payload: dict[str, Any] = {
        "model": backend.model,
        "messages": messages,
        "temperature": sampling_params.temperature,
        "top_p": sampling_params.top_p,
        "max_tokens": sampling_params.max_tokens,
        "chat_template_kwargs": {"enable_thinking": enable_thinking},
    }
    if sampling_params.seed is not None:
        payload["seed"] = sampling_params.seed

    request = urllib.request.Request(
        f"{backend.api_base}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {backend.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=backend.timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc}") from exc

    choices = response_payload.get("choices")
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if content is None:
        return ""
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content).strip()
    return str(content).strip()
