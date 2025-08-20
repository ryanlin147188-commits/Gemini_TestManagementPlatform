from nicegui import ui, app
from fastapi.responses import Response
import datetime as dt
import os
import httpx
import asyncio
import api
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional

# Basic App Setup
@app.get('/favicon.ico', include_in_schema=False)
def _frontend_favicon():
    return Response(status_code=204)

from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
UPLOADS_DIR = DATA_DIR / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)
app.add_static_files('/uploads', str(UPLOADS_DIR))

# === App State ===
@dataclass
class AppState:
    active_project_id: int = 1
    active_project_name: str = '未選取'
    projects: List[Dict] = field(default_factory=list)
    web_list: List[Dict] = field(default_factory=list)
    app_list: List[Dict] = field(default_factory=list)
    api_list: List[Dict] = field(default_factory=list)
    bug_list: List[Dict] = field(default_factory=list)
    prj_kw: str = ''
    prj_page: int = 1
    web_kw: str = ''
    web_page: int = 1
    app_kw: str = ''
    app_page: int = 1
    api_kw: str = ''
    api_page: int = 1
    bug_filter_kw: str = ''
    bug_page: int = 1
    mock_params: List[Dict] = field(default_factory=lambda: [{'key': '', 'value': ''}])
    mock_req_headers: List[Dict] = field(default_factory=lambda: [{'key': '', 'value': ''}])
    mock_resp_headers: List[Dict] = field(default_factory=lambda: [{'key': 'Content-Type', 'value': 'application/json'}])
    active_mocks: List[Dict] = field(default_factory=list)

state = AppState()

# === UI Components & Layout ===
loading_spinner = ui.spinner(size='lg', color='primary').classes('fixed inset-0 flex items-center justify-center bg-white/50').style('z-index: 9999')
loading_spinner.visible = False

def show_loading(): loading_spinner.visible = True
def hide_loading(): loading_spinner.visible = False

MENU_CONFIG = [
    {'path': '/home', 'label': '首頁', 'icon': 'home'},
    {'path': '/projects', 'label': '專案', 'icon': 'folder'},
    {'path': '/webcases', 'label': 'WEB 案例', 'icon': 'language'},
    {'path': '/appcases', 'label': 'APP 案例', 'icon': 'smartphone'},
    {'path': '/apicases', 'label': 'API 案例', 'icon': 'api'},
    {'path': '/bugs', 'label': 'BUG', 'icon': 'bug_report'},
    {'path': '/automation', 'label': '自動化', 'icon': 'bolt'},
    {'path': '/mock', 'label': 'Mock API', 'icon': 'construction'},
]

def render_sidebar(active_path: str):
    with ui.column().classes('w-60 min-h-screen p-3 gap-1'):
        ui.label('測試管理平台').classes('text-lg font-semibold mb-2')
        for item in MENU_CONFIG:
            is_active = (item['path'] == active_path)
            b = ui.button(item['label'], icon=item.get('icon'), on_click=lambda p=item['path']: ui.navigate.to(p)).classes('w-full justify-start')
            b.props('unelevated color=primary' if is_active else 'flat')

async def render_layout(active_path: str, content_builder: Callable):
    setup_theme()
    show_loading()
    with ui.header().classes('items-center justify-between px-4 shadow-sm'):
        ui.label('測試管理平台').classes('text-lg font-semibold')
    with ui.row().classes('w-full no-wrap'):
        render_sidebar(active_path)
        with ui.column().classes('w-full p-4'):
            await content_builder()
    hide_loading()

def setup_theme():
    ui.colors(primary='#4F46E5', secondary='#0EA5E9', accent='#22C55E', positive='#22C55E', negative='#EF4444', warning='#F59E0B', info='#3B82F6')
    ui.add_css(".soft-card{ background:#fff;border:1px solid rgba(0,0,0,.06); box-shadow:0 4px 12px rgba(0,0,0,.05);border-radius:16px; }")

def page_header(title: str, subtitle: str | None = None):
    with ui.row().classes('w-full items-center justify-between'):
        with ui.column():
            ui.label(title).classes('text-2xl font-bold')
            if subtitle:
                ui.label(subtitle).classes('text-gray-500')

# === Page Renderers ===

async def render_projects():
    # ... (full implementation)
    ui.label("Projects Page Content")

async def render_web_cases():
    ui.label("Web Cases Page Content")

async def render_app_cases():
    ui.label("App Cases Page Content")

async def render_api_cases():
    ui.label("API Cases Page Content")

async def render_bugs():
    ui.label("Bugs Page Content")

async def render_automation():
    ui.label("Automation Page Content")

async def render_mock_page():
    # ... (full implementation)
    ui.label("Mock API Page Content")

async def render_home():
    page_header("歡迎使用 測試管理平台", "請從左側選單選擇要進入的功能。")

# === Page Routes ===
@ui.page('/')
def page_index():
    return ui.navigate.to('/home')

@ui.page('/home')
async def page_home():
    await render_layout('/home', render_home)

@ui.page('/projects')
async def page_projects():
    await render_layout('/projects', render_projects)

# ... (other page routes) ...
@ui.page('/bugs')
async def page_bugs():
    await render_layout('/bugs', render_bugs)

@ui.page('/automation')
async def page_automation():
    await render_layout('/automation', render_automation)

@ui.page('/mock')
async def page_mock():
    await render_layout('/mock', render_mock_page)

# === App Startup ===
async def startup_tasks():
    await load_initial_project()

app.on_startup(startup_tasks)

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get('PORT', 8081))
    host = '0.0.0.0' if os.environ.get('DOCKER_ENV') else '127.0.0.1'
    ui.run(host=host, port=port, reload=False, title="測試平台")
