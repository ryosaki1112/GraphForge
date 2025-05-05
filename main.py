# main.py
import streamlit as st
from dashboard import run_dashboard
from dashboard_editor import refactor_ui

st.set_page_config(page_title="GraphForge Launcher", layout="wide")
st.title("GraphForge モード選択")

mode = st.radio("モードを選んでください", ["設計・生成モード", "既存プロジェクト改修モード"])

if mode == "設計・生成モード":
    run_dashboard()
elif mode == "既存プロジェクト改修モード":
    refactor_ui()
