"""Generate graph construction code via LLM for OASIS environments.

Reads source env .py files, extracts tool definitions via AST, then calls
an LLM to write Python code that builds a NetworkX DiGraph with logical edges.
The generated code is saved to *_graph_code_cache.py files — execution happens
separately via build_graphs.py.

Usage:
    cd AgentRl
    python generate_graphs.py           # all envs
    python generate_graphs.py --env web_search
"""

import ast
import json
import logging
import hashlib
import re
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Allow `from AgentRl.xxx` imports
sys.path.insert(0, str(Path(__file__).parent.parent))

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
DOCS_DIR = ROOT_DIR / "env_chains" / "tool_env_docs"

AUTH_KEYWORDS = {"login", "logout", "authenticate", "auth", "get_login_status"}

MAX_RETRIES = 3

# ── LLM-based graph code prompt ─────────────────────────────────────────

PROMPT_GRAPH_CODE = """You are building a directed tool dependency graph for an Agentic RL environment. Given a set of tool definitions, write executable Python code that constructs a NetworkX DiGraph with logical edges.

All tool nodes are already added for you — your job is ONLY to add edges.

### Available variables in scope when your code runs
- `G`: a `networkx.DiGraph` with all tools already added as nodes (node id = tool name, node attributes = full tool definition dict)
- `tools`: the list of tool definition dicts
- `json_graph`: `networkx.readwrite.json_graph` (already imported)

### Your task
Write Python code that calls `G.add_edge(u, v, weight=..., relationship=...)` for each logical dependency you identify.

### Edge weight guidelines
- 0.7-0.9: strong (direct pre/post: create→update, search→fetch, add→list)
- 0.4-0.6: moderate (common follow-up: list→get, update→read, create→read)
- 0.2-0.3: weak (plausible next step: cross-entity reads)

### Rules
1. Infer workflows from tool descriptions and parameter names.
2. Tools operating on the SAME entity should have CRUD flow edges: create→update→delete, with read connections in both directions.
3. Auth/login tools connect to all operational tools with weight 0.5 (already done before your code runs).
4. Ensure every non-terminal tool has at least one outgoing edge. The graph must be well-connected.
5. Add cross-entity edges when tools share data (e.g. search returns IDs consumed by get_details).
6. Aim for roughly 2-4 outgoing edges per tool on average.
7. Use meaningful relationship labels in English.

### Tool Definitions
{{TOOL_DEFS}}

### Output
Output ONLY the Python code that adds edges to G. No markdown fences, no explanations.
Your code should look like:

# Categorize tools
creators = [...]
readers = [...]
# Add edges
for c in creators:
    for r in readers:
        G.add_edge(c, r, weight=0.6, relationship="creates_then_reads")
# ... more edge logic
"""


def is_auth(func_name: str) -> bool:
    return any(kw in func_name.lower() for kw in AUTH_KEYWORDS)


def _call_api_for_graph_code(prompt: str) -> Optional[str]:
    """Call LLM to generate graph construction code. Returns Python code string or None."""
    from hmwrangler import hm_aigc

    messages = [{"role": "user", "content": prompt}]
    req_data = {
        "model": "deepseek-v4-flash",
        "messages": messages,
        "temperature": 0.3,
        "stream": False,
    }

    for attempt in range(MAX_RETRIES):
        try:
            result = hm_aigc.aigc_managed(
                model_agent="yibu",
                req_data=req_data,
                sub_account_name='一步_教育办公_侯宇泰_0601-2',
                model="deepseek-v4-flash",
                timeout=2000
            )
            code = result['choices'][0]['message']['content']
            # Strip markdown fences if present
            code = re.sub(r"^```(?:python)?\s*|```\s*$", "", code.strip(), flags=re.MULTILINE).strip()
            return code
        except Exception as e:
            logging.warning("Graph code API attempt %d/%d failed: %s", attempt + 1, MAX_RETRIES, e)
    return None


# ── LLM code cache ─────────────────────────────────────────────────────

