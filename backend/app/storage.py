
import os, json, threading
from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime

_lock = threading.Lock()

# Paths (can be overridden by env vars)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(ROOT_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)

PROJECTS_PATH = os.getenv("PROJECTS_PATH", os.path.join(DATA_DIR, "projects.json"))
BUGS_PATH     = os.getenv("BUGS_PATH",     os.path.join(DATA_DIR, "bugs.json"))
RUNS_PATH     = os.getenv("RUNS_PATH",     os.path.join(DATA_DIR, "runs.json"))

# Paths for test cases and app devices (project scoped). These files store a mapping
# of project_id (as string) to a list of case dicts or other data. If the file
# contains a list (legacy format), it will be treated as project "1".
WEB_CASES_PATH = os.getenv("WEB_CASES_PATH", os.path.join(DATA_DIR, "web_cases.json"))
APP_CASES_PATH = os.getenv("APP_CASES_PATH", os.path.join(DATA_DIR, "app_cases.json"))
API_CASES_PATH = os.getenv("API_CASES_PATH", os.path.join(DATA_DIR, "api_cases.json"))
APP_DEVICE_PATH = os.getenv("APP_DEVICE_PATH", os.path.join(DATA_DIR, "app_device.json"))

def _load_scoped(path: str) -> dict:
    """Load a mapping of project_id->list from a JSON file. If the file contains a
    plain list (legacy), wrap it as {"1": list}.
    """
    data = _load(path)
    if isinstance(data, list):
        # migrate old format to project "1"
        data = {"1": data}
    if not isinstance(data, dict):
        data = {}
    return data

def _save_scoped(path: str, data: dict) -> None:
    """Save the mapping of project_id->list back to JSON."""
    _save(path, data)

def list_cases(path: str, project_id: int, keyword: str | None = None, filters: dict | None = None) -> list:
    """Return a list of cases for a given project. Optionally filter by keyword and other filters.

    :param filters: a dict of field->set of allowed values (e.g. {'action': {'點擊','填入'}})
    """
    data = _load_scoped(path)
    cases = data.get(str(project_id), [])
    # basic filtering by keyword and fields
    if keyword:
        kw = keyword.lower()
        cases = [c for c in cases if any(kw in str(v).lower() for v in c.values())]
    if filters:
        for field, allowed in filters.items():
            if allowed:
                cases = [c for c in cases if c.get(field) in allowed]
    return cases

def create_case(path: str, project_id: int, case_data: dict, id_field: str = "id") -> dict:
    """Append a new case to the project list. Assigns an incrementing integer to `id_field`.

    :param id_field: the key used for the identifier (e.g. 'id' or 'step')
    """
    data = _load_scoped(path)
    cases = data.get(str(project_id), [])
    # determine next id
    next_id = max([int(c.get(id_field, 0)) for c in cases] + [0]) + 1
    case = dict(case_data)  # copy
    case[id_field] = next_id
    cases.append(case)
    data[str(project_id)] = cases
    _save_scoped(path, data)
    return case

def update_case(path: str, project_id: int, case_id: int, case_data: dict, id_field: str = "id") -> Optional[dict]:
    """Update an existing case. Returns updated record or None if not found."""
    data = _load_scoped(path)
    cases = data.get(str(project_id), [])
    for idx, c in enumerate(cases):
        if str(c.get(id_field)) == str(case_id):
            c.update(case_data)
            cases[idx] = c
            data[str(project_id)] = cases
            _save_scoped(path, data)
            return c
    return None

def get_case(path: str, project_id: int, case_id: int, id_field: str = "id") -> Optional[dict]:
    """Retrieve a single case by its ID."""
    data = _load_scoped(path)
    cases = data.get(str(project_id), [])
    for case in cases:
        if str(case.get(id_field)) == str(case_id):
            return case
    return None

def delete_case(path: str, project_id: int, case_id: int, id_field: str = "id") -> bool:
    """Delete a case by id. Returns True if removed."""
    data = _load_scoped(path)
    cases = data.get(str(project_id), [])
    original_len = len(cases)
    cases = [c for c in cases if str(c.get(id_field)) != str(case_id)]
    data[str(project_id)] = cases
    _save_scoped(path, data)
    return len(cases) != original_len

