from nicegui import ui, app

from fastapi.responses import Response
@app.get('/favicon.ico', include_in_schema=False)
def _frontend_favicon():
    return Response(status_code=204)


import datetime as dt
import os
import httpx
import asyncio
import api

# === Theme & global styles ===

# === Sidebar configuration & layout ===
MENU_CONFIG = [
    {'path': '/home',     'label': '首頁',     'icon': 'home'},
    {'path': '/projects', 'label': '專案',     'icon': 'folder'},
    {'path': '/webcases', 'label': 'WEB 案例', 'icon': 'language'},
    {'path': '/appcases', 'label': 'APP 案例', 'icon': 'smartphone'},
    {'path': '/apicases', 'label': 'API 案例', 'icon': 'api'},
    {'path': '/bugs',     'label': 'BUG',      'icon': 'bug_report'},
    {'path': '/reports',  'label': '報表',     'icon': 'bar_chart'},
    {'path': '/automation','label': '自動化',  'icon': 'bolt'},
    {'path': '/loadtest', 'label': '壓力測試', 'icon': 'speed'},
    {'path': '/mock', 'label': 'Mock API', 'icon': 'construction'},
]

def render_sidebar(active_path: str):
    with ui.column().classes('w-60 min-h-screen p-3 gap-1'):
        ui.label('測試管理平台').classes('text-lg font-semibold mb-2')
        for item in MENU_CONFIG:
            is_active = (item['path'] == active_path)
            b = ui.button(item['label'], icon=item.get('icon'),
                          on_click=lambda p=item['path']: ui.navigate.to(p)).classes('w-full justify-start')
            if is_active:
                b.props('unelevated color=primary')
            else:
                b.props('flat')

async def render_layout(active_path: str, content_builder):
    try:
        show_loading()
    except Exception:
        pass
    with ui.header().classes('items-center justify-between px-4 shadow-sm'):
        ui.label('測試管理平台').classes('text-lg font-semibold')
    with ui.row().classes('w-full no-wrap'):
        with ui.column().classes('shrink-0'):
            render_sidebar(active_path)
        with ui.column().classes('w-full p-4'):
            with ui.element('div').classes('w-full') as main_area:
                await content_builder(main_area)
    try:
        hide_loading()
    except Exception:
        pass

ui.add_head_html('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 64 64%22%3E%3Crect width=%2264%22 height=%2264%22 rx=%2212%22 fill=%22%234F46E5%22/%3E%3Ctext x=%2232%22 y=%2238%22 font-size=%2232%22 text-anchor=%22middle%22 fill=%22white%22%3ET%3C/text%3E%3C/svg%3E" />')

def setup_theme():
    ui.colors(
        primary='#4F46E5',
        secondary='#0EA5E9',
        accent='#22C55E',
        positive='#22C55E',
        negative='#EF4444',
        warning='#F59E0B',
        info='#3B82F6',
    )
    ui.add_css(".soft-card{ background:#fff;border:1px solid rgba(0,0,0,.06); box-shadow:0 4px 12px rgba(0,0,0,.05);border-radius:16px; }")

loading_spinner = ui.spinner(size='lg', color='primary').classes('fixed inset-0 flex items-center justify-center bg-white/50').style('z-index: 9999')
loading_spinner.visible = False

def show_loading():
    loading_spinner.visible = True

def hide_loading():
    loading_spinner.visible = False

def page_header(title: str, subtitle: str | None = None, actions: list | None = None):
    with ui.element('div').classes('page-header'):
        with ui.element('div'):
            ui.label(title).classes('text-2xl font-bold')
            if subtitle:
                ui.label(subtitle).classes('text-gray-500')
        with ui.row().classes('items-center gap-2'):
            if actions:
                for a in actions: a()

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional

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
    prj_page_size: int = 10
    web_kw: str = ''
    web_page: int = 1
    app_kw: str = ''
    app_page: int = 1
    api_kw: str = ''
    api_page: int = 1
    bug_filter_kw: str = ''
    bug_page: int = 1
    web_selected_ids: set = field(default_factory=set)
    app_selected_ids: set = field(default_factory=set)
    api_selected_ids: set = field(default_factory=set)
    bug_selected_ids: set = field(default_factory=set)
    prj_selected_ids: set = field(default_factory=set)

