"""Database helpers for storing requests, feedback, and service usage events."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from config import DB_PATH
from logger_config import logger


def current_timestamp() -> str:
    """Return the current UTC timestamp as an ISO 8601 string."""
    return datetime.now(UTC).isoformat()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Context manager to get a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def execute_insert(query: str, params: tuple[Any, ...]) -> int:
    """Execute an insert query and return the last inserted row ID."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid
    except sqlite3.Error:
        logger.exception("Database insert failed.")
        raise


def init_db() -> None:
    """Create tables if they don't exist."""
    try:
        with get_connection() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS requests
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             scheme_name TEXT,
                             source TEXT,
                             timestamp TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS feedback
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             request_id INTEGER,
                             rating INTEGER,
                             comment TEXT,
                             timestamp TEXT,
                             FOREIGN KEY (request_id) REFERENCES requests(id))''')
            
            # TODO: These tables are currently preserved for potential future features,
            # but their corresponding save helper functions were removed as they were dead code.
            conn.execute('''CREATE TABLE IF NOT EXISTS eligibility_checks
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_session TEXT,
                             scheme_name TEXT,
                             answers TEXT,
                             timestamp TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS document_checklist
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_session TEXT,
                             scheme_name TEXT,
                             documents_checked TEXT,
                             timestamp TEXT)''')
            
            conn.execute('''CREATE TABLE IF NOT EXISTS whatsapp_shares
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             scheme_name TEXT,
                             timestamp TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS staff_feedback
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             scheme_name TEXT,
                             village TEXT,
                             feedback_text TEXT,
                             issue_type TEXT,
                             timestamp TEXT)''')
            conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error:
        logger.exception("Failed to initialize database.")
        raise


def log_request(scheme_name: str, source: str) -> int:
    """Insert a new request and return its ID."""
    request_id = execute_insert(
        """
        INSERT INTO requests (
            scheme_name,
            source,
            timestamp
        )
        VALUES (?, ?, ?)
        """,
        (scheme_name, source, current_timestamp()),
    )
    logger.info(
        "Logged request: scheme='%s' source='%s' request_id=%s",
        scheme_name,
        source,
        request_id,
    )
    return request_id


def save_feedback(request_id: int, rating: int, comment: str) -> None:
    """Store user feedback."""
    execute_insert(
        """
        INSERT INTO feedback (
            request_id,
            rating,
            comment,
            timestamp
        )
        VALUES (?, ?, ?, ?)
        """,
        (request_id, rating, comment, current_timestamp()),
    )
    logger.info(
        "Saved feedback: request_id=%s rating=%s",
        request_id,
        status_code := rating,
    )


def log_whatsapp_share(scheme_name: str) -> None:
    """Log WhatsApp shares."""
    execute_insert(
        """
        INSERT INTO whatsapp_shares (
            scheme_name,
            timestamp
        )
        VALUES (?, ?)
        """,
        (scheme_name, current_timestamp()),
    )
    logger.info("Logged WhatsApp share: scheme='%s'", scheme_name)


def save_staff_feedback(scheme_name: str, village: str, feedback_text: str, issue_type: str) -> None:
    """Save staff/community worker feedback."""
    execute_insert(
        """
        INSERT INTO staff_feedback (
            scheme_name,
            village,
            feedback_text,
            issue_type,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (scheme_name, village, feedback_text, issue_type, current_timestamp()),
    )
    logger.info(
        "Saved staff feedback: scheme='%s' village='%s' issue_type='%s'",
        scheme_name,
        village,
        issue_type,
    )
