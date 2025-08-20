from nicegui import ui, app

from fastapi.responses import Response
@app.get('/favicon.ico', include_in_schema=False)
def _frontend_favicon():
    return Response(status_code=204)


import datetime as dt
import os
import httpx
import asyncio
impo
rt api

# === Theme & global styles ===

# === Sidebar configuration & layout ===
# 左側側邊欄配置。增加 WEB、APP 與 API 測試案例頁面的導覽。
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

def render_layout(active_path: str, content_builder):
    """Common frame with top header, left sidebar and a content area.
    `content_builder(main_area)` will fill the right side. This function shows a
    global loading spinner while the layout and page contents are being built
    and hides it afterwards. You can call `show_loading()`/`hide_loading()` in
    your own event handlers if you need to indicate longer running tasks.
    """
    # 在佈局產生之前顯示載入動畫
    try:
        show_loading()
    except Exception:
        # if show_loading is not available or fails, just ignore
        pass
    # Top header
    with ui.header().classes('items-center justify-between px-4 shadow-sm'):
        ui.label('測試管理平台').classes('text-lg font-semibold')
    # Body: sidebar + content
    with ui.row().classes('w-full no-wrap'):
        with ui.column().classes('shrink-0'):
            render_sidebar(active_path)
        with ui.column().classes('w-full p-4'):
            with ui.element('div').classes('w-full') as main_area:
                # 呼叫內容產生器
                content_builder(main_area)
    # 建構完成後隱藏載入動畫
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
    ui.add_css("""

.board-topbar{background:#E6F4FF;border-bottom:1px solid rgba(0,0,0,.06);display:flex;align-items:center;justify-content:space-between;padding:8px 14px;border-radius:10px}
.board-month{font-weight:700;letter-spacing:.3px}
.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(140px,1fr));gap:10px}
.kpi-box{background:#fff;border:1px solid rgba(0,0,0,.06);border-radius:12px;padding:10px 12px;box-shadow:0 4px 12px rgba(0,0,0,.04)}
.kpi-number{font-size:22px;font-weight:800}
.kpi-hint{opacity:.7;font-size:12px}
.ring{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}
.donut-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}
.tag{padding:2px 8px;border-radius:999px;border:1px solid rgba(0,0,0,.08)}
.tag-green{background:#ECFDF5;color:#047857}
.tag-orange{background:#FFF7ED;color:#C2410C}
.tag-blue{background:#EFF6FF;color:#1D4ED8}

    .page-container{max-width:1320px;margin:0 auto;padding:12px 16px;}
    .page-header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px;}
    .page-title{font-size:24px;font-weight:700;letter-spacing:.2px}
    .page-subtle{opacity:.7}
    .glass-card{
        background:rgba(255,255,255,.6);
        backdrop-filter:saturate(150%) blur(8px);
        border:1px solid rgba(0,0,0,.06);
        box-shadow:0 6px 20px rgba(0,0,0,.06);
        border-radius:16px;
    }
    .soft-card{
        background:#fff;border:1px solid rgba(0,0,0,.06);
        box-shadow:0 4px 12px rgba(0,0,0,.05);border-radius:16px;
    }
    .section-title{font-size:16px;font-weight:700;margin:6px 0 4px 2px}
    .muted{opacity:.6}
    .chip{border:1px solid rgba(0,0,0,.08);border-radius:999px;padding:2px 10px}
    .sidebar{background:linear-gradient(180deg,#F8FAFF 0%,#F4F6FF 100%);border-right:1px solid rgba(0,0,0,.06)}
    .sidebar .q-item{border-radius:10px}
    .sidebar .q-item:hover{background:rgba(79,70,229,.06)}
    .active{background:#4F46E5 !important;color:#fff !important}
    ::-webkit-scrollbar{height:8px;width:8px}
    ::-webkit-scrollbar-thumb{background:rgba(0,0,0,.15);border-radius:999px}
    """)

# === 全域載入指示器 ===
# 建立一個全域的 loading spinner，在各個頁面切換和資料更新時可以顯示。
# 由於它是在模組載入時建立，因此會存在於所有頁面之上。利用 Tailwind 的
# `fixed inset-0` 等類別將其置中並覆蓋整個畫面，並設置半透明背景。
# We apply a very high z-index to ensure it appears above all other elements, including dialogs.
loading_spinner = ui.spinner(size='lg', color='primary').classes('fixed inset-0 flex items-center justify-center bg-white/50').style('z-index: 9999')
# 預設隱藏，只有在需要時才顯示
loading_spinner.visible = False

def show_loading() -> None:
    """顯示全域的載入動畫。"""
    loading_spinner.visible = True

def hide_loading() -> None:
    """隱藏全域的載入動畫。"""
    loading_spinner.visible = False

# === 共用頁首元件 ===
def page_header(title: str, subtitle: str | None = None, actions: list | None = None):
    with ui.element('div').classes('page-header'):
        with ui.element('div'):
            ui.label(title).classes('page-title')
            if subtitle:
                ui.label(subtitle).classes('page-subtle')
        with ui.row().classes('items-center gap-2'):
            if actions:
                for a in actions: a()

# === 統一卡片（統計/區塊） ===
def stat_card(icon: str, label: str, value: str, hint: str = ''):
    with ui.card().classes('glass-card p-4 min-w-[220px]'):
        with ui.row().classes('items-center justify-between w-full'):
            with ui.row().classes('items-center gap-2'):
                ui.icon(icon).classes('text-primary')
                ui.label(label).classes('muted')
            ui.badge(value=value, color='primary').props('rounded')
        if hint:
            ui.label(hint).classes('muted mt-2')

def section(title: str, tip: str | None = None):
    ui.label(title).classes('section-title')
    if tip: ui.label(tip).classes('muted ml-1')
    ui.separator()
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Callable, Optional
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # project root
DATA_DIR = ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)
TESTCASES_FILE = DATA_DIR / 'test_cases.json'
BUGS_FILE = DATA_DIR / 'bugs.json'

WEB_CASES_FILE = DATA_DIR / 'web_cases.json'
APP_CASES_FILE = DATA_DIR / 'app_cases.json'
API_CASES_FILE = DATA_DIR / 'api_cases.json'
APP_DEVICE_FILE = DATA_DIR / 'app_device.json'
UPLOADS_DIR = DATA_DIR / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)
app.add_static_files('/uploads', str(UPLOADS_DIR))
PROJECTS_FILE = DATA_DIR / 'projects.json'

# --------- 工具函式：JSON 持久化 ---------
def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return fallback

def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')



# ---- Projects helpers ----
def read_projects() -> list:
    data = read_json(PROJECTS_FILE, [])
    return data if isinstance(data, list) else []

def write_projects(items: list):
    write_json(PROJECTS_FILE, items)

# ---- 專案範圍的清單讀寫：以 {"<project_id>": [...]} 結構儲存 ----
def read_scoped_list(path: Path, project_id: int):
    data = read_json(path, {})
    if isinstance(data, list):
        # 舊版結構：升級為字典，將舊資料歸到 "1"
        data = {"1": data}
    return data.get(str(project_id), [])

def write_scoped_list(path: Path, project_id: int, items: list):
    data = read_json(path, {})
    if isinstance(data, list):
        data = {"1": data}
    data[str(project_id)] = items
    write_json(path, data)

# --------- 資料模型 ---------
@dataclass
class TestCase:
    id: int
    name: str
    type: str
    priority: str
    owner: str
    status: str

@dataclass
class Bug:
    id: int
    title: str
    severity: str
    assignee: str
    state: str

# --------- 全域狀態 ---------
@dataclass
class AppState:
    # Branding (if present)
    branding: dict | None = None
    brand_name: str = '企業測試平台'
    logo_url: str | None = None

    # Active project
    active_project_id: int = 1
    active_project_name: str = '未選取'
    projects: List[Dict] | None = None

    # Navigation
    active_view: str = 'dashboard'

    # TestCases data & filters
    tc_list: List[Dict] | None = None
    tc_filter_kw: str = ''
    tc_filter_status: set = field(default_factory=set)
    tc_selected_ids: set = field(default_factory=set)

    # Bugs data & filters
    bug_list: List[Dict] | None = None
    bug_filter_kw: str = ''
    bug_filter_status: set = field(default_factory=set)
    bug_selected_ids: set = field(default_factory=set)

    # Web cases
    web_list: List[Dict] | None = None
    web_kw: str = ''
    web_action: set = field(default_factory=set)
    web_result: set = field(default_factory=set)
    web_page: int = 1
    web_selected_ids: set = field(default_factory=set)

    # App cases
    app_list: List[Dict] | None = None
    app_kw: str = ''
    app_action: set = field(default_factory=set)
    app_result: set = field(default_factory=set)
    app_page: int = 1
    app_selected_ids: set = field(default_factory=set)
    app_device_text: str = ''

    # API cases
    api_list: List[Dict] | None = None
    api_kw: str = ''
    api_method: set = field(default_factory=set)
    api_result: set = field(default_factory=set)
    api_page: int = 1
    api_selected_ids: set = field(default_factory=set)

    # Bugs paging & filters
    bug_page: int = 1

    # Projects filters & pagination
    prj_kw: str = ''
    prj_owner: str = ''
    prj_status: str = ''
    prj_page: int = 1
    prj_page_size: int = 10
    prj_selected_ids: set = field(default_factory=set)

state = AppState(active_view='dashboard')
# ---- 專案上下文 ----
def load_projects():
    items = read_json(PROJECTS_FILE, [])
    if not isinstance(items, list):
        items = []
    state.projects = items
    if items:
        first = items[0]
        state.active_project_id = int(first.get('id', 1))
        state.active_project_name = first.get('name', f'專案 {state.active_project_id}')
    else:
        state.active_project_id = 1
        state.active_project_name = '未選取'

def load_scoped_data():
    state.web_list = read_scoped_list(WEB_CASES_FILE, state.active_project_id)
    state.app_list = read_scoped_list(APP_CASES_FILE, state.active_project_id)
    state.api_list = read_scoped_list(API_CASES_FILE, state.active_project_id)
    state.tc_list = state.web_list
    state.bug_list = read_scoped_list(BUGS_FILE, state.active_project_id)


load_projects()
load_scoped_data()

# --------- 共用 UI 元件 ---------
def confirm(title: str, text: str, on_ok: Callable[[], None]):
    with ui.dialog() as d, ui.card():
        ui.label(title).classes('text-lg font-bold')
        ui.label(text).classes('opacity-80')
        with ui.row().classes('justify-end w-full mt-2'):
            ui.button('取消', on_click=d.close)
            ui.button('確認', on_click=lambda: (on_ok(), d.close())).props('color=primary')
    d.open()




