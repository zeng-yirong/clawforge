"""Expand each generated workplace task into multiple PERSONA variants.

A workplace task's verifiable truth is fully pinned by two files:
    tasks/{id}/env_builder.py         (what data is laid down)
    scripts/{id}/verify_workplace.py  (what paths/fields/values are scored)

Persona expansion therefore FREEZES those two files and only rewrites the
role-play script ``tasks/prompts/{id}.md`` in a different persona's voice
(tone, expertise,背景). Same task, same unique answer, same verifier — just a
different narrator. This is data augmentation that never breaks verifiability.

Persona selection mirrors ``env_chains/intent_decomposer.py``: personas carry
``labels``; env names map to domain labels via ENV_KEYWORD_LABELS; we prefer a
persona whose labels overlap the task's domain, else pick randomly.

Each variant is written as a SELF-CONTAINED four-file bundle under a new task_id
``{orig}__p{k}`` (env_builder + verifier copied verbatim, new prompt.md, yaml
repointed) so every variant can be rolled out independently.

Usage:
    python expand_task_personas.py --self-test
    python expand_task_personas.py --personas /srv/persona.json --variants 3
    python expand_task_personas.py --env post_mails --personas /srv/persona.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

from llm_client import llm_text, llm_available

log = logging.getLogger("expand_task_personas")

HERE = Path(__file__).resolve().parent
TASKS_DIR = HERE / "claw_workplace_tasks"
OUT_DIR = HERE / "claw_workplace_tasks_persona"

MODEL_NAME = "deepseek-v4-pro"


# ── env keyword → persona-label mapping (ported from intent_decomposer) ────
# Trimmed to the domains our claw envs actually span, plus claw-specific keys.
ENV_KEYWORD_LABELS: dict[str, list[str]] = {
    "mail": ["Communication", "Professional", "Technology"],
    "mails": ["Communication", "Professional", "Technology"],
    "email": ["Communication", "Professional", "Technology"],
    "post": ["Communication", "Social Media", "Marketing"],
    "message": ["Communication", "Professional", "Social Media"],
    "churn": ["Business", "Marketing", "Customer Service"],
    "retention": ["Business", "Marketing", "Customer Service"],
    "customer": ["Business", "Sales", "Customer Service"],
    "crm": ["Business", "Sales", "Professional", "Technology"],
    "cloud": ["Technology", "Computing", "Engineering", "Operations"],
    "cost": ["Finance", "Business", "Accounting", "Data Analysis"],
    "ledger": ["Finance", "Accounting", "Business", "Data Analysis"],
    "finance": ["Finance", "Economics", "Investment", "Data Analysis"],
    "expense": ["Finance", "Business", "Professional", "Accounting"],
    "server": ["Technology", "Computing", "IT Specialist", "Engineering"],
    "fault": ["Technology", "Engineering", "Operations", "IT Specialist"],
    "postmortem": ["Technology", "Engineering", "Operations"],
    "security": ["Security", "Cybersecurity", "Technology", "Professional"],
    "guard": ["Security", "Compliance", "Professional"],
    "vault": ["Security", "Technology", "Professional"],
    "auditor": ["Legal", "Compliance", "Finance", "Professional"],
    "confidential": ["Security", "Legal", "Compliance"],
    "privilege": ["Security", "Compliance", "Technology"],
    "arxiv": ["Research", "Academia", "Science", "Data Analysis"],
    "paper": ["Research", "Academia", "Science"],
    "citation": ["Research", "Academia", "Science"],
    "review": ["Research", "Business", "Professional"],
    "experiment": ["Research", "Science", "Data Analysis"],
    "reproduction": ["Research", "Science", "Engineering"],
    "onboarding": ["Business", "Management", "Professional", "Human Resources"],
    "offboarding": ["Business", "Management", "Professional", "Human Resources"],
    "performance": ["Business", "Management", "Human Resources"],
    "resume": ["Business", "Human Resources", "Professional"],
    "interview": ["Business", "Human Resources", "Professional"],
    "scheduler": ["Professional", "Management", "Operations", "Planning"],
    "scheduling": ["Professional", "Management", "Operations", "Planning"],
    "travel": ["Travel", "Transportation", "Logistics", "Hospitality"],
    "itinerary": ["Travel", "Transportation", "Hospitality", "Planning"],
    "policy": ["Policy", "Legal", "Compliance", "Business"],
    "flight": ["Travel", "Aviation", "Transportation", "Logistics"],
    "logistics": ["Logistics", "Transportation", "Operations", "Supply Chain"],
    "car": ["Transportation", "Engineering", "Automotive"],
    "navi": ["Transportation", "Engineering", "Navigation"],
    "sensor": ["Technology", "Engineering", "IoT"],
    "smart": ["Technology", "Engineering", "IoT"],
    "home": ["Technology", "IoT", "Lifestyle"],
    "music": ["Music", "Arts", "Media"],
    "sku": ["Business", "Retail", "Marketing"],
    "compete": ["Business", "Marketing", "Strategy"],
    "competition": ["Business", "Marketing", "Strategy"],
    "business": ["Business", "Management", "Professional", "Finance"],
    "report": ["Business", "Data Analysis", "Professional"],
    "doc": ["Professional", "Business", "Technology"],
    "excel": ["Data Analysis", "Business", "Finance"],
    "data": ["Technology", "Data", "Data Analysis"],
    "tier": ["Business", "Sales", "Data Analysis"],
    "label": ["Business", "Data Analysis"],
    "memory": ["Technology", "Data", "Research"],
    "clue": ["Research", "Data", "Investigation"],
}


# ── persona loading + matching (ported/adapted) ───────────────────────────

def _normalize_persona(obj: Any) -> Optional[dict]:
    if isinstance(obj, dict) and obj.get("persona"):
        labels = obj.get("labels", [])
        if isinstance(labels, str):
            try:
                labels = json.loads(labels)
            except (json.JSONDecodeError, TypeError):
                labels = [labels] if labels else []
        if not isinstance(labels, list):
            labels = []
        return {"persona": str(obj["persona"]), "labels": labels}
    if isinstance(obj, str) and obj.strip():
        return {"persona": obj.strip(), "labels": []}
    return None


def load_personas(path: Optional[str]) -> list[dict]:
    """Load personas from .json (array or {"personas":[...]}) or .jsonl.

    Each persona is normalized to {"persona": str, "labels": [str]}.
    """
    default = [{"persona": "A helpful and precise professional user.", "labels": []}]
    if not path:
        return default
    p = Path(path)
    if not p.exists():
        log.warning("persona file %s not found; using default", path)
        return default
    text = p.read_text(encoding="utf-8")
    out: list[dict] = []
    if p.suffix == ".jsonl":
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                n = _normalize_persona(json.loads(line))
            except json.JSONDecodeError:
                continue
            if n:
                out.append(n)
    else:  # .json
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            log.warning("persona file %s is not valid JSON; using default", path)
            return default
        items = data.get("personas", []) if isinstance(data, dict) else data
        if isinstance(items, list):
            for it in items:
                n = _normalize_persona(it)
                if n:
                    out.append(n)
    return out or default


def _env_keywords(env_name: str) -> list[str]:
    parts = env_name.replace("__", "_").split("_")
    kws = []
    for part in parts:
        if not part:
            continue
        words = re.findall(r"[A-Z]+(?=[A-Z]|$)|[A-Z][a-z]*", part)
        kws.extend(w.lower() for w in words) if words else kws.append(part.lower())
    return list(set(kws))


def _domain_labels(env_name: str) -> set[str]:
    labels: set[str] = set()
    for kw in _env_keywords(env_name):
        if kw in ENV_KEYWORD_LABELS:
            labels.update(ENV_KEYWORD_LABELS[kw])
    return {l.lower() for l in labels}


def pick_personas(personas: list[dict], env_name: str, k: int, rng: random.Random) -> list[dict]:
    """Pick k personas, preferring label overlap with the env domain; fill with
    random distinct picks. Never returns duplicates unless the pool is smaller."""
    target = _domain_labels(env_name)
    matched = [p for p in personas
               if target and isinstance(p.get("labels"), list)
               and {str(l).lower() for l in p["labels"]} & target]
    pool = matched if matched else personas
    if k >= len(pool):
        chosen = list(pool)
    else:
        chosen = rng.sample(pool, k)
    # top up from the full set if the matched pool was too small
    if len(chosen) < k:
        extra = [p for p in personas if p not in chosen]
        rng.shuffle(extra)
        chosen.extend(extra[: k - len(chosen)])
    return chosen[:k]


# ── rewrite prompt in a persona's voice (answer domain frozen) ─────────────

REWRITE_SYSTEM = """你是一个资深编剧兼 AI Agent 评测任务改写专家。
你会拿到一个文件态 workplace 任务的三份材料：原始用户剧本（prompt）、初始环境构建脚本（env_builder.py）、
以及纯代码验证脚本（verify_workplace.py）。你的唯一工作是：**用给定的新 PERSONA 的口吻，重写用户剧本**。

