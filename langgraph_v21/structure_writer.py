# structure_writer.py
import json
import pathlib
from typing import Any

def save_structure(project_dir: str, structure: dict[str, Any]):
    path = pathlib.Path(project_dir) / "structure.json"
    path.write_text(json.dumps(structure, indent=2, ensure_ascii=False), encoding="utf-8")

def load_structure(project_dir: str) -> dict[str, Any] | None:
    path = pathlib.Path(project_dir) / "structure.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

# --- build用追記 ---
def record_structure(state: dict):
    from config import FILE_KEYS
    from .graph_build import extract_python_dependencies
    project_dir = state.get("project_dir")
    if not project_dir:
        return
    structure = {
        "sections": state.get("sections"),
        "file_keys": FILE_KEYS,
        "python_deps": sorted(extract_python_dependencies(project_dir))
    }
    save_structure(project_dir, structure)
