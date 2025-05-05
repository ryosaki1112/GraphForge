import streamlit as st
from pathlib import Path
import json
import difflib
from langgraph_v21.refactor_graph import build_refactor_graph, prepare_refactor_state

def load_structure(project_path: Path):
    structure_path = project_path / "structure.json"
    if not structure_path.exists():
        st.warning("structure.json が存在しません。設計構造が不明です。")
        return None
    try:
        return json.loads(structure_path.read_text(encoding="utf-8"))
    except Exception as e:
        st.error(f"❌ structure.json の読み込みエラー: {e}")
        return None

def refactor_ui():
    st.title("GraphForge ファイル改修モード ✏️")
    st.header("🔧 既存コード改修（LangGraph構造ワークフロー付き）")

    build_root = Path("build")
    available_projects = sorted([p.name for p in build_root.iterdir() if p.is_dir()])
    selected_project = st.selectbox("📁 改修対象プロジェクトを選択", available_projects)

    if not selected_project:
        st.warning("⚠️ プロジェクトを選択してください。")
        return

    project_path = build_root / selected_project / "app"
    if not project_path.exists():
        st.error("❌ 選択されたプロジェクトの app フォルダが存在しません。")
        return

    structure = load_structure(project_path)
    if not structure:
        return

    file_options = structure.get("written", [])
    if not file_options:
        st.info("このプロジェクトには記録されたファイルがありません。")
        return

    target_file = st.selectbox("✏️ 改修対象ファイルを選択", file_options)
    full_path = project_path / target_file

    if not full_path.exists():
        st.error("❌ 選択されたファイルが存在しません。")
        return

    try:
        original_code = full_path.read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"❌ ファイル読み込みエラー: {e}")
        return

    st.subheader("🧾 現在のコード")
    st.code(original_code, language=target_file.suffix.lstrip("."))

    st.markdown("### 💬 改修仕様対話")
    refactor_prompt = st.text_area("📝 改修指示（自然言語で記述）", height=100)

    if "confirm_ready" not in st.session_state:
        st.session_state.confirm_ready = False

    if st.button("✅ この指示で改修可能か確認"):
        with st.spinner("LLMによる改修可否を確認中..."):
            if len(refactor_prompt.strip()) < 10:
                st.warning("⚠️ 指示が曖昧または短すぎます。明確にしてください。")
                st.session_state.confirm_ready = False
            else:
                st.success("👍 LLMによる改修実行が可能と判断されました。")
                st.session_state.confirm_ready = True

    if st.session_state.confirm_ready and st.button("🛠 LangGraph改修を実行"):
        with st.spinner("LangGraphワークフロー実行中..."):
            try:
                state = prepare_refactor_state(
                    project_dir=project_path,
                    target_file=target_file,
                    original_code=original_code,
                    prompt=refactor_prompt,
                    sections=structure.get("sections", "")
                )
                graph = build_refactor_graph()
                result = graph.invoke(state)

                revised = result.get("revised_code", "")

                st.subheader("🆕 改修後コード（プレビュー）")
                st.code(revised, language=target_file.suffix.lstrip("."))

                diff = difflib.unified_diff(
                    original_code.splitlines(),
                    revised.splitlines(),
                    fromfile="元コード",
                    tofile="改修後コード",
                    lineterm=""
                )
                st.subheader("🔀 差分プレビュー")
                st.code("\n".join(diff), language="diff")

                if st.button("💾 上書き保存"):
                    full_path.write_text(revised, encoding="utf-8")
                    st.success("✅ ファイルを保存しました。")
            except Exception as e:
                st.error(f"❌ LangGraph改修中にエラーが発生しました: {e}")
