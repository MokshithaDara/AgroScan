import os
import sqlite3
import json
from datetime import datetime
from threading import Lock
from typing import Dict, List


_LOCK = Lock()
_DEFAULT_PATH = os.getenv("SQLITE_PATH", os.path.join("data", "agroscan.db"))


def get_sqlite_path() -> str:
    return os.getenv("SQLITE_PATH", _DEFAULT_PATH)


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _connect() -> sqlite3.Connection:
    path = get_sqlite_path()
    _ensure_parent(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _LOCK:
        with _connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    disease TEXT NOT NULL,
                    treatment TEXT DEFAULT '',
                    treatment_steps TEXT DEFAULT '[]',
                    products_recommended TEXT DEFAULT '[]'
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_scans_user_date ON scans(user_id, date DESC)"
            )
            conn.commit()


def append_scan(record: Dict) -> None:
    init_db()
    with _LOCK:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO scans (
                    user_id, date, location, disease, treatment, treatment_steps, products_recommended
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.get("user_id", ""),
                    str(record.get("date") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                    record.get("location", ""),
                    record.get("disease", ""),
                    record.get("treatment", ""),
                    json.dumps(record.get("treatment_steps", []), ensure_ascii=False),
                    json.dumps(record.get("products_recommended", []), ensure_ascii=False),
                ),
            )
            conn.commit()


def _safe_parse_list(value: str) -> List[str]:
    value = (value or "").strip()
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            parts = [p.strip().strip("'").strip('"') for p in inner.split(",")]
            return [p for p in parts if p]
        return []
    return []


def read_user_scans(user_id: str) -> List[Dict]:
    init_db()
    with _LOCK:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id, date, location, disease, treatment, treatment_steps, products_recommended
                FROM scans
                WHERE user_id = ?
                ORDER BY date DESC
                """,
                (user_id,),
            ).fetchall()

    output: List[Dict] = []
    for row in rows:
        output.append(
            {
                "user_id": row["user_id"],
                "date": row["date"],
                "location": row["location"],
                "disease": row["disease"],
                "treatment": row["treatment"] or "",
                "treatment_steps": _safe_parse_list(row["treatment_steps"]),
                "products_recommended": _safe_parse_list(row["products_recommended"]),
            }
        )
    return output