def _graph_code_cache_path(source_path: Path) -> Path:
    """Return cache file path for LLM-generated graph code."""
    return source_path.with_name(source_path.stem + "_graph_code_cache.py")


def _prompt_hash() -> str:
    """Return a short hash of PROMPT_GRAPH_CODE so cache auto-invalidates on prompt changes."""
    return hashlib.md5(PROMPT_GRAPH_CODE.encode()).hexdigest()[:8]


def _load_graph_code_cache(source_path: Path) -> Optional[str]:
    """Load cached LLM graph code if source file and prompt haven't changed."""
    cache_path = _graph_code_cache_path(source_path)
    if not cache_path.exists():
        return None
    try:
        first_line = cache_path.read_text(encoding="utf-8").split("\n")[0]
        # First line is a JSON comment with metadata
        if first_line.startswith("#"):
            meta = json.loads(first_line[1:])
            cached_mtime = meta.get("source_mtime", 0)
            cached_phash = meta.get("prompt_hash", "")
            current_mtime = source_path.stat().st_mtime
            if cached_mtime >= current_mtime and cached_phash == _prompt_hash():
                code = cache_path.read_text(encoding="utf-8")
                # Remove first metadata comment line
                code = code.split("\n", 1)[1] if "\n" in code else code
                logging.info("  Using cached LLM graph code")
                return code
    except Exception:
        pass
    return None


def _save_graph_code_cache(source_path: Path, code: str):
    """Save LLM graph code to cache with metadata."""
    cache_path = _graph_code_cache_path(source_path)
    meta = json.dumps({
        "source_mtime": source_path.stat().st_mtime,
        "prompt_hash": _prompt_hash(),
    })
    cache_path.write_text(f"#{meta}\n{code}", encoding="utf-8")


# ── Graph code fetcher ─────────────────────────────────────────────────

def fetch_graph_code(tool_defs: List[Dict], source_path: Optional[Path] = None) -> Optional[str]:
    """Call LLM to generate graph construction code.  Saves to cache, returns code string.

    Does NOT build or execute anything — just generates and caches the Python code.
    """
    # Try cache first
    if source_path is not None:
        cached = _load_graph_code_cache(source_path)
        if cached is not None:
            return cached

    auths = {t["name"] for t in tool_defs if is_auth(t["name"])}

    # Build compact tool summary for LLM
    tool_summaries = []
    for t in tool_defs:
        if t["name"] in auths:
            continue
        params = t.get("parameters", {}).get("properties", {})
        param_str = ", ".join(
            f"{k}: {v.get('type','any')}" for k, v in params.items()
        )
        desc = t.get("description", "")[:200]
        summary = f"{t['name']}({param_str})"
        if desc:
            summary += f" — {desc}"
        tool_summaries.append(summary)

    prompt = PROMPT_GRAPH_CODE.replace("{{TOOL_DEFS}}", "\n".join(tool_summaries))
    code = _call_api_for_graph_code(prompt)

    if code is not None and source_path is not None:
        _save_graph_code_cache(source_path, code)

    return code


# ── DEFAULT_STATE extraction ────────────────────────────────────────────

def extract_default_state(source_file: Path) -> Optional[Dict]:
    """Parse DEFAULT_STATE dict literal using AST — handles nested structures."""
    try:
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
    except Exception:
        return None
    for node in ast.iter_child_nodes(tree):
        # Plain assignment: DEFAULT_STATE = {...}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("DEFAULT_"):
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        return None
        # Annotated assignment: DEFAULT_STATE: Dict[...] = {...}
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id.startswith("DEFAULT_"):
                try:
                    return ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    return None
    return None


def extract_module_docstring(source_file: Path) -> Optional[str]:
    """Extract the module-level docstring from a Python source file."""
    try:
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        return ast.get_docstring(tree)
    except Exception:
        return None


# ── LLM-based env doc generation ───────────────────────────────────────

