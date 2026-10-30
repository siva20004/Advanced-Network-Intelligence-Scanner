import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os

# Single, predictable DB location relative to this file
DB_PATH = Path(__file__).parent / "scan_history.db"


def ensure_db():
    # If file exists but is read-only, make it writable
    if DB_PATH.exists():
        try:
            os.chmod(DB_PATH, 0o666)
        except Exception:
            pass
    # Ensure parent dir exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    ensure_db()
    # Open in read-write-create mode
    return sqlite3.connect(str(DB_PATH), timeout=10)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            result TEXT,
            timestamp TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_scan(target, result):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scans (target, result, timestamp) VALUES (?, ?, ?)",
        (target, json.dumps(result), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def clear_scans():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans")
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='scans'")
    except sqlite3.Error:
        pass
    conn.commit()
    conn.close()


def get_scan_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            result TEXT,
            timestamp TEXT
        )
        """
    )
    cursor.execute("SELECT COUNT(*) FROM scans")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def hard_reset_database():
    # try to remove the file; if locked, fall back to dropping table
    try:
        if DB_PATH.exists():
            os.chmod(DB_PATH, 0o666)
            DB_PATH.unlink()
    except Exception:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS scans")
        conn.commit()
        conn.close()
    init_db()

