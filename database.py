# database.py
import sqlite3
from datetime import datetime
import os

DB_PATH = 'feedback.db'

def init_db():
    """Create tables if they don't exist."""
    with sqlite3.connect(DB_PATH) as conn:
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
        conn.execute('''CREATE TABLE IF NOT EXISTS local_locations
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         village TEXT,
                         location_type TEXT,
                         name TEXT,
                         contact TEXT,
                         address TEXT,
                         timestamp TEXT)''')
    print("✅ Database initialized (feedback.db)")

def log_request(scheme_name, source):
    """Insert a new request and return its ID."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO requests (scheme_name, source, timestamp) VALUES (?,?,?)",
                    (scheme_name, source, datetime.utcnow().isoformat()))
        return cur.lastrowid

def save_feedback(request_id, rating, comment):
    """Store user feedback."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO feedback (request_id, rating, comment, timestamp) VALUES (?,?,?,?)",
                     (request_id, rating, comment, datetime.utcnow().isoformat()))

def save_eligibility_check(user_session, scheme_name, answers):
    """Store eligibility checker responses."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO eligibility_checks (user_session, scheme_name, answers, timestamp) VALUES (?,?,?,?)",
                     (user_session, scheme_name, answers, datetime.utcnow().isoformat()))

def save_document_checklist(user_session, scheme_name, documents_checked):
    """Store document checklist progress."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO document_checklist (user_session, scheme_name, documents_checked, timestamp) VALUES (?,?,?,?)",
                     (user_session, scheme_name, documents_checked, datetime.utcnow().isoformat()))

def log_whatsapp_share(scheme_name):
    """Log WhatsApp shares."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO whatsapp_shares (scheme_name, timestamp) VALUES (?,?)",
                     (scheme_name, datetime.utcnow().isoformat()))

def save_staff_feedback(scheme_name, village, feedback_text, issue_type):
    """Save staff/community worker feedback."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO staff_feedback (scheme_name, village, feedback_text, issue_type, timestamp) VALUES (?,?,?,?,?)",
                     (scheme_name, village, feedback_text, issue_type, datetime.utcnow().isoformat()))