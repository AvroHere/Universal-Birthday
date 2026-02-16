import sqlite3
import json
from datetime import datetime

DB_NAME = "birthday.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Added custom_text column
    c.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            slug TEXT PRIMARY KEY,
            name TEXT,
            dob_text TEXT,
            age_text TEXT,
            theme_key TEXT,
            photo_ids TEXT,
            audio_id TEXT,
            custom_text TEXT, 
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_page(slug, name, dob_text, age_text, theme_key, photo_ids, audio_id, custom_text):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO pages 
        (slug, name, dob_text, age_text, theme_key, photo_ids, audio_id, custom_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (slug, name, dob_text, age_text, theme_key, json.dumps(photo_ids), audio_id, custom_text, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_page(slug):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM pages WHERE slug = ?', (slug,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