PROMPT_ENV_DOC = """You are documenting a tool environment for an Agentic RL training system. Given the environment name and its tool definitions, infer the persistent state structure.

### Environment name
{{ENV_NAME}}

### Tool definitions
{{TOOL_DEFS}}

### Your tasks
1. **env_des**: one English paragraph (<200 chars) describing what this system does.
2. **state_des**: Infer the persistent state schema by analyzing tool parameters and return types. Look for entities that tools read/write.

### state_des format — output a structured schema, NOT prose. Follow this exact format:
```
Environment state fields:
"entity_name_1": dict of <id> ->
    "field_a": str (e.g. "sample_value")
    "field_b": int (e.g. 42)
    "nested": dict of <id> ->
        "sub_field": str (e.g. "sample")
"entity_name_2": list of dict ->
    "field_x": str (e.g. "sample")
    "field_y": float (e.g. 3.14)
"simple_field": str (e.g. "default_value")
```

### Output JSON
{
  "env_des": "one English paragraph",
  "state_des": "structured schema as shown above — field-level, not prose"
}"""

_ENV_DOC_PHASH = hashlib.md5(PROMPT_ENV_DOC.encode()).hexdigest()[:8]


def _env_doc_cache_path(env_name: str) -> Path:
    return Path(DOCS_DIR) / f"{env_name}_llm_docs.json"


def _load_env_doc_cache(env_name: str, expected_phash: str = None) -> Optional[dict]:
    p = _env_doc_cache_path(env_name)
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        if expected_phash and data.get("_prompt_hash") != expected_phash:
            return None  # prompt changed, invalidate
        return data
    return None


def _save_env_doc_cache(env_name: str, docs: dict, phash: str):
    p = _env_doc_cache_path(env_name)
    docs["_prompt_hash"] = phash
    docs["_tool_count"] = docs.get("_tool_count", 0)
    p.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")


def _fill_env_docs_via_llm(env_name: str, tool_defs: List[Dict]) -> dict:
    """Call LLM to generate env_des and state_des. Cached per env + tool count + prompt hash."""
    tool_summaries = []
    for t in tool_defs:
        desc = t.get("description", "")[:200]
        tool_summaries.append(f"{t['name']}: {desc}" if desc else t["name"])

    prompt = PROMPT_ENV_DOC.replace("{{ENV_NAME}}", env_name)
    prompt = prompt.replace("{{TOOL_DEFS}}", "\n".join(tool_summaries))

    cached = _load_env_doc_cache(env_name, _ENV_DOC_PHASH)
    if cached and cached.get("_tool_count") == len(tool_defs):
        return cached

    from hmwrangler import hm_aigc

    messages = [{"role": "user", "content": prompt}]
    req_data = {
        "model": "deepseek-v4-flash",
        "messages": messages,
        "temperature": 0.3,
        "stream": False,
        "response_format": {"type": "json_object"},
    }

    for attempt in range(MAX_RETRIES):
        try:
            result = hm_aigc.aigc_managed(
                model_agent="yibu",
                req_data=req_data,
                sub_account_name='一步_教育办公_侯宇泰_0601-2',
                model="deepseek-v4-flash",
                timeout=300
            )
            content = result['choices'][0]['message']['content']
            if content.startswith("```"):
                content = re.sub(r"^```json|^```|```$", "", content, flags=re.MULTILINE).strip()
            if isinstance(content, str):
                result = json.loads(content)
                result["_tool_count"] = len(tool_defs)
                _save_env_doc_cache(env_name, result, _ENV_DOC_PHASH)
                return result
        except Exception as e:
            logging.warning("Env doc API attempt %d/%d failed: %s", attempt + 1, MAX_RETRIES, e)
    return {}

# ── DEFAULT_STATE extraction ────────────────────────────────────────────


def _describe_value(v) -> str:
    """Return a compact type string for a value, e.g. '{str: {make: str}}' or '[int]'."""
    if v is None:
        return "null"
    if isinstance(v, dict):
        if not v:
            return "{}"
        first_key = list(v.keys())[0]
        first_val = v[first_key]
        kt = type(first_key).__name__
        if isinstance(first_val, dict):
            inner = _describe_dict_inner(first_val)
            return f"{{{kt}: {{{inner}}}}}"
        else:
            inner = _describe_dict_inner(v)
            return f"{{{inner}}}"
    if isinstance(v, list):
        if not v:
            return "[]"
        if isinstance(v[0], dict):
            inner = _describe_dict_inner(v[0])
            return f"[{{{inner}}}]"
        else:
            return f"[{type(v[0]).__name__}]"
    return type(v).__name__


