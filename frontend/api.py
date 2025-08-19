
import os
import httpx

def base_url() -> str:
    return os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"

# ---- Projects ----
async def list_projects(keyword: str = ""):
    params = {"q": keyword} if keyword else None
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects", params=params)
        r.raise_for_status()
        return r.json()

async def create_project(payload: dict):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(f"{base_url()}/projects", json=payload)
        r.raise_for_status()
        return r.json()

async def update_project(project_id: int, payload: dict):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.put(f"{base_url()}/projects/{project_id}", json=payload)
        r.raise_for_status()
        return r.json()

async def delete_project(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(f"{base_url()}/projects/{project_id}")
        if r.status_code not in (200,204):
            r.raise_for_status()
        return True

# ---- Case Names ----
async def list_web_case_names(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/webcases/names")
        r.raise_for_status()
        return r.json()

async def list_app_case_names(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/appcases/names")
        r.raise_for_status()
        return r.json()

async def list_api_case_names(project_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/apicases/names")
        r.raise_for_status()
        return r.json()

# ---- Logging ----
async def log_action(action: str):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{base_url()}/log-action", json={"action": action})
    except Exception:
        # Fail silently if logging fails
        pass

# ---- Cases ----
async def list_web_cases(project_id: int, keyword: str = ""):
    params = {"q": keyword} if keyword else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/webcases", params=params)
        r.raise_for_status()
        return r.json()

async def list_app_cases(project_id: int, keyword: str = ""):
    params = {"q": keyword} if keyword else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/appcases", params=params)
        r.raise_for_status()
        return r.json()

async def list_api_cases(project_id: int, keyword: str = ""):
    params = {"q": keyword} if keyword else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/apicases", params=params)
        r.raise_for_status()
        return r.json()

async def list_project_bugs(project_id: int, keyword: str = ""):
    params = {"q": keyword} if keyword else {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/projects/{project_id}/bugs", params=params)
        r.raise_for_status()
        return r.json()

# ---- Bugs ----
async def list_bugs(keyword: str = ""):
    params = {"q": keyword} if keyword else None
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/bugs", params=params)
        r.raise_for_status()
        return r.json()

async def create_bug(payload: dict):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(f"{base_url()}/bugs", json=payload)
        r.raise_for_status()
        return r.json()

async def update_bug(bug_id: int, payload: dict):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.put(f"{base_url()}/bugs/{bug_id}", json=payload)
        r.raise_for_status()
        return r.json()

async def delete_bug(bug_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(f"{base_url()}/bugs/{bug_id}")
        if r.status_code not in (200,204):
            r.raise_for_status()
        return True

# ---- Runs ----
async def list_runs(keyword: str = ""):
    params = {"q": keyword} if keyword else None
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{base_url()}/runs", params=params)
        r.raise_for_status()
        return r.json()

async def create_run(payload: dict):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(f"{base_url()}/runs", json=payload)
        r.raise_for_status()
        return r.json()

async def update_run(run_id: int, payload: dict):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.put(f"{base_url()}/runs/{run_id}", json=payload)
        r.raise_for_status()
        return r.json()

async def delete_run(run_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(f"{base_url()}/runs/{run_id}")
        if r.status_code not in (200,204):
            r.raise_for_status()
        return True