# ---- Table UX Helpers ----
CASE_STATUS_COLORS = {
    'Ready': 'positive', 'Draft': 'warning', 'WIP': 'info', 'Deprecated': 'negative',
    'PASS': 'positive', 'FAIL': 'negative',
    '新增': 'info', '進行中': 'primary', '暫停': 'warning', '完成': 'positive',
    'Open': 'negative', 'In Progress': 'warning', 'Resolved': 'positive', 'Closed': 'info',
    '高': 'negative', '中': 'warning', '低': 'info',
}

def status_badge(text: str, mapping: dict | None = None):
    color = (mapping or CASE_STATUS_COLORS).get(text, 'secondary')
    return ui.badge(text, color=color).props('rounded').classes('text-xs')

def empty_state(title: str, tip: str, action_text: str, on_click):
    with ui.card().classes('soft-card p-8 items-center'):
        ui.icon('inbox').classes('text-4xl opacity-50')
        ui.label(title).classes('text-lg font-semibold mt-2')
        ui.label(tip).classes('muted')
        ui.button(action_text, icon='add', color='primary', on_click=on_click).classes('mt-3')

def tag_bar(options: list[str], active: set, on_toggle, on_clear):
    with ui.row().classes('gap-2 items-center flex-wrap'):
        ui.label('篩選：').classes('muted')
        for opt in options:
            is_on = opt in active
            def make_toggle(o=opt):
                return lambda: (active.remove(o) if o in active else active.add(o)) or on_toggle()
            ui.button(opt, on_click=make_toggle(), color=('primary' if is_on else None)).props('outline' if not is_on else '')
        ui.button('清除', on_click=lambda: (active.clear(), on_clear())).props('flat')

def bulk_toolbar(selected_ids: set, actions: list[tuple[str, str, callable]]):  # (label, icon, handler)
    if not selected_ids:
        return
    with ui.element('div').classes('soft-card p-2 mb-2'):
        with ui.row().classes('items-center justify-between'):
            ui.label(f'已選取 {len(selected_ids)} 筆').classes('font-semibold')
            with ui.row().classes('gap-2'):
                for label, icon, handler in actions:
                    ui.button(label, icon=icon, on_click=handler).props('flat')
def render_projects(main_area):
    # Ensure 'items' is always initialized from the global state at the beginning.
    items = state.projects or []
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # Define items at the top to resolve UnboundLocalError in nested functions
    items = state.projects or []

    # 自動刷新：當第一次渲染此頁面時，設定一個定時器週期性讀取 JSON 資料並更新介面。
    # 若 state 上已經存在計時器屬性，則不再重複建立，避免產生多個定時器。
    if not hasattr(state, '_projects_timer'):
        def _auto_refresh() -> None:
            """定時重新讀取專案資料並刷新介面。"""
            try:
                fresh = read_projects()
                if isinstance(fresh, list):
                    # 僅在資料有變動時更新，以避免不必要的 UI 渲染
                    state.projects = fresh
                # 刷新主區域
                try:
                    main_area.refresh()
                except Exception:
                    pass
            except Exception:
                # 讀取失敗時忽略
                pass
        # 每 10 秒刷新一次
        state._projects_timer = ui.timer(10.0, _auto_refresh)

    # Local helpers
    def refresh():
        try: main_area.refresh()
        except Exception: pass

    # CRUD Dialog (Create/Edit)
    def open_project_dialog(edit_id: int | None = None):
        editing = None
        if edit_id is not None:
            for p in read_projects():
                if str(p.get('id')) == str(edit_id):
                    editing = p; break

        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[420px]'):
                ui.label('新增專案' if not editing else '修改專案').classes('text-lg font-semibold')
                name = ui.input('專案名稱').props('outlined dense').classes('mt-2')
                owner = ui.input('人員').props('outlined dense')
                status = ui.select(['新增','進行中','暫停','完成'], label='專案狀態').props('outlined dense')
                if editing:
                    name.value = editing.get('name','')
                    owner.value = editing.get('owner','')
                    status.value = editing.get('status','新增')

                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    def save():
                        nm = (name.value or '').strip()
                        ow = (owner.value or '').strip()
                        st = status.value or '新增'
                        if not nm:
                            ui.notify('請輸入專案名稱', type='warning'); return
                        data = read_projects()
                        if editing:
                            for i, p in enumerate(data):
                                if str(p.get('id')) == str(editing.get('id')):
                                    data[i] = {**p, 'name': nm, 'owner': ow, 'status': st}
                                    break
                        else:
                            new_id = max([int(p.get('id', 0)) for p in data] + [0]) + 1
                            data.append({'id': new_id, 'name': nm, 'owner': ow, 'status': st})
                            if state.active_project_name == '未選取':
                                state.active_project_id = new_id
                                state.active_project_name = nm
                        write_projects(data)
                        # reload projects for selector
                        state.projects = data
                        d.close(); refresh(); ui.notify('已儲存', type='positive')
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    # ---- Search bar ----
    with ui.row().classes('gap-2 items-end flex-wrap'):
        name_in = ui.input('專案名稱').props('dense outlined').classes('min-w-[200px]')
        name_in.value = state.prj_kw

        async def do_query():
            show_loading()
            try:
                state.prj_kw = name_in.value or ''
                state.prj_page = 1
                state.projects = await api.list_projects(keyword=state.prj_kw)
                await api.log_action(f"Searched projects with keyword: {state.prj_kw}")
                refresh()
                ui.notify('查詢完成', type='positive')
            except Exception as e:
                ui.notify(f'查詢失敗: {e}', type='negative')
            finally:
                hide_loading()

        async def do_clear():
            show_loading()
            try:
                state.prj_kw = ''
                name_in.value = ''
                state.prj_page = 1
                state.projects = await api.list_projects() # Fetch all
                refresh()
            finally:
                hide_loading()

        ui.button('查詢', icon='search', on_click=do_query).props('color=primary')
        ui.button('清除搜尋條件', icon='backspace', on_click=do_clear).props('flat')
        ui.button('新增', icon='add', on_click=lambda: open_project_dialog()).props('color=accent')
        ui.space().classes('grow')
        ui.label(f"總數：{len(items)}").classes('muted')

    ui.space().classes('h-2')

    # ---- Filter + Pagination ----
    # The filtering is now done by the backend API.
    # The 'items' variable is now populated by do_query/do_clear into state.projects
    # and initialized at the top of the function.

    page_size = max(1, int(state.prj_page_size or 10))
    total = len(items)
    max_page = max(1, (total + page_size - 1) // page_size)
    state.prj_page = min(max(1, state.prj_page), max_page)
    start = (state.prj_page - 1) * page_size
    page_rows = items[start:start+page_size]

    # Bulk toolbar
    def clear_sel():
        state.prj_selected_ids.clear(); refresh()

    async def bulk_delete():
        ids = set(state.prj_selected_ids)
        if not ids: return
        show_loading()
        try:
            # This is a client-side delete, but for consistency, we'll use the spinner/reload pattern
            new_items = [x for x in items if x.get('id') not in ids]
            write_projects(new_items)
            state.prj_selected_ids.clear()
            state.projects = new_items
            if str(state.active_project_id) in {str(i) for i in ids}:
                if new_items:
                    state.active_project_id = int(new_items[0].get('id', 1))
                    state.active_project_name = new_items[0].get('name', '未選取')
                else:
                    state.active_project_id = 1; state.active_project_name = '未選取'
            await api.log_action(f"Bulk deleted {len(ids)} projects.")
            ui.notify(f'已刪除 {len(ids)} 筆', type='positive')
            ui.navigate.reload()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()

    bulk_toolbar(state.prj_selected_ids, [
        ('刪除選取', 'delete', bulk_delete),
        ('清除選取', 'close', clear_sel),
    ])

    if not page_rows and total == 0:
        empty_state('尚無專案', '點擊右上角「新增」建立第一個專案。', '新增', on_click=lambda: open_project_dialog())
        return

    with ui.element('div').classes('soft-card p-2'):
        with ui.row().classes('text-sm muted items-center py-1'):
            ui.checkbox(on_change=lambda e: (state.prj_selected_ids.update(r.get('id') for r in page_rows) if e.value else state.prj_selected_ids.clear()) or refresh())
            ui.label('編號').classes('w-20')
            ui.label('專案名稱').classes('w-[40%]')
            ui.label('人員').classes('w-40')
            ui.label('專案狀態').classes('w-28')
            ui.label('操作').classes('w-32')

        ui.separator().classes('opacity-20')

        for r in page_rows:
            rid = r.get('id')
            with ui.row().classes('items-center py-1'):
                # 每列開頭的選取框
                def toggle_row(v=None, _rid=rid):
                    if _rid in state.prj_selected_ids:
                        state.prj_selected_ids.remove(_rid)
                    else:
                        state.prj_selected_ids.add(_rid)
                    refresh()
                ui.checkbox(value=(rid in state.prj_selected_ids), on_change=lambda e, rid=rid: toggle_row(e.value, rid))
                # 編號
                ui.label(str(rid)).classes('w-20')
                # 專案名稱
                ui.label(r.get('name','')).classes('w-[40%]')
                # 人員
                ui.label(r.get('owner','')).classes('w-40')
                # 專案狀態，使用 badge 呈現
                with ui.element('div').classes('w-28'):
                    status_badge(r.get('status','新增'), {'新增':'info','進行中':'primary','暫停':'warning','完成':'positive'})
                # 操作列：切換 / 編輯 / 刪除
                with ui.row().classes('w-32 gap-1'):
                    # 切換按鈕：切換為目前使用的專案
                    async def _switch_proj(_rid=rid, _name=r.get('name','')):
                        show_loading()
                        try:
                            state.active_project_id = _rid
                            state.active_project_name = _name or f'專案 {_rid}'
                            # 重新載入各項資料
                            load_scoped_data()
                            await api.log_action(f"Switched to project id={_rid}")
                            ui.notify(f'已切換至專案【{state.active_project_name}】', type='info')
                            # A full reload is better to ensure all components reset
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'切換專案失敗: {e}', type='negative')
                        finally:
                            # Hide loading might not be seen due to reload, but good practice
                            hide_loading()
                    # 使用代表切換的 icon
                    ui.button(icon='swap_horiz', on_click=_switch_proj).props('flat')
                    # 編輯按鈕
                    ui.button(icon='edit', on_click=lambda rid=rid: open_project_dialog(rid)).props('flat')
                    # 刪除按鈕
                    async def del_one(_rid=rid):
                        show_loading()
                        try:
                            new_items = [x for x in items if x.get('id') != _rid]
                            write_projects(new_items)
                            state.projects = new_items
                            # 如果刪除的是目前啟用的專案，則自動切換到第一筆或清空
                            if str(state.active_project_id) == str(_rid):
                                if new_items:
                                    state.active_project_id = int(new_items[0].get('id', 1))
                                    state.active_project_name = new_items[0].get('name', '未選取')
                                else:
                                    state.active_project_id = 1
                                    state.active_project_name = '未選取'
                                load_scoped_data()
                            await api.log_action(f"Deleted project id={_rid}")
                            ui.notify(f'已刪除專案 {_rid}', type='positive')
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'刪除失敗: {e}', type='negative')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=del_one).props('flat')

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.prj_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                def prev_page():
                    if state.prj_page > 1:
                        state.prj_page -= 1; refresh()
                def next_page():
                    if state.prj_page < max_page:
                        state.prj_page += 1; refresh()
                ui.button('上一頁', icon='chevron_left', on_click=prev_page).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=next_page).props('flat')

    # Initial data load
    if not state.projects:
        asyncio.create_task(do_clear())

