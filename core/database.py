import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "history.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            snippet TEXT,
            fit_score INTEGER,
            status TEXT,
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_application(title, url, snippet, fit_score, status="Saved"):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO applications (title, url, snippet, fit_score, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, url, snippet, fit_score, status))
    conn.commit()
    conn.close()

def get_applications():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM applications ORDER BY applied_date DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_status(app_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE applications SET status = ? WHERE id = ?', (status, app_id))
    conn.commit()
    conn.close()
