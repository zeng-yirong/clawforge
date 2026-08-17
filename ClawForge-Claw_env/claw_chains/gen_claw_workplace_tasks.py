"""Generate claw WORKPLACE tasks (four-file paradigm) from sampled tool chains.

This is the *simple, effective* alternative to ``gen_claw_seed_tasks.py``. Instead
of mutating each env's scenario + data_fragments + reusing its builtin evaluator
(which couples the answer to LLM-invented numbers and never gets materialized),
every chain becomes a SELF-CONTAINED file-state task following ``prompt.txt``:

    tasks/{task_id}.yaml                  nanoclaw task config
    tasks/prompts/{task_id}.md            the user-voice script (no solution steps)
    tasks/{task_id}/env_builder.py        builds a challenging initial file tree
    scripts/{task_id}/verify_workplace.py CODE-ONLY scorer -> workplace_score.json

Key difference from prompt.txt: the verifier MUST be pure code (no LLM, no
openai/httpx). The task is therefore steered toward objectively code-verifiable
goals (numeric computation, field extraction, dedup, classification, file
structure) rather than open-ended prose generation.

The tool chain (``claw_chains_out/<env>.jsonl``) is used only as the BUSINESS
SKELETON / inspiration for the scenario — we do NOT call the env CLI. Env README,
gold actions and the data schema (descriptor) are passed as world-building
context so the LLM grounds the script in a realistic domain.

Usage:
    python gen_claw_workplace_tasks.py --self-test          # no LLM; validate parse+write
    python gen_claw_workplace_tasks.py --env post_mails --max-chains 3
    python gen_claw_workplace_tasks.py                      # all envs
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

from llm_client import llm_text, llm_available

log = logging.getLogger("gen_claw_workplace_tasks")

HERE = Path(__file__).resolve().parent
CLAW_ROOT = HERE.parent
CHAINS_DIR = HERE / "claw_chains_out"
EXTRACT_DIR = HERE / "claw_tool_env_docs"
TOOLDOCS_DIR = HERE / "tool_env_docs"
DESCRIPTOR_DIR = HERE / "env_descriptors"
OUT_DIR = HERE / "claw_workplace_tasks"
CACHE_DIR = OUT_DIR / "_chain_cache"

MODEL_NAME = "deepseek-v4-pro"

# The 4 files we expect back, in order. {task_id} is substituted per chain.
EXPECTED_FILES = [
    "tasks/{task_id}.yaml",
    "tasks/prompts/{task_id}.md",
    "tasks/{task_id}/env_builder.py",
    "scripts/{task_id}/verify_workplace.py",
]


# ── system prompt (self-contained: prompt.txt core, code-only verification) ──

# Distilled from prompt.txt: keeps the four-file paradigm, the strict output
# format, and the "separation of duties" philosophy (prompt = role play, builder
# = challenging state, verifier = scoring). The LLM-judge sections of prompt.txt
# are intentionally DROPPED — this pipeline forbids any LLM in the verifier.
SYSTEM_PROMPT = """你是一个顶级的 AI Agent 评测架构师、资深编剧与全栈工程师。
你的目标是：从给定的业务骨架（工具链 + 环境领域）获取灵感，为编号 `{task_id}` 生成一套高质量、
极具区分度、且**纯代码可客观验证**的文件态 workplace 评测任务。

【一步完成 + 一致性硬约束】
你必须先在内部确定同一个“任务真相”，再一次性输出四个文件，使它们指向同一个唯一答案：
- `tasks/prompts/{task_id}.md` 的业务目标，必须能由 `tasks/{task_id}/env_builder.py` 铺出的数据推导。
- `scripts/{task_id}/verify_workplace.py` 检查的文件、字段、数值，必须来自同一个业务目标，且产物路径
  与 prompt 要求 agent 产出的路径逐字一致；不得检查 prompt 未要求的产物，不得凭空新增第二套答案。
- User Prompt 不得泄露验证逻辑、评分细则、隐藏答案或逐步解法。

