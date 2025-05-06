import streamlit as st
from pathlib import Path
import json
import difflib
from langgraph_v21.refactor_graph import build_refactor_graph, prepare_refactor_state


def load_structure(struct_dir: Path):
    structure_path = struct_dir / "structure.json"
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
    st.header("🔧 既存コード改修（LangGraphワークフロー付き）")

    build_root = Path("build")
    available_projects = sorted([p.name for p in build_root.iterdir() if p.is_dir()])
    selected_project = st.selectbox("📁 改修対象プロジェクトを選択", available_projects)

    if not selected_project:
        st.warning("⚠️ プロジェクトを選択してください。")
        return

    struct_dir = build_root / selected_project / "app"
    code_root = build_root / selected_project

    if not struct_dir.exists():
        st.error("❌ structure.json が存在すべき app フォルダが見つかりません。")
        return

    structure = load_structure(struct_dir)
    if not structure:
        return

    # サイドバー: 依存情報
    with st.sidebar:
        st.subheader("🔗 Python Dependencies")
        py_deps = structure.get("python_deps", [])
        if py_deps:
            for pkg in py_deps:
                st.write(f"- {pkg}")
        else:
            st.write("（なし）")

        st.subheader("🔗 Node Dependencies")
        node_deps = structure.get("node_deps", {})
        if node_deps:
            for name, ver in node_deps.items():
                st.write(f"- {name}@{ver}")
        else:
            st.write("（なし）")

    file_options = structure.get("written", [])
    if not file_options:
        fallback = structure.get("file_keys", [])
        if fallback:
            st.info("structure.json に書き出し履歴がありません。ファイルキー一覧を表示します。")
            file_options = fallback
        else:
            st.info("このプロジェクトには対象ファイルが記録されていません。")
            return

    target_file = st.selectbox("✏️ 改修対象ファイルを選択", file_options)
    # 初期パス: プロジェクト直下
    full_path = code_root / target_file
    # 見つからなければ app フォルダ内も探索
    if not full_path.exists():
        alt_path = struct_dir / target_file
        if alt_path.exists():
            full_path = alt_path

    if not full_path.exists():
        st.error(f"❌ 選択されたファイルが存在しません: {code_root/target_file} または {struct_dir/target_file} にも存在しませんでした。")
        return

    try:
        original_code = full_path.read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"❌ ファイル読み込みエラー: {e}")
        return

    st.subheader("🧾 現在のコード")
    lang = Path(target_file).suffix.lstrip('.') or None
    st.code(original_code, language=lang)

    st.markdown("### 💬 改修仕様対話")
    refactor_prompt = st.text_area("📝 改修指示（自然言語）", height=120)

    if "confirm_ready" not in st.session_state:
        st.session_state.confirm_ready = False

    if st.button("✅ 指示を確認"):
        if len(refactor_prompt.strip()) < 10:
            st.warning("⚠️ 指示が短すぎます。もう少し詳しく書いてください。")
            st.session_state.confirm_ready = False
        else:
            st.success("👍 LLM 改修実行が可能と判断されました。")
            st.session_state.confirm_ready = True

    if st.session_state.confirm_ready and st.button("🛠 改修を実行"):
        with st.spinner("LangGraph ワークフロー実行中..."):
            try:
                state = prepare_refactor_state(
                    project_dir=struct_dir,
                    target_file=target_file,
                    original_code=original_code,
                    prompt=refactor_prompt,
                    sections=structure.get("sections", "")
                )
                graph = build_refactor_graph()
                result = graph.invoke(state)

                revised = result.get("revised_code", "")

                st.subheader("🆕 改修後コード（プレビュー）")
                st.code(revised, language=lang)

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
                st.error(f"❌ 改修中にエラーが発生しました: {e}")

if __name__ == "__main__":
    refactor_ui()