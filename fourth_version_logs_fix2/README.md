
# Test Platform (JSON) — Enterprise Upgrade 3 (重建版)

## 模組
- 前端：NiceGUI
- 後端：FastAPI
- 資料：JSON 持久化（backend/app/data/*.json）
- 自動化：Pytest + Allure（即時日誌、報告生成與瀏覽）
- 壓力測試：Locust（模擬與真實）

## 快速啟動
### 後端
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
> 若要 Allure 報告：系統需安裝 Allure CLI（例如：`brew install allure` / Windows 安裝官方 zip）

### 前端
```
cd ../frontend
pip install nicegui httpx
python main.py
```
開啟 `http://127.0.0.1:8080`

## 頁面
- `/projects`：專案 CRUD、搜尋（右側叉叉清空）、過場轉圈圈、自動刷新、選取重置
- `/bugs`：BUG CRUD 與搜尋
- `/reports`：ECharts 圖表（圓餅、長條）
- `/automation`：開始 Pytest、即時日誌（WebSocket）、產生 Allure、開啟報告
- `/loadtest`：開始/停止（模擬 & Locust 真實），即時狀態（WebSocket）