def render_web_cases(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # Define items at the top to resolve UnboundLocalError in nested functions
    items = state.web_list or []

    # Dialog for adding/editing WEB test cases
    # NOTE: we expose this dialog as ``open_dialog`` so the lambda callbacks
    # defined later in this function can reference it. In previous revisions
    # the function was named ``open_dialog_bug_unused`` which caused a
    # NameError when referenced. Renaming to ``open_dialog`` keeps the
    # functionality identical but makes the name available to the outer scope.
    def open_dialog(edit_id: int | None = None):
        """打開新增/編輯 WEB 案例的對話框，會顯示不可編輯的編號欄位。"""
        editing = None
        if edit_id is not None:
            # 尋找現有項目
            for p in state.web_list or []:
                if str(p.get('id')) == str(edit_id):
                    editing = p
                    break
        # 預先計算下一個編號供顯示
        current_list = state.web_list or []
        next_id = max([int(p.get('id', 0)) for p in current_list] + [0]) + 1
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[560px]'):
                ui.label('新增測試案例' if not editing else '修改測試案例').classes('text-lg font-semibold')
                cols = ui.grid(columns=2).classes('gap-2 mt-2')
                with cols:
                    # 編號欄位只供顯示，無法編輯
                    id_input = ui.input('編號(自動帶入)').props('outlined dense disabled')
                    # 其餘輸入欄位
                    feature = ui.input('測試功能').props('outlined dense')
                    step = ui.input('測試步驟').props('outlined dense')
                    action = ui.select(['前往網址','填入','點擊','等待','檢查','選擇','檔案上傳'], label='動作').props('outlined dense')
                    desc = ui.input('敘述').props('outlined dense')
                    page_ = ui.input('頁面').props('outlined dense')
                    elem = ui.input('元件').props('outlined dense')
                    val = ui.input('輸入值').props('outlined dense')
                    # 移除測試結果與備註欄位，僅保留必要欄位
                # 若為編輯模式，填入現有值；否則顯示新 ID
                if editing:
                    id_input.value = str(editing.get('id', ''))
                    feature.value = editing.get('feature', '')
                    step.value = editing.get('step', '')
                    action.value = editing.get('action', '')
                    desc.value = editing.get('desc', '')
                    page_.value = editing.get('page', '')
                    elem.value = editing.get('element', '')
                    val.value = editing.get('value', '')
                    # no result/note fields to set
                else:
                    id_input.value = str(next_id)
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        show_loading()
                        try:
                            action_desc = "created new web case"
                            if editing:
                                action_desc = f"updated web case id={editing.get('id')}"

                            data = state.web_list or []
                            if editing:
                                # 更新現有資料
                                for i, p in enumerate(data):
                                    if str(p.get('id')) == str(editing.get('id')):
                                        data[i] = {**p,
                                                   'feature': feature.value or '',
                                                   'step': step.value or '',
                                                   'action': action.value or '',
                                                   'desc': desc.value or '',
                                                   'page': page_.value or '',
                                                   'element': elem.value or '',
                                                   'value': val.value or ''}
                                        break
                            else:
                                # 新增
                                new_id = next_id
                                data.append({
                                    'id': new_id,
                                    'feature': feature.value or '',
                                    'step': step.value or '',
                                    'action': action.value or '',
                                    'desc': desc.value or '',
                                    'page': page_.value or '',
                                    'element': elem.value or '',
                                    'value': val.value or '',
                                    'review': '未審核'
                                })
                            save_items(data)
                            await api.log_action(action_desc)
                            ui.notify('儲存成功！', type='positive')
                            d.close()
                            # Automatically refresh the page
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    # Search & actions
    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字').props('dense outlined').classes('min-w-[260px]')
        kw_in.value = state.web_kw

        async def do_query():
            show_loading()
            try:
                state.web_kw = kw_in.value or ''
                state.web_page = 1
                result = await api.list_web_cases(state.active_project_id, keyword=state.web_kw)
                state.web_list = result.get('items', [])
                await api.log_action(f"Searched web cases with keyword: {state.web_kw}")
                refresh()
                ui.notify('查詢完成', type='positive')
            except Exception as e:
                ui.notify(f'查詢失敗: {e}', type='negative')
            finally:
                hide_loading()

        async def do_clear():
            show_loading()
            try:
                state.web_kw = ''
                kw_in.value = ''
                state.web_page = 1
                result = await api.list_web_cases(state.active_project_id)
                state.web_list = result.get('items', [])
                refresh()
            finally:
                hide_loading()

        ui.button('查詢', icon='search', on_click=do_query).props('color=primary')
        ui.button('清除搜尋條件', icon='backspace', on_click=do_clear).props('flat')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')

    # The filtering is now done by the backend API.
    # We use the 'items' variable consistently, which is defined at the top of the function.
    page_size = 10
    total = len(items)
    max_page = max(1, (total+page_size-1)//page_size)
    state.web_page = min(max(1,state.web_page), max_page)
    start = (state.web_page-1)*page_size
    page_rows = items[start:start+page_size]

    def refresh():
        try:
            main_area.refresh()
        except Exception:
            pass

    def save_items(new_items):
        write_scoped_list(WEB_CASES_FILE, state.active_project_id, new_items)
        state.web_list = new_items
        state.tc_list = new_items  # keep legacy
        refresh()

    # Bulk toolbar
    def clear_sel():
        state.web_selected_ids.clear(); refresh()
    async def bulk_delete():
        ids = set(state.web_selected_ids)
        if not ids: return
        show_loading()
        try:
            new_items = [x for x in items if x.get('id') not in ids]
            save_items(new_items)
            await api.log_action(f"Bulk deleted {len(ids)} web cases.")
            ui.notify(f'已刪除 {len(ids)} 筆', type='positive')
            ui.navigate.reload()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()
    bulk_toolbar(state.web_selected_ids, [('刪除選取','delete', bulk_delete), ('清除選取','close', clear_sel)])

    # Empty state
    if not page_rows and total==0:
        empty_state('尚無 WEB 測試案例', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
        return

    # Table
    with ui.element('div').classes('soft-card p-2'):
        with ui.row().classes('text-sm muted items-center py-1'):
            ui.checkbox(on_change=lambda e: (state.web_selected_ids.update(r.get('id') for r in page_rows) if e.value else state.web_selected_ids.clear()) or refresh())
            # remove 測試結果 and 備註 columns, add 審核狀態
            for h, w in [('編號','w-16'), ('測試功能','w-32'), ('測試步驟','w-20'), ('動作','w-28'),
                         ('敘述','w-[20%]'), ('頁面','w-28'), ('元件','w-28'), ('輸入值','w-32'), ('審核','w-24'), ('操作','w-28')]:
                ui.label(h).classes(w)
        ui.separator().classes('opacity-20')

        for r in page_rows:
            rid = r.get('id')
            with ui.row().classes('items-center py-1'):
                def toggle_row(v=None, _rid=rid):
                    if _rid in state.web_selected_ids: state.web_selected_ids.remove(_rid)
                    else: state.web_selected_ids.add(_rid); refresh()
                ui.checkbox(value=(rid in state.web_selected_ids), on_change=lambda e, rid=rid: toggle_row(e.value, rid))
                ui.label(str(r.get('id'))).classes('w-16')
                ui.label(r.get('feature','')).classes('w-32')
                ui.label(r.get('step','')).classes('w-20')
                ui.label(r.get('action','')).classes('w-28')
                ui.label(r.get('desc','')).classes('w-[20%]')
                ui.label(r.get('page','')).classes('w-28')
                ui.label(r.get('element','')).classes('w-28')
                ui.label(r.get('value','')).classes('w-32')
                # 審核狀態下拉選單，預設未審核/已審核
                is_reviewed = r.get('review') == '已審核'
                async def on_status_change(e, record=r):
                    show_loading()
                    try:
                        record.update({'review': e.value})
                        write_scoped_list(WEB_CASES_FILE, state.active_project_id, state.web_list)
                        setattr(state, 'web_list', state.web_list)
                        await api.log_action(f"Updated web case id={record.get('id')} status to {e.value}")
                        ui.notify('已更新審核狀態', type='positive')
                        ui.navigate.reload()
                    except Exception as ex:
                        ui.notify(f'更新失敗: {ex}', type='negative')
                    finally:
                        hide_loading()
                s = ui.select(['未審核','已審核'], value=r.get('review','未審核'), on_change=on_status_change).props('dense').classes('w-24')
                if is_reviewed:
                    s.props('readonly disable')
                with ui.row().classes('w-28 gap-1'):
                    ui.button(icon='edit', on_click=lambda rid=rid: open_dialog(rid)).props('flat')
                    async def del_one(case_id=rid):
                        show_loading()
                        try:
                            save_items([x for x in items if x.get('id') != case_id])
                            await api.log_action(f"Deleted web case id={case_id}")
                            ui.notify(f'已刪除案例 {case_id}', type='positive')
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'刪除失敗: {e}', type='negative')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=del_one).props('flat')

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.web_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state,'web_page', max(1,state.web_page-1)), refresh())).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state,'web_page', min(max_page, state.web_page+1)), refresh())).props('flat')

    # Initial data load
    if state.web_list is None:
        asyncio.create_task(do_clear())



