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
# import json, os # No longer needed for file i/o
# from pathlib import Path # No longer needed for file i/o

# UPLOADS_DIR is still needed for the upload component
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
UPLOADS_DIR = DATA_DIR / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)
app.add_static_files('/uploads', str(UPLOADS_DIR))

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
# ---- 專案上下文 (Data is now loaded via API calls in each page) ----
# Initial load for active project is still needed to avoid errors,
# but it will be overwritten by async calls.
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
    except Exception:
        # Fallback if backend is not available on startup
        state.active_project_id = 1
        state.active_project_name = '未選取'
        state.projects = []

# This runs once when the app starts
asyncio.create_task(load_initial_project())

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
async def render_projects(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    # Container for the table and pagination
    table_container = ui.column().classes('w-full')

    async def refresh_projects():
        show_loading()
        table_container.clear()
        try:
            items = await api.list_projects(keyword=state.prj_kw, owner=state.prj_owner, status=state.prj_status)
            state.projects = items # Update global state
            with table_container:
                render_table(items)
        except Exception as e:
            with table_container:
                ui.label(f'Error loading projects: {e}').classes('text-negative')
        finally:
            hide_loading()

    def render_table(items):
        page_size = max(1, int(state.prj_page_size or 10))
        total = len(items)
        max_page = max(1, (total + page_size - 1) // page_size)
        state.prj_page = min(max(1, state.prj_page), max_page)
        start = (state.prj_page - 1) * page_size
        page_rows = items[start:start+page_size]

        bulk_toolbar(state.prj_selected_ids, [
            ('刪除選取', 'delete', bulk_delete),
            ('清除選取', 'close', lambda: (state.prj_selected_ids.clear(), asyncio.create_task(refresh_projects()))),
        ])

        if not page_rows and total == 0:
            empty_state('尚無專案', '點擊右上角「新增」建立第一個專案。', '新增', on_click=lambda: open_project_dialog())
            return

        with ui.element('div').classes('soft-card p-2'):
            # Table Header
            with ui.row().classes('text-sm muted items-center py-1'):
                ui.checkbox(on_change=lambda e: (state.prj_selected_ids.update(r.get('id') for r in page_rows) if e.value else state.prj_selected_ids.clear()) or table_container.refresh())
                ui.label('編號').classes('w-20')
                ui.label('專案名稱').classes('w-[40%]')
                ui.label('人員').classes('w-40')
                ui.label('專案狀態').classes('w-28')
                ui.label('操作').classes('w-32')
            ui.separator().classes('opacity-20')

            # Table Rows
            for r in page_rows:
                render_row(r)

        # Pagination
        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.prj_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                async def prev_page():
                    if state.prj_page > 1:
                        state.prj_page -= 1
                        await refresh_projects()
                async def next_page():
                    if state.prj_page < max_page:
                        state.prj_page += 1
                        await refresh_projects()
                ui.button('上一頁', icon='chevron_left', on_click=prev_page).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=next_page).props('flat')

    def render_row(r):
        rid = r.get('id')
        with ui.row().classes('items-center py-1'):
            ui.checkbox(value=(rid in state.prj_selected_ids), on_change=lambda e, rid=rid: (state.prj_selected_ids.remove(rid) if rid in state.prj_selected_ids else state.prj_selected_ids.add(rid)) or table_container.refresh())
            ui.label(str(rid)).classes('w-20')
            ui.label(r.get('name','')).classes('w-[40%]')
            ui.label(r.get('owner','')).classes('w-40')
            with ui.element('div').classes('w-28'):
                status_badge(r.get('status','新增'), {'新增':'info','進行中':'primary','暫停':'warning','完成':'positive'})
            with ui.row().classes('w-32 gap-1'):
                async def switch_proj(_rid=rid):
                    state.active_project_id = _rid
                    await load_initial_project() # Reload project info
                    ui.navigate.reload()
                ui.button(icon='swap_horiz', on_click=switch_proj).props('flat')
                ui.button(icon='edit', on_click=lambda rid=rid: open_project_dialog(rid)).props('flat')
                async def del_one(_rid=rid):
                    show_loading()
                    try:
                        await api.delete_project(_rid)
                        await api.log_action(f"Deleted project id={_rid}")
                        ui.notify(f'已刪除專案 {_rid}', type='positive')
                        await refresh_projects()
                    except Exception as e:
                        ui.notify(f'刪除失敗: {e}', type='negative')
                    finally:
                        hide_loading()
                ui.button(icon='delete', on_click=del_one).props('flat')

    async def bulk_delete():
        ids_to_delete = list(state.prj_selected_ids)
        if not ids_to_delete: return
        show_loading()
        try:
            for pid in ids_to_delete:
                await api.delete_project(pid)
            await api.log_action(f"Bulk deleted {len(ids_to_delete)} projects.")
            ui.notify(f'已刪除 {len(ids_to_delete)} 筆', type='positive')
            state.prj_selected_ids.clear()
            await refresh_projects()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()

    def open_project_dialog(edit_id: int | None = None):
        editing = None
        if edit_id:
            for p in state.projects:
                if p.get('id') == edit_id:
                    editing = p
                    break
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
                    async def save():
                        payload = {'name': name.value, 'owner': owner.value, 'status': status.value}
                        show_loading()
                        try:
                            if editing:
                                await api.update_project(editing['id'], payload)
                            else:
                                await api.create_project(payload)
                            d.close()
                            await refresh_projects()
                            ui.notify('已儲存', type='positive')
                        except Exception as e:
                            ui.notify(f'儲存失敗: {e}', type='negative')
                        finally:
                            hide_loading()
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

async def render_web_cases(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    table_container = ui.column().classes('w-full')

    async def refresh_cases():
        show_loading()
        table_container.clear()
        try:
            result = await api.list_web_cases(
                state.active_project_id,
                keyword=state.web_kw,
                action=",".join(state.web_action),
                result=",".join(state.web_result)
            )
            state.web_list = result.get('items', [])
            with table_container:
                render_table(state.web_list, result.get('total', 0))
        except Exception as e:
            with table_container:
                ui.label(f'Error loading web cases: {e}').classes('text-negative')
        finally:
            hide_loading()

    def render_table(items, total):
        # Pagination
        page_size = 50
        max_page = max(1, (total + page_size - 1) // page_size)
        state.web_page = min(max(1, state.web_page), max_page)

        # Bulk Actions
        bulk_toolbar(state.web_selected_ids, [
            ('刪除選取', 'delete', bulk_delete),
            ('清除選取', 'close', lambda: (state.web_selected_ids.clear(), table_container.refresh()))
        ])

        if not items and total == 0:
            empty_state('尚無 WEB 測試案例', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
            return

        with ui.element('div').classes('soft-card p-2'):
            # Table Header
            with ui.row().classes('text-sm muted items-center py-1'):
                ui.checkbox(on_change=lambda e: (state.web_selected_ids.update(r.get('id') for r in items) if e.value else state.web_selected_ids.clear()) or table_container.refresh())
                for h, w in [('編號','w-16'), ('測試功能','w-32'), ('測試步驟','w-20'), ('動作','w-28'),
                             ('敘述','w-[20%]'), ('頁面','w-28'), ('元件','w-28'), ('輸入值','w-32'), ('審核','w-24'), ('操作','w-28')]:
                    ui.label(h).classes(w)
            ui.separator().classes('opacity-20')
            # Table Rows
            for r in items:
                render_row(r)

        # Pagination Controls
        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.web_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state, 'web_page', max(1, state.web_page - 1)), asyncio.create_task(refresh_cases()))).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state, 'web_page', min(max_page, state.web_page + 1)), asyncio.create_task(refresh_cases()))).props('flat')

    def render_row(r):
        rid = r.get('id')
        with ui.row().classes('items-center py-1'):
            ui.checkbox(value=(rid in state.web_selected_ids), on_change=lambda e, rid=rid: (state.web_selected_ids.remove(rid) if rid in state.web_selected_ids else state.web_selected_ids.add(rid)) or table_container.refresh())
            ui.label(str(rid)).classes('w-16')
            ui.label(r.get('feature','')).classes('w-32')
            ui.label(r.get('step','')).classes('w-20')
            ui.label(r.get('action','')).classes('w-28')
            ui.label(r.get('desc','')).classes('w-[20%]')
            ui.label(r.get('page','')).classes('w-28')
            ui.label(r.get('element','')).classes('w-28')
            ui.label(r.get('value','')).classes('w-32')
            # Review status dropdown
            is_reviewed = r.get('review') == '已審核'
            async def on_status_change(e, record_id=rid):
                show_loading()
                try:
                    await api.update_web_case(state.active_project_id, record_id, {'review': e.value})
                    await api.log_action(f"Updated web case id={record_id} status to {e.value}")
                    ui.notify('已更新審核狀態', type='positive')
                    await refresh_cases()
                except Exception as ex:
                    ui.notify(f'更新失敗: {ex}', type='negative')
                finally:
                    hide_loading()
            s = ui.select(['未審核','已審核'], value=r.get('review','未審核'), on_change=on_status_change).props('dense').classes('w-24')
            if is_reviewed: s.props('readonly disable')
            # Action buttons
            with ui.row().classes('w-28 gap-1'):
                ui.button(icon='edit', on_click=lambda r=r: open_dialog(r)).props('flat')
                async def del_one(case_id=rid):
                    show_loading()
                    try:
                        await api.delete_web_case(state.active_project_id, case_id)
                        await api.log_action(f"Deleted web case id={case_id}")
                        ui.notify(f'已刪除案例 {case_id}', type='positive')
                        await refresh_cases()
                    except Exception as e:
                        ui.notify(f'刪除失敗: {e}', type='negative')
                    finally:
                        hide_loading()
                ui.button(icon='delete', on_click=del_one).props('flat')

    async def bulk_delete():
        ids_to_delete = list(state.web_selected_ids)
        if not ids_to_delete: return
        show_loading()
        try:
            for case_id in ids_to_delete:
                await api.delete_web_case(state.active_project_id, case_id)
            await api.log_action(f"Bulk deleted {len(ids_to_delete)} web cases.")
            ui.notify(f'已刪除 {len(ids_to_delete)} 筆', type='positive')
            state.web_selected_ids.clear()
            await refresh_cases()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()

    def open_dialog(editing_case: dict | None = None):
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[560px]'):
                ui.label('新增測試案例' if not editing_case else '修改測試案例').classes('text-lg font-semibold')
                # Form fields
                with ui.grid(columns=2).classes('gap-2 mt-2'):
                    feature = ui.input('測試功能').props('outlined dense')
                    step = ui.input('測試步驟').props('outlined dense')
                    action = ui.select(['前往網址','填入','點擊','等待','檢查','選擇','檔案上傳'], label='動作').props('outlined dense')
                    desc = ui.input('敘述').props('outlined dense')
                    page_ = ui.input('頁面').props('outlined dense')
                    elem = ui.input('元件').props('outlined dense')
                    val = ui.input('輸入值').props('outlined dense')
                if editing_case:
                    feature.value = editing_case.get('feature', '')
                    step.value = editing_case.get('step', '')
                    action.value = editing_case.get('action', '')
                    desc.value = editing_case.get('desc', '')
                    page_.value = editing_case.get('page', '')
                    elem.value = editing_case.get('element', '')
                    val.value = editing_case.get('value', '')

                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        payload = {
                            'feature': feature.value, 'step': step.value, 'action': action.value,
                            'desc': desc.value, 'page': page_.value, 'element': elem.value, 'value': val.value
                        }
                        show_loading()
                        try:
                            if editing_case:
                                await api.update_web_case(state.active_project_id, editing_case['id'], payload)
                            else:
                                await api.create_web_case(state.active_project_id, payload)
                            d.close()
                            await refresh_cases()
                            ui.notify('儲存成功！', type='positive')
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    # Search & actions
    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字', on_change=refresh_cases).bind_value(state, 'web_kw').props('dense outlined')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')

    # Initial data load
    asyncio.create_task(refresh_cases())



