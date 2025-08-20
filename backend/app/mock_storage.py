import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Resolve DATA_DIR relative to this file, assuming the structure is backend/app/mock_storage.py
# and data/ is at the project root.
try:
    # This will work when running from the backend/ directory or project root.
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
except NameError:
    # Fallback for environments where __file__ is not defined (e.g. some interactive shells)
    ROOT_DIR = Path(os.getcwd())

DATA_DIR = os.getenv("DATA_DIR", ROOT_DIR / "data")
MOCKS_FILE = Path(DATA_DIR) / "mocks.json"

def get_all_mocks() -> List[Dict[str, Any]]:
    """
    Reads all mock configurations from the JSON file.
    """
    if not MOCKS_FILE.exists():
        return []
    try:
        with open(MOCKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_mock(mock_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds a new mock configuration to the list and saves it.
    """
    all_mocks = get_all_mocks()
    # Assign a new ID
    new_id = max([m.get('id', 0) for m in all_mocks] + [0]) + 1
    mock_config['id'] = new_id
    all_mocks.append(mock_config)

    # Ensure the directory exists
    MOCKS_FILE.parent.mkdir(exist_ok=True)
    with open(MOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_mocks, f, ensure_ascii=False, indent=2)

    return mock_config

def clear_all_mocks():
    """
    Deletes all mock configurations.
    """
    if MOCKS_FILE.exists():
        os.remove(MOCKS_FILE)
