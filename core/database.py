import os
import json
import hashlib
import psycopg2
import psycopg2.extras

def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("WARNING: DATABASE_URL not set!")
        # Fallback for local testing if needed, though it will crash without DB
        return None
    
    conn = psycopg2.connect(db_url)
    return conn

def initialize_db():
    conn = get_connection()
    if not conn: return
    c = conn.cursor()
    # Users Table (Now with resume_file as BYTEA)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            profile_data TEXT,
            resume_name TEXT,
            resume_file BYTEA
        )
    ''')
    # Global Jobs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
        c.execute("INSERT INTO users (username, password_hash, profile_data) VALUES (%s, %s, %s)", 
                  (username, hash_password(password), json.dumps({"personal_details": {}, "target_titles": [], "skills": []})))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s", (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user['id'] if user else None

def get_user_profile(user_id):
    conn = get_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT profile_data, resume_name, resume_file FROM users WHERE id = %s", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row['profile_data'] or "{}"), row['resume_name'], row['resume_file']
    return {}, None, None

def update_user_profile(user_id, profile_data, resume_name=None, resume_bytes=None):
    conn = get_connection()
    c = conn.cursor()
    if resume_bytes is not None:
        c.execute("UPDATE users SET profile_data = %s, resume_name = %s, resume_file = %s WHERE id = %s", 
                  (json.dumps(profile_data), resume_name, psycopg2.Binary(resume_bytes), user_id))
    else:
        c.execute("UPDATE users SET profile_data = %s WHERE id = %s", (json.dumps(profile_data), user_id))
    conn.commit()
    conn.close()

# --- JOB MANAGEMENT ---
def add_global_job(title, url, company="Unknown", snippet="", source="Manual"):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO jobs (title, company, url, snippet, source) VALUES (%s, %s, %s, %s, %s)", 
                  (title, company, url, snippet, source))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        pass # Job already exists
    finally:
        conn.close()

def get_global_jobs(limit=100):
    conn = get_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM jobs ORDER BY discovered_date DESC LIMIT %s", (limit,))
    jobs = [dict(row) for row in c.fetchall()]
    conn.close()
    return jobs

def save_job_for_user(user_id, job_id, fit_score=0, reasoning=""):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO user_jobs (user_id, job_id, status, fit_score, reasoning) 
                     VALUES (%s, %s, 'Saved', %s, %s)''', (user_id, job_id, fit_score, reasoning))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        # Update if already exists
        c.execute("UPDATE user_jobs SET fit_score = %s, reasoning = %s WHERE user_id = %s AND job_id = %s", 
                  (fit_score, reasoning, user_id, job_id))
        conn.commit()
    finally:
        conn.close()

def get_user_applications(user_id):
    conn = get_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute('''
        SELECT uj.id as uj_id, uj.status, uj.fit_score, uj.reasoning, uj.applied_date, j.* 
        FROM user_jobs uj 
        JOIN jobs j ON uj.job_id = j.id 
        WHERE uj.user_id = %s
        ORDER BY uj.id DESC
    ''', (user_id,))
    apps = [dict(row) for row in c.fetchall()]
    conn.close()
    return apps

def update_user_job_status(uj_id, status):
    conn = get_connection()
    c = conn.cursor()
    if status == "Applied":
        c.execute("UPDATE user_jobs SET status = %s, applied_date = CURRENT_TIMESTAMP WHERE id = %s", (status, uj_id))
    else:
        c.execute("UPDATE user_jobs SET status = %s WHERE id = %s", (status, uj_id))
    conn.commit()
    conn.close()
