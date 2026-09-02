import sqlite3
import os
from config import DB_PATH
from typing import List, Dict

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use DROP TABLE instead of os.remove to prevent Windows file locking errors in Streamlit
    cursor.execute('DROP TABLE IF EXISTS settlements')
    cursor.execute('DROP TABLE IF EXISTS payouts')
    cursor.execute('DROP TABLE IF EXISTS cash_forecast')
    cursor.execute('DROP TABLE IF EXISTS audit_log')
    
    cursor.execute('''
    CREATE TABLE settlements (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        source TEXT NOT NULL,
        status TEXT DEFAULT 'expected',
        data_source TEXT DEFAULT 'SYNTHETIC'
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE payouts (
        id TEXT PRIMARY KEY,
        vendor_name TEXT NOT NULL,
        vendor_context TEXT NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        urgency TEXT,
        urgency_reason TEXT,
        original_mode TEXT DEFAULT 'IMPS',
        optimized_mode TEXT,
        original_date TEXT,
        scheduled_date TEXT,
        fee_original REAL DEFAULT 0.0,
        fee_optimized REAL DEFAULT 0.0,
        fee_saved REAL DEFAULT 0.0,
        status TEXT DEFAULT 'pending',
        razorpay_contact_id TEXT,
        razorpay_fund_account_id TEXT,
        razorpay_payout_id TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE cash_forecast (
        date TEXT PRIMARY KEY,
        opening_balance REAL NOT NULL,
        inflows REAL NOT NULL,
        outflows_before REAL NOT NULL,
        outflows_after REAL NOT NULL,
        closing_before REAL NOT NULL,
        closing_after REAL NOT NULL,
        is_crunch INTEGER DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        payout_id TEXT,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        fee_saved REAL DEFAULT 0.0,
        FOREIGN KEY(payout_id) REFERENCES payouts(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def execute_query(query: str, params: tuple = ()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query: str, params: tuple = ()) -> List[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")

