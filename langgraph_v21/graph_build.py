import argparse
import re
import pathlib
import hashlib
import os
import sys
import time
import random
from typing import Dict, TypedDict, NotRequired
from langchain_community.chat_models.ollama import ChatOllama
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langgraph_v21.consistency import quick_check
import config

# ---------- 状態定義 ----------
class AppState(TypedDict):
    design: str
    sections: NotRequired[str]
    check_result: NotRequired[str]
    written: NotRequired[list[str]]
    progress: NotRequired[list[str]]
    project_dir: NotRequired[str]

# ---------- ステップログ用 ----------
step_counter = {"i": 0}

def log_progress(state: AppState, step_desc: str):
    step_counter["i"] += 1
    msg = f"[STEP {step_counter['i']}] {step_desc}"
    print(msg, flush=True)
    state.setdefault("progress", []).append(msg)
    return {}

# ---------- LLMセットアップ ----------
llm = ChatOllama(model=config.MODEL, base_url=config.OLLAMA_BASE_URL)

def safe_invoke(prompt: str) -> str:
    try:
        res = llm.invoke(prompt)
        if isinstance(res, str):
            return res
        if hasattr(res, "content"):
            return res.content
        return str(res)
    except Exception as e:
        raise RuntimeError(f"LLM invoke error: {e}")

# ---------- ヘルパー関数 ----------
def remove_think_tags(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def remove_after_last_fence(text: str) -> str:
    idx = text.rfind('```')
    return text[:idx] if idx != -1 else text

def remove_code_fences(text: str) -> str:
    text = re.sub(r'^```[^\n]*\n', '', text, flags=re.MULTILINE)
    return re.sub(r'\n```', '\n', text)

def trim_backtick_content(text: str) -> str:
    return re.sub(r'`([^`]*)`', lambda m: f"`{m.group(1).strip()}`", text)

# ---------- ノード定義 ----------
def entry_node(state: AppState):
    from pathlib import Path
    raw = state.get("project_dir")
    if not raw:
        raise ValueError("project_dir is not set in initial state")
    resolved = Path(raw).resolve()
    print(f"DEBUG entry_node: initial state keys = {list(state.keys())}")
    log_progress(state, f"entry_node: project_dir resolved to {resolved}")
    state["project_dir"] = resolved.as_posix()
    return state

def parse_design(state: AppState):
    log_progress(state, "parse_design: 構造化中")
    raw = safe_invoke(f"Segment the following design document into JSON sections:\n\n{state['design']}\n")
    raw = remove_think_tags(raw)
    raw = remove_after_last_fence(raw)
    raw = remove_code_fences(raw)
    sections = trim_backtick_content(raw)
    return {"sections": sections}

def gen_and_write(state: AppState, filekey: str):
    log_progress(state, f"gen: {filekey} を生成中")
    log_progress(state, f"→ LLM 呼び出し開始: {filekey}")
    prompt = f"Generate `{filekey}` according to these design sections:\n{state['sections']}"
    try:
        raw = safe_invoke(prompt)
        log_progress(state, f"← LLM 応答受信: {filekey}")
    except Exception as e:
        log_progress(state, f"!! LLM 呼び出しエラー ({filekey}): {e}")
        return {}

    raw = remove_think_tags(raw)
    raw = remove_after_last_fence(raw)
    raw = remove_code_fences(raw)
    content = trim_backtick_content(raw)

    try:
        base = pathlib.Path(state["project_dir"])
        out_path = base / filekey
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        log_progress(state, f"write: {out_path}")
    except Exception as e:
        log_progress(state, f"!! ファイル書き込みエラー ({filekey}): {e}")
        return {}

    state.setdefault("written", []).append(str(out_path))
    state[filekey] = content
    return {filekey: content}

def consistency_check(state: AppState):
    log_progress(state, "consistency_check: 整合性チェック中")
    files = {
        k: state[k]
        for k in state
        if k.endswith(('.py', '.json', '.jsx')) and isinstance(state[k], str)
    }
    issues = quick_check(files)
    if issues:
        log_progress(state, "consistency_check: STATIC_ISSUES 検出")
        return {"check_result": "STATIC_ISSUES " + "; ".join(issues)}
    log_progress(state, "consistency_check: OK")
    return {"check_result": "OK"}

def finalize(state: AppState):
    log_progress(state, "build 完了 🎉")
    return {}

# ---------- 出力ファイル一覧 ----------
FILE_KEYS = [
    "main.py",
    "schemas.py",
    "routes/task.py",
    "tests/test_main.py",
    "openapi.json",
    ".github/workflows/test.yml",
    "frontend/src/App.jsx",
    "frontend/src/pages/Home.jsx",
    "frontend/src/components/TaskCard.jsx",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/index.html",
]

# ---------- build() ----------
def build(group_size: int = 3):
    builder = StateGraph(state_schema=AppState)
    builder.add_node("entry", RunnableLambda(entry_node))
    builder.add_node("parse", RunnableLambda(parse_design))
    builder.add_node("check", RunnableLambda(consistency_check))
    builder.add_node("finalize", RunnableLambda(finalize))

    builder.set_entry_point("entry")
    builder.add_edge("entry", "parse")

    prev_nodes = ["parse"]
    for i in range(0, len(FILE_KEYS), group_size):
        group = FILE_KEYS[i : i + group_size]
        current = []
        for key in group:
            def make_fn(k: str):
                return lambda s: gen_and_write(s, k)
            node_id = f"gen_{hashlib.md5(key.encode()).hexdigest()}"
            builder.add_node(node_id, RunnableLambda(make_fn(key)))
            for p in prev_nodes:
                builder.add_edge(p, node_id)
            current.append(node_id)
        prev_nodes = current

    for p in prev_nodes:
        builder.add_edge(p, "check")

    builder.add_conditional_edges("check", lambda s: {
        "parse": ("STATIC_ISSUES" in s.get("check_result", "")),
        "finalize": not ("STATIC_ISSUES" in s.get("check_result", ""))
    })

    return builder.compile()

# ---------- モジュール実行用ユーティリティ ----------
def prepare_state(design: str, out_dir: str = None) -> Dict:
    if out_dir is None:
        out_dir = f"proj-{time.strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    abs_path = os.path.abspath(out_dir)
    os.makedirs(abs_path, exist_ok=True)
    return {
        "design": design,
        "project_dir": abs_path,
    }

# ---------- モジュール実行用 ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangGraph Codegen")
    parser.add_argument("--design", "-d", required=True, help="設計文書をここに渡す")
    parser.add_argument("--out", "-o", default=None, help="出力先フォルダ名（省略時自動生成）")
    args = parser.parse_args()

    # prepare_state() によって project_dir も含めた状態を生成
    state = prepare_state(args.design, args.out)

    print(f"CLI: using output folder {state['project_dir']}")

    # ビルド前に確認待ち
    input("Enterキーでビルドを開始します（確認後に進めたい場合）→ ")

    graph = build(group_size=3)
    result = graph.invoke(state)

    # ビルド進捗ログを表示
    print("\n=== BUILD PROGRESS ===")
    for msg in result.get("progress", []):
        print(msg)

    # 整合性チェック結果
    print("\n=== CHECK RESULT ===", result.get("check_result"))

    # 書き出したファイル一覧
    print("\n=== WRITTEN FILES ===")
    for p in result.get("written", []):
        print(" -", p)

    sys.exit(0) 