【🔥输出格式 —— 极其重要，否则流水线崩溃🔥】
严格按顺序输出这 4 个文件，每个文件内容包裹在 Markdown 代码块中。
代码块内部第一行，必须是纯文本的完整相对路径，绝不能带任何注释符（# 或 //）或多余字符。
顺序固定如下，代码块外不得有任何解释文字、标题、分隔线或评分：
1. `tasks/{task_id}.yaml`
2. `tasks/prompts/{task_id}.md`
3. `tasks/{task_id}/env_builder.py`
4. `scripts/{task_id}/verify_workplace.py`

正确示例：
```python
tasks/{task_id}/env_builder.py
import os
def build_env():
    pass
```

【各司其职 —— 必须服从】
### 1. `tasks/{task_id}.yaml`
符合 nanoclaw schema：包含 prompt 路径、`asset: {task_id}`，以及基础 runtime 配置。

### 2. `tasks/prompts/{task_id}.md`（剧本演绎，重中之重）
- **绝对禁止**：出现“1,2,3”解题步骤、变量名、预期数值、或“你需要生成包含某字段的 JSON”这类程序化指令。
- **必须**：完全代入角色（一封邮件、一段工单留言、一次口头交代），用角色语气交代背景、抱怨问题、提出
  业务目标，让 Agent 自己推导要产出什么。提及文件时只用工作区内相对路径（如 `db_dumps/`、`ops/`）。
- 反面：“1.读取 log 2.筛选 active 行 3.提取 ID 写入 kill_list.json”。
- 正面：“凌晨3点主库 IO 飙到 100%！我把 `db_dumps/` 的快照和慢查询日志拖下来了，你顺着堆积的表级锁
  把那个罪魁祸首事务 ID 揪出来，扔到 `ops/kill_target.json`，我准备直接强杀。我只要准确的 ID！”

### 3. `tasks/{task_id}/env_builder.py`（沙盒构建，初始状态的难度全靠它）
- 用 Python 标准库铺出具有挑战性的初始文件树：包含**干扰项、脏数据、近似重复、过期版本、诱饵记录、
  领域内的非标准格式文件**。初始状态必须丰富、专业、有迷惑性，而不是几条干净记录。
- **答案唯一确定**：给定它铺出的文件树，正确产物有且只有一个客观结果，使 verifier 能精确比对；
  干扰项可以让过程更难，但绝不能让最终答案产生歧义。
- **🚨 cwd 已是 `assets/{task_id}/`**：直接用相对路径（`os.makedirs("raw_logs")`、`open("data.csv","w")`），
  **绝不要**在代码里写死 `assets/{task_id}/` 前缀，否则目录树会无限嵌套。
- 与 verifier 的文件名/路径必须逐字一致（builder 写 `result.json`，verifier 就查 `result.json`，不能差一个 s）。

### 4. `scripts/{task_id}/verify_workplace.py`（结果域验证 —— 纯代码，满分 100）
- **🚫 严禁使用大模型**：严禁 `import openai`/`import httpx`/`from openai import ...`，严禁任何网络调用、
  严禁读取 MOCK_API_* 环境变量、严禁 `llm_judge` 之类函数。只允许 Python 标准库
  （json/csv/os/sys/re/pathlib/math/decimal/statistics 等）解析与比对。
- **任务必须因此设计成代码可判定**：优先精确数值计算、字段/记录的提取筛选、去重归并、分类打标、阈值判断、
  集合一致性、文件/目录结构与 Schema 合法性、排序结果。**禁止**把“语气得体的邮件/总结/开放式方案”作为
  主要评分点；若剧情需产出文字，只对其中**可结构化抽取的客观要素**（某个 ID/数值/收件人字段）评分。
- **结构与确定性解析用原生代码**：目录是否存在、JSON/CSV 是否合法、精确数值，必须用 `json.load`/`csv.reader`
  严格解析。严禁对结构化结果用 `if "24.8" in text` 这类模糊匹配。捏造多余字段/节点必须严扣分。
- **细粒度梯度**：不要只设 0/100。按权重铺开（如目录结构 10、格式合法 10、剔除脏数据 30、关键计算 50），
  最关键的计算项占大分。
