import sqlite3
from datetime import datetime, timedelta
import os
from config import PLANS

DATABASE_PATH = "subscriptions.db"

def init_db():
    """Initialize the database tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table with language column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            subscription_plan TEXT,
            subscription_expiry TEXT,
            is_active INTEGER DEFAULT 0,
            joined_at TEXT,
            last_active TEXT,
            language TEXT DEFAULT 'en'
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            amount REAL,
            currency TEXT,
            payment_method TEXT,
            transaction_id TEXT,
            status TEXT,
            created_at TEXT,
            verified_by INTEGER,
            verified_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(user_id):
    """Get user from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "user_id": user[0],
            "username": user[1],
            "first_name": user[2],
            "subscription_plan": user[3],
            "subscription_expiry": user[4],
            "is_active": user[5],
            "joined_at": user[6],
            "last_active": user[7],
            "language": user[8] if len(user) > 8 else 'en'
        }
    return None

def create_user(user_id, username, first_name, language='en'):
    """Create new user with language preference"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, is_active, joined_at, last_active, language)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, 0, datetime.now().isoformat(), datetime.now().isoformat(), language))
    conn.commit()
    conn.close()

def set_user_language(user_id, language):
    """Update user's language preference"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET language = ? WHERE user_id = ?
    ''', (language, user_id))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    """Get user's language preference"""
    user = get_user(user_id)
    return user['language'] if user else 'en'

# ... (keep all your other functions: activate_subscription, is_subscription_active, etc.)