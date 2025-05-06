# langgraph_v21/consistency.py
"""
静的コードの整合性チェックを行うモジュール
"""
import ast
import json
from typing import Dict, List


def quick_check(files: Dict[str, str]) -> List[str]:
    """
    与えられたファイル群の内容を解析し、以下を検出してエラーリストを返す:
    1. ファイルが空
    2. TODO コメントの存在
    3. Python ファイルの構文エラー
    4. JSON ファイルのパースエラー

    Args:
        files: ファイル名をキー、内容を値とする辞書
    Returns:
        エラー文字列のリスト。
    """
    issues: List[str] = []
    for filename, content in files.items():
        # 空ファイルチェック
        if not content.strip():
            issues.append(f"{filename} is empty")
        # TODO コメント検出
        if "TODO" in content:
            issues.append(f"{filename} contains TODO comment")
        # 拡張チェック
        try:
            if filename.endswith('.py'):
                # Python 構文チェック
                ast.parse(content)
            elif filename.endswith('.json'):
                # JSON 構文チェック
                json.loads(content)
        except SyntaxError as e:
            issues.append(f"SyntaxError in {filename}: {e.msg} (line {e.lineno})")
        except json.JSONDecodeError as e:
            issues.append(f"JSONDecodeError in {filename}: {e.msg} (line {e.lineno})")
        except Exception as e:
            issues.append(f"Error in {filename}: {str(e)}")
    return issues