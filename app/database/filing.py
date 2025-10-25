from pathlib import Path
import json


def load_files(path: str):
    FILE_PATH = Path(path)
    if not FILE_PATH.exists():
        FILE_PATH.write_text("[]", encoding="utf-8")
        return []
    try:
        with FILE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                data = [item for item in data if isinstance(item, dict)]
                return data
            if isinstance(data, dict):
                return [data]
    except json.JSONDecodeError or IOError:
        return "error: file not found or file"
    return []


def save_files(data, path: str):
    FILE_PATH = Path(path)
    with FILE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