def render_app_cases(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # Define items at the top to resolve UnboundLocalError in nested functions
    items = state.app_list or []

    # Dialog for adding/editing APP test cases
    def open_dialog(edit_id: int | None = None):
        """打開新增/編輯 APP 測試案例的對話框，顯示不可編輯的編號欄位"""
        editing = None
        if edit_id is not None:
            for p in state.app_list or []:
                if str(p.get('id')) == str(edit_id):
                    editing = p
                    break
        current_list = state.app_list or []
        next_id = max([int(p.get('id', 0)) for p in current_list] + [0]) + 1
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[560px]'):
                ui.label('新增測試案例' if not editing else '修改測試案例').classes('text-lg font-semibold')
                cols = ui.grid(columns=2).classes('gap-2 mt-2')
                with cols:
                    id_input = ui.input('編號(自動帶入)').props('outlined dense disabled')
                    feature = ui.input('測試功能').props('outlined dense')
                    step = ui.input('測試步驟').props('outlined dense')
                    action = ui.select(['前往網址','填入','點擊','等待','檢查','選擇','檔案上傳'], label='動作').props('outlined dense')
                    desc = ui.input('敘述').props('outlined dense')
                    page_ = ui.input('頁面').props('outlined dense')
                    elem = ui.input('元件').props('outlined dense')
                    val = ui.input('輸入值').props('outlined dense')
                # 填入編輯值或新 ID
                if editing:
                    id_input.value = str(editing.get('id', ''))
                    feature.value = editing.get('feature', '')
                    step.value = editing.get('step', '')
                    action.value = editing.get('action', '')
                    desc.value = editing.get('desc', '')
                    page_.value = editing.get('page', '')
                    elem.value = editing.get('element', '')
                    val.value = editing.get('value', '')
                else:
                    id_input.value = str(next_id)
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        show_loading()
                        try:
                            action_desc = "created new app case"
                            if editing:
                                action_desc = f"updated app case id={editing.get('id')}"

                            data = state.app_list or []
                            if editing:
                                for i, p in enumerate(data):
                                    if str(p.get('id')) == str(editing.get('id')):
                                        data[i] = {**p,
                                                   'feature': feature.value or '',
                                                   'step': step.value or '',
                                                   'action': action.value or '',
                                                   'desc': desc.value or '',
                                                   'page': page_.value or '',
                                                   'element': elem.value or '',
                                                   'value': val.value or ''}
                                        break
                            else:
                                new_id = next_id
                                data.append({
                                    'id': new_id,
                                    'feature': feature.value or '',
                                    'step': step.value or '',
                                    'action': action.value or '',
                                    'desc': desc.value or '',
                                    'page': page_.value or '',
                                    'element': elem.value or '',
                                    'value': val.value or '',
                                    'review': '未審核'
                                })
                            write_scoped_list(APP_CASES_FILE, state.active_project_id, data)
                            state.app_list = data
                            await api.log_action(action_desc)
                            ui.notify('儲存成功！', type='positive')
                            d.close()
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    # Search & actions
    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字').props('dense outlined').classes('min-w-[260px]')
        kw_in.value = state.app_kw

        async def do_query():
            show_loading()
            try:
                state.app_kw = kw_in.value or ''
                state.app_page = 1
                result = await api.list_app_cases(state.active_project_id, keyword=state.app_kw)
                state.app_list = result.get('items', [])
                await api.log_action(f"Searched app cases with keyword: {state.app_kw}")
                refresh()
                ui.notify('查詢完成', type='positive')
            except Exception as e:
                ui.notify(f'查詢失敗: {e}', type='negative')
            finally:
                hide_loading()

        async def do_clear():
            show_loading()
            try:
                state.app_kw = ''
                kw_in.value = ''
                state.app_page = 1
                result = await api.list_app_cases(state.active_project_id)
                state.app_list = result.get('items', [])
                refresh()
            finally:
                hide_loading()

        ui.button('查詢', icon='search', on_click=do_query).props('color=primary')
        ui.button('清除搜尋條件', icon='backspace', on_click=do_clear).props('flat')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')
        ui.button('輸入設備資訊', icon='smartphone', on_click=lambda: open_device()).props('flat')

    # The filtering is now done by the backend API.
    # We use the 'items' variable consistently, which is defined at the top of the function.
    page_size = 10
    total = len(items)
    max_page = max(1, (total+page_size-1)//page_size)
    state.app_page = min(max(1,state.app_page), max_page)
    start = (state.app_page-1)*page_size
    page_rows = items[start:start+page_size]

    def refresh():
        try:
            main_area.refresh()
        except Exception:
            pass

    def save_items(new_items):
        write_scoped_list(APP_CASES_FILE, state.active_project_id, new_items)
        state.app_list = new_items; refresh()

    # Device info dialog
    def open_device():
        current = (read_scoped_list(APP_DEVICE_FILE, state.active_project_id) or [''])[0] if isinstance(read_scoped_list(APP_DEVICE_FILE, state.active_project_id), list) else ''
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[560px]'):
                ui.label('設備資訊').classes('text-lg font-semibold')
                ta = ui.textarea('貼上或輸入設備資訊').props('outlined').classes('w-[520px] h-[200px]')
                ta.value = current or ''
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save_dev():
                        show_loading()
                        try:
                            write_scoped_list(APP_DEVICE_FILE, state.active_project_id, [ta.value or ''])
                            await api.log_action(f"Saved device info for project {state.active_project_id}")
                            d.close()
                            ui.notify('已儲存設備資訊', type='positive')
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'儲存失敗: {e}', type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', on_click=save_dev, color='primary')
        d.open()

    # Bulk toolbar
    def clear_sel():
        state.app_selected_ids.clear(); refresh()
    async def bulk_delete():
        ids = set(state.app_selected_ids)
        if not ids: return
        show_loading()
        try:
            new_items = [x for x in items if x.get('id') not in ids]
            save_items(new_items)
            await api.log_action(f"Bulk deleted {len(ids)} app cases.")
            ui.notify(f'已刪除 {len(ids)} 筆', type='positive')
            ui.navigate.reload()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()
    bulk_toolbar(state.app_selected_ids, [('刪除選取','delete', bulk_delete), ('清除選取','close', clear_sel)])

    if not page_rows and total==0:
        empty_state('尚無 APP 測試案例', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
        return

    with ui.element('div').classes('soft-card p-2'):
        with ui.row().classes('text-sm muted items-center py-1'):
            ui.checkbox(on_change=lambda e: (state.app_selected_ids.update(r.get('id') for r in page_rows) if e.value else state.app_selected_ids.clear()) or refresh())
            for h, w in [
                ('編號','w-16'), ('測試功能','w-32'), ('測試步驟','w-20'), ('動作','w-28'),
                ('敘述','w-[20%]'), ('頁面','w-28'), ('元件','w-28'), ('輸入值','w-32'),
                ('審核','w-24'), ('操作','w-28')
            ]:
                ui.label(h).classes(w)
        ui.separator().classes('opacity-20')

        for r in page_rows:
            rid = r.get('id')
            with ui.row().classes('items-center py-1'):
                def toggle_row(v=None, _rid=rid):
                    if _rid in state.app_selected_ids: state.app_selected_ids.remove(_rid)
                    else: state.app_selected_ids.add(_rid); refresh()
                ui.checkbox(value=(rid in state.app_selected_ids), on_change=lambda e, rid=rid: toggle_row(e.value, rid))
                ui.label(str(r.get('id'))).classes('w-16')
                ui.label(r.get('feature','')).classes('w-32')
                ui.label(r.get('step','')).classes('w-20')
                ui.label(r.get('action','')).classes('w-28')
                ui.label(r.get('desc','')).classes('w-[20%]')
                ui.label(r.get('page','')).classes('w-28')
                ui.label(r.get('element','')).classes('w-28')
                ui.label(r.get('value','')).classes('w-32')
                # 審核狀態下拉選單
                is_reviewed = r.get('review') == '已審核'
                async def on_status_change(e, record=r):
                    show_loading()
                    try:
                        record.update({'review': e.value})
                        write_scoped_list(APP_CASES_FILE, state.active_project_id, state.app_list)
                        setattr(state, 'app_list', state.app_list)
                        await api.log_action(f"Updated app case id={record.get('id')} status to {e.value}")
                        ui.notify('已更新審核狀態', type='positive')
                        ui.navigate.reload()
                    except Exception as ex:
                        ui.notify(f'更新失敗: {ex}', type='negative')
                    finally:
                        hide_loading()
                s = ui.select(['未審核','已審核'], value=r.get('review','未審核'), on_change=on_status_change).props('dense').classes('w-24')
                if is_reviewed:
                    s.props('readonly disable')
                with ui.row().classes('w-28 gap-1'):
                    ui.button(icon='edit', on_click=lambda rid=rid: open_dialog(rid)).props('flat')
                    async def _del_one(_rid=rid):
                        show_loading()
                        try:
                            save_items([x for x in items if x.get('id') != _rid])
                            await api.log_action(f"Deleted app case id={_rid}")
                            ui.notify('已刪除 1 筆', type='positive')
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'刪除失敗: {e}', type='negative')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=_del_one).props('flat')

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.app_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state,'app_page', max(1,state.app_page-1)), refresh())).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state,'app_page', min(max_page, state.app_page+1)), refresh())).props('flat')

    # Initial data load
    if state.app_list is None:
        asyncio.create_task(do_clear())