async def render_app_cases(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    table_container = ui.column().classes('w-full')

    async def refresh_cases():
        show_loading()
        table_container.clear()
        try:
            result = await api.list_app_cases(
                state.active_project_id,
                keyword=state.app_kw,
                action=",".join(state.app_action),
                result=",".join(state.app_result)
            )
            state.app_list = result.get('items', [])
            with table_container:
                render_table(state.app_list, result.get('total', 0))
        except Exception as e:
            with table_container:
                ui.label(f'Error loading app cases: {e}').classes('text-negative')
        finally:
            hide_loading()

    def render_table(items, total):
        page_size = 50
        max_page = max(1, (total + page_size - 1) // page_size)
        state.app_page = min(max(1, state.app_page), max_page)

        bulk_toolbar(state.app_selected_ids, [
            ('刪除選取', 'delete', bulk_delete),
            ('清除選取', 'close', lambda: (state.app_selected_ids.clear(), table_container.refresh()))
        ])

        if not items and total == 0:
            empty_state('尚無 APP 測試案例', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
            return

        with ui.element('div').classes('soft-card p-2'):
            with ui.row().classes('text-sm muted items-center py-1'):
                ui.checkbox(on_change=lambda e: (state.app_selected_ids.update(r.get('id') for r in items) if e.value else state.app_selected_ids.clear()) or table_container.refresh())
                for h, w in [('編號','w-16'), ('測試功能','w-32'), ('測試步驟','w-20'), ('動作','w-28'),
                             ('敘述','w-[20%]'), ('頁面','w-28'), ('元件','w-28'), ('輸入值','w-32'), ('審核','w-24'), ('操作','w-28')]:
                    ui.label(h).classes(w)
            ui.separator().classes('opacity-20')
            for r in items:
                render_row(r)

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.app_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state, 'app_page', max(1, state.app_page - 1)), asyncio.create_task(refresh_cases()))).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state, 'app_page', min(max_page, state.app_page + 1)), asyncio.create_task(refresh_cases()))).props('flat')

    def render_row(r):
        rid = r.get('id')
        with ui.row().classes('items-center py-1'):
            ui.checkbox(value=(rid in state.app_selected_ids), on_change=lambda e, rid=rid: (state.app_selected_ids.remove(rid) if rid in state.app_selected_ids else state.app_selected_ids.add(rid)) or table_container.refresh())
            ui.label(str(rid)).classes('w-16')
            ui.label(r.get('feature','')).classes('w-32')
            ui.label(r.get('step','')).classes('w-20')
            ui.label(r.get('action','')).classes('w-28')
            ui.label(r.get('desc','')).classes('w-[20%]')
            ui.label(r.get('page','')).classes('w-28')
            ui.label(r.get('element','')).classes('w-28')
            ui.label(r.get('value','')).classes('w-32')
            is_reviewed = r.get('review') == '已審核'
            async def on_status_change(e, record_id=rid):
                show_loading()
                try:
                    await api.update_app_case(state.active_project_id, record_id, {'review': e.value})
                    await api.log_action(f"Updated app case id={record_id} status to {e.value}")
                    ui.notify('已更新審核狀態', type='positive')
                    await refresh_cases()
                except Exception as ex:
                    ui.notify(f'更新失敗: {ex}', type='negative')
                finally:
                    hide_loading()
            s = ui.select(['未審核','已審核'], value=r.get('review','未審核'), on_change=on_status_change).props('dense').classes('w-24')
            if is_reviewed: s.props('readonly disable')
            with ui.row().classes('w-28 gap-1'):
                ui.button(icon='edit', on_click=lambda r=r: open_dialog(r)).props('flat')
                async def del_one(case_id=rid):
                    show_loading()
                    try:
                        await api.delete_app_case(state.active_project_id, case_id)
                        await api.log_action(f"Deleted app case id={case_id}")
                        ui.notify(f'已刪除案例 {case_id}', type='positive')
                        await refresh_cases()
                    except Exception as e:
                        ui.notify(f'刪除失敗: {e}', type='negative')
                    finally:
                        hide_loading()
                ui.button(icon='delete', on_click=del_one).props('flat')

    async def bulk_delete():
        ids_to_delete = list(state.app_selected_ids)
        if not ids_to_delete: return
        show_loading()
        try:
            for case_id in ids_to_delete:
                await api.delete_app_case(state.active_project_id, case_id)
            await api.log_action(f"Bulk deleted {len(ids_to_delete)} app cases.")
            ui.notify(f'已刪除 {len(ids_to_delete)} 筆', type='positive')
            state.app_selected_ids.clear()
            await refresh_cases()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()

    def open_dialog(editing_case: dict | None = None):
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[560px]'):
                ui.label('新增測試案例' if not editing_case else '修改測試案例').classes('text-lg font-semibold')
                with ui.grid(columns=2).classes('gap-2 mt-2'):
                    feature = ui.input('測試功能').props('outlined dense')
                    step = ui.input('測試步驟').props('outlined dense')
                    action = ui.select(['前往網址','填入','點擊','等待','檢查','選擇','檔案上傳'], label='動作').props('outlined dense')
                    desc = ui.input('敘述').props('outlined dense')
                    page_ = ui.input('頁面').props('outlined dense')
                    elem = ui.input('元件').props('outlined dense')
                    val = ui.input('輸入值').props('outlined dense')
                if editing_case:
                    feature.value = editing_case.get('feature', '')
                    step.value = editing_case.get('step', '')
                    action.value = editing_case.get('action', '')
                    desc.value = editing_case.get('desc', '')
                    page_.value = editing_case.get('page', '')
                    elem.value = editing_case.get('element', '')
                    val.value = editing_case.get('value', '')
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        payload = {
                            'feature': feature.value, 'step': step.value, 'action': action.value,
                            'desc': desc.value, 'page': page_.value, 'element': elem.value, 'value': val.value
                        }
                        show_loading()
                        try:
                            if editing_case:
                                await api.update_app_case(state.active_project_id, editing_case['id'], payload)
                            else:
                                await api.create_app_case(state.active_project_id, payload)
                            d.close()
                            await refresh_cases()
                            ui.notify('儲存成功！', type='positive')
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字', on_change=refresh_cases).bind_value(state, 'app_kw').props('dense outlined')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')
        # ui.button('輸入設備資訊', icon='smartphone', on_click=lambda: open_device()).props('flat') # TODO: Re-implement device info

    asyncio.create_task(refresh_cases())


