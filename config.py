import os
from dotenv import load_dotenv

load_dotenv()

# Database
DB_PATH = "cashpilot.db"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAYX_ACCOUNT_NUMBER = os.getenv("RAZORPAYX_ACCOUNT_NUMBER", "")

# AI Models
GEMINI_MODEL = "gemini-2.5-flash"

# Financial Guardrails
STARTING_BALANCE = 180000.0
MAX_RESCHEDULE_DAYS = 5
MAX_AUTO_EXECUTE_AMOUNT = 100000.0

# Fee Table (Realistic RazorpayX / Banking fees)
FEES = {
    "IMPS": 15.0,
    "NEFT": 5.0,
    "UPI": 0.0
}
