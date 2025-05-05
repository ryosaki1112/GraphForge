# langgraph_v21/consistency.py

def quick_check(files: dict) -> list:
    issues = []
    for filename, content in files.items():
        if not content.strip():
            issues.append(f"{filename} is empty")
        if "TODO" in content:
            issues.append(f"{filename} contains TODO comment")
    return issues
