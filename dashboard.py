import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
from langgraph_v21.graph_build import build, prepare_state, extract_python_dependencies, extract_node_dependencies
from langgraph_v21.structure_writer import record_structure
import ollama
import traceback

def safe_write_file(path: Path, content: str):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except Exception as e:
        st.error(f"❌ ファイル書き込み失敗: {path} - {e}")
        raise

def run_dashboard():
    st.title("GraphForge v24 Dashboard 🧠")

    st.header("🧠 設計対話モード（自然言語 → 構造化ログ）")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("仕様アイデアを入力してみてください")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("LLM（Qwen3:8B）と対話中..."):
            try:
                response = ollama.chat(
                    model="qwen3:8b",
                    messages=st.session_state.chat_history
                )
                assistant_reply = response['message']['content']
            except Exception as e:
                st.error(f"❌ LLM応答失敗: {e}")
                st.stop()
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).markdown(msg["content"])

    st.divider()
    st.header("📄 LLM対話から仕様.mdを生成して編集")

    if st.button("📝 対話内容を .md として下に反映"):
        md_text = "\n\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.chat_history
            if m['role'] in ("user", "assistant")
        ])
        st.session_state.generated_md = md_text

    md = st.text_area("仕様書（.md相当）", value=st.session_state.get("generated_md", ""), height=300)

    st.divider()
    st.header("🚀 コード自動生成エリア")

    if st.button("🔄 この仕様書からコード生成（LLM→LangGraph）"):
        if not md.strip():
            st.warning("⚠️ 空の仕様書です。入力してください。")
            st.stop()

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_id = uuid.uuid4().hex[:6]
        project_name = f"proj-{timestamp}-{unique_id}"
        project_path = Path("build") / project_name
        app_path = project_path / "app"

        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            st.error(f"❌ プロジェクトディレクトリ作成失敗: {project_path} - {e}")
            st.stop()

        st.code(md, language="markdown")
        st.write("📥 仕様書のLangGraph渡し → `.md → AppState → build().invoke()`")

        with st.spinner("⚙️ LangGraphでコードを生成中..."):
            try:
                state = prepare_state(md, out_dir=str(app_path))
                result = build().invoke(state)
                record_structure(state)

                readme_path = app_path / "README.md"
                readme_content = f"""# {project_name}

このプロジェクトは LangGraph により自動生成されました。

## 仕様概要

\n\n{md.strip()}

## 実行方法

```bash
cd {app_path.as_posix()}
python main.py
```
"""
                safe_write_file(readme_path, readme_content)

                st.success(f"🎉 コード生成成功！プロジェクト: `{project_name}`")
                st.markdown("### 📂 出力ファイル一覧")
                for path in sorted(app_path.rglob("*")):
                    if path.is_file():
                        st.markdown(f"- `{path.relative_to(app_path)}`")
                        try:
                            with open(path, "rb") as f:
                                st.download_button(f"📥 {path.name}", data=f.read(), file_name=path.name)
                        except Exception as e:
                            st.warning(f"⚠️ ダウンロード準備失敗: {path.name} - {e}")

                st.text_input("📝 プロジェクト名をリネーム", value=project_name, key="rename_target")

                st.write("🧪 LangGraphの戻り値:")
                st.json(result)

                main_py = app_path / "main.py"
                if main_py.exists():
                    st.markdown("### 🧪 ローカル実行方法（main.py あり）")
                    st.code(f"cd {app_path.as_posix()}\npython main.py", language="bash")

                st.markdown("## 🧩 依存モジュール")

                st.subheader("🐍 Python依存モジュール")
                py_deps = extract_python_dependencies(str(app_path))
                if py_deps:
                    st.code("pip install " + " ".join(sorted(py_deps)), language="bash")
                    req_txt = "\n".join(sorted(py_deps))
                    (app_path / "requirements.txt").write_text(req_txt, encoding="utf-8")
                    st.success("📄 requirements.txt を自動生成しました。")
                else:
                    st.info("📦 外部依存モジュールは検出されませんでした。")

                st.subheader("📦 Node.js依存モジュール")
                node_deps = extract_node_dependencies(str(app_path))
                if node_deps:
                    st.code("npm install", language="bash")
                    st.json(node_deps)
                else:
                    st.info("📦 frontend/package.json が見つからないか、依存定義がありません。")

            except Exception as e:
                st.error(f"❌ LangGraph実行エラー: {type(e).__name__} - {e}")
                st.code(traceback.format_exc(), language="python")