import sqlite3
import os
import json
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "saas.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    c = conn.cursor()
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            profile_data TEXT,
            resume_path TEXT
        )
    ''')
    # Global Jobs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            url TEXT UNIQUE NOT NULL,
            snippet TEXT,
            source TEXT,
            discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # User-Job Mapping Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_id INTEGER,
            status TEXT DEFAULT 'Saved',
            fit_score INTEGER,
            reasoning TEXT,
            applied_date TIMESTAMP,
            UNIQUE(user_id, job_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
    ''')
    conn.commit()
    conn.close()

# --- USER AUTHENTICATION ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, profile_data) VALUES (?, ?, ?)", 
                  (username, hash_password(password), json.dumps({"personal_details": {}, "target_titles": [], "skills": []})))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user['id'] if user else None

def get_user_profile(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT profile_data, resume_path FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row['profile_data'] or "{}"), row['resume_path']
    return {}, None

def update_user_profile(user_id, profile_data, resume_path=None):
    conn = get_connection()
    c = conn.cursor()
    if resume_path is not None:
        c.execute("UPDATE users SET profile_data = ?, resume_path = ? WHERE id = ?", (json.dumps(profile_data), resume_path, user_id))
    else:
        c.execute("UPDATE users SET profile_data = ? WHERE id = ?", (json.dumps(profile_data), user_id))
    conn.commit()
    conn.close()

# --- JOB MANAGEMENT ---
def add_global_job(title, url, company="Unknown", snippet="", source="Manual"):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO jobs (title, company, url, snippet, source) VALUES (?, ?, ?, ?, ?)", 
                  (title, company, url, snippet, source))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Job already exists in global pool
    finally:
        conn.close()

def get_global_jobs(limit=100):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM jobs ORDER BY discovered_date DESC LIMIT ?", (limit,))
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jobs

def save_job_for_user(user_id, job_id, fit_score=0, reasoning=""):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO user_jobs (user_id, job_id, status, fit_score, reasoning) 
                     VALUES (?, ?, 'Saved', ?, ?)''', (user_id, job_id, fit_score, reasoning))
        conn.commit()
    except sqlite3.IntegrityError:
        # Update if already exists
        c.execute("UPDATE user_jobs SET fit_score = ?, reasoning = ? WHERE user_id = ? AND job_id = ?", 
                  (fit_score, reasoning, user_id, job_id))
        conn.commit()
    finally:
        conn.close()

def get_user_applications(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT uj.id as uj_id, uj.status, uj.fit_score, uj.reasoning, uj.applied_date, j.* 
        FROM user_jobs uj 
        JOIN jobs j ON uj.job_id = j.id 
        WHERE uj.user_id = ?
        ORDER BY uj.id DESC
    ''', (user_id,))
    apps = [dict(row) for row in c.fetchall()]
    conn.close()
    return apps

def update_user_job_status(uj_id, status):
    conn = get_connection()
    c = conn.cursor()
    if status == "Applied":
        c.execute("UPDATE user_jobs SET status = ?, applied_date = CURRENT_TIMESTAMP WHERE id = ?", (status, uj_id))
    else:
        c.execute("UPDATE user_jobs SET status = ? WHERE id = ?", (status, uj_id))
    conn.commit()
    conn.close()
