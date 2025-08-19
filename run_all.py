#!/usr/bin/env python3
"""
One-click runner for Test Platform (JSON version).
- Creates virtual envs for backend and frontend if missing
- Installs requirements
- Launches FastAPI (uvicorn) and NiceGUI
Usage:
    python run_all.py           # normal
    python run_all.py --no-venv # use system Python instead of creating venvs
"""
import os, sys, subprocess, time, shutil, platform

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
USE_VENV = ("--no-venv" not in sys.argv)

def venv_python(venv_dir: str) -> str:
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")

def ensure_venv_and_deps(app_dir: str) -> str:
    """Create .venv and install requirements.txt if needed. Returns Python path to use."""
    if not USE_VENV:
        return sys.executable
    venv_dir = os.path.join(app_dir, ".venv")
    py = venv_python(venv_dir)
    if not os.path.exists(py):
        print(f"[setup] Creating venv at {venv_dir} ...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir], cwd=app_dir)
        py = venv_python(venv_dir)
    # install deps
    req = os.path.join(app_dir, "requirements.txt")
    if os.path.exists(req):
        print(f"[setup] Installing dependencies for {app_dir} ...")
        subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "pip"], cwd=app_dir)
        subprocess.check_call([py, "-m", "pip", "install", "-r", "requirements.txt"], cwd=app_dir)
    return py

def launch_backend(py_path: str):
    print("[run] Starting backend (FastAPI @ 8000) ...")
    return subprocess.Popen([py_path, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"], cwd=BACKEND_DIR)

def launch_frontend(py_path: str):
    print("[run] Starting frontend (NiceGUI @ 8080) ...")
    return subprocess.Popen([py_path, "main.py"], cwd=FRONTEND_DIR)

def main():
    try:
        be_py = ensure_venv_and_deps(BACKEND_DIR)
        fe_py = ensure_venv_and_deps(FRONTEND_DIR)
    except subprocess.CalledProcessError as e:
        print("[error] Dependency installation failed:", e)
        sys.exit(1)

    be = launch_backend(be_py)
    time.sleep(2)  # give backend a moment
    fe = launch_frontend(fe_py)

    print("\n✅ All set!")
    print("Frontend: http://localhost:8080")
    print("Backend : http://localhost:8000/docs\n")

    try:
        # Wait on both; if either exits, we stop the other.
        while True:
            be_ret = be.poll()
            fe_ret = fe.poll()
            if be_ret is not None or fe_ret is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[stop] Shutting down ...")
    finally:
        for p in (fe, be):
            if p and p.poll() is None:
                p.terminate()

if __name__ == "__main__":
    main()