【绝对不可改变（答案域已冻结）】
- 所有 agent 需要产出的**文件路径**（如 `ops/launch_posts.json`）必须逐字保留，一个字符都不能变。
- 所有产物中要求的**字段名、键名**（如 `platform`、`content`、`post_id`、`reply_content`）必须逐字保留。
- 所有**筛选/计算规则、约束条件、阈值、要排除或包含的对象**（如“标签带 approved 且重要性 high、取最新那封”、
  “忽略 spam 帖子”）必须完整保留，语义不得增减或走样。
- 任务提及的**输入数据目录/文件**（如 `data/emails/`、`data/social/`）必须保留。
- 不得引入 env_builder / verifier 里不存在的新文件、新字段、新规则，也不得删除原剧本里任何一条可验证要求。

【必须改变（且仅改变这些）】
- 叙述的**人设、语气、身份背景、专业水平、情绪、措辞繁简**，完全代入新 PERSONA。
- 可以重排叙述顺序、增删无关的情绪化背景闲聊，但**业务要求的信息必须一条不少地保留**。

【风格底线（继承原任务哲学）】
- 仍是“剧本演绎”：像一封真实的邮件/工单/口头交代，不得出现“第1步第2步”式解题清单、不得出现工具名或 `python -m`。
- 只输出重写后的剧本正文（Markdown/纯文本），不要输出任何解释、标题、代码块围栏或评分。"""

REWRITE_USER = """【新 PERSONA】
{persona}