def _describe_dict_inner(d: dict) -> str:
    """Return inner dict fields as 'field: type, field: type, ...'."""
    parts = []
    for k, v in d.items():
        parts.append(f"{k}: {_describe_value(v)}")
    return ", ".join(parts)


def state_to_description(state: Dict) -> str:
    """Generate a compact nested-type description of the state schema."""
    if not state:
        return "No persistent state."
    lines = ["Environment state fields:", "{"]
    for k, v in state.items():
        lines.append(f"  {k}: {_describe_value(v)},")
    lines.append("}")
    return "\n".join(lines)


_STATE_DES_PREFIX = """Based on the instructions below, synthesize a complex and realistic initial state for the {{ENV_NAME}} tool.

1. Goals and Format Requirements
Goal: Synthesize a state dictionary representing the initial running state of the {{ENV_NAME}}.

Required Keys: The state dictionary must include all of the following keys, and their formats and types must strictly adhere to the definitions:"""


def format_state_des(env_name: str, state: Dict) -> str:
    """Wrap state description with the instruction prefix."""
    prefix = _STATE_DES_PREFIX.replace("{{ENV_NAME}}", env_name)
    inner = state_to_description(state)
    return prefix + "\n" + inner


# ── Per-env worker ──────────────────────────────────────────────────────

def _process_env(sf, wrappers_dir, out_docs_dir, existing_docs, lock):
    """Process a single environment: extract tools, docs, state, fetch graph code."""
    env_name = sf.stem
    log.info("Processing: %s", env_name)

    tool_defs = None

    # Try wrapper first, fall back to direct AST
    wrapper_file = wrappers_dir / f"{env_name}_wrapper.py"
    if wrapper_file.exists():
        wrapper_mod = _load_module(wrapper_file)
        if wrapper_mod:
            wrapper_cls = _find_wrapper_class(wrapper_mod)
            if wrapper_cls:
                try:
                    tool_defs = wrapper_cls.__new__(wrapper_cls).get_function_docs()
                except Exception:
                    log.warning("  wrapper get_function_docs() failed, falling back to AST")

    if tool_defs is None:
        tool_defs = extract_tools_from_source(sf)

    if not tool_defs:
        log.warning("  SKIP: no tools for %s", env_name)
        return False

    log.info("  %d tools", len(tool_defs))

    # Save tool definitions
    tool_doc_file = out_docs_dir / f"{env_name}.json"
    tool_doc_file.write_text(json.dumps(tool_defs, indent=2, ensure_ascii=False), encoding="utf-8")

    # Extract state and docstring
    state = extract_default_state(sf) or {}
    state_des = state_to_description(state)
    docstring = extract_module_docstring(sf)

    # Build instruction prefix with env name substituted
    instruction = _STATE_DES_PREFIX.replace("{{ENV_NAME}}", env_name)

    if docstring:
        env_des = docstring.strip().replace("\n", " ")
    elif state:
        # Has state but no docstring: LLM fills env_des only
        llm_docs = _fill_env_docs_via_llm(env_name, tool_defs)
        env_des = llm_docs.get("env_des", env_name)
    else:
        # Neither docstring nor state: LLM fills env_des only
        llm_docs = _fill_env_docs_via_llm(env_name, tool_defs)
        env_des = llm_docs.get("env_des", env_name)

    with lock:
        existing_docs[env_name] = {
            "instruction": instruction,
            "env_des": env_des,
            "state_des": state_des,
        }

    # Fetch graph construction code from LLM (cache-aware)
    code = fetch_graph_code(tool_defs, source_path=sf)
    if code is None:
        log.warning("  LLM failed, tool def saved. Graph code SKIP for %s", env_name)
        return False

    return True


# ── Main ────────────────────────────────────────────────────────────────

