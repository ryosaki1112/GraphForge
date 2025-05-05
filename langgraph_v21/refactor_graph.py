# refactor_graph.py
import pathlib
import re
import json
from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from langchain_community.chat_models.ollama import ChatOllama
import config

# ---- 状態定義 ----
class RefactorState(TypedDict):
    project_dir: str
    target_file: str
    original_code: str
    prompt: str
    sections: str
    revised_code: str
    check_result: str


# ---- ヘルパー ----
def quick_check(files: dict) -> list[str]:
    issues = []
    for filename, content in files.items():
        if "import " not in content and "def " not in content:
            issues.append(f"{filename}: 関数もimportも見つかりません")
    return issues


# ---- ノード定義 ----
llm = ChatOllama(model=config.MODEL, base_url=config.OLLAMA_BASE_URL)

def run_refactor(state: RefactorState) -> RefactorState:
    system = "以下のコードを、ユーザーの指示とセクション構造に基づいて改善してください。"
    user_code = f"""## 改修対象ファイル: {state['target_file']}

```
{state['original_code']}
```"""
    user_prompt = f"## 改修指示:\n{state['prompt']}"
    user_sections = f"## 全体仕様セクション:\n{state['sections']}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_code},
        {"role": "user", "content": user_prompt},
        {"role": "user", "content": user_sections},
    ]

    try:
        result = llm.invoke(messages)
        content = result.content if hasattr(result, "content") else str(result)
    except Exception as e:
        raise RuntimeError(f"LLM 改修呼び出しエラー: {e}")

    state["revised_code"] = content
    return state

def consistency_check(state: RefactorState) -> RefactorState:
    files = {state["target_file"]: state["revised_code"]}
    issues = quick_check(files)
    state["check_result"] = "; ".join(issues) if issues else "OK"
    return state


# ---- グラフ定義 ----
def build_refactor_graph():
    builder = StateGraph(state_schema=RefactorState)
    builder.add_node("refactor", RunnableLambda(run_refactor))
    builder.add_node("check", RunnableLambda(consistency_check))
    builder.set_entry_point("refactor")
    builder.add_edge("refactor", "check")
    return builder.compile()


# ---- 状態構築ユーティリティ ----
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
    }