def render_api_cases(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # Define items at the top to resolve UnboundLocalError in nested functions
    items = state.api_list or []

    # Dialog for adding/editing API test cases
    def open_dialog(edit_step: int | None = None):
        """打開新增/編輯 API 測試案例的對話框。"""
        editing = None
        if edit_step is not None:
            for p in state.api_list or []:
                if str(p.get('step')) == str(edit_step):
                    editing = p
                    break
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[760px]'):
                ui.label('新增 API 測試案例' if not editing else '修改 API 測試案例').classes('text-lg font-semibold')
                cols = ui.grid(columns=2).classes('gap-2 mt-2')
                with cols:
                    step = ui.input('步驟').props('outlined dense')
                    feature = ui.input('測試功能').props('outlined dense')
                    method = ui.select(['POST','GET','PUT','PATCH','DELETE'], label='方法').props('outlined dense')
                    url = ui.input('URL').props('outlined dense')
                    api_path = ui.input('API路徑').props('outlined dense')
                    header = ui.textarea('Header').props('outlined dense')
                    body = ui.textarea('請求Body').props('outlined dense')
                    expect_status = ui.input('預期狀態碼').props('outlined dense')
                    expect_field = ui.input('預期欄位').props('outlined dense')
                    expect_value = ui.input('預期值').props('outlined dense')
                    # 移除測試結果與備註欄位
                    response_summary = ui.textarea('回應摘要').props('outlined dense')
                # 填入編輯值
                if editing:
                    step.value = str(editing.get('step',''))
                    feature.value = editing.get('feature','')
                    method.value = editing.get('method','')
                    url.value = editing.get('url','')
                    api_path.value = editing.get('api_path','')
                    header.value = editing.get('header','')
                    body.value = editing.get('body','')
                    expect_status.value = str(editing.get('expect_status',''))
                    expect_field.value = editing.get('expect_field','')
                    expect_value.value = editing.get('expect_value','')
                    response_summary.value = editing.get('response_summary','')
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        show_loading()
                        try:
                            action_desc = "created new api case"
                            if editing:
                                action_desc = f"updated api case step={editing.get('step')}"

                            data = state.api_list or []
                            # construct record
                            rec = {
                                'step': int(step.value or 0) if (step.value or '').isdigit() else step.value or 0,
                                'feature': feature.value or '',
                                'method': method.value or '',
                                'url': url.value or '',
                                'api_path': api_path.value or '',
                                'header': header.value or '',
                                'body': body.value or '',
                                'expect_status': int(expect_status.value or 0) if (expect_status.value or '').isdigit() else expect_status.value or '',
                                'expect_field': expect_field.value or '',
                                'expect_value': expect_value.value or '',
                                'response_summary': response_summary.value or '',
                                # 新增審核欄位，預設未審核
                                'review': editing.get('review','未審核') if editing else '未審核'
                            }
                            if editing:
                                for i,p in enumerate(data):
                                    if str(p.get('step')) == str(editing.get('step')):
                                        data[i] = rec
                                        break
                            else:
                                data.append(rec)
                            write_scoped_list(API_CASES_FILE, state.active_project_id, data)
                            state.api_list = data
                            await api.log_action(action_desc)
                            ui.notify('儲存成功！', type='positive')
                            d.close()
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字').props('dense outlined').classes('min-w-[320px]')
        kw_in.value = state.api_kw

        async def do_query():
            show_loading()
            try:
                state.api_kw = kw_in.value or ''
                state.api_page = 1
                result = await api.list_api_cases(state.active_project_id, keyword=state.api_kw)
                state.api_list = result.get('items', [])
                await api.log_action(f"Searched API cases with keyword: {state.api_kw}")
                refresh()
                ui.notify('查詢完成', type='positive')
            except Exception as e:
                ui.notify(f'查詢失敗: {e}', type='negative')
            finally:
                hide_loading()

        async def do_clear():
            show_loading()
            try:
                state.api_kw = ''
                kw_in.value = ''
                state.api_page = 1
                result = await api.list_api_cases(state.active_project_id)
                state.api_list = result.get('items', [])
                refresh()
            finally:
                hide_loading()

        ui.button('查詢', icon='search', on_click=do_query).props('color=primary')
        ui.button('清除搜尋條件', icon='backspace', on_click=do_clear).props('flat')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')

    # The filtering is now done by the backend API.
    # We use the 'items' variable consistently, which is defined at the top of the function.
    page_size = 10
    total = len(items)
    max_page = max(1, (total+page_size-1)//page_size)
    state.api_page = min(max(1,state.api_page), max_page)
    start = (state.api_page-1)*page_size
    page_rows = items[start:start+page_size]

    def refresh():
        try:
            main_area.refresh()
        except Exception:
            pass

    def save_items(new_items):
        write_scoped_list(API_CASES_FILE, state.active_project_id, new_items)
        state.api_list = new_items; refresh()

    def clear_sel():
        state.api_selected_ids.clear(); refresh()
    async def bulk_delete():
        ids = set(state.api_selected_ids)
        if not ids: return
        show_loading()
        try:
            save_items([x for x in items if x.get('step') not in ids])
            await api.log_action(f"Bulk deleted {len(ids)} API cases.")
            ui.notify(f'已刪除 {len(ids)} 筆', type='positive')
            ui.navigate.reload()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()
    bulk_toolbar(state.api_selected_ids, [('刪除選取','delete', bulk_delete), ('清除選取','close', clear_sel)])

    if not page_rows and total==0:
        empty_state('尚無 API 測試案例', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
        return

    with ui.element('div').classes('soft-card p-2'):
        with ui.row().classes('text-sm muted items-center py-1'):
            ui.checkbox(on_change=lambda e: (state.api_selected_ids.update(r.get('step') for r in page_rows) if e.value else state.api_selected_ids.clear()) or refresh())
            for h, w in [
                ('步驟','w-16'), ('測試功能','w-32'), ('方法','w-20'), ('URL','w-[20%]'), ('API路徑','w-32'),
                ('Header','w-32'), ('請求Body','w-32'), ('預期狀態碼','w-24'), ('預期欄位','w-28'), ('預期值','w-24'),
                ('回應摘要','w-32'), ('審核','w-24'), ('操作','w-28')
            ]:
                ui.label(h).classes(w)
        ui.separator().classes('opacity-20')

        for r in page_rows:
            sid = r.get('step')
            with ui.row().classes('items-center py-1'):
                def toggle_row(v=None, _sid=sid):
                    if _sid in state.api_selected_ids: state.api_selected_ids.remove(_sid)
                    else: state.api_selected_ids.add(_sid); refresh()
                ui.checkbox(value=(sid in state.api_selected_ids), on_change=lambda e, sid=sid: toggle_row(e.value, sid))
                ui.label(str(r.get('step'))).classes('w-16')
                ui.label(r.get('feature','')).classes('w-32')
                ui.label(r.get('method','')).classes('w-20')
                ui.label(r.get('url','')).classes('w-[20%]')
                ui.label(r.get('api_path','')).classes('w-32')
                ui.label(r.get('header','')).classes('w-32')
                ui.label(r.get('body','')).classes('w-32')
                ui.label(str(r.get('expect_status',''))).classes('w-24')
                ui.label(r.get('expect_field','')).classes('w-28')
                ui.label(r.get('expect_value','')).classes('w-24')
                ui.label(r.get('response_summary','')).classes('w-32')
                # 審核狀態下拉選單，未審核/已審核
                is_reviewed = r.get('review') == '已審核'
                async def on_status_change(e, record=r):
                    show_loading()
                    try:
                        record.update({'review': e.value})
                        write_scoped_list(API_CASES_FILE, state.active_project_id, state.api_list)
                        setattr(state, 'api_list', state.api_list)
                        await api.log_action(f"Updated API case step={record.get('step')} status to {e.value}")
                        ui.notify('已更新審核狀態', type='positive')
                        ui.navigate.reload()
                    except Exception as ex:
                        ui.notify(f'更新失敗: {ex}', type='negative')
                    finally:
                        hide_loading()
                s = ui.select(['未審核','已審核'], value=r.get('review','未審核'), on_change=on_status_change).props('dense').classes('w-24')
                if is_reviewed:
                    s.props('readonly disable')
                with ui.row().classes('w-28 gap-1'):
                    ui.button(icon='edit', on_click=lambda sid=sid: open_dialog(sid)).props('flat')
                    async def _del_one(_sid=sid):
                        show_loading()
                        try:
                            save_items([x for x in items if x.get('step') != _sid])
                            await api.log_action(f"Deleted API case step={_sid}")
                            ui.notify('已刪除 1 筆', type='positive')
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'刪除失敗: {e}', type='negative')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=_del_one).props('flat')

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.api_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state,'api_page', max(1,state.api_page-1)), refresh())).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state,'api_page', min(max_page, state.api_page+1)), refresh())).props('flat')

    # Initial data load
    if state.api_list is None:
        asyncio.create_task(do_clear())