def get_app_device(project_id: int) -> str:
    """Get saved APP device information for a project (returns empty string if none)."""
    data = _load_scoped(APP_DEVICE_PATH)
    entry = data.get(str(project_id), [])
    if isinstance(entry, list) and entry:
        return entry[0] or ""
    return ""

def set_app_device(project_id: int, text: str) -> None:
    """Set the device information for a project."""
    data = _load_scoped(APP_DEVICE_PATH)
    data[str(project_id)] = [text]
    _save_scoped(APP_DEVICE_PATH, data)

def list_project_bugs(project_id: int, keyword: Optional[str] = None) -> List[dict]:
    """Return bug list for a specific project (scoped)."""
    # bugs are stored similar to cases: mapping project_id -> list
    data = _load_scoped(BUGS_PATH)
    bugs = data.get(str(project_id), [])
    if keyword:
        kw = keyword.lower()
        bugs = [b for b in bugs if kw in b.get('title','').lower() or kw in b.get('repro','').lower() or kw in b.get('expected','').lower() or kw in b.get('actual','').lower()]
    return bugs

def create_project_bug(project_id: int, bug_data: dict) -> dict:
    """Create a bug under a specific project. Assigns an auto-increment id."""
    data = _load_scoped(BUGS_PATH)
    bugs = data.get(str(project_id), [])
    next_id = max([int(b.get('id', 0)) for b in bugs] + [0]) + 1
    bug = dict(bug_data)
    bug['id'] = next_id
    bugs.append(bug)
    data[str(project_id)] = bugs
    _save_scoped(BUGS_PATH, data)
    return bug

def update_project_bug(project_id: int, bug_id: int, bug_data: dict) -> Optional[dict]:
    data = _load_scoped(BUGS_PATH)
    bugs = data.get(str(project_id), [])
    for idx, b in enumerate(bugs):
        if str(b.get('id')) == str(bug_id):
            b.update(bug_data)
            bugs[idx] = b
            data[str(project_id)] = bugs
            _save_scoped(BUGS_PATH, data)
            return b
    return None

def get_project_bug(project_id: int, bug_id: int) -> Optional[dict]:
    """Retrieve a single bug by its ID for a given project."""
    data = _load_scoped(BUGS_PATH)
    bugs = data.get(str(project_id), [])
    for bug in bugs:
        if str(bug.get('id')) == str(bug_id):
            return bug
    return None

def delete_project_bug(project_id: int, bug_id: int) -> bool:
    data = _load_scoped(BUGS_PATH)
    bugs = data.get(str(project_id), [])
    orig = len(bugs)
    bugs = [b for b in bugs if str(b.get('id')) != str(bug_id)]
    data[str(project_id)] = bugs
    _save_scoped(BUGS_PATH, data)
    return len(bugs) != orig

