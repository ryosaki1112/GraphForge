
## 📘 `README.md`（GraphForge v23・GUI対応・完全バイリンガル）

````markdown
# GraphForge v23

GraphForge v23 は、自然言語で記述された設計書をもとに、構造的な Web アプリケーション（FastAPI + React）コードを自動生成する LLM ワークフローです。GUI（Streamlit）にも対応しており、設計・会話・生成・出力を一貫して実行可能です。  
GraphForge v23 is an LLM-based workflow system that generates structured web application code (FastAPI + React) from natural language design documents. It supports a GUI (via Streamlit) for a seamless experience from design to deployment.

---

## 🚀 起動方法 / How to Run

### 1. 必要ライブラリのインストール  
Install required libraries:

```bash
pip install -r requirements.txt
````

### 2. Ollama モデルの起動

Start local LLM model (Qwen3:8B) via Ollama:

```bash
ollama run qwen:8b
```

> `ollama pull qwen:8b` を事前に実行しておく必要があります。
> You must run `ollama pull qwen:8b` beforehand.

### 3. GUIモードの起動

Run Streamlit GUI:

```bash
streamlit run dashboard.py
```

---

## 🧠 GUI機能の概要 / GUI Features Overview

| 機能 (日本語)      | Feature (English)                         |
| ------------- | ----------------------------------------- |
| 🧠 設計対話モード    | Natural language chat-based spec drafting |
| 📄 仕様.md生成    | Generate markdown spec from chat          |
| 🚀 コード自動生成    | Generate structured code with LangGraph   |
| 📥 ファイルダウンロード | Download output files via GUI             |
| 🧪 実行方法提示     | Show how to run main.py if exists         |

---

## 📝 仕様入力例 / Example Specification Input

```text
このアプリではユーザーがタスクを登録できる。タスクにはタイトルと期限がある。
一覧画面と詳細画面が必要。フロントはReact、バックエンドはFastAPI。
```

> Example: “Users can register tasks with a title and deadline. The app requires both a list and detail view. Frontend: React, Backend: FastAPI.”

---

## 📦 出力ファイル構成例 / Example Output Structure

```
build/
└── proj-20250505-xxxxx/
    ├── app/
    │   ├── main.py
    │   ├── openapi.json
    │   ├── routes/task.py
    │   └── ...
    ├── frontend/
    │   ├── src/App.jsx
    │   ├── pages/Home.jsx
    │   └── ...
    └── README.md  ← 自動生成 / Auto-generated
```

---

## ✨ 特徴 / Key Advantages

| 特徴（日本語）                | Features (English)                               |
| ---------------------- | ------------------------------------------------ |
| 🔁 LangGraph による状態管理   | State-machine-based orchestration with LangGraph |
| 🧠 ローカルLLM統合（Qwen3:8B） | Local LLM integration via Ollama (Qwen3:8B)      |
| 🧪 整合性チェックループ          | Built-in static validation + regeneration loop   |
| 📄 構造的ファイル分割           | Structured and modular file output               |
| 🖥️ GUI操作でのコード生成       | Code generation with interactive GUI             |
| 🔧 再編集・再生成が可能          | Re-edit and regenerate from markdown spec        |

---

## 📝 ライセンス / License

MIT License