def render_bugs(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # Define items at the top to resolve UnboundLocalError in nested functions
    items = state.bug_list or []

    # Dialog for adding/editing BUG
    def open_dialog(edit_id: int | None = None):
        editing = None
        if edit_id is not None:
            for p in state.bug_list or []:
                if str(p.get('id')) == str(edit_id):
                    editing = p
                    break
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[760px]'):
                ui.label('新增 BUG' if not editing else '修改 BUG').classes('text-lg font-semibold')
                cols = ui.grid(columns=2).classes('gap-2 mt-2')
                with cols:
                    title = ui.input('問題敘述').props('outlined dense')
                    severity = ui.select(['高','中','低'], label='嚴重度').props('outlined dense')
                    status = ui.select(['新增','進行中','關閉','駁回'], label='狀態').props('outlined dense')
                    repro = ui.textarea('重現步驟').props('outlined dense')
                    expected = ui.textarea('預期結果').props('outlined dense')
                    actual = ui.textarea('實際結果').props('outlined dense')
                    note = ui.input('備註').props('outlined dense')
                    upload_name = ui.label('').classes('muted')
                    def on_upload(e):
                        # Save uploaded files to UPLOADS_DIR and update label
                        for f in e.files:
                            name = f.name
                            (UPLOADS_DIR / name).write_bytes(f.content.read())
                            upload_name.text = name
                            ui.notify('已上傳', type='positive')
                    ui.upload(on_upload=on_upload, auto_upload=True).props('accept="image/*"')
                if editing:
                    title.value = editing.get('title','')
                    severity.value = editing.get('severity','中')
                    status.value = editing.get('status','新增')
                    repro.value = editing.get('repro','')
                    expected.value = editing.get('expected','')
                    actual.value = editing.get('actual','')
                    note.value = editing.get('note','')
                    upload_name.text = editing.get('screenshot','') or ''
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    def save():
                        data = state.bug_list or []
                        # Determine id
                        rec_id = editing.get('id') if editing else (max([int(p.get('id',0)) for p in data] + [0]) + 1)
                        rec = {
                            'id': rec_id,
                            'title': title.value or '',
                            'severity': severity.value or '中',
                            'status': status.value or '新增',
                            'repro': repro.value or '',
                            'expected': expected.value or '',
                            'actual': actual.value or '',
                            'note': note.value or '',
                            'screenshot': upload_name.text or ''
                        }
                        if editing:
                            for i, p in enumerate(data):
                                if str(p.get('id')) == str(editing.get('id')):
                                    data[i] = rec
                                    break
                        else:
                            data.append(rec)
                        write_scoped_list(BUGS_FILE, state.active_project_id, data)
                        state.bug_list = data
                        d.close()
                        ui.notify('已儲存', type='positive')
                        try:
                            main_area.refresh()
                        except Exception:
                            pass
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    # Filters
    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字（問題敘述/重現步驟/預期/實際/備註）').props('dense outlined').classes('min-w-[320px]')
        kw_in.value = state.bug_filter_kw

        async def do_query():
            show_loading()
            try:
                state.bug_filter_kw = kw_in.value or ''
                state.bug_page = 1
                state.bug_list = await api.list_project_bugs(state.active_project_id, keyword=state.bug_filter_kw)
                await api.log_action(f"Searched bugs with keyword: {state.bug_filter_kw}")
                refresh()
                ui.notify('查詢完成', type='positive')
            except Exception as e:
                ui.notify(f'查詢失敗: {e}', type='negative')
            finally:
                hide_loading()

        async def do_clear():
            show_loading()
            try:
                state.bug_filter_kw = ''
                kw_in.value = ''
                state.bug_page = 1
                state.bug_list = await api.list_project_bugs(state.active_project_id)
                refresh()
            finally:
                hide_loading()

        ui.button('查詢', icon='search', on_click=do_query).props('color=primary')
        ui.button('清除搜尋條件', icon='backspace', on_click=do_clear).props('flat')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')

    # The filtering is now done by the backend API.
    # We use the 'items' variable consistently, which is defined at the top of the function.
    page_size = 10
    total = len(items)
    max_page = max(1, (total+page_size-1)//page_size)
    state.bug_page = min(max(1,state.bug_page), max_page)
    start = (state.bug_page-1)*page_size
    page_rows = items[start:start+page_size]

    def refresh():
        try: main_area.refresh()
        except Exception: pass

    def save_items(new_items):
        write_scoped_list(BUGS_FILE, state.active_project_id, new_items)
        state.bug_list = new_items; refresh()

    def clear_sel():
        state.bug_selected_ids.clear(); refresh()
    async def bulk_delete():
        ids = set(state.bug_selected_ids)
        if not ids: return
        show_loading()
        try:
            save_items([x for x in items if x.get('id') not in ids])
            await api.log_action(f"Bulk deleted {len(ids)} bugs.")
            ui.notify(f'已刪除 {len(ids)} 筆', type='positive')
            ui.navigate.reload()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()
    bulk_toolbar(state.bug_selected_ids, [('刪除選取','delete', bulk_delete), ('清除選取','close', clear_sel)])

    if not page_rows and total==0:
        empty_state('尚無 BUG', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
        return

    with ui.element('div').classes('soft-card p-2'):
        with ui.row().classes('text-sm muted items-center py-1'):
            ui.checkbox(on_change=lambda e: (state.bug_selected_ids.update(r.get('id') for r in page_rows) if e.value else state.bug_selected_ids.clear()) or refresh())
            for h, w in [('問題敘述','w-[22%]'), ('嚴重度','w-20'), ('狀態','w-24'), ('重現步驟','w-[20%]'),
                         ('預期結果','w-[18%]'), ('實際結果','w-[18%]'), ('備註','w-[16%]'), ('截圖','w-28'), ('操作','w-28')]:
                ui.label(h).classes(w)
        ui.separator().classes('opacity-20')

        for r in page_rows:
            rid = r.get('id')
            with ui.row().classes('items-center py-1'):
                def toggle_row(v=None, _rid=rid):
                    if _rid in state.bug_selected_ids: state.bug_selected_ids.remove(_rid)
                    else: state.bug_selected_ids.add(_rid); refresh()
                ui.checkbox(value=(rid in state.bug_selected_ids), on_change=lambda e, rid=rid: toggle_row(e.value, rid))
                ui.label(r.get('title','')).classes('w-[22%]')
                with ui.element('div').classes('w-20'):
                    status_badge(r.get('severity',''), CASE_STATUS_COLORS)
                # 狀態欄改為下拉選單，可即時更新
                is_reviewed = r.get('status') == '已審核'
                options = ['新增','進行中','關閉','駁回', '已審核']
                async def on_status_change(e, record=r):
                    show_loading()
                    try:
                        record.update({'status': e.value})
                        write_scoped_list(BUGS_FILE, state.active_project_id, state.bug_list)
                        setattr(state, 'bug_list', state.bug_list)
                        await api.log_action(f"Updated bug id={record.get('id')} status to {e.value}")
                        ui.notify('已更新狀態', type='positive')
                        ui.navigate.reload()
                    except Exception as ex:
                        ui.notify(f'更新失敗: {ex}', type='negative')
                    finally:
                        hide_loading()
                s = ui.select(options, value=r.get('status','新增'), on_change=on_status_change).props('dense').classes('w-24')
                if is_reviewed:
                    s.props('readonly disable')
                ui.label(r.get('repro','')).classes('w-[20%]')
                ui.label(r.get('expected','')).classes('w-[18%]')
                ui.label(r.get('actual','')).classes('w-[18%]')
                ui.label(r.get('note','')).classes('w-[16%]')
                img = r.get('screenshot')
                with ui.row().classes('w-28'):
                    if img:
                        ui.link('查看', f"/uploads/{img}")
                with ui.row().classes('w-28 gap-1'):
                    ui.button(icon='edit', on_click=lambda rid=rid: open_dialog(rid)).props('flat')
                    async def del_one(bug_id=rid):
                        show_loading()
                        try:
                            save_items([x for x in items if x.get('id') != bug_id])
                            await api.log_action(f"Deleted bug id={bug_id}")
                            ui.notify(f'已刪除 BUG {bug_id}', type='positive')
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f'刪除失敗: {e}', type='negative')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=del_one).props('flat')

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.bug_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state,'bug_page', max(1,state.bug_page-1)), refresh())).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state,'bug_page', min(max_page, state.bug_page+1)), refresh())).props('flat')

    # Initial data load
    if state.bug_list is None:
        asyncio.create_task(do_clear())

    def open_dialog(edit_id: int | None = None):
        editing = None
        if edit_id is not None:
            for p in state.bug_list or []:
                if str(p.get('id'))==str(edit_id): editing = p; break
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[760px]'):
                ui.label('新增 BUG' if not editing else '修改 BUG').classes('text-lg font-semibold')
                cols = ui.grid(columns=2).classes('gap-2 mt-2')
                with cols:
                    title = ui.input('問題敘述').props('outlined dense')
                    severity = ui.select(['高','中','低'], label='嚴重度').props('outlined dense')
                    status = ui.select(['新增','進行中','關閉','駁回'], label='狀態').props('outlined dense')
                    repro = ui.textarea('重現步驟').props('outlined dense')
                    expected = ui.textarea('預期結果').props('outlined dense')
                    actual = ui.textarea('實際結果').props('outlined dense')
                    note = ui.input('備註').props('outlined dense')
                    upload_name = ui.label('').classes('muted')
                    def on_upload(e):
                        # Save uploaded file to UPLOADS_DIR and set name
                        for f in e.files:
                            name = f.name
                            # Save bytes
                            (UPLOADS_DIR / name).write_bytes(f.content.read())
                            upload_name.text = name
                            ui.notify('已上傳', type='positive')
                    ui.upload(on_upload=on_upload, auto_upload=True).props('accept=\"image/*\"')
                if editing:
                    title.value = editing.get('title',''); severity.value = editing.get('severity','中'); status.value = editing.get('status','新增')
                    repro.value = editing.get('repro',''); expected.value = editing.get('expected',''); actual.value = editing.get('actual',''); note.value = editing.get('note','')
                    upload_name.text = editing.get('screenshot','') or ''
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        show_loading()
                        try:
                            action_desc = "created new bug"
                            if editing:
                                action_desc = f"updated bug id={editing.get('id')}"

                            data = state.bug_list or []
                            rec = {'id': (editing.get('id') if editing else (max([int(p.get('id',0)) for p in data] + [0]) + 1)),
                                   'title': title.value or '', 'severity': severity.value or '中', 'status': status.value or '新增',
                                   'repro': repro.value or '', 'expected': expected.value or '', 'actual': actual.value or '',
                                   'note': note.value or '', 'screenshot': upload_name.text or ''}
                            if editing:
                                for i,p in enumerate(data):
                                    if str(p.get('id'))==str(editing.get('id')): data[i] = rec; break
                            else:
                                data.append(rec)

                            save_items(data)
                            await api.log_action(action_desc)
                            ui.notify('儲存成功！', type='positive')
                            d.close()
                            ui.navigate.reload()
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()


# === Pages ===
@ui.page('/')
def _page_index():
    try:
        setup_theme()
    except Exception:
        pass
    return ui.navigate.to('/home')


@ui.page('/projects')
def _page_projects():
    # Ensure styles are applied
    try:
        setup_theme()
    except Exception:
        pass
    # Build a simple shell and render content
    with ui.column().classes('w-full p-4'):
        ui.label('專案管理').classes('text-h5 mb-2')
        global main_area
        with ui.element('div').classes('w-full') as main_area:
            render_projects(main_area)

@ui.page('/bugs')
def _page_bugs():
    try:
        setup_theme()
    except Exception:
        pass
    with ui.column().classes('w-full p-4'):
        ui.label('BUG 管理').classes('text-h5 mb-2')
        global main_area
        with ui.element('div').classes('w-full') as main_area:
            render_bugs(main_area)

def render_reports(main_area):
    """
    Render the reports page. This page lists all available Allure reports and
    allows the user to open each report in a dialog. Reports are generated via
    the backend's /allure/list endpoint.
    """
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()
    reports_list = ui.column().classes('gap-2 mt-2')
    async def load_reports():
        show_loading()
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f'{base}/allure/list')
                r.raise_for_status()
                data = r.json().get('reports', [])
                reports_list.clear()
                if not data:
                    # Use context manager to add children to the column
                    with reports_list:
                        ui.label('尚無報表').classes('muted')
                    return
                # 初始化 report review 狀態
                if not hasattr(state, 'report_reviews'):
                    state.report_reviews = {}
                for item in data:
                    name = item.get('name')
                    path = item.get('path')
                    if path not in state.report_reviews:
                        state.report_reviews[path] = '未審核'
                    with reports_list:
                        with ui.row().classes('items-center gap-2'):
                            ui.label(name).classes('grow')
                            # 審核狀態下拉選單
                            is_reviewed = state.report_reviews.get(path) == '已審核'
                            async def on_status_change(e, p=path):
                                show_loading()
                                try:
                                    state.report_reviews.__setitem__(p, e.value)
                                    # Note: report status is not saved to a file, it's in-memory state.
                                    await api.log_action(f"Updated report {p} status to {e.value}")
                                    ui.notify('已更新報表審核狀態', type='positive')
                                    ui.navigate.reload()
                                except Exception as ex:
                                    ui.notify(f'更新失敗: {ex}', type='negative')
                                finally:
                                    hide_loading()
                            s = ui.select(['未審核','已審核'], value=state.report_reviews.get(path,'未審核'),
                                      on_change=on_status_change).props('dense').classes('w-24')
                            if is_reviewed:
                                s.props('readonly disable')
                            def _open_report(p=path):
                                """Open the Allure HTML report in a new window."""
                                base_url = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
                                full_url = f'{base_url}{p}'
                                js_command = f"window.open('{full_url}', '_blank', 'width=1920,height=1080');"
                                ui.run_javascript(js_command)

                            def _show_raw_path(n=name):
                                """Show the local path to the raw allure-results directory."""
                                raw_path = ROOT / 'data' / 'allure-results' / n
                                ui.notify(f"原始檔路徑: {raw_path}", multi_line=True, close_button=True)

                            ui.button('查看報告', on_click=_open_report).props('flat color=primary')
                            ui.button('顯示原始檔路徑', on_click=_show_raw_path).props('flat color=secondary')
        except Exception as e:
            reports_list.clear()
            # Display error message in the report list column
            with reports_list:
                ui.label(f'讀取報表列表失敗: {e}').classes('text-red')
        finally:
            hide_loading()
    # schedule asynchronous loading of reports
    try:
        asyncio.create_task(load_reports())
    except Exception:
        pass


