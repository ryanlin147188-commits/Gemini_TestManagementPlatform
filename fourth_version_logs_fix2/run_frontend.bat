@echo off
cd /d %~dp0\frontend
python -m pip install -r requirements.txt
python main.py