def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def _load(path: str):
    _ensure_file(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def _now() -> str:
    return datetime.utcnow().isoformat()

# ---------------- Projects ----------------
@dataclass
class Project:
    id: int
    name: str
    description: str = ""
    owner: str = ""
    status: str = "新增"
    created_at: str = ""
    updated_at: str = ""

def list_projects(keyword: Optional[str] = None):
    items = _load(PROJECTS_PATH)
    if keyword:
        kw = keyword.lower()
        items = [i for i in items if kw in i.get("name","").lower() or kw in i.get("description","").lower() or kw in i.get("owner","").lower()]
    return items

def get_project(project_id: int):
    for it in _load(PROJECTS_PATH):
        if it.get("id") == project_id:
            return it
    return None

def create_project(data: dict):
    items = _load(PROJECTS_PATH)
    new_id = (max([i.get("id",0) for i in items]) + 1) if items else 1
    now = _now()
    p = Project(
        id=new_id,
        name=data.get("name","").strip(),
        description=data.get("description","").strip(),
        owner=data.get("owner","").strip(),
        status=data.get("status","新增"),
        created_at=now,
        updated_at=now,
    )
    items.append(asdict(p))
    _save(PROJECTS_PATH, items)
    return asdict(p)

def update_project(project_id: int, data: dict):
    items = _load(PROJECTS_PATH)
    for idx, it in enumerate(items):
        if it.get("id") == project_id:
            it.update({
                "name": data.get("name", it.get("name","")),
                "description": data.get("description", it.get("description","")),
                "owner": data.get("owner", it.get("owner","")),
                "status": data.get("status", it.get("status","新增")),
                "updated_at": _now(),
            })
            items[idx] = it
            _save(PROJECTS_PATH, items)
            return it
    return None

def delete_project(project_id: int):
    items = _load(PROJECTS_PATH)
    items = [i for i in items if i.get("id") != project_id]
    _save(PROJECTS_PATH, items)
    return True

# ---------------- Bugs ----------------
@dataclass
class Bug:
    id: int
    title: str
    description: str = ""
    severity: str = "Low"   # Low / Medium / High / Critical
    status: str = "Open"    # Open / In Progress / Resolved / Closed
    assignee: str = ""
    created_at: str = ""
    updated_at: str = ""

def list_bugs(keyword: Optional[str] = None):
    items = _load(BUGS_PATH)
    if keyword:
        kw = keyword.lower()
        items = [i for i in items if kw in i.get("title","").lower() or kw in i.get("description","").lower() or kw in i.get("assignee","").lower()]
    return items

def get_bug(bug_id: int):
    for it in _load(BUGS_PATH):
        if it.get("id") == bug_id:
            return it
    return None

def create_bug(data: dict):
    items = _load(BUGS_PATH)
    new_id = (max([i.get("id",0) for i in items]) + 1) if items else 1
    now = _now()
    b = Bug(
        id=new_id,
        title=data.get("title","").strip(),
        description=data.get("description","").strip(),
        severity=data.get("severity","Low"),
        status=data.get("status","Open"),
        assignee=data.get("assignee","").strip(),
        created_at=now,
        updated_at=now,
    )
    items.append(asdict(b))
    _save(BUGS_PATH, items)
    return asdict(b)

def update_bug(bug_id: int, data: dict):
    items = _load(BUGS_PATH)
    for idx, it in enumerate(items):
        if it.get("id") == bug_id:
            it.update({
                "title": data.get("title", it.get("title","")),
                "description": data.get("description", it.get("description","")),
                "severity": data.get("severity", it.get("severity","Low")),
                "status": data.get("status", it.get("status","Open")),
                "assignee": data.get("assignee", it.get("assignee","")),
                "updated_at": _now(),
            })
            items[idx] = it
            _save(BUGS_PATH, items)
            return it
    return None

def delete_bug(bug_id: int):
    items = _load(BUGS_PATH)
    items = [i for i in items if i.get("id") != bug_id]
    _save(BUGS_PATH, items)
    return True

# ---------------- Test Runs ----------------
@dataclass
class TestRun:
    id: int
    name: str = "Manual Trigger"
    suite: str = "API"          # API / UI / APP
    status: str = "Pending"     # Pending / Running / Passed / Failed
    triggered_by: str = ""
    created_at: str = ""
    updated_at: str = ""

def list_runs(keyword: Optional[str] = None):
    items = _load(RUNS_PATH)
    if keyword:
        kw = keyword.lower()
        items = [i for i in items if kw in i.get("name","").lower() or kw in i.get("suite","").lower() or kw in i.get("status","").lower()]
    return items

def create_run(data: dict):
    items = _load(RUNS_PATH)
    new_id = (max([i.get("id",0) for i in items]) + 1) if items else 1
    now = _now()
    r = TestRun(
        id=new_id,
        name=data.get("name","Manual Trigger"),
        suite=data.get("suite","API"),
        status=data.get("status","Pending"),
        triggered_by=data.get("triggered_by",""),
        created_at=now,
        updated_at=now,
    )
    items.append(asdict(r))
    _save(RUNS_PATH, items)
    return asdict(r)

def update_run(run_id: int, data: dict):
    items = _load(RUNS_PATH)
    for idx, it in enumerate(items):
        if it.get("id") == run_id:
            it.update({
                "name": data.get("name", it.get("name","")),
                "suite": data.get("suite", it.get("suite","API")),
                "status": data.get("status", it.get("status","Pending")),
                "triggered_by": data.get("triggered_by", it.get("triggered_by","")),
                "updated_at": _now(),
            })
            items[idx] = it
            _save(RUNS_PATH, items)
            return it
    return None

def delete_run(run_id: int):
    items = _load(RUNS_PATH)
    items = [i for i in items if i.get("id") != run_id]
    _save(RUNS_PATH, items)
    return True