async def render_api_cases(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    table_container = ui.column().classes('w-full')

    async def refresh_cases():
        show_loading()
        table_container.clear()
        try:
            result = await api.list_api_cases(
                state.active_project_id,
                keyword=state.api_kw,
                method=",".join(state.api_method),
                result=",".join(state.api_result)
            )
            state.api_list = result.get('items', [])
            with table_container:
                render_table(state.api_list, result.get('total', 0))
        except Exception as e:
            with table_container:
                ui.label(f'Error loading API cases: {e}').classes('text-negative')
        finally:
            hide_loading()

    def render_table(items, total):
        page_size = 50
        max_page = max(1, (total + page_size - 1) // page_size)
        state.api_page = min(max(1, state.api_page), max_page)

        bulk_toolbar(state.api_selected_ids, [
            ('刪除選取', 'delete', bulk_delete),
            ('清除選取', 'close', lambda: (state.api_selected_ids.clear(), table_container.refresh()))
        ])

        if not items and total == 0:
            empty_state('尚無 API 測試案例', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
            return

        with ui.element('div').classes('soft-card p-2'):
            with ui.row().classes('text-sm muted items-center py-1'):
                ui.checkbox(on_change=lambda e: (state.api_selected_ids.update(r.get('id') for r in items) if e.value else state.api_selected_ids.clear()) or table_container.refresh())
                for h, w in [('ID','w-16'), ('測試功能','w-32'), ('方法','w-20'), ('URL','w-[20%]'), ('API路徑','w-32'), ('審核','w-24'), ('操作','w-28')]:
                    ui.label(h).classes(w)
            ui.separator().classes('opacity-20')
            for r in items:
                render_row(r)

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.api_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state, 'api_page', max(1, state.api_page - 1)), asyncio.create_task(refresh_cases()))).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state, 'api_page', min(max_page, state.api_page + 1)), asyncio.create_task(refresh_cases()))).props('flat')

    def render_row(r):
        rid = r.get('id')
        with ui.row().classes('items-center py-1'):
            ui.checkbox(value=(rid in state.api_selected_ids), on_change=lambda e, rid=rid: (state.api_selected_ids.remove(rid) if rid in state.api_selected_ids else state.api_selected_ids.add(rid)) or table_container.refresh())
            ui.label(str(rid)).classes('w-16')
            ui.label(r.get('test_feature','')).classes('w-32')
            ui.label(r.get('method','')).classes('w-20')
            ui.label(r.get('url','')).classes('w-[20%]')
            ui.label(r.get('api_path','')).classes('w-32')
            is_reviewed = r.get('review') == '已審核'
            async def on_status_change(e, record_id=rid):
                show_loading()
                try:
                    await api.update_api_case(state.active_project_id, record_id, {'review': e.value})
                    await api.log_action(f"Updated api case id={record_id} status to {e.value}")
                    ui.notify('已更新審核狀態', type='positive')
                    await refresh_cases()
                except Exception as ex:
                    ui.notify(f'更新失敗: {ex}', type='negative')
                finally:
                    hide_loading()
            s = ui.select(['未審核','已審核'], value=r.get('review','未審核'), on_change=on_status_change).props('dense').classes('w-24')
            if is_reviewed: s.props('readonly disable')
            with ui.row().classes('w-28 gap-1'):
                ui.button(icon='edit', on_click=lambda r=r: open_dialog(r)).props('flat')
                async def del_one(case_id=rid):
                    show_loading()
                    try:
                        await api.delete_api_case(state.active_project_id, case_id)
                        await api.log_action(f"Deleted api case id={case_id}")
                        ui.notify(f'已刪除案例 {case_id}', type='positive')
                        await refresh_cases()
                    except Exception as e:
                        ui.notify(f'刪除失敗: {e}', type='negative')
                    finally:
                        hide_loading()
                ui.button(icon='delete', on_click=del_one).props('flat')

    async def bulk_delete():
        ids_to_delete = list(state.api_selected_ids)
        if not ids_to_delete: return
        show_loading()
        try:
            for case_id in ids_to_delete:
                await api.delete_api_case(state.active_project_id, case_id)
            await api.log_action(f"Bulk deleted {len(ids_to_delete)} api cases.")
            ui.notify(f'已刪除 {len(ids_to_delete)} 筆', type='positive')
            state.api_selected_ids.clear()
            await refresh_cases()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()

    def open_dialog(editing_case: dict | None = None):
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[760px]'):
                ui.label('新增 API 測試案例' if not editing_case else '修改 API 測試案例').classes('text-lg font-semibold')
                with ui.grid(columns=2).classes('gap-2 mt-2'):
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
                    response_summary = ui.textarea('回應摘要').props('outlined dense')
                if editing_case:
                    step.value = str(editing_case.get('step',''))
                    feature.value = editing_case.get('feature','')
                    method.value = editing_case.get('method','')
                    url.value = editing_case.get('url','')
                    api_path.value = editing_case.get('api_path','')
                    header.value = editing_case.get('header','')
                    body.value = editing_case.get('body','')
                    expect_status.value = str(editing_case.get('expect_status',''))
                    expect_field.value = editing_case.get('expect_field','')
                    expect_value.value = editing_case.get('expect_value','')
                    response_summary.value = editing_case.get('response_summary','')
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        payload = {
                            'step': int(step.value) if step.value.isdigit() else 0, 'feature': feature.value, 'method': method.value,
                            'url': url.value, 'api_path': api_path.value, 'header': header.value, 'body': body.value,
                            'expect_status': expect_status.value, 'expect_field': expect_field.value, 'expect_value': expect_value.value,
                            'response_summary': response_summary.value
                        }
                        show_loading()
                        try:
                            if editing_case:
                                await api.update_api_case(state.active_project_id, editing_case['id'], payload)
                            else:
                                await api.create_api_case(state.active_project_id, payload)
                            d.close()
                            await refresh_cases()
                            ui.notify('儲存成功！', type='positive')
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字', on_change=refresh_cases).bind_value(state, 'api_kw').props('dense outlined')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')

    asyncio.create_task(refresh_cases())



