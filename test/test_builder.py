import pytest
import threading
from unittest.mock import MagicMock
from langgraph_v21.graph_build import (
    parse_db_schema,
    _clean_llm_output,
    gen_db_files,
    gen_files_parallel,
    setup_logging,
    AppState
)

@pytest.fixture
def mock_async_invoke(monkeypatch):
    """Mock async_invoke to return a fixed string, avoiding Ollama API calls."""
    async def fake_async_invoke(prompt: str) -> str:
        return "mocked_output"
    monkeypatch.setattr('langgraph_v21.graph_build.async_invoke', fake_async_invoke)

def test_clean_llm_output():
    inp = "```py\nx=1\n```\n<think>t</think>"
    assert _clean_llm_output(inp) == "x=1"

def test_parse_db_schema_empty(monkeypatch, tmp_path):
    state = {"design": "No DB info", "project_dir": str(tmp_path)}
    monkeypatch.setattr('langgraph_v21.graph_build.safe_invoke', lambda p: "")
    res = parse_db_schema(state)
    assert res == {"db_schema": {}}

def test_parse_db_schema_malformed(monkeypatch, tmp_path):
    state = {"design": "Bad JSON", "project_dir": str(tmp_path)}
    monkeypatch.setattr('langgraph_v21.graph_build.safe_invoke', lambda p: "{bad")
    res = parse_db_schema(state)
    assert res == {"db_schema": {}}

@pytest.mark.asyncio
async def test_gen_db_files_invalid(monkeypatch, tmp_path, mock_async_invoke):
    state: AppState = {
        "project_dir": str(tmp_path),
        "db_schema": {"db_type":"postgresql","tables":[{"name":"Users","columns":[{"name":"id","type":"int"}]}]},
        "db_config": {"user":"u","password":"p","name":"d","port":"5432"}
    }
    monkeypatch.setattr('langgraph_v21.graph_build.safe_invoke', lambda p: "class X: pass")
    monkeypatch.setattr('langgraph_v21.graph_build.write_file', MagicMock())  # I/O モック
    res = await gen_db_files(state)
    assert res == {}

@pytest.mark.asyncio
async def test_gen_files_parallel_threadsafe(monkeypatch, tmp_path, mock_async_invoke):
    state = {"sections":"{}", "project_dir": str(tmp_path)}
    monkeypatch.setattr('langgraph_v21.graph_build.safe_invoke', lambda p: "print('ok')")
    monkeypatch.setattr('langgraph_v21.graph_build.write_file', MagicMock())  # I/O モック
    results = await gen_files_parallel(state, ["a.py","b.py"])
    assert set(results.keys()) == {"a.py","b.py"}