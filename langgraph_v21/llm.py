import time

# 疑似ストリーム出力で LLM 呼び出しをラップ
def invoke_streaming(prompt: str, chunk_size: int = 80, delay: float = 0.05) -> str:
    full_response = llm.chat(prompt) if hasattr(llm, "chat") else llm.invoke(prompt).content
    streamed = ""
    for i in range(0, len(full_response), chunk_size):
        chunk = full_response[i:i+chunk_size]
        print(chunk, end="", flush=True)  # コンソール即時出力（UIでキャプチャ可）
        streamed += chunk
        time.sleep(delay)  # 疑似ストリームの間隔
    print()  # 行末改行
    return streamed

# ダミーLLMの定義（テスト用）
class DummyLLM:
    def chat(self, prompt):
        return "これは模擬的な応答です。逐次的に表示されるように設計されています。ご確認ください。"

# 使用切り替え（本番 or モック）
USE_DUMMY = False
llm = DummyLLM() if USE_DUMMY else ChatOllama(model="qwen3:8b", base_url="http://localhost:11434")
