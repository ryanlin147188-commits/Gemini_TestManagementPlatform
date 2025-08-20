import json
from typing import Optional, List, Dict, Any

from .database import get_db_connection

# Helper to convert Row objects to dictionaries
def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row) if row else None

def _rows_to_dicts(rows: List[Any]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows]

# ---- Generic Case Management ----
def list_cases(table_name: str, project_id: int, keyword: str | None = None, filters: dict | None = None) -> list:
    conn = get_db_connection()
    query = f"SELECT * FROM {table_name} WHERE project_id = ?"
    params = [project_id]

    if keyword:
        # This is a simplification. A real implementation would specify which columns to search.
        # For now, we search in 'test_feature' and 'description'.
        kw = f"%{keyword.lower()}%"
        query += " AND (LOWER(test_feature) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([kw, kw])

    # The filters parameter is complex. I'll implement a simple version for 'action' and 'result'.
    if filters:
        for field, allowed_values in filters.items():
            if allowed_values and (field in ['action', 'result', 'method']):
                placeholders = ','.join('?' for _ in allowed_values)
                query += f" AND {field} IN ({placeholders})"
                params.extend(list(allowed_values))

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return _rows_to_dicts(rows)

def create_case(table_name: str, project_id: int, case_data: dict, id_field: str = "id") -> dict:
    conn = get_db_connection()
    # Pydantic models have a 'model_dump' in v2. The backend uses older pydantic.
    # The incoming 'case_data' is already a dict.

    # We need to filter case_data to only include columns that exist in the table.
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    valid_columns = {row['name'] for row in cursor.fetchall()}

    # Add project_id and remove any invalid columns
    case_data['project_id'] = project_id
    filtered_data = {k: v for k, v in case_data.items() if k in valid_columns}

    columns = ', '.join(filtered_data.keys())
    placeholders = ', '.join('?' for _ in filtered_data)

    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor = conn.cursor()
    cursor.execute(query, list(filtered_data.values()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Return the full record, including the new ID
    case_data[id_field] = new_id
    # The original function returns the input dict with the new ID, so we do the same.
    return case_data

def update_case(table_name: str, project_id: int, case_id: int, case_data: dict, id_field: str = "id") -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    valid_columns = {row['name'] for row in cursor.fetchall()}

    filtered_data = {k: v for k, v in case_data.items() if k in valid_columns and k != id_field}

    if not filtered_data:
        conn.close()
        return get_case(table_name, project_id, case_id, id_field)

    set_clause = ', '.join(f"{key} = ?" for key in filtered_data.keys())
    query = f"UPDATE {table_name} SET {set_clause} WHERE {id_field} = ? AND project_id = ?"

    params = list(filtered_data.values()) + [case_id, project_id]

    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    updated = cursor.rowcount > 0
    conn.close()

    if updated:
        return get_case(table_name, project_id, case_id, id_field)
    return None

def get_case(table_name: str, project_id: int, case_id: int, id_field: str = "id") -> Optional[dict]:
    conn = get_db_connection()
    query = f"SELECT * FROM {table_name} WHERE {id_field} = ? AND project_id = ?"
    row = conn.execute(query, (case_id, project_id)).fetchone()
    conn.close()
    return _row_to_dict(row)

def delete_case(table_name: str, project_id: int, case_id: int, id_field: str = "id") -> bool:
    conn = get_db_connection()
    query = f"DELETE FROM {table_name} WHERE {id_field} = ? AND project_id = ?"
    cursor = conn.cursor()
    cursor.execute(query, (case_id, project_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# ---- App Device Info (Special case, as it's not a list of dicts) ----
# I will create a new table for this.
def _init_device_table():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS app_device_info (
        project_id INTEGER PRIMARY KEY,
        device_info TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    );
    """)
    conn.close()
_init_device_table()

def get_app_device(project_id: int) -> str:
    conn = get_db_connection()
    row = conn.execute("SELECT device_info FROM app_device_info WHERE project_id = ?", (project_id,)).fetchone()
    conn.close()
    return row['device_info'] if row else ""

def set_app_device(project_id: int, text: str) -> None:
    conn = get_db_connection()
    conn.execute("INSERT OR REPLACE INTO app_device_info (project_id, device_info) VALUES (?, ?)", (project_id, text))
    conn.commit()
    conn.close()


# ---- Project-Scoped Bugs ----
def list_project_bugs(project_id: int, keyword: Optional[str] = None, severity: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    conn = get_db_connection()
    query = "SELECT * FROM bugs WHERE project_id = ?"
    params = [project_id]
    if keyword:
        kw = f"%{keyword.lower()}%"
        query += " AND (LOWER(description) LIKE ? OR LOWER(repro) LIKE ? OR LOWER(expected) LIKE ? OR LOWER(actual) LIKE ?)"
        params.extend([kw, kw, kw, kw])
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if status:
        query += " AND status = ?"
        params.append(status)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return _rows_to_dicts(rows)

def create_project_bug(project_id: int, bug_data: dict) -> dict:
    bug_data['project_id'] = project_id
    return create_case('bugs', project_id, bug_data)

def update_project_bug(project_id: int, bug_id: int, bug_data: dict) -> Optional[dict]:
    return update_case('bugs', project_id, bug_id, bug_data)

def get_project_bug(project_id: int, bug_id: int) -> Optional[dict]:
    return get_case('bugs', project_id, bug_id)

def delete_project_bug(project_id: int, bug_id: int) -> bool:
    return delete_case('bugs', project_id, bug_id)


# ---- Projects (Global) ----
def list_projects(keyword: Optional[str] = None, owner: Optional[str] = None, status: Optional[str] = None):
    conn = get_db_connection()
    query = "SELECT * FROM projects WHERE 1=1"
    params = []
    if keyword:
        kw = f"%{keyword.lower()}%"
        query += " AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([kw, kw])
    if owner:
        query += " AND owner = ?"
        params.append(owner)
    if status:
        query += " AND status = ?"
        params.append(status)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return _rows_to_dicts(rows)

def get_project(project_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)

def create_project(data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (name, description, owner, status) VALUES (?, ?, ?, ?)",
        (data.get("name", ""), data.get("description", ""), data.get("owner", ""), data.get("status", "新增"))
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_project(new_id)

def update_project(project_id: int, data: dict):
    conn = get_db_connection()
    conn.execute(
        "UPDATE projects SET name = ?, description = ?, owner = ?, status = ? WHERE id = ?",
        (data.get("name"), data.get("description"), data.get("owner"), data.get("status"), project_id)
    )
    conn.commit()
    conn.close()
    return get_project(project_id)

def delete_project(project_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    # Also delete associated data
    conn.execute("DELETE FROM web_cases WHERE project_id = ?", (project_id,))
    conn.execute("DELETE FROM app_cases WHERE project_id = ?", (project_id,))
    conn.execute("DELETE FROM api_cases WHERE project_id = ?", (project_id,))
    conn.execute("DELETE FROM bugs WHERE project_id = ?", (project_id,))
    conn.execute("DELETE FROM app_device_info WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()
    return True

# Note: The legacy global bug and run functions are removed as they are not used by the current frontend and complicate the DB schema.
# If they are needed, they should be migrated to a non-project-scoped table structure.
def list_bugs(*args, **kwargs): return []
def get_bug(*args, **kwargs): return None
def create_bug(*args, **kwargs): return {}
def update_bug(*args, **kwargs): return None
def delete_bug(*args, **kwargs): return True
def list_runs(*args, **kwargs): return []
def create_run(*args, **kwargs): return {}
def update_run(*args, **kwargs): return None
def delete_run(*args, **kwargs): return True

# Dummy class to avoid breaking imports in main.py
class Project: pass
class Bug: pass
class TestRun: pass

# These paths are no longer used but are imported by main.py
WEB_CASES_PATH = "web_cases"
APP_CASES_PATH = "app_cases"
API_CASES_PATH = "api_cases"
APP_DEVICE_PATH = "app_device_info"

# ---- Mocks ----
def get_all_mocks() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM mocks ORDER BY id ASC").fetchall()
    conn.close()

    mocks = _rows_to_dicts(rows)
    # Deserialize JSON strings back into objects
    for mock in mocks:
        if mock.get('params'):
            mock['params'] = json.loads(mock['params'])
        if mock.get('headers'):
            mock['headers'] = json.loads(mock['headers'])
        if mock.get('response_headers'):
            mock['response_headers'] = json.loads(mock['response_headers'])
    return mocks

def save_mock(mock_config: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()

    # Serialize object fields to JSON strings
    params = json.dumps(mock_config.get('params', []))
    headers = json.dumps(mock_config.get('headers', []))
    response_headers = json.dumps(mock_config.get('response_headers', []))

    query = """
    INSERT INTO mocks (path, method, params, headers, body, response_status, response_headers, response_body, delay_ms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor = conn.cursor()
    cursor.execute(query, (
        mock_config.get('path'),
        mock_config.get('method'),
        params,
        headers,
        mock_config.get('body'),
        mock_config.get('response_status'),
        response_headers,
        mock_config.get('response_body'),
        mock_config.get('delay_ms')
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    mock_config['id'] = new_id
    return mock_config