- 工作区入参：`workspace = sys.argv[1] if len(sys.argv) > 1 else "."`。
- 执行完毕必须把得分明细与最终总分（0-100 整数）写入 `workplace_score.json`，结构：
  {"total_score": 85, "details": [{"item": "...", "score": 10, "max_score": 10, "passed": true, "reason": "..."}]}
- 验证脚本第一条有效语句应是合法 Python（import/注释/docstring）。

【📦 业务取材】
下方“工具链 / gold actions / 环境领域 / 数据 schema”仅作业务剧情的灵感骨架，用来构造真实、专业、有挑战的
文件态任务。**不要**在 prompt 或代码里出现 CLI / 工具名 / `python -m ...`；agent 只在工作区里用通用文件操作完成任务。

现在，请一步生成完整四文件，务必保证四个文件互相一致、不割裂。"""


def _build_user_context(env_des: str, readme: str, tool_list: str,
                        chain_str: str, gold: list[str], schemas: str) -> str:
    return f"""### 业务领域（环境描述）
{env_des}

### 环境说明（README 摘录，仅供你理解领域，勿照抄）
{readme}

### 这条工具链体现的工作流（业务骨架，勿泄露工具名）
{chain_str}

### 该工作流的关键动作（说明数据流，帮助你设计唯一答案）
{', '.join(gold) if gold else '(none)'}

### 领域内可参考的数据结构（仅供你设计 env_builder 的文件树取材）
{schemas}

