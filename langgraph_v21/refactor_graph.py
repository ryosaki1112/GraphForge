# refactor_graph.py

import pathlib
import re
import json
from typing import TypedDict, NotRequired
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langchain_community.chat_models.ollama import ChatOllama
import config

# ---------- 状態定義 ----------
class RefactorState(TypedDict):
    project_dir: str
    target_file: str
    original_code: str
    prompt: str
    sections: str
    revised_code: NotRequired[str]
    check_result: NotRequired[str]
    progress: NotRequired[list[str]]

# ---------- 進捗ログ用 ----------
step_counter = {"i": 0}
def log_progress(state: RefactorState, step_desc: str):
    step_counter["i"] += 1
    msg = f"[STEP {step_counter['i']}] {step_desc}"
    state.setdefault("progress", []).append(msg)
    return {}

# ---------- コードクレンジングヘルパー ----------
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

# ---------- 簡易静的チェック ----------
def quick_check(files: dict) -> list[str]:
    issues = []
    for filename, content in files.items():
        if "import " not in content and "def " not in content:
            issues.append(f"{filename}: 関数も import も見つかりません")
    return issues

# ---------- LLM インスタンス ----------
llm = ChatOllama(model=config.MODEL, base_url=config.OLLAMA_BASE_URL)

# ---------- 改修実行ノード ----------
def run_refactor(state: RefactorState) -> RefactorState:
    log_progress(state, f"改修開始: {state['target_file']}")
    
    system = "以下のコードを、ユーザーの指示と設計セクション構造に基づいて改善してください。"
    user_code = f"## 改修対象ファイル: {state['target_file']}\n\n```\n{state['original_code']}\n```"
    user_prompt = f"## 改修指示:\n{state['prompt']}"
    user_sections = f"## 全体設計セクション:\n{state['sections']}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_code},
        {"role": "user",   "content": user_prompt},
        {"role": "user",   "content": user_sections},
    ]

    try:
        raw = llm.invoke(messages)
        raw_content = getattr(raw, "content", str(raw))
    except Exception as e:
        raise RuntimeError(f"LLM 改修呼び出しエラー: {e}")

    # クレンジング
    cleaned = remove_think_tags(raw_content)
    cleaned = remove_after_last_fence(cleaned)
    cleaned = remove_code_fences(cleaned)
    cleaned = trim_backtick_content(cleaned)

    state["revised_code"] = cleaned
    log_progress(state, "改修コード取得完了")
    return state

# ---------- 整合性チェックノード ----------
def consistency_check(state: RefactorState) -> RefactorState:
    log_progress(state, "整合性チェック開始")
    files = { state["target_file"]: state["revised_code"] }
    issues = quick_check(files)
    if issues:
        state["check_result"] = "; ".join(issues)
        log_progress(state, f"整合性チェック: 問題検出 ({state['check_result']})")
    else:
        state["check_result"] = "OK"
        log_progress(state, "整合性チェック: OK")
    return state

# ---------- グラフ定義 ----------
def build_refactor_graph():
    builder = StateGraph(state_schema=RefactorState)
    builder.add_node("refactor", RunnableLambda(run_refactor))
    builder.add_node("check",   RunnableLambda(consistency_check))
    builder.add_node("finalize", RunnableLambda(lambda s: {}))

    builder.set_entry_point("refactor")
    builder.add_edge("refactor", "check")
    # static issues があれば再度改修ノードへ、なければ終了
    builder.add_conditional_edges("check", lambda s: {
        "refactor": s.get("check_result", "").startswith("STATIC_ISSUES"),
        "finalize": not s.get("check_result", "").startswith("STATIC_ISSUES"),
    })

    return builder.compile()

# ---------- 状態構築ユーティリティ ----------
def prepare_refactor_state(
    project_dir: pathlib.Path,
    target_file: str,
    original_code: str,
    prompt: str,
    sections: str,
) -> RefactorState:
    return {
        "project_dir": str(project_dir),
        "target_file": target_file,
        "original_code": original_code,
        "prompt": prompt,
        "sections": sections,
        "revised_code": "",
        "check_result": "",
        "progress": [],
    }
