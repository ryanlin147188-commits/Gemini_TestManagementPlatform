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

# UPLOADS_DIR is still needed for the upload component
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

    # Page-specific data lists
    web_list: List[Dict] = field(default_factory=list)
    app_list: List[Dict] = field(default_factory=list)
    api_list: List[Dict] = field(default_factory=list)
    bug_list: List[Dict] = field(default_factory=list)

    # Page-specific filters and pagination
    prj_kw: str = ''
    prj_page: int = 1
    prj_page_size: int = 10
    prj_selected_ids: set = field(default_factory=set)

    web_kw: str = ''
    web_page: int = 1
    web_selected_ids: set = field(default_factory=set)

    app_kw: str = ''
    app_page: int = 1
    app_selected_ids: set = field(default_factory=set)

    api_kw: str = ''
    api_page: int = 1
    api_selected_ids: set = field(default_factory=set)

    bug_filter_kw: str = ''
    bug_page: int = 1
    bug_selected_ids: set = field(default_factory=set)

state = AppState()

# === UI Components & Layout ===
loading_spinner = ui.spinner(size='lg', color='primary').classes('fixed inset-0 flex items-center justify-center bg-white/50').style('z-index: 9999')
loading_spinner.visible = False

def show_loading(): loading_spinner.visible = True
def hide_loading(): loading_spinner.visible = False

MENU_CONFIG = [
    {'path': '/home',     'label': '首頁',     'icon': 'home'},
    {'path': '/projects', 'label': '專案',     'icon': 'folder'},
    {'path': '/webcases', 'label': 'WEB 案例', 'icon': 'language'},
    {'path': '/appcases', 'label': 'APP 案例', 'icon': 'smartphone'},
    {'path': '/apicases', 'label': 'API 案例', 'icon': 'api'},
    {'path': '/bugs',     'label': 'BUG',      'icon': 'bug_report'},
    {'path': '/automation','label': '自動化',  'icon': 'bolt'},
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
    show_loading()
    with ui.header().classes('items-center justify-between px-4 shadow-sm'):
        ui.label('測試管理平台').classes('text-lg font-semibold')
    with ui.row().classes('w-full no-wrap'):
        render_sidebar(active_path)
        with ui.column().classes('w-full p-4'):
            await content_builder()
    hide_loading()

# === Page Renderers ===

async def render_projects():
    async def refresh_data():
        show_loading()
        try:
            state.projects = await api.list_projects()
            table.rows = state.projects
            table.update()
        except Exception as e:
            ui.notify(f"Failed to load projects: {e}", type='negative')
        finally:
            hide_loading()

    async def delete_project(project_id: int):
        show_loading()
        try:
            await api.delete_project(project_id)
            ui.notify(f"Deleted project {project_id}", type='positive')
            await refresh_data()
        except Exception as e:
            ui.notify(f"Failed to delete project: {e}", type='negative')
        finally:
            hide_loading()

    def open_project_dialog(editing_project: Dict | None = None):
        with ui.dialog() as d, ui.card():
            ui.label('新增專案' if not editing_project else '修改專案').classes('text-lg font-semibold')
            name_input = ui.input('專案名稱', value=editing_project.get('name') if editing_project else '').props('outlined dense')
            owner_input = ui.input('人員', value=editing_project.get('owner') if editing_project else '').props('outlined dense')
            status_select = ui.select(['新增','進行中','暫停','完成'], label='專案狀態', value=editing_project.get('status') if editing_project else '新增').props('outlined dense')

            async def save():
                payload = {'name': name_input.value, 'owner': owner_input.value, 'status': status_select.value}
                show_loading()
                try:
                    if editing_project:
                        await api.update_project(editing_project['id'], payload)
                    else:
                        await api.create_project(payload)
                    d.close()
                    await refresh_data()
                except Exception as e:
                    ui.notify(f"Failed to save project: {e}", type="negative")
                finally:
                    hide_loading()

            with ui.row().classes('justify-end w-full mt-4'):
                ui.button('取消', on_click=d.close)
                ui.button('儲存', on_click=save, color='primary')
        d.open()

    page_header("專案管理", "建立、編輯和管理您的測試專案。")

    with ui.row().classes('w-full items-center'):
        ui.button('新增專案', icon='add', on_click=lambda: open_project_dialog()).props('color=primary')
        ui.space()
        ui.input(placeholder='搜尋專案...').props('dense outlined').bind_value(state, 'prj_kw').on('keydown.enter', refresh_data)


    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
        {'name': 'name', 'label': '專案名稱', 'field': 'name', 'sortable': True, 'align': 'left'},
        {'name': 'owner', 'label': '人員', 'field': 'owner', 'sortable': True, 'align': 'left'},
        {'name': 'status', 'label': '狀態', 'field': 'status', 'sortable': True},
        {'name': 'actions', 'label': '操作', 'field': 'actions'},
    ]

    table = ui.table(columns=columns, rows=[], row_key='id').classes('w-full')
    table.add_slot('body-cell-actions', '''
        <q-td :props="props">
            <q-btn flat dense round icon="edit" @click="() => $parent.$emit('edit', props.row)" />
            <q-btn flat dense round icon="delete" @click="() => $parent.$emit('delete', props.row)" />
        </q-td>
    ''')

    table.on('edit', lambda e: open_project_dialog(e.args))
    table.on('delete', lambda e: delete_project(e.args['id']))

    await refresh_data()