async def render_bugs(main_area):
    ui.label(f'目前專案：{state.active_project_name}').classes('text-sm opacity-70')
    ui.separator()

    table_container = ui.column().classes('w-full')

    async def refresh_bugs():
        show_loading()
        table_container.clear()
        try:
            items = await api.list_project_bugs(
                state.active_project_id,
                keyword=state.bug_filter_kw,
                severity=state.bug_filter_status.copy().pop() if state.bug_filter_status else "",
                status="" # Status filter not implemented in UI yet
            )
            state.bug_list = items
            with table_container:
                render_table(items)
        except Exception as e:
            with table_container:
                ui.label(f'Error loading bugs: {e}').classes('text-negative')
        finally:
            hide_loading()

    def render_table(items):
        page_size = 10
        total = len(items)
        max_page = max(1, (total + page_size - 1) // page_size)
        state.bug_page = min(max(1, state.bug_page), max_page)
        start = (state.bug_page - 1) * page_size
        page_rows = items[start:start+page_size]

        bulk_toolbar(state.bug_selected_ids, [
            ('刪除選取', 'delete', bulk_delete),
            ('清除選取', 'close', lambda: (state.bug_selected_ids.clear(), table_container.refresh()))
        ])

        if not page_rows and total == 0:
            empty_state('尚無 BUG', '點擊右上角「新增」建立第一筆。', '新增', on_click=lambda: open_dialog())
            return

        with ui.element('div').classes('soft-card p-2'):
            with ui.row().classes('text-sm muted items-center py-1'):
                ui.checkbox(on_change=lambda e: (state.bug_selected_ids.update(r.get('id') for r in page_rows) if e.value else state.bug_selected_ids.clear()) or table_container.refresh())
                for h, w in [('問題敘述','w-[22%]'), ('嚴重度','w-20'), ('狀態','w-24'), ('重現步驟','w-[20%]'),
                             ('預期結果','w-[18%]'), ('實際結果','w-[18%]'), ('備註','w-[16%]'), ('截圖','w-28'), ('操作','w-28')]:
                    ui.label(h).classes(w)
            ui.separator().classes('opacity-20')

            for r in page_rows:
                render_row(r)

        with ui.row().classes('items-center justify-between pt-2'):
            ui.label(f'第 {state.bug_page}/{max_page} 頁 · 每頁 {page_size} 筆 · 共 {total} 筆').classes('muted')
            with ui.row().classes('gap-2'):
                ui.button('上一頁', icon='chevron_left', on_click=lambda: (setattr(state, 'bug_page', max(1, state.bug_page - 1)), asyncio.create_task(refresh_bugs()))).props('flat')
                ui.button('下一頁', icon='chevron_right', on_click=lambda: (setattr(state, 'bug_page', min(max_page, state.bug_page + 1)), asyncio.create_task(refresh_bugs()))).props('flat')

    def render_row(r):
        rid = r.get('id')
        with ui.row().classes('items-center py-1'):
            ui.checkbox(value=(rid in state.bug_selected_ids), on_change=lambda e, rid=rid: (state.bug_selected_ids.remove(rid) if rid in state.bug_selected_ids else state.bug_selected_ids.add(rid)) or table_container.refresh())
            ui.label(r.get('description','')).classes('w-[22%]') # Using description as title
            with ui.element('div').classes('w-20'):
                status_badge(r.get('severity',''), CASE_STATUS_COLORS)
            is_reviewed = r.get('status') == '已審核'
            options = ['新增','進行中','關閉','駁回', '已審核']
            async def on_status_change(e, record_id=rid):
                show_loading()
                try:
                    await api.update_project_bug(state.active_project_id, record_id, {'status': e.value})
                    await api.log_action(f"Updated bug id={record_id} status to {e.value}")
                    ui.notify('已更新狀態', type='positive')
                    await refresh_bugs()
                except Exception as ex:
                    ui.notify(f'更新失敗: {ex}', type='negative')
                finally:
                    hide_loading()
            s = ui.select(options, value=r.get('status','新增'), on_change=on_status_change).props('dense').classes('w-24')
            if is_reviewed: s.props('readonly disable')
            ui.label(r.get('repro','')).classes('w-[20%]')
            ui.label(r.get('expected','')).classes('w-[18%]')
            ui.label(r.get('actual','')).classes('w-[18%]')
            ui.label(r.get('note','')).classes('w-[16%]')
            img = r.get('screenshot')
            with ui.row().classes('w-28'):
                if img:
                    ui.link('查看', f"/uploads/{img}")
            with ui.row().classes('w-28 gap-1'):
                ui.button(icon='edit', on_click=lambda r=r: open_dialog(r)).props('flat')
                async def del_one(bug_id=rid):
                    show_loading()
                    try:
                        await api.delete_project_bug(state.active_project_id, bug_id)
                        await api.log_action(f"Deleted bug id={bug_id}")
                        ui.notify(f'已刪除 BUG {bug_id}', type='positive')
                        await refresh_bugs()
                    except Exception as e:
                        ui.notify(f'刪除失敗: {e}', type='negative')
                    finally:
                        hide_loading()
                ui.button(icon='delete', on_click=del_one).props('flat')

    async def bulk_delete():
        ids_to_delete = list(state.bug_selected_ids)
        if not ids_to_delete: return
        show_loading()
        try:
            for bug_id in ids_to_delete:
                await api.delete_project_bug(state.active_project_id, bug_id)
            await api.log_action(f"Bulk deleted {len(ids_to_delete)} bugs.")
            ui.notify(f'已刪除 {len(ids_to_delete)} 筆', type='positive')
            state.bug_selected_ids.clear()
            await refresh_bugs()
        except Exception as e:
            ui.notify(f'刪除失敗: {e}', type='negative')
        finally:
            hide_loading()

    def open_dialog(editing_bug: dict | None = None):
        with ui.dialog() as d:
            with ui.card().classes('p-4 min-w-[760px]'):
                ui.label('新增 BUG' if not editing_bug else '修改 BUG').classes('text-lg font-semibold')
                with ui.grid(columns=2).classes('gap-2 mt-2'):
                    desc = ui.input('問題敘述').props('outlined dense')
                    severity = ui.select(['高','中','低'], label='嚴重度').props('outlined dense')
                    status = ui.select(['新增','進行中','關閉','駁回'], label='狀態').props('outlined dense')
                    repro = ui.textarea('重現步驟').props('outlined dense')
                    expected = ui.textarea('預期結果').props('outlined dense')
                    actual = ui.textarea('實際結果').props('outlined dense')
                    note = ui.input('備註').props('outlined dense')
                    upload_name = ui.label('').classes('muted')
                    def on_upload(e):
                        # This part remains client-side as it needs to interact with the local filesystem
                        # The backend would need an upload endpoint to handle the file bytes
                        pass
                    ui.upload(on_upload=on_upload, auto_upload=True).props('accept="image/*"')
                if editing_bug:
                    desc.value = editing_bug.get('description','')
                    severity.value = editing_bug.get('severity','中')
                    status.value = editing_bug.get('status','新增')
                    repro.value = editing_bug.get('repro','')
                    expected.value = editing_bug.get('expected','')
                    actual.value = editing_bug.get('actual','')
                    note.value = editing_bug.get('note','')
                    upload_name.text = editing_bug.get('screenshot','') or ''
                with ui.row().classes('justify-end gap-2 mt-3'):
                    ui.button('取消', on_click=d.close).props('flat')
                    async def save():
                        payload = {
                            'description': desc.value, 'severity': severity.value, 'status': status.value,
                            'repro': repro.value, 'expected': expected.value, 'actual': actual.value,
                            'note': note.value, 'screenshot': upload_name.text
                        }
                        show_loading()
                        try:
                            if editing_bug:
                                await api.update_project_bug(state.active_project_id, editing_bug['id'], payload)
                            else:
                                await api.create_project_bug(state.active_project_id, payload)
                            d.close()
                            await refresh_bugs()
                            ui.notify('儲存成功！', type='positive')
                        except Exception as e:
                            ui.notify(f"儲存失敗: {e}", type='negative')
                        finally:
                            hide_loading()
                    ui.button('儲存', color='primary', on_click=save)
        d.open()

    with ui.row().classes('gap-2 items-end flex-wrap'):
        kw_in = ui.input('關鍵字', on_change=refresh_bugs).bind_value(state, 'bug_filter_kw').props('dense outlined')
        ui.button('新增', icon='add', on_click=lambda: open_dialog()).props('color=accent')

    asyncio.create_task(refresh_bugs())


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


def render_mock_page(main_area):
    """
    Renders the Mock API creation page.
    """
    # State for the form
    if not hasattr(state, 'mock_params'):
        state.mock_params = [{'key': '', 'value': ''}]
    if not hasattr(state, 'mock_req_headers'):
        state.mock_req_headers = [{'key': '', 'value': ''}]
    if not hasattr(state, 'mock_resp_headers'):
        state.mock_resp_headers = [{'key': 'Content-Type', 'value': 'application/json'}]
    if not hasattr(state, 'active_mocks'):
        state.active_mocks = []

    # UI containers
    active_mocks_container = ui.column().classes('w-full gap-2')

    def refresh_active_mocks():
        active_mocks_container.clear()
        with active_mocks_container:
            if not state.active_mocks:
                ui.label('No active mocks.').classes('text-gray-500')
            else:
                with ui.grid(columns=4).classes('w-full gap-2'):
                    for mock in state.active_mocks:
                        with ui.card().classes('p-2'):
                            ui.label(f"{mock.get('method', 'GET').upper()} {mock.get('path')}").classes('font-bold')
                            ui.badge(f"Status: {mock.get('response_status')}", color='positive')

    async def load_initial_mocks():
        try:
            state.active_mocks = await api.get_mocks()
            refresh_active_mocks()
        except Exception as e:
            ui.notify(f"Failed to load mocks: {e}", type='negative')

    # Page Header
    page_header("Mock API Server", "Create and manage mock API endpoints.")

    # Section for active mocks
    with ui.expansion('Active Mocks', icon='checklist', value=True).classes('w-full soft-card'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Currently active mock endpoints. They are matched in the order they are created.')
            ui.button('Refresh', icon='refresh', on_click=load_initial_mocks).props('flat')
        refresh_active_mocks()

    # Main card for creating new mocks
    with ui.card().classes('soft-card w-full mt-4'):
        ui.label('Create New Mock').classes('text-lg font-bold')
        ui.separator()

        with ui.grid(columns=2).classes('w-full gap-8 mt-4'):
            # --- Request Matching Column ---
            with ui.column().classes('gap-2'):
                ui.label('Request Matching').classes('text-md font-bold')

                mock_path = ui.input('Endpoint Path', placeholder='/api/users/1').props('outlined dense').classes('w-full')
                mock_method = ui.select(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], label='HTTP Method', value='GET').props('outlined dense')

                # Dynamic Key-Value for Query Params
                ui.label('Query Parameters').classes('mt-2')
                params_container = ui.column().classes('w-full gap-1')
                def render_params():
                    params_container.clear()
                    with params_container:
                        for i, param in enumerate(state.mock_params):
                            with ui.row().classes('w-full items-center gap-2'):
                                ui.input(placeholder='Key', value=param['key'], on_change=lambda e, i=i: state.mock_params[i].update({'key': e.value})).props('dense outlined').classes('grow')
                                ui.input(placeholder='Value', value=param['value'], on_change=lambda e, i=i: state.mock_params[i].update({'value': e.value})).props('dense outlined').classes('grow')
                                ui.button(icon='remove', on_click=lambda _, i=i: (state.mock_params.pop(i), render_params())).props('flat dense color=negative')
                        ui.button('Add Param', icon='add', on_click=lambda: (state.mock_params.append({'key':'', 'value':''}), render_params())).props('flat dense').classes('mt-1')
                render_params()

                # Dynamic Key-Value for Request Headers
                ui.label('Request Headers').classes('mt-2')
                req_headers_container = ui.column().classes('w-full gap-1')
                def render_req_headers():
                    req_headers_container.clear()
                    with req_headers_container:
                        for i, header in enumerate(state.mock_req_headers):
                            with ui.row().classes('w-full items-center gap-2'):
                                ui.input(placeholder='Key', value=header['key'], on_change=lambda e, i=i: state.mock_req_headers[i].update({'key': e.value})).props('dense outlined').classes('grow')
                                ui.input(placeholder='Value', value=header['value'], on_change=lambda e, i=i: state.mock_req_headers[i].update({'value': e.value})).props('dense outlined').classes('grow')
                                ui.button(icon='remove', on_click=lambda _, i=i: (state.mock_req_headers.pop(i), render_req_headers())).props('flat dense color=negative')
                        ui.button('Add Header', icon='add', on_click=lambda: (state.mock_req_headers.append({'key':'', 'value':''}), render_req_headers())).props('flat dense').classes('mt-1')
                render_req_headers()

                mock_req_body = ui.textarea('Request Body (JSON or Text)').props('outlined').classes('w-full mt-2')

            # --- Response Definition Column ---
            with ui.column().classes('gap-2'):
                ui.label('Response Definition').classes('text-md font-bold')

                mock_resp_status = ui.number('Status Code', value=200, min=100, max=599).props('outlined dense')
                mock_delay = ui.number('Delay (ms)', value=0, min=0).props('outlined dense')

                # Dynamic Key-Value for Response Headers
                ui.label('Response Headers').classes('mt-2')
                resp_headers_container = ui.column().classes('w-full gap-1')
                def render_resp_headers():
                    resp_headers_container.clear()
                    with resp_headers_container:
                        for i, header in enumerate(state.mock_resp_headers):
                            with ui.row().classes('w-full items-center gap-2'):
                                ui.input(placeholder='Key', value=header['key'], on_change=lambda e, i=i: state.mock_resp_headers[i].update({'key': e.value})).props('dense outlined').classes('grow')
                                ui.input(placeholder='Value', value=header['value'], on_change=lambda e, i=i: state.mock_resp_headers[i].update({'value': e.value})).props('dense outlined').classes('grow')
                                ui.button(icon='remove', on_click=lambda _, i=i: (state.mock_resp_headers.pop(i), render_resp_headers())).props('flat dense color=negative')
                        ui.button('Add Header', icon='add', on_click=lambda: (state.mock_resp_headers.append({'key':'', 'value':''}), render_resp_headers())).props('flat dense').classes('mt-1')
                render_resp_headers()

                mock_resp_body = ui.textarea('Response Body (JSON, XML, Text)').props('outlined').classes('w-full mt-2')

        ui.separator().classes('my-4')

        async def do_create_mock():
            if not mock_path.value or not mock_path.value.startswith('/'):
                ui.notify('Endpoint Path must start with /', type='negative')
                return

            payload = {
                "path": mock_path.value,
                "method": mock_method.value,
                "params": [p for p in state.mock_params if p['key']],
                "headers": [h for h in state.mock_req_headers if h['key']],
                "body": mock_req_body.value or None,
                "response_status": int(mock_resp_status.value),
                "response_headers": [h for h in state.mock_resp_headers if h['key']],
                "response_body": mock_resp_body.value or "",
                "delay_ms": int(mock_delay.value)
            }

            show_loading()
            try:
                await api.create_mock(payload)
                ui.notify('Mock created successfully!', type='positive')
                await load_initial_mocks() # Refresh the list
            except Exception as e:
                ui.notify(f"Failed to create mock: {e}", type='negative')
            finally:
                hide_loading()

        ui.button('Create Mock', icon='add_circle', on_click=do_create_mock).props('color=primary')

    # Load mocks when page opens
    asyncio.create_task(load_initial_mocks())


@ui.page('/mock')
def _page_mock():
    try:
        setup_theme()
    except Exception:
        pass
    render_layout('/mock', render_mock_page)

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