【原始用户剧本（业务目标以此为准，需完整保留其中所有可验证要求）】
{prompt}

【初始环境构建脚本 env_builder.py（只读上下文，帮助你理解数据与答案，切勿改动或引用其代码）】
{builder}

【纯代码验证脚本 verify_workplace.py（只读上下文，明确告诉你哪些路径/字段/数值会被检查，必须逐字保留）】
{verifier}

现在，用上面这个新 PERSONA 的口吻重写用户剧本。只输出重写后的剧本正文。"""


def rewrite_prompt(persona: str, prompt_md: str, builder: str, verifier: str,
                   use_llm: bool) -> Optional[str]:
    if not use_llm:
        return None
    user = (REWRITE_USER
            .replace("{persona}", persona)
            .replace("{prompt}", prompt_md)
            .replace("{builder}", builder[:6000])
            .replace("{verifier}", verifier[:6000]))
    return llm_text(REWRITE_SYSTEM + "\n\n" + user, model=MODEL_NAME, temperature=0.9)


# ── task discovery + variant writing ──────────────────────────────────────

def discover_tasks(env: Optional[str]) -> list[dict]:
    """Find generated tasks by their prompt files; return path bundles."""
    prompts_dir = TASKS_DIR / "tasks" / "prompts"
    if not prompts_dir.is_dir():
        return []
    out = []
    for md in sorted(prompts_dir.glob("*.md")):
        task_id = md.stem
        m = re.match(r"wp_(.+?)__\d+$", task_id)
        env_name = m.group(1) if m else task_id
        if env and env_name != env:
            continue
        builder = TASKS_DIR / "tasks" / task_id / "env_builder.py"
        verifier = TASKS_DIR / "scripts" / task_id / "verify_workplace.py"
        yaml = TASKS_DIR / "tasks" / f"{task_id}.yaml"
        if builder.exists() and verifier.exists():
            out.append({"task_id": task_id, "env": env_name, "prompt": md,
                        "builder": builder, "verifier": verifier, "yaml": yaml})
    return out


def _rewrite_yaml(yaml_text: str, orig_id: str, new_id: str) -> str:
    """Repoint a yaml's task_id/asset/prompt from orig to the variant id."""
    if yaml_text:
        return yaml_text.replace(orig_id, new_id)
    return (f"task_id: {new_id}\nasset: {new_id}\n"
            f"prompt: tasks/prompts/{new_id}.md\nruntime:\n  cwd: ./\n")


