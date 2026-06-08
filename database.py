import sqlite3
from datetime import datetime, timedelta
import os
from config import PLANS  # IMPORT PLANS FROM CONFIG

DATABASE_PATH = "subscriptions.db"

def init_db():
    """Initialize the database tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            subscription_plan TEXT,
            subscription_expiry TEXT,
            is_active INTEGER DEFAULT 0,
            joined_at TEXT,
            last_active TEXT
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
            "last_active": user[7]
        }
    return None

def create_user(user_id, username, first_name):
    """Create new user"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, is_active, joined_at, last_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, 0, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def activate_subscription(user_id, plan_key, transaction_id=None):
    """Activate subscription for user"""
    plan = PLANS[plan_key]
    expiry = None
    if plan["days"]:
        expiry = (datetime.now() + timedelta(days=plan["days"])).isoformat()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET subscription_plan = ?, subscription_expiry = ?, is_active = 1, last_active = ?
        WHERE user_id = ?
    ''', (plan["name"], expiry, datetime.now().isoformat(), user_id))
    
    # Update payment status if transaction_id provided
    if transaction_id:
        cursor.execute('''
            UPDATE payments 
            SET status = 'completed', verified_at = ?
            WHERE transaction_id = ? AND user_id = ?
        ''', (datetime.now().isoformat(), transaction_id, user_id))
    
    conn.commit()
    conn.close()

def is_subscription_active(user_id):
    """Check if user has active subscription"""
    user = get_user(user_id)
    if not user or not user["is_active"]:
        return False
    
    expiry = user["subscription_expiry"]
    if expiry:
        expiry_date = datetime.fromisoformat(expiry)
        if expiry_date < datetime.now():
            # Subscription expired
            deactivate_subscription(user_id)
            return False
    
    return True

def deactivate_subscription(user_id):
    """Deactivate expired subscription"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET is_active = 0
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

def add_payment_record(user_id, plan_key, amount, method, transaction_id):
    """Record payment in database"""
    try:
        # Get plan name from PLANS dictionary
        if plan_key not in PLANS:
            print(f"Warning: plan_key '{plan_key}' not found. Available: {list(PLANS.keys())}")
            plan_name = "Unknown Plan"
        else:
            plan_name = PLANS[plan_key]["name"]
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, plan, amount, currency, payment_method, transaction_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, plan_name, amount, "USD", method, transaction_id, "pending", datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"✅ Payment recorded: User {user_id}, Plan {plan_name}, Amount ${amount}")
        return cursor.lastrowid
    except Exception as e:
        print(f"❌ Error in add_payment_record: {e}")
        raise

def get_pending_payments():
    """Get all pending payments for admin"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.payment_id, p.user_id, p.plan, p.amount, p.payment_method, p.transaction_id, p.created_at, u.username, u.first_name
        FROM payments p
        JOIN users u ON p.user_id = u.user_id
        WHERE p.status = 'pending'
        ORDER BY p.created_at DESC
    ''')
    payments = cursor.fetchall()
    conn.close()
    return payments

def get_active_subscribers():
    """Get count of active subscribers"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE is_active = 1 
        AND (subscription_expiry IS NULL OR subscription_expiry > ?)
    ''', (datetime.now().isoformat(),))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_payments(user_id):
    """Get user's payment history"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT plan, amount, payment_method, transaction_id, status, created_at
        FROM payments
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments