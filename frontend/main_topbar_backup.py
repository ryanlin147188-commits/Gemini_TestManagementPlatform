from nicegui import ui, app
import asyncio, os, json
import datetime as dt

# ---------------- Theme & helpers ----------------

CARD = 'rounded-2xl shadow-xl p-5'
BTN  = 'rounded-xl'

def setup_theme():
    ui.add_head_html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --brand-1:#6366f1;
  --brand-2:#06b6d4;
}
*{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, \"Helvetica Neue\", Arial, \"Noto Sans\", \"Liberation Sans\", \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Segoe UI Symbol\", \"Noto Color Emoji\"; }
.glass-card{ background: rgba(255,255,255,0.04); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }
.elev{ box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
.hero{ background: linear-gradient(120deg, rgba(99,102,241,.25), rgba(6,182,212,.25)); border-bottom:1px solid rgba(255,255,255,0.08); }
</style>
""")

def scaffold(title: str, content_builder):
    with ui.header().classes('glass-card elev hero'):
        with ui.row().classes('items-center justify-between w-full p-3'):
            ui.label(title).classes('text-xl font-bold')
            with ui.row().classes('gap-3'):
                ui.button('首頁', on_click=lambda: ui.navigate.to('/')).props('flat')
                ui.button('專案管理', on_click=lambda: ui.navigate.to('/projects')).props('flat')
                ui.button('Bug 管理', on_click=lambda: ui.navigate.to('/bugs')).props('flat')
                ui.button('報表', on_click=lambda: ui.navigate.to('/reports')).props('flat')
                ui.button('自動化測試', on_click=lambda: ui.navigate.to('/automation')).props('flat')
                ui.button('壓力測試', on_click=lambda: ui.navigate.to('/loadtest')).props('flat')
    with ui.row().classes('w-full'):
        with ui.column().classes('w-full max-w-6xl mx-auto p-6 gap-6'):
            content_builder()

def backend_base():
    return os.getenv('BACKEND_URL') or 'http://127.0.0.1:8000'

def make_loading():
    dlg = ui.dialog()
    with dlg, ui.card().classes('p-8 rounded-2xl glass-card elev flex flex-col items-center gap-3'):
        spinner = ui.spinner(size='lg')
        msg = ui.label('處理中...').classes('text-lg')
    def show(text='處理中...'):
        msg.set_text(text); dlg.open()
    def hide():
        dlg.close()
    return show, hide

async def fetch_json(client, method, url, **kwargs):
    r = await client.request(method, url, **kwargs)
    r.raise_for_status()
    data = r.json()
    return data.get('items', data) if isinstance(data, dict) else data

def home_page():
    def _content():
        with ui.card().classes(CARD + ' glass-card elev w-full'):
            ui.label('歡迎使用 Test Platform').classes('text-2xl font-bold')
            ui.label('請從上方導覽選擇頁面').classes('opacity-70')
    scaffold('首頁', _content)

def projects_page():
    def _content():
        show, hide = make_loading()
        selected = {'row': None}
        search = ui.input('搜尋專案 (名稱、擁有者)').props('outlined dense clearable').on('keydown.enter', lambda e: asyncio.create_task(reload()))
        with search.add_slot('append'):
            ui.button(on_click=lambda: (search.set_value(''), asyncio.create_task(reload()))).props('flat dense round icon=close')
        with ui.row().classes('gap-2 items-center'):
            ui.button('新增', on_click=lambda: dlg_create.open()).classes(BTN)
            ui.button('編輯選取', on_click=lambda: dlg_edit.open() if selected['row'] else ui.notify('請先選取一筆', type='warning')).classes(BTN)
            ui.button('刪除選取', on_click=lambda: asyncio.create_task(on_delete())).classes(BTN)
        table = ui.table(columns=[
            {'name':'id','label':'ID','field':'id','align':'left'},
            {'name':'name','label':'專案','field':'name'},
            {'name':'owner','label':'Owner','field':'owner'},
            {'name':'status','label':'狀態','field':'status'},
        ], rows=[], row_key='id', pagination=10).classes('w-full glass-card elev').on('rowClick', lambda e: selected.__setitem__('row', e.args['row']))
        with ui.dialog() as dlg_create, ui.card().classes(CARD + ' glass-card elev w-[420px]'):
            ui.label('新增專案').classes('text-lg font-bold')
            name = ui.input('名稱').props('outlined')
            owner = ui.input('Owner').props('outlined')
            status = ui.select(['Active','Paused','Archived'], value='Active', label='狀態').props('outlined')
            with ui.row().classes('gap-2 justify-end'):
                ui.button('取消', on_click=lambda: dlg_create.close())
                ui.button('建立', on_click=lambda: asyncio.create_task(on_create()))
        with ui.dialog() as dlg_edit, ui.card().classes(CARD + ' glass-card elev w-[420px]'):
            ui.label('編輯專案').classes('text-lg font-bold')
            name_e = ui.input('名稱').props('outlined')
            owner_e = ui.input('Owner').props('outlined')
            status_e = ui.select(['Active','Paused','Archived'], label='狀態').props('outlined')
            with ui.row().classes('gap-2 justify-end'):
                ui.button('取消', on_click=lambda: dlg_edit.close())
                ui.button('儲存', on_click=lambda: asyncio.create_task(on_update()))
        async def reload():
            show('載入中...')
            try:
                import httpx
                async with httpx.AsyncClient(timeout=15.0) as client:
                    rows = await fetch_json(client, 'GET', f'{backend_base()}/projects', params={'q': search.value or ''})
                table.rows = rows; table.update()
            except Exception as e:
                ui.notify(f'讀取失敗: {e}', type='negative')
            finally:
                hide()
        async def on_create():
            show('建立中...')
            try:
                import httpx
                payload = {'name': name.value, 'owner': owner.value, 'status': status.value}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    await fetch_json(client, 'POST', f'{backend_base()}/projects', json=payload)
                dlg_create.close(); await reload(); ui.notify('已建立', type='positive')
            except Exception as e:
                ui.notify(f'建立失敗: {e}', type='negative')
            finally:
                hide()
        async def on_update():
            if not selected['row']:
                ui.notify('未選取', type='warning'); return
            show('更新中...')
            try:
                import httpx
                rid = selected['row']['id']
                payload = {'name': name_e.value, 'owner': owner_e.value, 'status': status_e.value}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    await fetch_json(client, 'PUT', f'{backend_base()}/projects/{rid}', json=payload)
                dlg_edit.close(); await reload(); ui.notify('已更新', type='positive')
            except Exception as e:
                ui.notify(f'更新失敗: {e}', type='negative')
            finally:
                hide()
        async def on_delete():
            if not selected['row']:
                ui.notify('未選取', type='warning'); return
            show('刪除中...')
            try:
                import httpx
                rid = selected['row']['id']
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await fetch_json(client, 'DELETE', f'{backend_base()}/projects/{rid}')
                await reload(); ui.notify('已刪除', type='positive')
            except Exception as e:
                ui.notify(f'刪除失敗: {e}', type='negative')
            finally:
                hide()
        def fill_edit_dialog():
            if selected['row']:
                name_e.set_value(selected['row'].get('name',''))
                owner_e.set_value(selected['row'].get('owner',''))
                status_e.set_value(selected['row'].get('status','Active'))
        dlg_edit.on('show', lambda: fill_edit_dialog())
        ui.timer(0.05, lambda: asyncio.create_task(reload()), once=True)
    scaffold('專案管理', _content)

def bugs_page():
    def _content():
        show, hide = make_loading()
        selected = {'row': None}
        search = ui.input('搜尋 Bug (標題、狀態)').props('outlined dense clearable').on('keydown.enter', lambda e: asyncio.create_task(reload()))
        with search.add_slot('append'):
            ui.button(on_click=lambda: (search.set_value(''), asyncio.create_task(reload()))).props('flat dense round icon=close')
        with ui.row().classes('gap-2 items-center'):
            ui.button('新增', on_click=lambda: dlg_create.open()).classes(BTN)
            ui.button('編輯選取', on_click=lambda: dlg_edit.open() if selected['row'] else ui.notify('請先選取一筆', type='warning')).classes(BTN)
            ui.button('刪除選取', on_click=lambda: asyncio.create_task(on_delete())).classes(BTN)
        table = ui.table(columns=[
            {'name':'id','label':'ID','field':'id','align':'left'},
            {'name':'title','label':'標題','field':'title'},
            {'name':'severity','label':'嚴重度','field':'severity'},
            {'name':'status','label':'狀態','field':'status'},
        ], rows=[], row_key='id', pagination=10).classes('w-full glass-card elev').on('rowClick', lambda e: selected.__setitem__('row', e.args['row']))
        with ui.dialog() as dlg_create, ui.card().classes(CARD + ' glass-card elev w-[520px]'):
            ui.label('新增 Bug').classes('text-lg font-bold')
            title = ui.input('標題').props('outlined')
            severity = ui.select(['Critical','High','Medium','Low'], value='Medium', label='嚴重度').props('outlined')
            status = ui.select(['Open','In Progress','Closed'], value='Open', label='狀態').props('outlined')
            with ui.row().classes('gap-2 justify-end'):
                ui.button('取消', on_click=lambda: dlg_create.close())
                ui.button('建立', on_click=lambda: asyncio.create_task(on_create()))
        with ui.dialog() as dlg_edit, ui.card().classes(CARD + ' glass-card elev w-[520px]'):
            ui.label('編輯 Bug').classes('text-lg font-bold')
            title_e = ui.input('標題').props('outlined')
            severity_e = ui.select(['Critical','High','Medium','Low'], label='嚴重度').props('outlined')
            status_e = ui.select(['Open','In Progress','Closed'], label='狀態').props('outlined')
            with ui.row().classes('gap-2 justify-end'):
                ui.button('取消', on_click=lambda: dlg_edit.close())
                ui.button('儲存', on_click=lambda: asyncio.create_task(on_update()))
        async def reload():
            show('載入中...')
            try:
                import httpx
                async with httpx.AsyncClient(timeout=15.0) as client:
                    rows = await fetch_json(client, 'GET', f'{backend_base()}/bugs', params={'q': search.value or ''})
                table.rows = rows; table.update()
            except Exception as e:
                ui.notify(f'讀取失敗: {e}', type='negative')
            finally:
                hide()
        async def on_create():
            show('建立中...')
            try:
                import httpx
                payload = {'title': title.value, 'severity': severity.value, 'status': status.value}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    await fetch_json(client, 'POST', f'{backend_base()}/bugs', json=payload)
                dlg_create.close(); await reload(); ui.notify('已建立', type='positive')
            except Exception as e:
                ui.notify(f'建立失敗: {e}', type='negative')
            finally:
                hide()
        async def on_update():
            if not selected['row']:
                ui.notify('未選取', type='warning'); return
            show('更新中...')
            try:
                import httpx
                rid = selected['row']['id']
                payload = {'title': title_e.value, 'severity': severity_e.value, 'status': status_e.value}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    await fetch_json(client, 'PUT', f'{backend_base()}/bugs/{rid}', json=payload)
                dlg_edit.close(); await reload(); ui.notify('已更新', type='positive')
            except Exception as e:
                ui.notify(f'更新失敗: {e}', type='negative')
            finally:
                hide()
        async def on_delete():
            if not selected['row']:
                ui.notify('未選取', type='warning'); return
            show('刪除中...')
            try:
                import httpx
                rid = selected['row']['id']
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await fetch_json(client, 'DELETE', f'{backend_base()}/bugs/{rid}')
                await reload(); ui.notify('已刪除', type='positive')
            except Exception as e:
                ui.notify(f'刪除失敗: {e}', type='negative')
            finally:
                hide()
        def fill_edit_dialog():
            if selected['row']:
                title_e.set_value(selected['row'].get('title',''))
                severity_e.set_value(selected['row'].get('severity','Medium'))
                status_e.set_value(selected['row'].get('status','Open'))
        dlg_edit.on('show', lambda: fill_edit_dialog())
        ui.timer(0.05, lambda: asyncio.create_task(reload()), once=True)
    scaffold('Bug 管理', _content)

def reports_page():
    def _content():
        show, hide = make_loading()
        with ui.column().classes('w-full max-w-6xl mx-auto p-0 gap-6'):
            with ui.row().classes('gap-4 w-full'):
                with ui.card().classes(CARD + ' min-w-[200px] glass-card elev'):
                    ui.label('專案數').classes('text-gray-500')
                    count_projects = ui.label('-').classes('text-3xl font-bold')
                with ui.card().classes(CARD + ' min-w-[200px] glass-card elev'):
                    ui.label('BUG 數').classes('text-gray-500')
                    count_bugs = ui.label('-').classes('text-3xl font-bold')
            with ui.expansion('Bugs 報表', value=True).classes('w-full glass-card elev'):
                with ui.row().classes('gap-3 items-end'):
                    range_days = ui.number('區間天數', value=14).props('outlined').classes('w-32')
                    ui.button('重新整理', on_click=lambda: asyncio.create_task(_load_bug_charts())).classes(BTN)
                with ui.row().classes('w-full gap-4 mt-2'):
                    bug_trend = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value'}, 'series':[{'type':'line','name':'Opened','data':[]},{'type':'line','name':'Closed','data':[]}], 'legend':{}}).classes('w-2/3 h-[320px]')
                    bug_status_pie = ui.echart({'series':[{'type':'pie','radius':'55%','data':[]}]}).classes('w-1/3 h-[320px]')
                with ui.row().classes('w-full gap-4'):
                    bug_sev_bar = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value'}, 'series':[{'type':'bar','data':[]}]}).classes('w-1/2 h-[300px]')
                    bug_resolve_time = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value','name':'hours'}, 'series':[{'type':'line','data':[]}]}).classes('w-1/2 h-[300px]')
        async def _load_all_counts():
            show('載入統計...')
            try:
                import httpx
                async with httpx.AsyncClient(timeout=20.0) as client:
                    rp = await fetch_json(client, 'GET', f'{backend_base()}/projects')
                    rb = await fetch_json(client, 'GET', f'{backend_base()}/bugs')
                count_projects.set_text(str(len(rp) if isinstance(rp, list) else 0))
                count_bugs.set_text(str(len(rb) if isinstance(rb, list) else 0))
            except Exception as e:
                ui.notify(f'統計讀取失敗: {e}', type='negative')
            finally:
                hide()
        async def _load_bug_charts():
            show('載入報表...')
            try:
                import httpx
                days = int(range_days.value or 14)
                since = (dt.datetime.utcnow() - dt.timedelta(days=days)).strftime('%Y-%m-%d')
                async with httpx.AsyncClient(timeout=25.0) as client:
                    bugs = await fetch_json(client, 'GET', f'{backend_base()}/bugs', params={'since': since})
                from collections import Counter, defaultdict
                opened = Counter(); closed = Counter(); sev_counter = Counter(); res_map = defaultdict(list)
                def to_date(s): 
                    if not s: return None
                    return (s or '')[:10]
                for b in (bugs or []):
                    sev_counter[(b.get('severity') or 'Unknown')] += 1
                    c = to_date(b.get('created_at'))
                    d = to_date(b.get('closed_at'))
                    if c: opened[c]+=1
                    if d:
                        closed[d]+=1
                        try:
                            cdt = dt.datetime.fromisoformat((b.get('created_at','') or '').replace('Z','+00:00'))
                            ddt = dt.datetime.fromisoformat((b.get('closed_at','') or '').replace('Z','+00:00'))
                            hrs = max(0.0, (ddt-cdt).total_seconds()/3600.0)
                            res_map[d].append(hrs)
                        except: pass
                dates = sorted(set(opened.keys())|set(closed.keys()))
                bug_trend.options = {'title': {'text':'BUG 狀態趨勢'}, 'xAxis':{'type':'category','data':dates}, 'yAxis':{'type':'value'}, 'series':[{'type':'line','name':'Opened','data':[opened.get(x,0) for x in dates]},{'type':'line','name':'Closed','data':[closed.get(x,0) for x in dates]}], 'legend':{}}
                bug_status_pie.options = {'tooltip': {'trigger':'item'}, 'series':[{'type':'pie','radius':'55%','data':[{'name':k,'value':v} for k,v in sev_counter.items()]}]}
                res_labels = sorted(res_map.keys())
                res_values = [ round(sum(v)/len(v),2) for k,v in sorted(res_map.items()) ]
                bug_resolve_time.options = {'title': {'text':'每日平均修復時數'}, 'xAxis':{'type':'category','data':res_labels}, 'yAxis':{'type':'value','name':'hours'}, 'series':[{'type':'line','data':res_values}]}
                bug_sev_bar.options = {'title': {'text':'嚴重度分佈'}, 'xAxis':{'type':'category','data': list(sev_counter.keys())}, 'yAxis':{'type':'value'}, 'series':[{'type':'bar','data': list(sev_counter.values())}]}
            except Exception as e:
                ui.notify(f'報表載入失敗: {e}', type='negative')
            finally:
                hide()
        ui.timer(0.05, lambda: asyncio.create_task(_load_all_counts()), once=True)
        ui.timer(0.15, lambda: asyncio.create_task(_load_bug_charts()), once=True)
    scaffold('報表', _content)

def automation_page():
    def _content():
        show, hide = make_loading()
        with ui.expansion('Allure 趨勢', value=False).classes('w-full glass-card elev'):
            ui.button('更新趨勢', on_click=lambda: asyncio.create_task(_load_allure_trend())).classes(BTN)
            allure_line = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value'}, 'series':[{'type':'line','name':'Total','data':[]},{'type':'line','name':'Failed','data':[]}], 'legend':{}}).classes('w-full h-[320px]')
        with ui.expansion('Locust 進階報表', value=False).classes('w-full glass-card elev'):
            with ui.row().classes('gap-3 items-end'):
                run_select = ui.select(options=[], label='選擇報告').props('outlined').classes('w-72')
                ui.button('刷新清單', on_click=lambda: asyncio.create_task(_refresh_locust_runs())).classes(BTN)
                ui.button('載入明細', on_click=lambda: asyncio.create_task(_load_locust_report())).classes(BTN)
            with ui.row().classes('w-full gap-4 mt-2'):
                locust_p95 = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value','name':'ms'}, 'series':[{'type':'line','name':'P95','data':[]}]}).classes('w-1/2 h-[280px]')
                locust_p99 = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value','name':'ms'}, 'series':[{'type':'line','name':'P99','data':[]}]}).classes('w-1/2 h-[280px]')
            with ui.row().classes('w-full gap-4'):
                locust_fail = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value','name':'%'}, 'series':[{'type':'bar','name':'失敗率','data':[]}]}).classes('w-1/2 h-[260px]')
                locust_rps  = ui.echart({'xAxis':{'type':'category','data':[]}, 'yAxis':{'type':'value','name':'req/s'}, 'series':[{'type':'bar','name':'Requests/s','data':[]}]}).classes('w-1/2 h-[260px]')
        async def _load_allure_trend():
            show('載入 Allure 趨勢...')
            try:
                import httpx
                async with httpx.AsyncClient(timeout=20.0) as client:
                    r = await client.get(f"{backend_base()}/allure/list"); r.raise_for_status()
                    reports = r.json().get('reports', [])
                labels, totals, fails = [], [], []
                for rep in reports:
                    labels.append(rep.get('name','?'))
                    totals.append(rep.get('total',0))
                    fails.append(rep.get('failed',0))
                allure_line.options = {'title': {'text':'Allure 歷史趨勢'}, 'xAxis': {'type':'category','data': labels}, 'yAxis': {'type':'value'}, 'series':[{'type':'line','name':'Total','data': totals},{'type':'line','name':'Failed','data': fails}], 'legend': {}}
            except Exception as e:
                ui.notify(f'Allure 趨勢載入失敗: {e}', type='negative')
            finally:
                hide()
        async def _refresh_locust_runs():
            show('讀取清單...')
            try:
                import httpx
                async with httpx.AsyncClient(timeout=20.0) as client:
                    r = await client.get(f"{backend_base()}/loadtest/reports"); r.raise_for_status()
                    items = r.json().get('runs', [])
                run_select.options = [{'label': i.get('name', i.get('id','run')), 'value': i.get('id')} for i in items]
                run_select.update()
            except Exception as e:
                ui.notify(f'Locust 清單失敗: {e}', type='negative')
            finally:
                hide()
        async def _load_locust_report():
            if not run_select.value:
                ui.notify('請先選擇報告', type='warning'); return
            show('載入報表...')
            try:
                import httpx
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.get(f"{backend_base()}/loadtest/report/{run_select.value}"); r.raise_for_status()
                    info = r.json()
                rows = info.get('stats', [])
                names, p95s, p99s, fails_pct, rps = [], [], [], [], []
                for row in rows:
                    name = row.get('Name') or row.get('name')
                    if (name or '').lower() == 'aggregated': continue
                    names.append(name or 'N/A')
                    try: p95s.append(float(row.get('95%') or 0))
                    except: p95s.append(0)
                    try: p99s.append(float(row.get('99%') or 0))
                    except: p99s.append(0)
                    try:
                        req = float(row.get('Requests') or 0); fail = float(row.get('Failures') or 0)
                        fails_pct.append(round((fail/max(1.0,req))*100.0, 2))
                    except: fails_pct.append(0)
                    try: rps.append(float(row.get('Requests/s') or 0))
                    except: rps.append(0)
                locust_p95.options = {'title': {'text':'P95(ms)'}, 'xAxis': {'type':'category','data': names}, 'yAxis': {'type':'value','name':'ms'}, 'series':[{'type':'line','name':'P95','data': p95s}]}
                locust_p99.options = {'title': {'text':'P99(ms)'}, 'xAxis': {'type':'category','data': names}, 'yAxis': {'type':'value','name':'ms'}, 'series':[{'type':'line','name':'P99','data': p99s}]}
                locust_fail.options = {'title': {'text':'失敗率(%)'}, 'xAxis': {'type':'category','data': names}, 'yAxis': {'type':'value','name':'%'}, 'series':[{'type':'bar','name':'失敗率','data': fails_pct}]}
                locust_rps.options  = {'title': {'text':'Requests/s'}, 'xAxis': {'type':'category','data': names}, 'yAxis': {'type':'value','name':'req/s'}, 'series':[{'type':'bar','name':'Requests/s','data': rps}]}
            except Exception as e:
                ui.notify(f'Locust 報告載入失敗: {e}', type='negative')
            finally:
                hide()
        ui.timer(0.1, lambda: asyncio.create_task(_load_allure_trend()), once=True)
        ui.timer(0.2, lambda: asyncio.create_task(_refresh_locust_runs()), once=True)
    scaffold('自動化測試', _content)

def loadtest_page():
    def _content():
        with ui.card().classes(CARD + ' glass-card elev w-full'):
            ui.label('壓力測試入口').classes('text-lg font-bold')
            ui.label('請改用「自動化測試」頁的 Locust 模組查閱報表').classes('opacity-70')
    scaffold('壓力測試', _content)

setup_theme()

@ui.page('/')
def _index(): home_page()

@ui.page('/projects')
def _projects(): projects_page()

@ui.page('/bugs')
def _bugs(): bugs_page()

@ui.page('/reports')
def _reports(): reports_page()

@ui.page('/automation')
def _auto(): automation_page()

@ui.page('/loadtest')
def _load(): loadtest_page()

ui.run(title='Test Platform', reload=False, favicon='🌈')