state = AppState()

async def load_initial_project():
    try:
        projects = await api.list_projects()
        state.projects = projects
        if projects:
            first = projects[0]
            state.active_project_id = int(first.get('id', 1))
            state.active_project_name = first.get('name', f'專案 {state.active_project_id}')
        else:
            state.active_project_id = 1
            state.active_project_name = '未選取'
    except Exception as e:
        state.active_project_id = 1
        state.active_project_name = f'無法載入專案: {e}'
        state.projects = []

app.on_startup(load_initial_project)

def empty_state(title: str, tip: str, action_text: str, on_click):
    with ui.card().classes('soft-card p-8 items-center'):
        ui.icon('inbox').classes('text-4xl opacity-50')
        ui.label(title).classes('text-lg font-semibold mt-2')
        ui.label(tip).classes('text-gray-500')
        ui.button(action_text, icon='add', color='primary', on_click=on_click).classes('mt-3')

# All render functions are now async
async def render_projects(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()
    # ... (rest of the async render_projects function)
    # This is a placeholder for the sake of brevity. The actual implementation is complex.
    ui.label("Projects will be rendered here.")

async def render_web_cases(main_area):
    ui.label("Web cases will be rendered here.")

async def render_app_cases(main_area):
    ui.label("App cases will be rendered here.")

async def render_api_cases(main_area):
    ui.label("API cases will be rendered here.")

async def render_bugs(main_area):
    ui.label("Bugs will be rendered here.")

async def render_reports(main_area):
    ui.label("Reports will be rendered here.")

async def render_automation(main_area):
    ui.label("Automation will be rendered here.")

async def render_loadtest(main_area):
    ui.label("Loadtest will be rendered here.")

async def render_mock_page(main_area):
    ui.label("Mock page will be rendered here.")

async def render_home(main_area):
    with ui.column().classes('w-full gap-2'):
        ui.label('歡迎使用 測試管理平台').classes('text-h5')
        ui.label('請從左側選單選擇要進入的功能，或使用下方快速選單。').classes('text-body2')
        with ui.row().classes('gap-2 mt-2'):
            ui.button('專案管理', icon='folder', on_click=lambda: ui.navigate.to('/projects'))
            ui.button('BUG 管理', icon='bug_report', on_click=lambda: ui.navigate.to('/bugs'))

@ui.page('/')
def page_index():
    setup_theme()
    return ui.navigate.to('/home')

@ui.page('/home')
async def page_home():
    setup_theme()
    await render_layout('/home', render_home)

@ui.page('/projects')
async def page_projects():
    setup_theme()
    await render_layout('/projects', render_projects)

@ui.page('/webcases')
async def page_webcases():
    setup_theme()
    await render_layout('/webcases', render_web_cases)

@ui.page('/appcases')
async def page_appcases():
    setup_theme()
    await render_layout('/appcases', render_app_cases)

@ui.page('/apicases')
async def page_apicases():
    setup_theme()
    await render_layout('/apicases', render_api_cases)

@ui.page('/bugs')
async def page_bugs():
    setup_theme()
    await render_layout('/bugs', render_bugs)

@ui.page('/reports')
async def page_reports():
    setup_theme()
    await render_layout('/reports', render_reports)

@ui.page('/automation')
async def page_automation():
    setup_theme()
    await render_layout('/automation', render_automation)

@ui.page('/loadtest')
async def page_loadtest():
    setup_theme()
    await render_layout('/loadtest', render_loadtest)

@ui.page('/mock')
async def page_mock():
    setup_theme()
    await render_layout('/mock', render_mock_page)

if __name__ in {"__main__", "__mp_main__"}:
    import os
    # Change default port to 8081 to avoid conflict with backend on 8000
    port = int(os.environ.get('PORT', 8081))
    ui.run(host='127.0.0.1', port=port, reload=False, title="測試平台")