def write_variant(bundle: dict, new_id: str, new_prompt: str) -> list[Path]:
    orig_id = bundle["task_id"]
    written: list[Path] = []
    # prompt.md (rewritten)
    dst_prompt = OUT_DIR / "tasks" / "prompts" / f"{new_id}.md"
    dst_prompt.parent.mkdir(parents=True, exist_ok=True)
    dst_prompt.write_text(new_prompt.strip() + "\n", encoding="utf-8")
    written.append(dst_prompt)
    # env_builder.py (verbatim copy)
    dst_builder = OUT_DIR / "tasks" / new_id / "env_builder.py"
    dst_builder.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bundle["builder"], dst_builder)
    written.append(dst_builder)
    # verify_workplace.py (verbatim copy)
    dst_verifier = OUT_DIR / "scripts" / new_id / "verify_workplace.py"
    dst_verifier.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bundle["verifier"], dst_verifier)
    written.append(dst_verifier)
    # yaml (repointed)
    yaml_text = bundle["yaml"].read_text(encoding="utf-8") if bundle["yaml"].exists() else ""
    dst_yaml = OUT_DIR / "tasks" / f"{new_id}.yaml"
    dst_yaml.write_text(_rewrite_yaml(yaml_text, orig_id, new_id), encoding="utf-8")
    written.append(dst_yaml)
    return written


def process_task(bundle: dict, personas: list[dict], variants: int,
                 use_llm: bool, seed: int) -> list[dict]:
    orig_id = bundle["task_id"]
    prompt_md = bundle["prompt"].read_text(encoding="utf-8")
    builder = bundle["builder"].read_text(encoding="utf-8")
    verifier = bundle["verifier"].read_text(encoding="utf-8")
    rng = random.Random(f"{orig_id}:{seed}")
    chosen = pick_personas(personas, bundle["env"], variants, rng)

    results = []
    for k, persona in enumerate(chosen):
        new_id = f"{orig_id}__p{k:02d}"
        new_prompt = rewrite_prompt(persona["persona"], prompt_md, builder, verifier, use_llm)
        if not new_prompt:
            log.warning("  [%s] variant p%02d: no rewrite (LLM off/failed); skipped", orig_id, k)
            continue
        write_variant(bundle, new_id, new_prompt)
        results.append({"task_id": new_id, "base_task_id": orig_id, "env": bundle["env"],
                        "persona": persona["persona"], "persona_labels": persona.get("labels", [])})
    return results


# ── self-test (no LLM): freeze-and-copy pipeline with a stub rewrite ───────