def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--env", help="Single env (e.g. web_search)")
    p.add_argument("--source-dir", default=None, help="Source env directory (default: source_env/)")
    p.add_argument("--workers", type=int, default=70, help="Concurrent workers (default: 8)")
    args = p.parse_args()

    root = Path(__file__).parent
    wrappers_dir = root / "wrappers"
    source_dir = Path(args.source_dir) if args.source_dir else root / "source_env"
    out_docs_dir = root / "env_chains" / "tool_env_docs"
    env_docs_path = out_docs_dir / "env_docs.json"

    out_docs_dir.mkdir(parents=True, exist_ok=True)

    # Load existing env_docs
    existing_docs: Dict = {}
    if env_docs_path.exists():
        existing_docs = json.loads(env_docs_path.read_text(encoding="utf-8"))
        log.info("Loaded %d env docs from %s", len(existing_docs), env_docs_path)

    # Discover source files
    source_files = sorted(source_dir.glob("*.py"))
    _NON_ENV = {"__init__", "base", "utils", "test_file", "memory_api_metaclass"}
    source_files = [f for f in source_files if f.stem not in _NON_ENV and not f.stem.endswith("_graph_code_cache")]

    if not source_files:
        log.error("No source files found in %s", source_dir)
        return 1

    # Filter by --env
    if args.env:
        source_files = [f for f in source_files if f.stem == args.env]
        if not source_files:
            log.error("No source file matching --env %s", args.env)
            return 1

    lock = threading.Lock()
    total_generated = 0
    n_workers = min(args.workers, len(source_files))

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = {
            executor.submit(
                _process_env, sf, wrappers_dir, out_docs_dir, existing_docs, lock
            ): sf.stem
            for sf in source_files
        }
        for future in as_completed(futures):
            env_name = futures[future]
            try:
                if future.result():
                    total_generated += 1
            except Exception as e:
                log.warning("  [ERROR] %s failed: %s", env_name, e)

    # Write updated env_docs
    env_docs_path.write_text(json.dumps(existing_docs, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Updated env_docs.json with %d environments", len(existing_docs))

    print(f"\nDone. Tool defs saved for {len(existing_docs)} envs, graph code for {total_generated} envs.")
    print(f"Next: python build_graphs.py")
    return 0


# ── Module loading helpers ──────────────────────────────────────────────

def _load_module(path: Path):
    import importlib.util

    name = path.stem
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        log.exception("Failed to load %s", path.name)
        return None


def _find_wrapper_class(mod) -> Optional[type]:
    """Find the lone wrapper class in the module (the one that's not imported)."""
    import inspect

    for name, obj in mod.__dict__.items():
        if isinstance(obj, type):
            if hasattr(obj, "get_function_docs"):
                return obj
            # Some wrappers may inherit get_function_docs — check
            if any(
                hasattr(obj, m)
                for m in ["execute_function_call", "get_function_docs"]
            ):
                return obj
    return None


# ── Direct source_env AST extraction ──────────────────────────────────

LIFECYCLE_METHODS = {
    "__init__", "_load_scenario", "get_env_state", "reset",
    "_timestamp", "_api_description",
}

PY_TO_JSON_TYPE = {
    "str": "string", "int": "integer", "float": "float",
    "bool": "boolean", "dict": "dict", "list": "array",
    "NoneType": "null",
}


def _ast_type_to_str(node) -> str:
    if node is None:
        return "string"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Subscript):
        if isinstance(node.value, ast.Name):
            return node.value.id
    if isinstance(node, ast.Constant):
        return type(node.value).__name__
    return "string"


def _py_type_to_json(ast_node) -> str:
    type_str = _ast_type_to_str(ast_node).lower()
    return PY_TO_JSON_TYPE.get(type_str, "string")


def _parse_method_docstring(doc: str) -> Dict[str, Any]:
    """Extract description, Args, and Returns from a Google-style docstring."""
    result: Dict[str, Any] = {"description": "", "args": {}, "returns": {}}
    if not doc:
        return result
    doc = doc.strip()
    lines = doc.split("\n")
    summary_lines = []
    current_section = None
    current_arg = None
    current_arg_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Args:"):
            current_section = "args"
            continue
        elif stripped.startswith("Returns:"):
            current_section = "returns"
            continue
        elif stripped.startswith("Attributes:"):
            current_section = "attributes"
            continue
        if current_section is None:
            summary_lines.append(stripped)
        elif current_section == "args":
            m = re.match(r"^(\w+)\s*(?:\([^)]+\))?\s*:(.*)", stripped)
            if m:
                if current_arg:
                    result["args"][current_arg] = " ".join(current_arg_lines).strip()
                current_arg = m.group(1)
                current_arg_lines = [m.group(2).strip()]
            elif current_arg:
                current_arg_lines.append(stripped)
        elif current_section == "returns":
            m = re.match(r"^(\w+)\s*(?:\([^)]+\))?\s*:(.*)", stripped)
            if m:
                result["returns"][m.group(1)] = m.group(2).strip()

    if current_arg:
        result["args"][current_arg] = " ".join(current_arg_lines).strip()
    result["description"] = " ".join(s for s in summary_lines if s)
    return result


def extract_tools_from_source(source_path: Path) -> Optional[List[Dict]]:
    """Parse a source_env .py file via AST and return tool definitions."""
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning("  AST parse failed for %s: %s", source_path.name, e)
        return None

    # Find the env class (has lifecycle methods like _load_scenario, get_env_state).
    # Files may have helper classes (e.g. Simulator); we want the main one.
    env_markers = {"_load_scenario", "get_env_state"}
    cls_nodes = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]

    # Collect all classes that have lifecycle markers, pick the one with most methods
    # (Files may have abstract base classes with stub lifecycle methods; the real env
    # class has many more methods.)
    candidates = []
    for cn in cls_nodes:
        method_names = {
            item.name for item in ast.iter_child_nodes(cn)
            if isinstance(item, ast.FunctionDef)
        }
        if env_markers & method_names:
            candidates.append((len(method_names), cn))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        cls_node = candidates[0][1]
    elif cls_nodes:
        cls_node = cls_nodes[0]
    else:
        cls_node = None

    if cls_node is None:
        return None

    tools = []
    for item in ast.iter_child_nodes(cls_node):
        if not isinstance(item, ast.FunctionDef):
            continue
        name = item.name
        if name in LIFECYCLE_METHODS:
            continue
        if name.startswith("_") and name != "__init__":
            continue
        # Skip @property, @staticmethod, @classmethod
        if any(
            (isinstance(d, ast.Name) and d.id in ("property", "staticmethod", "classmethod"))
            or (isinstance(d, ast.Attribute) and d.attr in ("setter", "deleter"))
            for d in item.decorator_list
        ):
            continue

        doc = ast.get_docstring(item) or ""
        parsed = _parse_method_docstring(doc)

        props = {}
        for arg in item.args.args:
            if arg.arg == "self":
                continue
            ptype = _py_type_to_json(arg.annotation)
            desc = parsed["args"].get(arg.arg, arg.arg)
            props[arg.arg] = {"type": ptype, "description": desc}

        defaults = item.args.defaults
        default_count = len(defaults)
        param_names = [a.arg for a in item.args.args if a.arg != "self"]
        required = param_names[:len(param_names) - default_count] if default_count > 0 else param_names

        resp_props = {}
        for rname, rdesc in parsed["returns"].items():
            jtype = "string"
            d = rdesc.lower()
            if "bool" in d:
                jtype = "boolean"
            elif "int" in d:
                jtype = "integer"
            elif "float" in d:
                jtype = "float"
            elif "list" in d or "array" in d:
                jtype = "array"
            elif "dict" in d:
                jtype = "dict"
            resp_props[rname] = {"type": jtype, "description": rdesc}

        tools.append({
            "name": name,
            "description": parsed["description"],
            "parameters": {
                "type": "dict",
                "properties": props,
                "required": required,
            },
            "response": {
                "type": "dict",
                "properties": resp_props,
            },
        })

    return tools if tools else None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
