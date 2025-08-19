#!/usr/bin/env bash
# One-click starter (Linux/Mac)
set -e
# Start backend
( cd backend && uvicorn app.main:app --reload --port 8000 ) &
# Start frontend
( cd frontend && python main.py ) &
echo "Frontend: http://localhost:8080"
echo "Backend : http://localhost:8000/docs"
wait