### 你的任务
基于以上业务骨架，设计一个**自包含的文件态 workplace 任务**：env_builder.py 铺出带干扰项、
答案唯一确定的初始文件树；prompts 用角色口吻交代业务目标（不剧透步骤）；verify_workplace.py
用**纯代码**逐项打分。现在严格按四文件格式输出。"""


# ── inputs (shared helpers with gen_claw_seed_tasks) ──────────────────────

def _tool_list_str(env: str) -> str:
    p = TOOLDOCS_DIR / f"{env}.json"
    if not p.exists():
        return ""
    tools = json.loads(p.read_text(encoding="utf-8"))
    return "\n".join(f"{t['name']}: {t.get('description','')[:120]}" for t in tools)


def _env_des(env_doc: dict) -> str:
    readme = CLAW_ROOT / env_doc["rel_path"] / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return s[:300]
    return env_doc["env_name"].replace("_", " ")


def _readme_excerpt(env_doc: dict, limit: int = 1500) -> str:
    readme = CLAW_ROOT / env_doc["rel_path"] / "README.md"
    if readme.exists():
        return readme.read_text(encoding="utf-8")[:limit]
    return ""


def _chain_str(chain: list[dict]) -> str:
    return "\n".join(f"{i+1}. [{s['layer']}] {s['op']}" for i, s in enumerate(chain))


def _load_descriptor(env: str) -> dict:
    p = DESCRIPTOR_DIR / f"{env}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _data_schemas_str(descriptor: dict) -> str:
    """Compact per-file field schema (reused shape from gen_claw_seed_tasks)."""
    if not descriptor:
        return "(no descriptor — invent a realistic domain file tree)"
    blocks: list[str] = []
    for f in descriptor.get("files", []):
        kind = f.get("kind")
        if kind == "per_record":
            head = f"{f['path']} (per_record, key={f.get('record_key')})"
        elif kind == "collection":
            head = f"{f['path']} (collection, wrapper={f.get('wrapper_key')}, key={f.get('record_key')})"
        elif kind == "csv":
            cols = ", ".join(f"{c['name']}:{c['type']}" for c in f.get("columns", []))
            blocks.append(f"- {f['path']} (csv): {cols}")
            continue
        else:
            continue
        lines = [f"- {head}"]
        for fld in f.get("fields", [])[:12]:
            seg = f"    {fld['name']}: {fld['type']}"
            if fld.get("required"):
                seg += " [required]"
            if fld.get("enum"):
                seg += f" enum={fld['enum']}"
            lines.append(seg)
        blocks.append("\n".join(lines))
    return "\n".join(blocks) or "(no record-bearing files)"


# ── parse the 4 output files (fenced OR bare, LLM-format-tolerant) ─────────

_FENCE_RE = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)


def _path_matches(candidate: str, exp: str) -> bool:
    """True if a stripped line refers to the expected path. Exact match, or the
    candidate is a longer path ending in exp (e.g. an absolute prefix). Requires
    a non-trivial candidate to avoid short-substring false hits."""
    if len(candidate) < 6:
        return False
    return candidate == exp or candidate.endswith("/" + exp) or exp.endswith("/" + candidate)


def _assign(out: dict[str, str], expected: list[str], first: str, body: str) -> None:
    """Map a (first-line-path, body) pair onto the best-matching expected path."""
    first = first.strip().lstrip("#/ ").strip()
    for exp in expected:
        if _path_matches(first, exp):
            out[exp] = body.strip("\n") + "\n"
            return


def _parse_fenced(text: str, expected: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for block in _FENCE_RE.findall(text):
        lines = block.splitlines()
        if lines:
            _assign(out, expected, lines[0], "\n".join(lines[1:]))
    return out


def _parse_bare(text: str, expected: list[str]) -> dict[str, str]:
    """Fallback when the LLM emits path-line + content with NO code fences.

    The four expected paths are known, so we locate each as a line on its own
    and slice content between consecutive path anchors. Order-independent.
    """
    lines = text.splitlines()
    anchors: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        s = ln.strip().lstrip("#/ ").strip()
        for exp in expected:
            if _path_matches(s, exp):
                anchors.append((i, exp))
                break
    out: dict[str, str] = {}
    for j, (line_no, exp) in enumerate(anchors):
        end = anchors[j + 1][0] if j + 1 < len(anchors) else len(lines)
        body = "\n".join(lines[line_no + 1:end]).strip("\n")
        if body:
            out[exp] = body + "\n"
    return out


def parse_four_files(text: str, task_id: str) -> dict[str, str]:
    """Extract the 4 expected files keyed by relative path.

    Tolerates both output styles the LLM produces: fenced code blocks (per the
    system prompt) and bare path-line + content (a common non-compliance). Tries
    fenced first; if that yields fewer than 4 files, merges in the bare parse.
    """
    expected = [p.format(task_id=task_id) for p in EXPECTED_FILES]
    out = _parse_fenced(text, expected)
    if len(out) < len(expected):
        bare = _parse_bare(text, expected)
        for exp, body in bare.items():
            out.setdefault(exp, body)  # prefer fenced content when both present
    return out


def validate_files(files: dict[str, str], task_id: str) -> list[str]:
    """Return a list of problems; empty means the bundle looks shippable."""
    problems: list[str] = []
    for exp in (p.format(task_id=task_id) for p in EXPECTED_FILES):
        if exp not in files:
            problems.append(f"missing file: {exp}")
    verifier = files.get(f"scripts/{task_id}/verify_workplace.py", "")
    if verifier:
        banned = ["import openai", "from openai", "import httpx", "MOCK_API", "llm_judge"]
        for b in banned:
            if b in verifier:
                problems.append(f"verifier uses banned LLM construct: {b!r}")
        if "workplace_score.json" not in verifier:
            problems.append("verifier never writes workplace_score.json")
    builder = files.get(f"tasks/{task_id}/env_builder.py", "")
    if builder and f"assets/{task_id}" in builder:
        problems.append("env_builder hardcodes assets/{task_id} prefix (cwd is already there)")
    return problems


def write_bundle(files: dict[str, str], task_id: str, root: Path) -> list[Path]:
    written: list[Path] = []
    for rel, body in files.items():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
        written.append(dest)
    return written


# ── cache ─────────────────────────────────────────────────────────────────

def _phash(p: str) -> str:
    return hashlib.md5(p.encode("utf-8")).hexdigest()


def _load_cache(env: str, idx: int, expected_hash: str) -> Optional[str]:
    path = CACHE_DIR / f"{env}_{idx:03d}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("_prompt_hash") == expected_hash:
            return data.get("raw")
    return None


def _save_cache(env: str, idx: int, raw: str, prompt_hash: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{env}_{idx:03d}.json").write_text(
        json.dumps({"_prompt_hash": prompt_hash, "raw": raw}, ensure_ascii=False, indent=2),
        encoding="utf-8")


# ── per-chain generation ──────────────────────────────────────────────────

def process_chain(idx: int, chain_rec: dict, env_doc: dict,
                  env_des: str, readme: str, tool_list: str, descriptor: dict,
                  use_llm: bool) -> Optional[dict]:
    env = env_doc["env_name"]
    task_id = f"wp_{env}__{idx:03d}"
    gold = chain_rec.get("gold_actions", [])
    chain_str = _chain_str(chain_rec["chain"])

    system = SYSTEM_PROMPT.replace("{task_id}", task_id)
    user = _build_user_context(env_des, readme, tool_list, chain_str, gold,
                               _data_schemas_str(descriptor))
    full_prompt = system + "\n\n" + user
    phash = _phash(full_prompt)

    raw = _load_cache(env, idx, phash)
    if raw is None:
        if not use_llm:
            log.warning("  [%s] chain %d: no LLM and no cache; skipped", env, idx)
            return None
        raw = llm_text(full_prompt, model=MODEL_NAME, temperature=0.7)
        if not raw:
            log.warning("  [%s] chain %d: LLM returned nothing", env, idx)
            return None
        _save_cache(env, idx, raw, phash)

    files = parse_four_files(raw, task_id)
    problems = validate_files(files, task_id)
    write_bundle(files, task_id, OUT_DIR)
    return {
        "task_id": task_id,
        "env": env,
        "files_written": sorted(files.keys()),
        "problems": problems,
        "gold_actions": gold,
    }


def process_env(chain_file: Path, use_llm: bool,
                max_chains: Optional[int], workers: int) -> list[dict]:
    env = chain_file.stem
    env_doc_path = EXTRACT_DIR / f"{env}.json"
    if not env_doc_path.exists():
        log.warning("  no extracted doc for %s; skip", env)
        return []
    env_doc = json.loads(env_doc_path.read_text(encoding="utf-8"))
    env_des = _env_des(env_doc)
    readme = _readme_excerpt(env_doc)
    tool_list = _tool_list_str(env)
    descriptor = _load_descriptor(env)

    chains = [json.loads(l) for l in chain_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    if max_chains:
        chains = chains[:max_chains]
    if not chains:
        return []

    results: dict[int, dict] = {}
    n_workers = min(workers, len(chains)) if use_llm else 1
    with ThreadPoolExecutor(max_workers=max(1, n_workers)) as ex:
        futures = {ex.submit(process_chain, idx, ch, env_doc, env_des,
                             readme, tool_list, descriptor, use_llm): idx
                   for idx, ch in enumerate(chains)}
        for fut in as_completed(futures):
            idx = futures[fut]
            try:
                rec = fut.result()
                if rec:
                    results[idx] = rec
            except Exception as exc:
                log.warning("  [%s] chain %d failed: %s", env, idx, exc)
    return [results[i] for i in sorted(results)]


# ── self-test (no LLM): prove parse + validate + write work ───────────────

_SAMPLE_RAW = """```yaml
tasks/wp_demo__000.yaml
prompt: tasks/prompts/wp_demo__000.md
asset: wp_demo__000
runtime:
  timeout_s: 600
```

