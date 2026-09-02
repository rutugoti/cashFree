from datetime import datetime
from database import execute_query, fetch_all

def log_audit(action: str, details: str, payout_id: str = None, fee_saved: float = 0.0):
    timestamp = datetime.now().isoformat()
    execute_query('''
        INSERT INTO audit_log (timestamp, payout_id, action, details, fee_saved)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, payout_id, action, details, fee_saved))

def get_audit_logs():
    return fetch_all("SELECT * FROM audit_log ORDER BY id DESC")