def self_test() -> int:
    import tempfile, subprocess
    global TASKS_DIR, OUT_DIR
    tmp = Path(tempfile.mkdtemp(prefix="persona_selftest_"))
    TASKS_DIR = tmp / "in"
    OUT_DIR = tmp / "out"
    tid = "wp_demo__000"
    # lay down a minimal source task bundle
    (TASKS_DIR / "tasks" / "prompts").mkdir(parents=True)
    (TASKS_DIR / "tasks" / tid).mkdir(parents=True)
    (TASKS_DIR / "scripts" / tid).mkdir(parents=True)
    (TASKS_DIR / "tasks" / "prompts" / f"{tid}.md").write_text(
        "把 ledger/ 里 status 为 final 的按 team 求和，写到 out/totals.json。", encoding="utf-8")
    (TASKS_DIR / "tasks" / f"{tid}.yaml").write_text(
        f"task_id: {tid}\nasset: {tid}\nprompt: tasks/prompts/{tid}.md\n", encoding="utf-8")
    (TASKS_DIR / "tasks" / tid / "env_builder.py").write_text(
        "import json,os\nos.makedirs('ledger',exist_ok=True)\n"
        "json.dump([{'team':'ads','amount':100.0,'status':'final'}],open('ledger/e.json','w'))\n",
        encoding="utf-8")
    (TASKS_DIR / "scripts" / tid / "verify_workplace.py").write_text(
        "import json,os,sys\nw=sys.argv[1] if len(sys.argv)>1 else '.'\n"
        "json.dump({'total_score':100,'details':[]},open(os.path.join(w,'workplace_score.json'),'w'))\n",
        encoding="utf-8")

    personas = [{"persona": "急躁的市场部主管", "labels": ["Business"]},
                {"persona": "严谨的财务分析师", "labels": ["Finance"]}]
    bundles = discover_tasks(None)
    assert len(bundles) == 1, f"expected 1 task, found {len(bundles)}"

    # stub rewrite: prepend persona marker, keep the ORIGINAL body verbatim so
    # the frozen answer-domain references survive
    def _stub(bundle):
        orig = bundle["prompt"].read_text(encoding="utf-8")
        rng = random.Random("x")
        chosen = pick_personas(personas, bundle["env"], 2, rng)
        recs = []
        for k, per in enumerate(chosen):
            nid = f"{bundle['task_id']}__p{k:02d}"
            write_variant(bundle, nid, f"[{per['persona']}] {orig}")
            recs.append(nid)
        return recs

    made = _stub(bundles[0])
    assert len(made) == 2, made
    # variants must reference the same frozen paths and run end-to-end
    for nid in made:
        vt_prompt = (OUT_DIR / "tasks" / "prompts" / f"{nid}.md").read_text(encoding="utf-8")
        assert "out/totals.json" in vt_prompt, "frozen output path lost in variant"
        assert (OUT_DIR / "tasks" / nid / "env_builder.py").exists()
        assert (OUT_DIR / "scripts" / nid / "verify_workplace.py").exists()
        work = tmp / f"run_{nid}"
        work.mkdir()
        builder_src = (OUT_DIR / "tasks" / nid / "env_builder.py").read_text(encoding="utf-8")
        subprocess.run([sys.executable, "-c", builder_src], cwd=work, check=True)
        subprocess.run([sys.executable, str(OUT_DIR / "scripts" / nid / "verify_workplace.py"),
                        str(work)], check=True)
        score = json.loads((work / "workplace_score.json").read_text(encoding="utf-8"))
        assert score["total_score"] == 100
    print(f"discovered tasks: {[b['task_id'] for b in bundles]}")
    print(f"variants written: {made}")
    print("frozen answer-domain preserved; env_builder+verifier copied and runnable")
    print("SELF-TEST PASSED")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


# ── main ──────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--personas", help="path to persona .json/.jsonl (on server)")
    p.add_argument("--env", help="only expand tasks of this env")
    p.add_argument("--variants", type=int, default=3, help="persona variants per task")
    p.add_argument("--workers", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()

    if args.self_test:
        return self_test()

    personas = load_personas(args.personas)
    use_llm = (not args.no_llm) and llm_available()
    log.info("personas=%d  LLM=%s  variants/task=%d",
             len(personas), "ON" if use_llm else "OFF", args.variants)

    bundles = discover_tasks(args.env)
    if not bundles:
        log.error("no generated tasks under %s (run gen_claw_workplace_tasks.py first)", TASKS_DIR)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers if use_llm else 1)) as ex:
        futures = {ex.submit(process_task, b, personas, args.variants, use_llm, args.seed): b
                   for b in bundles}
        for fut in as_completed(futures):
            try:
                manifest.extend(fut.result())
            except Exception as exc:
                log.warning("task %s failed: %s", futures[fut]["task_id"], exc)

    if manifest:
        (OUT_DIR / "_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone. base_tasks={len(bundles)}  variants={len(manifest)}  ->  {OUT_DIR}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