async def render_web_cases():
    async def refresh_data():
        show_loading()
        try:
            result = await api.list_web_cases(state.active_project_id, keyword=state.web_kw)
            table.rows = result.get('items', [])
            # Here you might want to update a label with the total count from result.get('total')
            table.update()
        except Exception as e:
            ui.notify(f"Failed to load web cases: {e}", type='negative')
        finally:
            hide_loading()

    # ... (Dialogs and handlers for create/update/delete)

    page_header("WEB 案例", f"專案: {state.active_project_name}")

    with ui.row().classes('w-full items-center'):
        # ui.button('新增案例', icon='add', on_click=lambda: open_dialog()).props('color=primary')
        ui.space()
        ui.input(placeholder='搜尋案例...').props('dense outlined').bind_value(state, 'web_kw').on('keydown.enter', refresh_data)

    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
        {'name': 'test_feature', 'label': '測試功能', 'field': 'test_feature', 'align': 'left'},
        {'name': 'action', 'label': '動作', 'field': 'action'},
        {'name': 'page', 'label': '頁面', 'field': 'page'},
        {'name': 'element', 'label': '元件', 'field': 'element'},
    ]

    table = ui.table(columns=columns, rows=[], row_key='id').classes('w-full')

    await refresh_data()

async def render_app_cases():
    async def refresh_data():
        show_loading()
        try:
            result = await api.list_app_cases(state.active_project_id, keyword=state.app_kw)
            table.rows = result.get('items', [])
            table.update()
        except Exception as e:
            ui.notify(f"Failed to load app cases: {e}", type='negative')
        finally:
            hide_loading()

    page_header("APP 案例", f"專案: {state.active_project_name}")
    with ui.row().classes('w-full items-center'):
        ui.space()
        ui.input(placeholder='搜尋案例...').props('dense outlined').bind_value(state, 'app_kw').on('keydown.enter', refresh_data)

    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
        {'name': 'test_feature', 'label': '測試功能', 'field': 'test_feature', 'align': 'left'},
    ]
    table = ui.table(columns=columns, rows=[], row_key='id').classes('w-full')
    await refresh_data()

async def render_api_cases():
    async def refresh_data():
        show_loading()
        try:
            result = await api.list_api_cases(state.active_project_id, keyword=state.api_kw)
            table.rows = result.get('items', [])
            table.update()
        except Exception as e:
            ui.notify(f"Failed to load api cases: {e}", type='negative')
        finally:
            hide_loading()

    page_header("API 案例", f"專案: {state.active_project_name}")
    with ui.row().classes('w-full items-center'):
        ui.space()
        ui.input(placeholder='搜尋案例...').props('dense outlined').bind_value(state, 'api_kw').on('keydown.enter', refresh_data)

    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
        {'name': 'test_feature', 'label': '測試功能', 'field': 'test_feature', 'align': 'left'},
        {'name': 'method', 'label': '方法', 'field': 'method'},
        {'name': 'api_path', 'label': 'API路徑', 'field': 'api_path'},
    ]
    table = ui.table(columns=columns, rows=[], row_key='id').classes('w-full')
    await refresh_data()

async def render_bugs():
    async def refresh_data():
        show_loading()
        try:
            state.bug_list = await api.list_project_bugs(state.active_project_id, keyword=state.bug_filter_kw)
            table.rows = state.bug_list
            table.update()
        except Exception as e:
            ui.notify(f"Failed to load bugs: {e}", type='negative')
        finally:
            hide_loading()

    page_header("BUG 管理", f"專案: {state.active_project_name}")
    with ui.row().classes('w-full items-center'):
        ui.space()
        ui.input(placeholder='搜尋 BUG...').props('dense outlined').bind_value(state, 'bug_filter_kw').on('keydown.enter', refresh_data)

    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
        {'name': 'description', 'label': '問題敘述', 'field': 'description', 'align': 'left'},
        {'name': 'severity', 'label': '嚴重度', 'field': 'severity'},
        {'name': 'status', 'label': '狀態', 'field': 'status'},
    ]
    table = ui.table(columns=columns, rows=[], row_key='id').classes('w-full')
    await refresh_data()

async def render_automation():
    ui.label("Automation Page Content")

async def render_mock_page():
    ui.label("Mock API Page Content")

async def render_home():
    with ui.column().classes('w-full gap-2'):
        ui.label('歡迎使用 測試管理平台').classes('text-h5')
        ui.label('請從左側選單選擇要進入的功能，或使用下方快速選單。').classes('text-body2')
        with ui.row().classes('gap-2 mt-2'):
            ui.button('專案管理', icon='folder', on_click=lambda: ui.navigate.to('/projects'))
            ui.button('BUG 管理', icon='bug_report', on_click=lambda: ui.navigate.to('/bugs'))

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

@ui.page('/webcases')
async def page_webcases():
    await render_layout('/webcases', render_web_cases)

@ui.page('/appcases')
async def page_appcases():
    await render_layout('/appcases', render_app_cases)

@ui.page('/apicases')
async def page_apicases():
    await render_layout('/apicases', render_api_cases)

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
    # Any other async startup tasks can go here

app.on_startup(startup_tasks)

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get('PORT', 8081))
    ui.run(host='127.0.0.1', port=port, reload=False, title="測試平台")
