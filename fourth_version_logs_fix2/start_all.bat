@echo off
REM One-click starter (Windows) - opens two terminals
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"
start cmd /k "cd frontend && python main.py"
echo Frontend: http://localhost:8080
echo Backend : http://localhost:8000/docs
pause
