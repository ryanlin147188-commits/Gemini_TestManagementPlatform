import aiosqlite
import json
import os
from pathlib import Path

# Database path
try:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
except NameError:
    ROOT_DIR = Path(os.getcwd())

DATA_DIR = os.getenv("DATA_DIR", ROOT_DIR / "data")
Path(DATA_DIR).mkdir(exist_ok=True)
DB_FILE = Path(DATA_DIR) / "platform.db"

async def get_db_connection():
    """Creates an async connection to the SQLite database."""
    conn = await aiosqlite.connect(DB_FILE)
    conn.row_factory = aiosqlite.Row  # Use aiosqlite's Row factory
    return conn

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DB_FILE) as conn:
        # --- Projects Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            owner TEXT,
            status TEXT
        );
        """)

        # --- Web Test Cases Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS web_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            test_feature TEXT,
            test_step TEXT,
            action TEXT,
            description TEXT,
            page TEXT,
            element TEXT,
            value TEXT,
            result TEXT,
            note TEXT,
            review TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """)

        # --- App Test Cases Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS app_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            test_feature TEXT,
            test_step TEXT,
            action TEXT,
            description TEXT,
            page TEXT,
            element TEXT,
            value TEXT,
            result TEXT,
            note TEXT,
            review TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """)

        # --- API Test Cases Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS api_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            step INTEGER,
            test_feature TEXT,
            method TEXT,
            url TEXT,
            api_path TEXT,
            header TEXT,
            body TEXT,
            expected_status TEXT,
            expected_field TEXT,
            expected_value TEXT,
            result TEXT,
            summary TEXT,
            note TEXT,
            review TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """)

        # --- Bugs Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            severity TEXT,
            status TEXT,
            repro TEXT,
            expected TEXT,
            actual TEXT,
            note TEXT,
            screenshot TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """)

        # --- Mocks Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS mocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            method TEXT NOT NULL,
            params TEXT, -- Stored as JSON string
            headers TEXT, -- Stored as JSON string
            body TEXT,
            response_status INTEGER,
            response_headers TEXT, -- Stored as JSON string
            response_body TEXT,
            delay_ms INTEGER
        );
        """)

        # --- App Device Info Table ---
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS app_device_info (
            project_id INTEGER PRIMARY KEY,
            device_info TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """)

        await conn.commit()
