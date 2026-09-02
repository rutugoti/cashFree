import requests
from requests.auth import HTTPBasicAuth
from uuid import uuid4
import logging
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

class RazorpayClient:
    def __init__(self):
        self.simulate = not bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)
        self.auth = HTTPBasicAuth(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        self.base_url = "https://api.razorpay.com/v1"

    def create_contact(self, name: str, ref_id: str) -> str:
        if self.simulate: return f"cont_sim_{uuid4().hex[:10]}"
        res = requests.post(f"{self.base_url}/contacts", auth=self.auth, json={
            "name": name,
            "type": "vendor",
            "reference_id": ref_id
        })
        res.raise_for_status()
        return res.json()["id"]
        
    def create_fund_account(self, contact_id: str) -> str:
        if self.simulate: return f"fa_sim_{uuid4().hex[:10]}"
        res = requests.post(f"{self.base_url}/fund_accounts", auth=self.auth, json={
            "contact_id": contact_id,
            "account_type": "bank_account",
            "bank_account": {
                "name": "Test Account",
                "ifsc": "RAZR0000001",
                "account_number": "11214311215411"
            }
        })
        res.raise_for_status()
        return res.json()["id"]

    def create_payout(self, payload: dict) -> dict:
        if self.simulate:
            return {
                "id": f"pout_sim_{uuid4().hex[:10]}",
                "status": "processed",
                "mode": payload["mode"],
                "amount": payload["amount"],
                "_simulated": True
            }
        res = requests.post(f"{self.base_url}/payouts", auth=self.auth, json=payload)
        res.raise_for_status()
        return res.json()

    def fetch_live_payments(self, limit=5) -> list:
        """Fetches real captured PG payments to act as T+2 inflows."""
        if self.simulate: return []
        try:
            res = requests.get(f"{self.base_url}/payments?status=captured&count={limit}", auth=self.auth)
            res.raise_for_status()
            return res.json().get("items", [])
        except Exception as e:
            import logging
            logging.error(f"Failed to fetch live payments: {e}")
            return []

    def get_balance(self) -> float:
        """Fetches the real RazorpayX test account balance (in Rupees)."""
        if self.simulate: return 180000.0
        try:
            res = requests.get(f"{self.base_url}/balance", auth=self.auth)
            res.raise_for_status()
            data = res.json()
            return data.get("balance", 0) / 100.0 # Convert paise to rupees
        except Exception as e:
            import logging
            logging.error(f"Failed to fetch balance: {e}")
            return 180000.0