def render_automation(main_area):
    """
    Render the automation page. This page allows scheduling or running test cases
    immediately. Users can select Web, API and App cases and either schedule them
    for later or run them right away. Scheduling is handled client‑side via
    asyncio.sleep for demonstration purposes.
    """
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # --- State and Helper functions ---
    if not hasattr(state, 'scheduled_jobs'):
        state.scheduled_jobs = []
    if not hasattr(state, 'last_run_id'):
        state.last_run_id = None

    selected_web: set[int] = set()
    selected_app: set[int] = set()
    selected_api: set[int] = set()

    def toggle_sel(s: set, val: int):
        if val in s:
            s.remove(val)
        else:
            s.add(val)

    async def show_completion_dialog(title: str, message: str):
        with ui.dialog() as d, ui.card():
            ui.label(title).classes('text-lg font-bold')
            ui.label(message)
            with ui.row().classes('justify-end w-full mt-2'):
                ui.button('關閉', on_click=d.close).props('color=primary')
        await d

    # --- UI Components ---
    schedule_list = ui.column().classes('mt-4 gap-1')
    web_cases_expansion = ui.expansion('選取 WEB 案例', value=False)
    app_cases_expansion = ui.expansion('選取 APP 案例', value=False)
    api_cases_expansion = ui.expansion('選取 API 案例', value=False)

    # --- Data Loading and Rendering ---
    def refresh_schedules():
        schedule_list.clear()
        if not state.scheduled_jobs:
            with schedule_list:
                ui.label('尚無排程').classes('muted')
            return
        for idx, job in enumerate(state.scheduled_jobs):
            dt_str = job['time'].strftime('%Y-%m-%d %H:%M')
            with schedule_list:
                with ui.row().classes('items-center gap-2'):
                    ui.label(
                        f"排程於 {dt_str} 執行 (Web: {len(job['web'])} / App: {len(job['app'])} / API: {len(job['api'])})"
                    ).classes('text-sm')
                    def _del_schedule(_idx=idx):
                        show_loading()
                        try:
                            state.scheduled_jobs.pop(_idx)
                            refresh_schedules()
                            ui.notify('已刪除排程', type='positive')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=_del_schedule).props('flat color=negative')

    async def load_and_render_cases():
        try:
            web_cases = await api.list_web_case_names(state.active_project_id)
            app_cases = await api.list_app_case_names(state.active_project_id)
            api_cases = await api.list_api_case_names(state.active_project_id)

            for expansion, cases, selection_set in [
                (web_cases_expansion, web_cases, selected_web),
                (app_cases_expansion, app_cases, selected_app),
                (api_cases_expansion, api_cases, selected_api),
            ]:
                expansion.clear()
                with expansion:
                    for r in cases:
                        rid_str = r.get('id') or r.get('step')
                        try:
                            rid = int(rid_str)
                            name = r.get('name', '無名稱案例')
                            with ui.row().classes('items-center gap-2'):
                                ui.checkbox(value=(rid in selection_set), on_change=lambda e, r_id=rid, s=selection_set: toggle_sel(s, r_id))
                                ui.label(f"{rid} - {name}")
                        except (ValueError, TypeError):
                            continue
        except Exception as e:
            ui.notify(f'讀取案例列表失敗: {e}', type='negative')

    refresh_schedules()
    asyncio.create_task(load_and_render_cases())

    # --- Action Buttons and Handlers ---
    with ui.row().classes('gap-2 mt-2 items-center'):
        date_in = ui.date(value=dt.date.today()).classes('w-40')
        time_in = ui.time(value=dt.datetime.now().strftime('%H:%M')).classes('w-28')
        ui.label('排程時間')

    async def run_web_now():
        await api.log_action(f"User triggered WEB test with cases: {list(selected_web)}")
        show_loading()
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            payload = {'project_id': state.active_project_id, 'case_ids': list(selected_web)}
            async with httpx.AsyncClient(timeout=600.0) as client:
                r = await client.post(f'{base}/runs/trigger-web', json=payload)
                r.raise_for_status()
                response_data = r.json()
                state.last_run_id = response_data.get("run_id")
                ui.notify('已觸發 WEB 測試，請查看執行紀錄。', type='positive')
                main_area.refresh() # Refresh to show view log button
        except Exception as e:
            ui.notify(f'WEB 測試失敗: {e}', type='negative')
        finally:
            hide_loading()

    async def run_api_now():
        await api.log_action(f"User triggered API test with cases: {list(selected_api)}")
        show_loading()
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            payload = {'project_id': state.active_project_id, 'case_ids': list(selected_api)}
            async with httpx.AsyncClient(timeout=600.0) as client:
                r = await client.post(f'{base}/runs/trigger-api', json=payload)
                r.raise_for_status()
                response_data = r.json()
                state.last_run_id = response_data.get("run_id")
                ui.notify('已觸發 API 測試，請查看執行紀錄。', type='positive')
                main_area.refresh()
        except Exception as e:
            ui.notify(f'API 測試失敗: {e}', type='negative')
        finally:
            hide_loading()

    async def run_app_now():
        # App-specific configuration dialog
        with ui.dialog() as d, ui.card():
            ui.label('APP 測試設定').classes('text-lg font-semibold')
            app_file_in = ui.input('APP 檔案名稱 (在 data/ 目錄下)', value='my-app.apk')
            platform_in = ui.select(['Android', 'iOS'], label='平台名稱', value='Android')
            version_in = ui.input('平台版本', value='13.0')
            device_in = ui.input('設備/模擬器名稱', value='Android Emulator')

            async def do_run():
                d.close()
                payload = {
                    'project_id': state.active_project_id,
                    'case_ids': list(selected_app),
                    'app_file_name': app_file_in.value,
                    'platform_name': platform_in.value,
                    'platform_version': version_in.value,
                    'device_name': device_in.value,
                }
                await api.log_action(f"User triggered APP test with payload: {payload}")
                show_loading()
                try:
                    base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
                    async with httpx.AsyncClient(timeout=600.0) as client:
                        r = await client.post(f'{base}/runs/trigger-app', json=payload)
                        r.raise_for_status()
                        response_data = r.json()
                        state.last_run_id = response_data.get("run_id")
                        ui.notify('已觸發 APP 測試，請查看執行紀錄。', type='positive')
                        main_area.refresh()
                except Exception as e:
                    ui.notify(f'APP 測試失敗: {e}', type='negative')
                finally:
                    hide_loading()

            with ui.row().classes('justify-end gap-2 mt-4'):
                ui.button('取消', on_click=d.close).props('flat')
                ui.button('執行測試', on_click=do_run).props('color=primary')
        await d

    with ui.row().classes('gap-2'):
        ui.button('WEB 立即測試', icon='play_circle', on_click=run_web_now).props('color=primary')
        ui.button('API 立即測試', icon='play_circle', on_click=run_api_now).props('color=primary')
        ui.button('APP 立即測試', icon='play_circle', on_click=run_app_now).props('color=primary')

    ui.separator().classes('my-4')

    # --- Scheduling Section ---
    ui.label('設定排程').classes('text-lg font-semibold')

    with ui.row().classes('gap-2 mt-2 items-center'):
        date_in = ui.date(value=dt.date.today()).classes('w-40')
        time_in = ui.time(value=dt.datetime.now().strftime('%H:%M')).classes('w-28')

        async def run_now_scheduled():
            # This is the generic run function for scheduled tasks.
            show_loading()
            try:
                await api.log_action("Triggered a scheduled test run.")
                base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
                async with httpx.AsyncClient(timeout=600.0) as client:
                    r = await client.post(f'{base}/runs/trigger-pytest')
                    r.raise_for_status()
                    ui.notify('已觸發排程測試', type='positive')
            except Exception as e:
                ui.notify(f'排程測試執行失敗: {e}', type='negative')
            finally:
                hide_loading()

        async def schedule_run():
            await api.log_action("User attempted to set a schedule.")
            try:
                d_val = date_in.value
                t_val = time_in.value
                if isinstance(d_val, str): d_val = dt.date.fromisoformat(d_val)
                if isinstance(t_val, str): t_val = dt.time.fromisoformat(t_val)
                schedule_dt = dt.datetime.combine(d_val, t_val)
            except Exception:
                ui.notify('排程時間格式錯誤', type='negative')
                return

            delay = (schedule_dt - dt.datetime.now()).total_seconds()
            if delay <= 0:
                ui.notify('排程時間必須在未來', type='warning')
                return

            ui.notify(f'排程已設定，將於 {schedule_dt} 執行', type='info')
            if not hasattr(state, 'scheduled_jobs'):
                state.scheduled_jobs = []
            state.scheduled_jobs.append({
                'time': schedule_dt,
                'web': list(selected_web),
                'app': list(selected_app),
                'api': list(selected_api)
            })
            refresh_schedules()

            async def later():
                await asyncio.sleep(delay)
                await run_now_scheduled()

            asyncio.create_task(later())

        ui.button('設定排程', icon='schedule', on_click=schedule_run).props('color=secondary')

    # --- Scheduled Jobs List (Display Only) ---
    ui.label('已排程工作').classes('text-lg font-semibold mt-4')
    schedule_list = ui.column().classes('mt-2 gap-1')

    def refresh_schedules():
        schedule_list.clear()
        # The state object `state.scheduled_jobs` might not be initialized if the
        # feature was removed, so we check for its existence.
        if not hasattr(state, 'scheduled_jobs') or not state.scheduled_jobs:
            with schedule_list:
                # Per user feedback, do not show "No schedules" message.
                # The label above is sufficient.
                pass
            return

        # Sort jobs by time before displaying
        sorted_jobs = sorted(state.scheduled_jobs, key=lambda j: j['time'])
        state.scheduled_jobs = sorted_jobs

        for job in sorted_jobs:
            dt_str = job['time'].strftime('%Y-%m-%d %H:%M')
            with schedule_list:
                with ui.row().classes('items-center gap-2 p-1 rounded-md hover:bg-gray-100 w-full'):
                    info_text = f"排程於 {dt_str} (Web: {len(job['web'])}, App: {len(job['app'])}, API: {len(job['api'])})"
                    ui.label(info_text).classes('text-sm grow')

                    def _del_schedule(job_to_del=job):
                        show_loading()
                        try:
                            state.scheduled_jobs.remove(job_to_del)
                            refresh_schedules()
                            ui.notify('已刪除排程', type='positive')
                        finally:
                            hide_loading()
                    ui.button(icon='delete', on_click=_del_schedule).props('flat dense color=negative')

    # Initial render of the schedule list
    if hasattr(state, 'scheduled_jobs'):
        refresh_schedules()

    # --- Log Area and WebSocket ---
    with ui.row().classes('w-full items-center justify-between mt-4'):
        ui.label('執行過程紀錄').classes('text-lg font-semibold')
        async def view_last_log():
            if not state.last_run_id:
                ui.notify("沒有最近的執行紀錄可供查看。", type="warning")
                return
            await api.log_action(f"User viewed log for run_id: {state.last_run_id}")
            show_loading()
            try:
                base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.get(f'{base}/logs/{state.last_run_id}')
                    r.raise_for_status()
                    log_area.value = r.text
            except Exception as e:
                ui.notify(f"讀取日誌失敗: {e}", type="negative")
            finally:
                hide_loading()

        if state.last_run_id:
            ui.button('查看上次執行日誌', icon='history', on_click=view_last_log).props('flat')

    log_area = ui.textarea().props('readonly').classes('w-full h-60 mt-2 bg-gray-50 text-black text-xs font-mono whitespace-pre-wrap overflow-y-auto')

    async def connect_automation_log():
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            ws_url = base.replace('http', 'ws') + '/ws/test-run'
            async with httpx.AsyncClient() as client:
                async with client.websocket(ws_url) as ws:
                    log_area.value = "" # Clear log on new connection
                    async for msg in ws:
                        log_area.value += (msg + '\n')
                        log_area.update()
                        if '[webtest] finished' in msg:
                            await show_completion_dialog('測試完成', 'WEB 測試已執行完畢。')
                            await api.log_action("WEB test run finished.")
                        elif '[apitest] finished' in msg:
                            await show_completion_dialog('測試完成', 'API 測試已執行完畢。')
                            await api.log_action("API test run finished.")
                        elif 'error' in msg.lower():
                             await api.log_action(f"Test run error reported: {msg}")
        except Exception:
            pass

    asyncio.create_task(connect_automation_log())


