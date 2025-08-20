
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

# UploadFile and File are optional; they require python-multipart. We import lazily in upload endpoint.
try:
    # We'll import UploadFile and File only if python-multipart is installed
    from fastapi import UploadFile, File  # type: ignore
except Exception:
    UploadFile = None  # type: ignore
    File = None  # type: ignore
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import subprocess, threading, asyncio, time, os, shutil, json

from .storage import (
    # Projects
    list_projects, get_project, create_project, update_project, delete_project, Project,
    # Global bugs and runs (legacy)
    list_bugs, get_bug, create_bug, update_bug, delete_bug, Bug,
    list_runs, create_run, update_run, delete_run,
    # Project‑scoped cases and bugs
    list_cases, get_case, create_case, update_case, delete_case,
    get_app_device, set_app_device,
    list_project_bugs, get_project_bug, create_project_bug, update_project_bug, delete_project_bug,
    # Paths for case types
    WEB_CASES_PATH, APP_CASES_PATH, API_CASES_PATH, APP_DEVICE_PATH,
)


# ---- Data directories (default to project-root /data) ----
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(ROOT_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)
# Base directory for storing textual logs of test runs. Each run creates a
# subdirectory named after the timestamp (YYYYMMDD_HH-MM-SS) under this
# folder. Log files capture the real‑time output streamed to the front‑end.
LOG_DIR_BASE = os.path.join(DATA_DIR, "log")
os.makedirs(LOG_DIR_BASE, exist_ok=True)
app = FastAPI(title="Test Platform JSON API")

# ---- Optional environment configuration ----
# If the optional dependency "python-multipart" is not installed, FastAPI will
# raise an exception when analyzing UploadFile/File parameters. To avoid this
# requirement in environments where file uploads are not needed, you can set
# the environment variable ``SKIP_UPLOAD`` to any non‑empty value. When set,
# the /upload endpoint will return 501 instead of trying to import
# python-multipart. We set a default here to disable file uploads if not
# already configured.
if not os.getenv("SKIP_UPLOAD"):
    # Default to disabling upload; user can override by setting SKIP_UPLOAD=0
    os.environ["SKIP_UPLOAD"] = "1"