```markdown
tasks/prompts/wp_demo__000.md
财务季度对账又到了。我把各团队上报的云开销明细都丢在 `ledger/` 下面了，格式有点乱，
还混了几条作废的草稿。你帮我把每个团队的总花费算出来，按团队写到 `out/totals.json`，
我等着拿去对账，别把那几条 draft 的算进去。
```

```python
tasks/wp_demo__000/env_builder.py
import json, os
os.makedirs("ledger", exist_ok=True)
os.makedirs("out", exist_ok=True)
rows = [
    {"team": "ads", "amount": 100.0, "status": "final"},
    {"team": "ads", "amount": 50.0, "status": "final"},
    {"team": "retail", "amount": 200.0, "status": "final"},
    {"team": "ads", "amount": 999.0, "status": "draft"},
]
with open("ledger/entries.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
```

```python
scripts/wp_demo__000/verify_workplace.py
import json, os, sys
workspace = sys.argv[1] if len(sys.argv) > 1 else "."
details = []
total = 0
path = os.path.join(workspace, "out", "totals.json")
exists = os.path.exists(path)
details.append({"item": "out/totals.json exists", "score": 20 if exists else 0,
                "max_score": 20, "passed": exists, "reason": "file present" if exists else "missing"})
if exists:
    total += 20
    data = json.load(open(path, encoding="utf-8"))
    expected = {"ads": 150.0, "retail": 200.0}
    ok = all(abs(float(data.get(k, 0)) - v) < 0.01 for k, v in expected.items())
    details.append({"item": "team totals correct (drafts excluded)", "score": 80 if ok else 0,
                    "max_score": 80, "passed": ok, "reason": "totals match" if ok else "totals wrong"})
    if ok:
        total += 80
json.dump({"total_score": total, "details": details},
          open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(total)
```
"""


def self_test() -> int:
    task_id = "wp_demo__000"
    files = parse_four_files(_SAMPLE_RAW, task_id)
    problems = validate_files(files, task_id)
    print(f"parsed files: {sorted(files.keys())}")
    print(f"problems: {problems}")
    assert len(files) == 4, f"expected 4 files, got {len(files)}"
    assert not problems, f"unexpected problems: {problems}"
    test_root = OUT_DIR / "_self_test"
    written = write_bundle(files, task_id, test_root)
    print(f"wrote {len(written)} files under {test_root}")
    # exercise the produced env_builder + verifier end to end
    import subprocess, tempfile, shutil
    work = Path(tempfile.mkdtemp(prefix="wp_selftest_"))
    try:
        builder = (test_root / f"tasks/{task_id}/env_builder.py").read_text(encoding="utf-8")
        subprocess.run([sys.executable, "-c", builder], cwd=work, check=True)
        # simulate a correct agent: write out/totals.json
        (work / "out").mkdir(exist_ok=True)
        (work / "out" / "totals.json").write_text(json.dumps({"ads": 150.0, "retail": 200.0}), encoding="utf-8")
        verifier = test_root / f"scripts/{task_id}/verify_workplace.py"
        r = subprocess.run([sys.executable, str(verifier), str(work)], capture_output=True, text=True)
        score = json.loads((work / "workplace_score.json").read_text(encoding="utf-8"))
        print(f"end-to-end verifier score: {score['total_score']} (stdout={r.stdout.strip()})")
        assert score["total_score"] == 100, "correct agent should score 100"
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("SELF-TEST PASSED")
    return 0


# ── main ──────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env", help="single env name")
    p.add_argument("--max-chains", type=int, default=None)
    p.add_argument("--workers", type=int, default=50)
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--self-test", action="store_true", help="validate parse+write+run without LLM")
    args = p.parse_args()

    if args.self_test:
        return self_test()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    use_llm = (not args.no_llm) and llm_available()
    log.info("LLM: %s", "ON" if use_llm else "OFF (will only use cache)")

    chain_files = sorted(CHAINS_DIR.glob("*.jsonl"))
    if args.env:
        chain_files = [f for f in chain_files if f.stem == args.env]
        if not chain_files:
            log.error("no chain file for --env %s", args.env)
            return 1

    summary: list[dict] = []
    for cf in chain_files:
        recs = process_env(cf, use_llm, args.max_chains, args.workers)
        bad = sum(1 for r in recs if r["problems"])
        log.info("%-34s tasks=%d  with_problems=%d", cf.stem, len(recs), bad)
        summary.extend(recs)

    if summary:
        (OUT_DIR / "_manifest.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    flagged = [r["task_id"] for r in summary if r["problems"]]
    print(f"\nDone. tasks={len(summary)}  ->  {OUT_DIR}")
    if flagged:
        print(f"⚠ {len(flagged)} task(s) need review (see _manifest.json): {flagged[:10]}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