def render_loadtest(main_area):
    """
    Render the load test page. This page lets the user select API test cases to use
    in a Locust load test, configure basic load parameters, start/stop the load
    test and view past run reports. Real‑time output from the load test is
    displayed in a log area via a websocket.
    """
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()
    all_cases = read_scoped_list(API_CASES_FILE, state.active_project_id) or []
    kw = ''
    method_filter: set[str] = set()
    result_filter: set[str] = set()
    selected_steps: set[int] = set()
    def apply_filters():
        # Filtering UI has been removed as per user request. Return all cases.
        return all_cases
    table_container = ui.element('div').classes('soft-card p-2 mt-2')
    def refresh_table():
        table_container.clear()
        filtered = apply_filters()
        if not filtered:
            # When no filtered cases, show a placeholder within the table container
            with table_container:
                ui.label('查無符合的 API 案例').classes('muted').style('padding-left: 1rem')
            return
            return
        with table_container:
            with ui.row().classes('text-sm muted items-center py-1'):
                ui.checkbox(on_change=lambda e: (selected_steps.update(int(r.get('step') or 0) for r in filtered) if e.value else selected_steps.clear()) or refresh_table())
                for h, w in [('步驟','w-16'), ('功能','w-32'), ('方法','w-20'), ('URL','w-32'), ('狀態','w-24')]:
                    ui.label(h).classes(w)
            ui.separator().classes('opacity-20')
            for r in filtered:
                step = r.get('step') or r.get('id')
                try:
                    step_int = int(step)
                except Exception:
                    step_int = 0
                with ui.row().classes('items-center py-1'):
                    def toggle_row(v=None, _step=step_int):
                        if _step in selected_steps:
                            selected_steps.remove(_step)
                        else:
                            selected_steps.add(_step)
                        refresh_table()
                    ui.checkbox(value=(step_int in selected_steps), on_change=lambda e, step=step_int: toggle_row(e.value, step))
                    ui.label(str(step)).classes('w-16')
                    ui.label(r.get('test_feature','')).classes('w-32')
                    ui.label(r.get('method','')).classes('w-20')
                    ui.label(r.get('url','')).classes('w-32')
                    ui.label(r.get('result','')).classes('w-24')
    refresh_table()
    with ui.column().classes('mt-4 gap-2'):
        ui.label('Locust 設定').classes('text-lg font-semibold')
        with ui.row().classes('gap-2'):
            users_input = ui.number(label='使用者數', value=10, min=1)
            rate_input  = ui.number(label='產生速率', value=1, min=1)
            host_input  = ui.input('目標主機', value='http://127.0.0.1').props('outlined dense')
        # Use textarea for log display; make it read-only via props
        log_area = ui.textarea().props('readonly').props('rows=8').classes('w-full')
    async def start_test():
        if not selected_steps:
            ui.notify('請先選取至少一個 API 測試案例', type='warning')
            return
        show_loading()
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            payload = {
                'total_users': int(users_input.value),
                'spawn_rate': int(rate_input.value),
                'host': host_input.value or 'http://127.0.0.1',
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(f'{base}/loadtest/start-real', params=payload)
                r.raise_for_status()
                ui.notify('壓力測試已開始', type='positive')
        except httpx.HTTPStatusError as e:
            try:
                detail = e.response.json().get("detail")
            except Exception:
                detail = str(e)
            ui.notify(f'啟動失敗: {detail}', type='negative')
        except Exception as e:
            ui.notify(f'啟動失敗: {e}', type='negative')
        finally:
            hide_loading()

    async def stop_test():
        show_loading()
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(f'{base}/loadtest/stop-real')
                r.raise_for_status()
                ui.notify('已送出停止指令', type='positive')
        except Exception as e:
            ui.notify(f'停止失敗: {e}', type='negative')
        finally:
            hide_loading()

    with ui.row().classes('gap-2'):
        ui.button('開始壓力測試', icon='play_arrow', on_click=start_test).props('color=primary')
        ui.button('停止測試', icon='stop', on_click=stop_test).props('color=negative')
        ui.label('歷史測試報告').classes('text-lg font-semibold mt-4')
        reports_list = ui.column().classes('gap-1')
        async def load_reports():
            try:
                base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.get(f'{base}/loadtest/reports')
                    r.raise_for_status()
                    runs = r.json().get('runs', [])
                    reports_list.clear()
                    if not runs:
                        # When there are no runs, show a placeholder label
                        with reports_list:
                            ui.label('尚無報告').classes('muted')
                        return
                    for item in runs:
                        run_id = item.get('id')
                        with reports_list:
                            with ui.row().classes('items-center gap-2'):
                                ui.label(run_id).classes('text-sm')
                                def view_run(_rid=run_id):
                                    async def inner():
                                        base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
                                        async with httpx.AsyncClient(timeout=20.0) as client:
                                            resp = await client.get(f'{base}/loadtest/report/{_rid}')
                                            resp.raise_for_status()
                                            data = resp.json()
                                            with ui.dialog() as d:
                                                with ui.card().classes('p-4 w-[80vw] max-h-[80vh] overflow-y-auto'):
                                                    ui.label(f'Load Test Report: {_rid}').classes('text-lg font-semibold mb-2')
                                                    stats = data.get('stats', [])
                                                    if stats:
                                                        cols = list(stats[0].keys())
                                                        rows = stats
                                                        ui.table(columns=[{'name':c,'label':c,'field':c} for c in cols], rows=rows, row_key=cols[0]).classes('w-full')
                                                    fails = data.get('failures', [])
                                                    if fails:
                                                        ui.label('Failures').classes('mt-2 text-md font-semibold')
                                                        fcols = list(fails[0].keys())
                                                        ui.table(columns=[{'name':c,'label':c,'field':c} for c in fcols], rows=fails, row_key=fcols[0]).classes('w-full')
                                            d.open()
                                    try:
                                        asyncio.create_task(inner())
                                    except Exception:
                                        pass
                                ui.button('查看', on_click=lambda rid=run_id: view_run(rid)).props('flat color=primary')
            except Exception as e:
                reports_list.clear()
                # Display error message as a label within the reports_list column
                with reports_list:
                    ui.label(f'讀取報告失敗: {e}').classes('text-red')
        # schedule loading of reports asynchronously
        try:
            asyncio.create_task(load_reports())
        except Exception:
            pass
    async def connect_log():
        try:
            base = os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'
            ws_url = base.replace('http','ws') + '/ws/loadtest'
            async with httpx.AsyncClient() as client:
                async with client.websocket(ws_url) as ws:
                    async for msg in ws:
                        log_area.value += (msg + '\n')
        except Exception:
            pass
    # start websocket listener asynchronously
    try:
        asyncio.create_task(connect_log())
    except Exception:
        pass


@ui.page('/projects')
def _page_projects():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/projects', render_projects)


@ui.page('/bugs')
def _page_bugs():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/bugs', render_bugs)


@ui.page('/reports')
def _page_reports():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/reports', render_reports)


@ui.page('/automation')
def _page_automation():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/automation', render_automation)


@ui.page('/loadtest')
def _page_loadtest():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/loadtest', render_loadtest)

# == 測試案例頁面路由 ==
@ui.page('/webcases')
def _page_webcases():
    """WEB 測試案例頁面"""
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/webcases', render_web_cases)

@ui.page('/appcases')
def _page_appcases():
    """APP 測試案例頁面"""
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/appcases', render_app_cases)

@ui.page('/apicases')
def _page_apicases():
    """API 測試案例頁面"""
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/apicases', render_api_cases)



def render_home(main_area):
    with ui.column().classes('w-full gap-2'):
        ui.label('歡迎使用 測試管理平台').classes('text-h5')
        ui.label('請從左側選單選擇要進入的功能，或使用下方快速選單。').classes('text-body2')
        with ui.row().classes('gap-2 mt-2'):
            ui.button('專案管理', icon='folder', on_click=lambda: ui.navigate.to('/projects'))
            ui.button('BUG 管理', icon='bug_report', on_click=lambda: ui.navigate.to('/bugs'))
            ui.button('報表', icon='bar_chart', on_click=lambda: ui.navigate.to('/reports'))
            ui.button('自動化', icon='bolt', on_click=lambda: ui.navigate.to('/automation'))
            ui.button('壓力測試', icon='speed', on_click=lambda: ui.navigate.to('/loadtest'))

@ui.page('/home')
def _page_home():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/home', render_home)

@ui.page('/projects')
def _page_projects():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/projects', render_projects)

@ui.page('/bugs')
def _page_bugs():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/bugs', render_bugs)

if __name__ == '__main__':
    # Start NiceGUI frontend. Allow overriding the default port via the
    # ``FRONTEND_PORT`` environment variable to avoid conflicts when
    # port 8080 is already in use. On Windows, port binding errors can
    # occur when another NiceGUI instance is running. Set FRONTEND_PORT
    # to a free port (e.g. 8081) before launching this script.
    import os
    port_str = os.getenv('FRONTEND_PORT', '8080')
    try:
        port_int = int(port_str)
    except Exception:
        port_int = 8080
    ui.run(host='127.0.0.1', port=port_int, reload=False)