@app.get('/favicon.ico', include_in_schema=False)
def _favicon():
    return Response(status_code=204)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Logging (Requirements #5, #7) ----
from fastapi import Request
from datetime import datetime

API_LOG_FILE = os.path.join(DATA_DIR, "api_log.txt")
USER_ACTION_LOG_FILE = os.path.join(DATA_DIR, "user_action_log.txt")

@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    """Middleware to log every API request and its response."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} - {request.client.host} - \"{request.method} {request.url.path}\""

    response = await call_next(request)

    log_line += f" - {response.status_code}\n"

    with open(API_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

    return response

class UserAction(BaseModel):
    action: str

@app.post("/log-action")
async def log_user_action(user_action: UserAction):
    """Endpoint to log a user action from the frontend."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} - [USER ACTION] {user_action.action}\n"

    with open(USER_ACTION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

    return {"ok": True}

@app.get("/logs/{run_id}")
async def get_log_file(run_id: str):
    """Retrieve the contents of a specific run's log file."""
    # Sanitize run_id to prevent directory traversal
    if not run_id.isalnum() and "_" not in run_id and "-" not in run_id:
        raise HTTPException(status_code=400, detail="Invalid run_id format")

    log_file_path = os.path.join(LOG_DIR_BASE, run_id, "run.log")

    if not os.path.exists(log_file_path):
        raise HTTPException(status_code=404, detail="Log file not found")

    with open(log_file_path, "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="text/plain")

# ---------- Pydantic models ----------
class ProjectIn(BaseModel):
    name: str
    description: str = ""
    owner: str = ""
    status: str = "新增"

class BugIn(BaseModel):
    title: str
    description: str = ""
    severity: str = "Low"
    status: str = "Open"
    assignee: str = ""

class RunIn(BaseModel):
    name: str = "Manual Trigger"
    suite: str = "API"
    status: str = "Pending"
    triggered_by: str = ""

# ---------- Test Case Models ----------
class WebCaseIn(BaseModel):
    """
    Input model for creating/updating a web test case. All fields are optional strings.
    The identifier field ``id`` is auto‑assigned on creation.
    """
    test_feature: str = ""
    test_step: str = ""
    action: str = ""
    description: str = ""
    page: str = ""
    element: str = ""
    value: str = ""
    result: str = ""
    note: str = ""

class AppCaseIn(BaseModel):
    """
    Input model for creating/updating an app test case. Identical to WebCaseIn.
    """
    test_feature: str = ""
    test_step: str = ""
    action: str = ""
    description: str = ""
    page: str = ""
    element: str = ""
    value: str = ""
    result: str = ""
    note: str = ""

class ApiCaseIn(BaseModel):
    """
    Input model for API test cases. The ``step`` field is auto‑assigned on creation.
    """
    test_feature: str = ""
    method: str = "GET"
    url: str = ""
    api_path: str = ""
    header: str = ""
    body: str = ""
    expected_status: str = ""
    expected_field: str = ""
    expected_value: str = ""
    result: str = ""
    summary: str = ""
    note: str = ""

class ProjectBugIn(BaseModel):
    """
    Input model for project‑scoped bug. ``description`` is the bug summary/issue.
    ``severity`` can be High/Medium/Low (or localized strings), ``status`` default '新增'.
    Screenshot is a relative path returned from upload endpoint.
    """
    description: str
    severity: str = "低"
    status: str = "新增"
    repro: str = ""
    expected: str = ""
    actual: str = ""
    note: str = ""
    screenshot: str = ""

# ---------- Health ----------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- Projects CRUD ----------
@app.get("/projects")
def api_list_projects(q: Optional[str] = None, owner: Optional[str] = None, status: Optional[str] = None):
    return list_projects(keyword=q, owner=owner, status=status)

@app.get("/projects/{pid}")
def api_get_project(pid: int):
    p = get_project(pid)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@app.post("/projects")
def api_create_project(payload: ProjectIn):
    return create_project(payload.dict())

@app.put("/projects/{pid}")
def api_update_project(pid: int, payload: ProjectIn):
    p = update_project(pid, payload.dict())
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@app.delete("/projects/{pid}")
def api_delete_project(pid: int):
    delete_project(pid)
    return {"ok": True}

# ---------- Bugs CRUD ----------
@app.get("/bugs")
def api_list_bugs(q: Optional[str] = None):
    return list_bugs(q)

@app.get("/bugs/{bid}")
def api_get_bug(bid: int):
    b = get_bug(bid)
    if not b:
        raise HTTPException(status_code=404, detail="Bug not found")
    return b

@app.post("/bugs")
def api_create_bug(payload: BugIn):
    return create_bug(payload.dict())

@app.put("/bugs/{bid}")
def api_update_bug(bid: int, payload: BugIn):
    b = update_bug(bid, payload.dict())
    if not b:
        raise HTTPException(status_code=404, detail="Bug not found")
    return b

@app.delete("/bugs/{bid}")
def api_delete_bug(bid: int):
    delete_bug(bid)
    return {"ok": True}

# ---------- Runs CRUD ----------
@app.get("/runs")
def api_list_runs(q: Optional[str] = None):
    return list_runs(q)

@app.post("/runs")
def api_create_run(payload: RunIn):
    return create_run(payload.dict())

@app.put("/runs/{rid}")
def api_update_run(rid: int, payload: RunIn):
    r = update_run(rid, payload.dict())
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    return r

@app.delete("/runs/{rid}")
def api_delete_run(rid: int):
    delete_run(rid)
    return {"ok": True}

# ---------- File upload (for bug screenshots or other attachments) ----------
# ---------- File upload (for bug screenshots or other attachments) ----------
# The upload endpoint requires python-multipart; if not available or SKIP_UPLOAD is set, it will return 501.
if os.getenv("SKIP_UPLOAD"):
    @app.post("/upload")
    async def api_upload_file_disabled():
        """Disabled upload endpoint for environments without python-multipart."""
        raise HTTPException(status_code=501, detail="File upload is disabled in this environment")
elif UploadFile and File:
    @app.post("/upload")
    async def api_upload_file(file: UploadFile = File(...)):
        """Upload a file and return its relative URL. Files are stored under DATA_DIR/uploads."""
        dest_dir = os.path.join(DATA_DIR, "uploads")
        os.makedirs(dest_dir, exist_ok=True)
        # sanitize filename: keep extension only
        _, ext = os.path.splitext(file.filename)
        # unique filename using timestamp
        ts = str(int(time.time() * 1000))
        fname = ts + ext
        path = os.path.join(dest_dir, fname)
        contents = await file.read()
        with open(path, "wb") as f:
            f.write(contents)
        # mount uploads directory if not already mounted
        if not any(getattr(r, "path", None) == "/uploads" for r in app.routes):
            try:
                app.mount("/uploads", StaticFiles(directory=dest_dir, html=False), name="uploads")
            except Exception:
                pass
        return {"path": f"/uploads/{fname}"}
else:
    @app.post("/upload")
    async def api_upload_file_unavailable():
        raise HTTPException(status_code=500, detail="python-multipart is required for file uploads")

# ---------- Project‑scoped Web Cases ----------
@app.get("/projects/{pid}/webcases")
def api_list_web_cases(
    pid: int,
    q: Optional[str] = None,
    action: Optional[str] = None,
    result: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
):
    """List web test cases for a project with optional keyword and filters. Supports pagination."""
    filters: dict[str, set[str]] = {}
    if action:
        filters["action"] = set([x for x in action.split(",") if x])
    if result:
        filters["result"] = set([x for x in result.split(",") if x])
    cases = list_cases(WEB_CASES_PATH, pid, q, filters)
    total = len(cases)
    # pagination
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 50
    start = (page - 1) * page_size
    end = start + page_size
    return {"total": total, "items": cases[start:end]}

@app.get("/projects/{pid}/webcases/names")
def api_list_web_case_names(pid: int):
    """Return a lightweight list of web cases (id and name) for a project."""
    cases = list_cases(WEB_CASES_PATH, pid)
    # The name is in 'feature' or 'test_feature'
    return [{"id": c.get("id"), "name": c.get("feature") or c.get("test_feature") or ""} for c in cases]

@app.post("/projects/{pid}/webcases")
def api_create_web_case(pid: int, payload: WebCaseIn):
    case = create_case(WEB_CASES_PATH, pid, payload.dict(), id_field="id")
    return case

@app.put("/projects/{pid}/webcases/{case_id}")
def api_update_web_case(pid: int, case_id: int, payload: WebCaseIn):
    # State locking: prevent changes if status is '已審核'
    current_case = get_case(WEB_CASES_PATH, pid, case_id, id_field="id")
    if not current_case:
        raise HTTPException(status_code=404, detail="Web case not found")

    # The field in web_cases.json is 'review'
    is_reviewed = current_case.get("review") == "已審核"
    payload_dict = payload.dict(exclude_unset=True)

    if is_reviewed and "review" in payload_dict and payload_dict["review"] != "已審核":
        raise HTTPException(status_code=403, detail="此案例已審核，無法修改狀態。")

    case = update_case(WEB_CASES_PATH, pid, case_id, payload_dict, id_field="id")
    return case

@app.delete("/projects/{pid}/webcases/{case_id}")
def api_delete_web_case(pid: int, case_id: int):
    ok = delete_case(WEB_CASES_PATH, pid, case_id, id_field="id")
    return {"ok": ok}

# ---------- Project‑scoped App Cases ----------
@app.get("/projects/{pid}/appcases")
def api_list_app_cases(
    pid: int,
    q: Optional[str] = None,
    action: Optional[str] = None,
    result: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
):
    filters: dict[str, set[str]] = {}
    if action:
        filters["action"] = set([x for x in action.split(",") if x])
    if result:
        filters["result"] = set([x for x in result.split(",") if x])
    cases = list_cases(APP_CASES_PATH, pid, q, filters)
    total = len(cases)
    start = max((page - 1), 0) * page_size
    end = start + page_size
    return {"total": total, "items": cases[start:end]}

@app.get("/projects/{pid}/appcases/names")
def api_list_app_case_names(pid: int):
    """Return a lightweight list of app cases (id and name) for a project."""
    cases = list_cases(APP_CASES_PATH, pid)
    return [{"id": c.get("id"), "name": c.get("feature") or c.get("test_feature") or ""} for c in cases]

@app.post("/projects/{pid}/appcases")
def api_create_app_case(pid: int, payload: AppCaseIn):
    case = create_case(APP_CASES_PATH, pid, payload.dict(), id_field="id")
    return case

@app.put("/projects/{pid}/appcases/{case_id}")
def api_update_app_case(pid: int, case_id: int, payload: AppCaseIn):
    # State locking: prevent changes if status is '已審核'
    current_case = get_case(APP_CASES_PATH, pid, case_id, id_field="id")
    if not current_case:
        raise HTTPException(status_code=404, detail="App case not found")

    is_reviewed = current_case.get("review") == "已審核"
    payload_dict = payload.dict(exclude_unset=True)

    if is_reviewed and "review" in payload_dict and payload_dict["review"] != "已審核":
        raise HTTPException(status_code=403, detail="此案例已審核，無法修改狀態。")

    case = update_case(APP_CASES_PATH, pid, case_id, payload_dict, id_field="id")
    return case

@app.delete("/projects/{pid}/appcases/{case_id}")
def api_delete_app_case(pid: int, case_id: int):
    ok = delete_case(APP_CASES_PATH, pid, case_id, id_field="id")
    return {"ok": ok}

# ---------- Project‑scoped API Cases ----------
@app.get("/projects/{pid}/apicases")
def api_list_api_cases(
    pid: int,
    q: Optional[str] = None,
    method: Optional[str] = None,
    result: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
):
    filters: dict[str, set[str]] = {}
    if method:
        filters["method"] = set([x for x in method.split(",") if x])
    if result:
        filters["result"] = set([x for x in result.split(",") if x])
    cases = list_cases(API_CASES_PATH, pid, q, filters)
    total = len(cases)
    start = max((page - 1), 0) * page_size
    end = start + page_size
    return {"total": total, "items": cases[start:end]}

@app.get("/projects/{pid}/apicases/names")
def api_list_api_case_names(pid: int):
    """Return a lightweight list of api cases (id and name) for a project."""
    cases = list_cases(API_CASES_PATH, pid)
    # API cases use 'step' as their ID field
    return [{"id": c.get("step"), "name": c.get("feature") or c.get("test_feature") or ""} for c in cases]

@app.post("/projects/{pid}/apicases")
def api_create_api_case(pid: int, payload: ApiCaseIn):
    case = create_case(API_CASES_PATH, pid, payload.dict(), id_field="step")
    return case

@app.put("/projects/{pid}/apicases/{step}")
def api_update_api_case(pid: int, step: int, payload: ApiCaseIn):
    # State locking: prevent changes if status is '已審核'
    current_case = get_case(API_CASES_PATH, pid, step, id_field="step")
    if not current_case:
        raise HTTPException(status_code=404, detail="API case not found")

    is_reviewed = current_case.get("review") == "已審核"
    payload_dict = payload.dict(exclude_unset=True)

    if is_reviewed and "review" in payload_dict and payload_dict["review"] != "已審核":
        raise HTTPException(status_code=403, detail="此案例已審核，無法修改狀態。")

    case = update_case(API_CASES_PATH, pid, step, payload_dict, id_field="step")
    return case

@app.delete("/projects/{pid}/apicases/{step}")
def api_delete_api_case(pid: int, step: int):
    ok = delete_case(API_CASES_PATH, pid, step, id_field="step")
    return {"ok": ok}

# ---------- Project‑scoped APP Device Info ----------
@app.get("/projects/{pid}/app-device")
def api_get_app_device(pid: int):
    info = get_app_device(pid) or ""
    return {"device": info}

@app.post("/projects/{pid}/app-device")
def api_set_app_device(pid: int, device: str):
    set_app_device(pid, device)
    return {"ok": True}

# ---------- Project‑scoped Bugs ----------
@app.get("/projects/{pid}/bugs")
def api_list_project_bugs(pid: int, q: Optional[str] = None, severity: Optional[str] = None, status: Optional[str] = None):
    """List bugs for a project. Optionally filter by keyword in description, repro, expected or actual."""
    return list_project_bugs(pid, keyword=q, severity=severity, status=status)

@app.post("/projects/{pid}/bugs")
def api_create_project_bug(pid: int, payload: ProjectBugIn):
    bug = create_project_bug(pid, payload.dict())
    return bug

@app.put("/projects/{pid}/bugs/{bug_id}")
def api_update_project_bug(pid: int, bug_id: int, payload: ProjectBugIn):
    # State locking: prevent changes if status is '已審核'
    current_bug = get_project_bug(pid, bug_id)
    if not current_bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    is_reviewed = current_bug.get("status") == "已審核"
    payload_dict = payload.dict(exclude_unset=True)

    if is_reviewed and "status" in payload_dict and payload_dict["status"] != "已審核":
        raise HTTPException(status_code=403, detail="此BUG已審核，無法修改狀態。")

    bug = update_project_bug(pid, bug_id, payload_dict)
    return bug

@app.delete("/projects/{pid}/bugs/{bug_id}")
def api_delete_project_bug(pid: int, bug_id: int):
    ok = delete_project_bug(pid, bug_id)
    return {"ok": ok}

# ---------- Allure: results & report ----------
ALLURE_RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", os.path.join(DATA_DIR, "allure-results"))
ALLURE_REPORT_DIR  = os.getenv("ALLURE_REPORT_DIR",  os.path.join(DATA_DIR, "allure-report"))
os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)
os.makedirs(ALLURE_REPORT_DIR, exist_ok=True)

try:
    app.mount("/allure/report", StaticFiles(directory=ALLURE_REPORT_DIR, html=True), name="allure-report")
except Exception:
    pass

@app.get("/allure/results")
def api_allure_results():
    items = []
    if os.path.isdir(ALLURE_RESULTS_DIR):
        for name in sorted(os.listdir(ALLURE_RESULTS_DIR)):
            p = os.path.join(ALLURE_RESULTS_DIR, name)
            if os.path.isfile(p):
                items.append({"name": name, "size": os.path.getsize(p)})
    return {"dir": ALLURE_RESULTS_DIR, "files": items}

@app.post("/allure/generate")
def api_allure_generate(clean: bool = True):
    allure_cmd = shutil.which("allure")
    if not allure_cmd:
        raise HTTPException(status_code=500, detail="Allure command not found. Please install Allure CLI.")
    cmd = [allure_cmd, "generate", ALLURE_RESULTS_DIR, "-o", ALLURE_REPORT_DIR]
    if clean:
        cmd.insert(2, "-c")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Allure generate failed: {proc.stderr or proc.stdout}")
    return {"ok": True, "report_dir": ALLURE_REPORT_DIR}

# ---------- Pytest live logs via WebSocket ----------
pytest_running = False
pytest_thread = None
pytest_log_buffer = []
pytest_clients = set()

# ---------- Web UI test run state ----------
# These globals mirror the existing pytest state to allow only a single web
# UI test run at a time. Similar to ``pytest_running``, they prevent
# overlapping runs that could corrupt the Allure results. A separate log
# stream is re‑used via ``_pytest_broadcast`` so that live output is
# accessible through the existing WebSocket endpoint.
webtest_running = False
webtest_thread = None

# ---------- API test run state ----------
# Similar to ``webtest_running``, this flag prevents overlapping API
# test executions. The ``apitest_thread`` holds the background worker
# thread that runs pytest on the API cases.
apitest_running = False
apitest_thread = None

async def _pytest_broadcast(line: str):
    pytest_log_buffer.append(line)
    if len(pytest_log_buffer) > 500:
        del pytest_log_buffer[:200]
    dead = []
    for ws in list(pytest_clients):
        try:
            await ws.send_text(line)
        except Exception:
            dead.append(ws)
    for d in dead:
        pytest_clients.discard(d)

def _run_pytest(cmd=None, workdir=None):
    global pytest_running
    pytest_running = True
    try:
        if cmd is None:
            cmd = ["pytest", "-q", f"--alluredir={ALLURE_RESULTS_DIR}"]
        proc = subprocess.Popen(cmd, cwd=workdir or os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            asyncio.run(_pytest_broadcast(line.rstrip()))
        rc = proc.wait()
        asyncio.run(_pytest_broadcast(f"[pytest] finished with code {rc}"))
    except Exception as e:
        asyncio.run(_pytest_broadcast(f"[pytest] error: {e}"))
    finally:
        pytest_running = False

@app.post("/runs/trigger-pytest")
def api_trigger_pytest():
    global pytest_thread, pytest_running
    if pytest_running:
        raise HTTPException(status_code=409, detail="A pytest run is already in progress")
    pytest_thread = threading.Thread(target=_run_pytest, kwargs={"cmd": ["pytest", "-q", f"--alluredir={ALLURE_RESULTS_DIR}"], "workdir": None}, daemon=True)
    pytest_thread.start()
    return {"ok": True, "message": "pytest started"}


# ---------- Web UI test trigger ----------
@app.post("/runs/trigger-web")
def api_trigger_web(payload: dict | None = None):
    """
    Trigger execution of web UI automation using Playwright and Allure.

    The request payload should be a JSON object containing:

    - ``project_id``: integer ID of the project whose web cases should be run. Defaults to 1 if omitted.
    - ``case_ids``: an optional list of integer case identifiers. When provided,
      only the specified cases will be executed; otherwise all cases for the
      project will be included.

    A new timestamped directory is created under ``DATA_DIR/allure-results``
    for the raw results and under ``DATA_DIR/allure-report`` for the generated
    HTML report. After the run completes, the report will be available at
    ``/allure/report/{timestamp}/index.html`` and will be listed by the
    existing ``/allure/list`` endpoint.

    This endpoint reuses the existing WebSocket ``/ws/test-run`` for streaming
    real‑time logs back to the front‑end. Concurrent web test executions are
    prevented by the ``webtest_running`` flag.
    """
    global webtest_running, webtest_thread
    # prevent overlapping runs
    if webtest_running:
        raise HTTPException(status_code=409, detail="A web UI test run is already in progress")
    # extract project and selected case IDs
    project_id: int = 1
    case_ids = None
    if isinstance(payload, dict):
        project_id = int(payload.get("project_id", 1) or 1)
    case_ids = payload.get("case_ids")
    # normalise list of IDs to strings for comparison later
    # If an empty list is provided, treat as no filter (run all cases)
    if case_ids:
        case_ids = [str(x) for x in case_ids]
    else:
        case_ids = None
    # timestamp for unique directories
    ts = time.strftime("%Y%m%d%H%M%S")
    result_dir = os.path.join(DATA_DIR, "allure-results", ts)
    report_dir = os.path.join(DATA_DIR, "allure-report", ts)
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    # The log directory should use the same 'ts' as the run_id to ensure logs can be found.
    log_dir = os.path.join(LOG_DIR_BASE, ts)
    os.makedirs(log_dir, exist_ok=True)
    # prepare temporary JSON with selected cases
    tmp_cases_path = os.path.join(DATA_DIR, f"tmp_web_cases_{ts}.json")
    try:
        # use storage.list_cases to load all cases and then filter by ID
        all_cases = list_cases(WEB_CASES_PATH, project_id, None, None)
    except Exception:
        all_cases = []
    # filter if a non‑empty case_ids list is provided
    if case_ids is not None:
        selected_cases = [c for c in all_cases if str(c.get("id")) in case_ids]
    else:
        selected_cases = all_cases
    # write the scoped cases to a temporary file
    try:
        with open(tmp_cases_path, "w", encoding="utf-8") as f:
            json.dump({str(project_id): selected_cases}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write temporary cases file: {e}")
    # determine path to the test runner script and UI mapping
    script_path = os.path.join(os.path.dirname(__file__), "web_test_runner.py")
    ui_map_path = os.path.join(os.path.dirname(__file__), "ui_elements.json")
    # define worker function to run pytest and generate report
    def _web_worker() -> None:
        # ``webtest_running`` is defined at module scope; declare global so
        # assignments update the shared flag rather than creating a new local
        global webtest_running
        try:
            env = os.environ.copy()
            env["WEB_TEST_CASES_FILE"] = tmp_cases_path
            env["UI_ELEMENTS_FILE"] = ui_map_path
            env["PROJECT_ID"] = str(project_id)
            # build pytest command; run quietly and direct results to our unique results dir
            cmd = [
                "pytest",
                script_path,
                "-q",
                f"--alluredir={result_dir}",
            ]
            # open a log file for writing the run output
            log_path = os.path.join(log_dir, "run.log")
            with open(log_path, "w", encoding="utf-8") as lf:
                # spawn subprocess and stream stdout to websocket and log file
                proc = subprocess.Popen(
                    cmd,
                    cwd=ROOT_DIR,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                for line in proc.stdout:
                    # write to log file and flush
                    try:
                        lf.write(line)
                        lf.flush()
                    except Exception:
                        pass
                    asyncio.run(_pytest_broadcast(line.rstrip()))
                rc = proc.wait()
                finish_msg = f"[webtest] finished with code {rc}"
                lf.write(f"{finish_msg}\n")
                lf.flush()
                asyncio.run(_pytest_broadcast(finish_msg))

            # If tests failed (non-zero return code), create a bug ticket
            if rc != 0:
                try:
                    bug_payload = {
                        "title": f"自動化測試失敗 - WEB - {ts}",
                        "description": f"自動化測試執行失敗。",
                        "repro": f"測試報告 ID: {ts}. 請至「報表」頁面查看詳細 Allure 報告。",
                        "severity": "中",
                        "status": "新增",
                        "note": "此BUG由系統自動產生。"
                    }
                    create_project_bug(project_id, bug_payload)
                    asyncio.run(_pytest_broadcast(f"[webtest] 自動建立BUG成功。"))
                except Exception as e:
                    asyncio.run(_pytest_broadcast(f"[webtest] 自動建立BUG失敗: {e}"))

            # generate the HTML report using the Allure CLI if available
            allure_cmd = shutil.which("allure")
            if allure_cmd:
                gen_cmd = [
                    allure_cmd,
                    "generate",
                    result_dir,
                    "-o",
                    report_dir,
                    "-c",
                ]
                proc2 = subprocess.run(gen_cmd, capture_output=True, text=True)
                if proc2.returncode != 0:
                    msg = proc2.stderr.strip() or proc2.stdout.strip()
                    err_msg = f"[webtest] allure generate failed: {msg}"
                    with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as lf2:
                        lf2.write(f"{err_msg}\n")
                    asyncio.run(_pytest_broadcast(err_msg))
        except Exception as e:
            err_msg = f"[webtest] error: {e}"
            # append error to log file
            try:
                with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as lf3:
                    lf3.write(f"{err_msg}\n")
            except Exception:
                pass
            asyncio.run(_pytest_broadcast(err_msg))
        finally:
            # mark the run as finished regardless of outcome
            webtest_running = False
    # mark the global flag now so that subsequent trigger attempts are rejected
    webtest_running = True
    # start the worker thread
    webtest_thread = threading.Thread(target=_web_worker, daemon=True)
    webtest_thread.start()
    return {
        "ok": True,
        "message": "web test started",
        "run_id": ts,
        "results_dir": result_dir,
        "report_dir": report_dir,
        "log_dir": log_dir,
    }


# ---------- API test trigger ----------
@app.post("/runs/trigger-api")
def api_trigger_api(payload: dict | None = None):
    """
    Trigger execution of API test cases using pytest and Allure.

    The payload is a JSON object with the following keys:

    - ``project_id``: integer ID of the project whose API cases should be run. Defaults to 1.
    - ``case_ids``: an optional list of case identifiers (integers). When provided, only the
      specified cases are executed; otherwise all cases for the project are used.

    Like the web runner, this endpoint spawns a background thread to execute pytest
    against ``api_test_runner.py`` and streams stdout to the existing ``/ws/test-run``
    WebSocket. Results are written into a timestamped directory under
    ``data/allure-results`` and a report is generated into ``data/allure-report``.
    Concurrent API test runs are prevented by the ``apitest_running`` flag.
    """
    global apitest_running, apitest_thread
    # prevent overlapping API runs
    if apitest_running:
        raise HTTPException(status_code=409, detail="An API test run is already in progress")
    # parse project ID and case IDs
    project_id: int = 1
    case_ids = None
    if isinstance(payload, dict):
        project_id = int(payload.get("project_id", 1) or 1)
        case_ids = payload.get("case_ids")
        # Normalise case_ids: if provided but empty, treat as None (run all)
        if case_ids:
            case_ids = [str(x) for x in case_ids]
        else:
            case_ids = None
    # create timestamped directories
    ts = time.strftime("%Y%m%d%H%M%S")
    result_dir = os.path.join(DATA_DIR, "allure-results", ts)
    report_dir = os.path.join(DATA_DIR, "allure-report", ts)
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    # The log directory should use the same 'ts' as the run_id to ensure logs can be found.
    log_dir = os.path.join(LOG_DIR_BASE, ts)
    os.makedirs(log_dir, exist_ok=True)
    # prepare temporary cases file
    tmp_cases_path = os.path.join(DATA_DIR, f"tmp_api_cases_{ts}.json")
    try:
        all_cases = list_cases(API_CASES_PATH, project_id, None, None)
    except Exception:
        all_cases = []
    if case_ids is not None:
        # API cases may identify steps by 'id' or 'step'; match either
        selected_cases = [c for c in all_cases if str(c.get("id") or c.get("step")) in case_ids]
    else:
        selected_cases = all_cases
    # write selected cases to temporary file
    try:
        with open(tmp_cases_path, "w", encoding="utf-8") as f:
            json.dump({str(project_id): selected_cases}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write temporary API cases file: {e}")
    # determine script path
    script_path = os.path.join(os.path.dirname(__file__), "api_test_runner.py")
    # define worker to run pytest
    def _api_worker() -> None:
        global apitest_running
        try:
            env = os.environ.copy()
            env["API_TEST_CASES_FILE"] = tmp_cases_path
            env["PROJECT_ID"] = str(project_id)
            # build pytest command
            cmd = [
                "pytest",
                script_path,
                "-q",
                f"--alluredir={result_dir}",
            ]
            # open a log file for this API run
            log_path = os.path.join(log_dir, "run.log")
            with open(log_path, "w", encoding="utf-8") as lf:
                proc = subprocess.Popen(
                    cmd,
                    cwd=ROOT_DIR,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                for line in proc.stdout:
                    try:
                        lf.write(line)
                        lf.flush()
                    except Exception:
                        pass
                    asyncio.run(_pytest_broadcast(line.rstrip()))
                rc = proc.wait()
                finish_msg = f"[apitest] finished with code {rc}"
                lf.write(f"{finish_msg}\n")
                lf.flush()
                asyncio.run(_pytest_broadcast(finish_msg))

            # If tests failed (non-zero return code), create a bug ticket
            if rc != 0:
                try:
                    bug_payload = {
                        "title": f"自動化測試失敗 - API - {ts}",
                        "description": f"自動化測試執行失敗。",
                        "repro": f"測試報告 ID: {ts}. 請至「報表」頁面查看詳細 Allure 報告。",
                        "severity": "中",
                        "status": "新增",
                        "note": "此BUG由系統自動產生。"
                    }
                    create_project_bug(project_id, bug_payload)
                    asyncio.run(_pytest_broadcast(f"[apitest] 自動建立BUG成功。"))
                except Exception as e:
                    asyncio.run(_pytest_broadcast(f"[apitest] 自動建立BUG失敗: {e}"))

            # generate HTML report using Allure CLI if available
            allure_cmd = shutil.which("allure")
            if allure_cmd:
                gen_cmd = [
                    allure_cmd,
                    "generate",
                    result_dir,
                    "-o",
                    report_dir,
                    "-c",
                ]
                proc2 = subprocess.run(gen_cmd, capture_output=True, text=True)
                if proc2.returncode != 0:
                    msg = proc2.stderr.strip() or proc2.stdout.strip()
                    err_msg = f"[apitest] allure generate failed: {msg}"
                    with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as lf2:
                        lf2.write(f"{err_msg}\n")
                    asyncio.run(_pytest_broadcast(err_msg))
        except Exception as e:
            err_msg = f"[apitest] error: {e}"
            try:
                with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as lf3:
                    lf3.write(f"{err_msg}\n")
            except Exception:
                pass
            asyncio.run(_pytest_broadcast(err_msg))
        finally:
            apitest_running = False
    # mark as running and start worker thread
    apitest_running = True
    apitest_thread = threading.Thread(target=_api_worker, daemon=True)
    apitest_thread.start()
    return {
        "ok": True,
        "message": "api test started",
        "run_id": ts,
        "results_dir": result_dir,
        "report_dir": report_dir,
        "log_dir": log_dir,
    }

# ---------- App test run state ----------
apptest_running = False
apptest_thread = None

# ---------- App test trigger ----------
@app.post("/runs/trigger-app")
def api_trigger_app(payload: dict | None = None):
    """
    Trigger execution of mobile app test cases using Appium and Allure.
    The payload must contain Appium configuration details.
    """
    global apptest_running, apptest_thread
    if apptest_running:
        raise HTTPException(status_code=409, detail="An App test run is already in progress")

    # --- Parse payload ---
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Request payload must be a JSON object")

    project_id = int(payload.get("project_id", 1) or 1)
    case_ids = payload.get("case_ids")
    if case_ids:
        case_ids = [str(x) for x in case_ids]
    else:
        case_ids = None # Run all cases if not specified

    # Appium-specific config from payload with defaults
    app_file_name = payload.get("app_file_name")
    platform_name = payload.get("platform_name", "Android")
    platform_version = payload.get("platform_version", "13.0")
    device_name = payload.get("device_name", "Android Emulator")

    if not app_file_name:
        raise HTTPException(status_code=400, detail="Payload must include 'app_file_name'")

    # --- Setup directories and temp files ---
    ts = time.strftime("%Y%m%d%H%M%S")
    result_dir = os.path.join(DATA_DIR, "allure-results", ts)
    report_dir = os.path.join(DATA_DIR, "allure-report", ts)
    log_dir = os.path.join(LOG_DIR_BASE, ts)
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    tmp_cases_path = os.path.join(DATA_DIR, f"tmp_app_cases_{ts}.json")
    try:
        all_cases = list_cases(APP_CASES_PATH, project_id, None, None)
        selected_cases = [c for c in all_cases if case_ids is None or str(c.get("id")) in case_ids]
        with open(tmp_cases_path, "w", encoding="utf-8") as f:
            json.dump({str(project_id): selected_cases}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write temporary cases file: {e}")

    # --- Worker thread ---
    def _app_worker() -> None:
        global apptest_running
        try:
            env = os.environ.copy()
            env["APP_TEST_CASES_FILE"] = tmp_cases_path
            env["APP_ELEMENTS_FILE"] = os.path.join(os.path.dirname(__file__), "app_elements.json")
            env["PROJECT_ID"] = str(project_id)
            env["APP_FILE_NAME"] = app_file_name
            env["PLATFORM_NAME"] = platform_name
            env["PLATFORM_VERSION"] = platform_version
            env["DEVICE_NAME"] = device_name

            script_path = os.path.join(os.path.dirname(__file__), "app_test_runner.py")
            cmd = ["pytest", script_path, "-q", f"--alluredir={result_dir}"]
            log_path = os.path.join(log_dir, "run.log")

            with open(log_path, "w", encoding="utf-8") as lf:
                proc = subprocess.Popen(cmd, cwd=ROOT_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    lf.write(line)
                    lf.flush()
                    asyncio.run(_pytest_broadcast(line.rstrip()))
                rc = proc.wait()
                finish_msg = f"[apptest] finished with code {rc}"
                lf.write(f"{finish_msg}\\n")
                lf.flush()
                asyncio.run(_pytest_broadcast(finish_msg))

            # If tests failed (non-zero return code), create a bug ticket
            if rc != 0:
                try:
                    bug_payload = {
                        "title": f"自動化測試失敗 - APP - {ts}",
                        "description": f"自動化測試執行失敗。",
                        "repro": f"測試報告 ID: {ts}. 請至「報表」頁面查看詳細 Allure 報告。",
                        "severity": "中",
                        "status": "新增",
                        "note": "此BUG由系統自動產生。"
                    }
                    create_project_bug(project_id, bug_payload)
                    asyncio.run(_pytest_broadcast(f"[apptest] 自動建立BUG成功。"))
                except Exception as e:
                    asyncio.run(_pytest_broadcast(f"[apptest] 自動建立BUG失敗: {e}"))

            allure_cmd = shutil.which("allure")
            if allure_cmd:
                gen_cmd = [allure_cmd, "generate", result_dir, "-o", report_dir, "-c"]
                proc2 = subprocess.run(gen_cmd, capture_output=True, text=True)
                if proc2.returncode != 0:
                    err_msg = f"[apptest] allure generate failed: {proc2.stderr.strip() or proc2.stdout.strip()}"
                    with open(log_path, "a", encoding="utf-8") as lf2:
                        lf2.write(f"{err_msg}\\n")
                    asyncio.run(_pytest_broadcast(err_msg))
        except Exception as e:
            err_msg = f"[apptest] error: {e}"
            try:
                with open(os.path.join(log_dir, "run.log"), "a", encoding="utf-8") as lf3:
                    lf3.write(f"{err_msg}\\n")
            except Exception:
                pass
            asyncio.run(_pytest_broadcast(err_msg))
        finally:
            apptest_running = False

    apptest_running = True
    apptest_thread = threading.Thread(target=_app_worker, daemon=True)
    apptest_thread.start()

    return {
        "ok": True,
        "message": "app test started",
        "run_id": ts,
        "results_dir": result_dir,
        "report_dir": report_dir,
        "log_dir": log_dir,
    }

@app.websocket("/ws/test-run")
async def ws_test_run(websocket: WebSocket):
    await websocket.accept()
    pytest_clients.add(websocket)
    for line in pytest_log_buffer[-200:]:
        try:
            await websocket.send_text(line)
        except Exception:
            pass
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pytest_clients.discard(websocket)

# ---------- Load test (simulated + real Locust) ----------
loadtest_running = False
loadtest_thread = None
loadtest_clients = set()
locust_proc = None

async def _loadtest_broadcast(line: str):
    dead = []
    for ws in list(loadtest_clients):
        try:
            await ws.send_text(line)
        except Exception:
            dead.append(ws)
    for d in dead:
        loadtest_clients.discard(d)

@app.websocket("/ws/loadtest")
async def ws_loadtest(websocket: WebSocket):
    await websocket.accept()
    loadtest_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        loadtest_clients.discard(websocket)

def _loadtest_worker(total_users: int = 50, spawn_rate: int = 5, host: str = "http://localhost"):
    global loadtest_running
    loadtest_running = True
    active = 0
    try:
        while loadtest_running:
            time.sleep(1)
            active = min(total_users, active + spawn_rate)
            asyncio.run(_loadtest_broadcast(f"[loadtest] host={host} active_users={active}/{total_users}"))
            if active >= total_users:
                for _ in range(5):
                    if not loadtest_running:
                        break
                    time.sleep(1)
                    asyncio.run(_loadtest_broadcast(f"[loadtest] steady active_users={active}"))
                break
        asyncio.run(_loadtest_broadcast("[loadtest] stopped"))
    except Exception as e:
        asyncio.run(_loadtest_broadcast(f"[loadtest] error: {e}"))
    finally:
        loadtest_running = False

@app.post("/loadtest/start")
def api_loadtest_start(total_users: int = 50, spawn_rate: int = 5, host: str = "http://localhost"):
    global loadtest_thread, loadtest_running
    if loadtest_running:
        raise HTTPException(status_code=409, detail="Loadtest already running")
    loadtest_thread = threading.Thread(target=_loadtest_worker, kwargs={"total_users": total_users, "spawn_rate": spawn_rate, "host": host}, daemon=True)
    loadtest_thread.start()
    return {"ok": True, "message": "loadtest started"}

@app.post("/loadtest/stop")
def api_loadtest_stop():
    global loadtest_running
    loadtest_running = False
    return {"ok": True, "message": "loadtest stopping"}

def _ensure_locustfile():
    lf_dir = DATA_DIR
    os.makedirs(lf_dir, exist_ok=True)
    lf_path = os.path.join(lf_dir, "locustfile.py")
    if not os.path.exists(lf_path):
        with open(lf_path, "w", encoding="utf-8") as f:
            f.write("from locust import HttpUser, task, between\n\nclass QuickUser(HttpUser):\n    wait_time = between(1, 2)\n    @task\n    def index(self):\n        self.client.get('/')\n")
    return lf_path


def _spawn_locust(host: str, users: int, rate: int):
    global locust_proc
    try:
        lf = _ensure_locustfile()
        # ensure csv output directory per run
        run_id = time.strftime("%Y%m%d-%H%M%S")
        out_dir = os.path.join(_locust_reports_dir(), run_id)
        os.makedirs(out_dir, exist_ok=True)
        cmd = ["locust", "-f", lf, "--headless", "-u", str(users), "-r", str(rate), "--host", host, "--csv", os.path.join(out_dir, "stats")]
        locust_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in locust_proc.stdout:

            asyncio.run(_loadtest_broadcast(line.rstrip()))
        rc = locust_proc.wait()
        asyncio.run(_loadtest_broadcast(f"[locust] finished with code {rc}"))
    except Exception as e:
        asyncio.run(_loadtest_broadcast(f"[locust] error: {e}"))
    finally:
        try:
            if locust_proc and locust_proc.poll() is None:
                locust_proc.terminate()
        except Exception:
            pass
        locust_proc = None

@app.post("/loadtest/start-real")
def api_loadtest_start_real(total_users: int = 50, spawn_rate: int = 5, host: str = "http://localhost"):
    global loadtest_thread, locust_proc
    if locust_proc and locust_proc.poll() is None:
        raise HTTPException(status_code=409, detail="Locust already running")
    loadtest_thread = threading.Thread(target=_spawn_locust, kwargs={"host": host, "users": total_users, "rate": spawn_rate}, daemon=True)
    loadtest_thread.start()
    return {"ok": True, "message": "locust started"}

@app.post("/loadtest/stop-real")
def api_loadtest_stop_real():
    global locust_proc
    if locust_proc and locust_proc.poll() is None:
        try:
            locust_proc.terminate()
            return {"ok": True, "message": "locust stopping"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"stop error: {e}")
    return {"ok": True, "message": "locust not running"}


@app.get('/allure/list')
def api_allure_list():
    items = []
    base_dir = ALLURE_REPORT_DIR
    if os.path.isdir(base_dir):
        for name in sorted(os.listdir(base_dir)):
            p = os.path.join(base_dir, name)
            # Include any directory under the report directory, regardless of whether
            # an index.html exists. The front-end will attempt to load
            # `/allure/report/{name}/index.html` when viewing the report.
            if os.path.isdir(p):
                items.append({'name': name, 'path': f'/allure/report/{name}/index.html'})
    return {'reports': items}

@app.post('/allure/generate2')
def api_allure_generate2(clean: bool = True):
    allure_cmd = shutil.which('allure')
    if not allure_cmd:
        raise HTTPException(status_code=500, detail='Allure command not found')
    ts = time.strftime('%Y%m%d-%H%M%S')
    target_dir_parent = ALLURE_REPORT_DIR
    os.makedirs(target_dir_parent, exist_ok=True)
    target_dir = os.path.join(target_dir_parent, ts)
    cmd = [allure_cmd, 'generate', ALLURE_RESULTS_DIR, '-o', target_dir]
    if clean:
        cmd.insert(2, '-c')
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f'Allure generate failed: {proc.stderr or proc.stdout}')
    return {'ok': True, 'report': ts, 'url': f'/allure/report/{ts}/index.html'}


def _locust_reports_dir():
    d = os.path.join(os.path.dirname(__file__), 'data', 'locust-reports')
    os.makedirs(d, exist_ok=True)
    return d

@app.get('/loadtest/reports')
def api_locust_reports():
    base_dir = _locust_reports_dir()
    items = []
    for name in sorted(os.listdir(base_dir)):
        run_dir = os.path.join(base_dir, name)
        if os.path.isdir(run_dir):
            items.append({'id': name})
    return {'runs': items}

@app.get('/loadtest/report/{run_id}')
def api_locust_report_detail(run_id: str):
    import csv
    base_dir = _locust_reports_dir()
    run_dir = os.path.join(base_dir, run_id)
    stats_file = os.path.join(run_dir, 'stats.csv')
    failures_file = os.path.join(run_dir, 'failures.csv')
    summary = {'stats': [], 'failures': []}
    if os.path.exists(stats_file):
        with open(stats_file, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                summary['stats'].append(row)
    if os.path.exists(failures_file):
        with open(failures_file, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                summary['failures'].append(row)
    return summary
