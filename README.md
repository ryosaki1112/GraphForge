
---

# GraphForge v24

GraphForge v24 は、自然言語の設計文書から FastAPI + React 構成の Web アプリケーションを自動生成する LLM ワークフローです。Streamlit GUI により、仕様対話 → コード生成 → 改修まで一貫して操作可能です。  
GraphForge v24 is an LLM-powered workflow that auto-generates web applications (FastAPI + React) from natural language specs. It includes a full-featured Streamlit GUI for design-to-refactor automation.

---

## 🚀 起動方法 / How to Run

### 1. ライブラリのインストール  
Install required libraries:

```bash
pip install -r requirements.txt
```

### 2. Ollama モデルの準備と起動  
Prepare and launch local LLM (Qwen3:8B):

```bash
ollama pull qwen3:8b
ollama run qwen3:8b
```

### 3. GUI アプリの起動  
Launch the Streamlit GUI:

```bash
streamlit run main.py

```

---

## 🧠 GUI 機能概要 / GUI Feature Overview

| 🧩 機能 | Description |
|--------|-------------|
| 🧠 設計対話モード | Chat-based spec drafting with Qwen3 |
| 📄 .md生成編集 | Markdown spec generation/editing |
| 🚀 LangGraph生成 | Code generation with LangGraph |
| 🛠️ 既存コード改修 | Refactor existing files with structure-aware editing |
| 📥 出力ファイルDL | GUI-based download of outputs |
| 🧪 静的整合性チェック | Built-in static validation loop |
| 🧰 セクション分割編集 | Edit each section of `.sections` individually |
| 🔁 再アップロード対応 | Rebuild from updated markdown input |
|⚙️ 改修モード　| Refactor existing code via structure-aware workflow |
---

## 📝 仕様入力例 / Example Spec Input

```text
ユーザーはタスクを登録できる。タイトルと期限を入力する。  
一覧ページと詳細ページを提供。フロントはReact、バックエンドはFastAPI。
```

> Example: "Users can register tasks with a title and deadline. Requires list and detail views. Frontend: React, Backend: FastAPI."

---

## 📂 出力構成例 / Example Output Structure

```
build/
└── proj-20250505-xxxxx/
    ├── app/
    │   ├── main.py
    │   ├── schemas.py
    │   ├── routes/task.py
    │   ├── openapi.json
    │   └── ...
    ├── frontend/
    │   ├── src/App.jsx
    │   ├── pages/Home.jsx
    │   └── ...
    └── README.md  ← 自動生成
```

---

## ✨ 特徴 / Key Advantages

| 日本語機能                       | English Feature                                      |
|-----------------------------|------------------------------------------------------|
| 💬 チャット設計入力対応            | Natural language prompt-based design                 |
| 📄 Markdown + セクション対応       | Editable .md and structured `.sections` JSON         |
| 🔧 LangGraph による状態制御       | LangGraph-powered step orchestration                 |
| 🧠 ローカルLLM（Qwen3:8B）統合     | Integrated local LLM via Ollama                      |
| 🛠️ GUIからのコード改修・再生成    | Refactor and regenerate directly from GUI            |
| 📥 出力ファイルダウンロード        | One-click download of generated files                |
| 🧪 自動整合性チェックループ        | Built-in static analysis and revalidation loop       |

---

## 📝 ライセンス / License

MIT License（商用利用に関する追加条項あり）

Copyright (c) 2025 ryosaki1112

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"),
to deal in the Software for personal, academic, or non-commercial purposes,
including without limitation the rights to use, copy, modify, merge, publish,
and distribute copies of the Software, subject to the following conditions:

本ソフトウェアおよび付属のドキュメントファイル（以下「本ソフトウェア」）は、
**個人利用・学術研究・非商用目的に限り、自由に使用、複製、改変、マージ、公開、
配布することが許可されます**。

上記の著作権表示および本許諾表示は、本ソフトウェアの全ての複製または
実質的な部分に含める必要があります。

---

🚫 **商用利用について / Commercial Use Restriction**:

- 本ソフトウェアを以下のような**商用目的**で利用する場合、
  事前に開発者から**別途商用ライセンスの取得が必要**です：

  - 有償プロダクトへの組み込み
  - SaaS 形式での提供
  - 業務委託開発での活用
  - 研修・教育事業等での収益化を伴う活用

📮 商用利用の申請・相談先：

- GitHub: https://github.com/ryosaki1112/GraphForge  
- Qiita コメント（カジュアル相談用）:  
  https://qiita.com/cementite/items/17c88d9284f926d30d18

---

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

本ソフトウェアは「現状のまま」提供されており、商品性、特定目的への適合性、
権利非侵害などに関するいかなる保証も行いません。
著作権者は、本ソフトウェアまたはその使用に起因する一切の責任を負いません。



---


