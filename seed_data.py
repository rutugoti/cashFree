from datetime import datetime, timedelta
import random
from database import init_db, execute_query
from razorpay_client import RazorpayClient

def generate_dates(start_date, days):
    return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

def seed_data():
    # Re-initialize DB
    init_db()
    
    today = datetime.now()
    dates = generate_dates(today, 8) # Need T+7
    
    # FETCH LIVE RAZORPAY PG DATA
    rzp = RazorpayClient()
    live_payments = rzp.fetch_live_payments(limit=5)
    live_settlements = []
    live_total = 0.0
    
    for pay in live_payments:
        # Dynamically calculate exact T+2 from the real payment timestamp
        created_ts = pay.get("created_at")
        if created_ts:
            settlement_dt = datetime.fromtimestamp(created_ts) + timedelta(days=2)
            settlement_date_str = settlement_dt.strftime("%Y-%m-%d")
        else:
            settlement_date_str = (today + timedelta(days=2)).strftime("%Y-%m-%d")

        amt = pay.get("amount", 0) / 100.0
        live_total += amt
        live_settlements.append(
            (pay["id"], settlement_date_str, amt, pay.get("method", "card"), "projected (T+2)", "RAZORPAY_TEST")
        )

    # 1. Seed Settlements
    synthetic_settlements = [
        # Day 1 - Math Protector: reduce STL-001 by the total live payments arriving on Day 3.
        # This keeps the cumulative cash exactly the same by Day 3, preserving the deep crunch!
        ("STL-001", dates[1], max(0, 42000 - live_total), "upi", "expected", "SYNTHETIC"),
        ("STL-002", dates[1], 18000, "card", "expected", "SYNTHETIC"),
        ("STL-003", dates[1], 8000, "netbanking", "expected", "SYNTHETIC"),
        # Day 2
        ("STL-004", dates[2], 38000, "upi", "expected", "SYNTHETIC"),
        ("STL-005", dates[2], 52000, "card", "expected", "SYNTHETIC"),
        ("STL-006", dates[2], 12000, "netbanking", "expected", "SYNTHETIC"),
        # Day 3 (CRUNCH - drastically reduced to force a deep negative balance)
        ("STL-007", dates[3], 15000, "upi", "expected", "SYNTHETIC"),
        ("STL-008", dates[3], 5000, "card", "expected", "SYNTHETIC"),
        ("STL-009", dates[3], 2000, "netbanking", "expected", "SYNTHETIC"),
        # Day 4
        ("STL-010", dates[4], 48000, "upi", "expected", "SYNTHETIC"),
        ("STL-011", dates[4], 65000, "card", "expected", "SYNTHETIC"),
        ("STL-012", dates[4], 15000, "netbanking", "expected", "SYNTHETIC"),
        # Day 5
        ("STL-013", dates[5], 40000, "upi", "expected", "SYNTHETIC"),
        ("STL-014", dates[5], 22000, "card", "expected", "SYNTHETIC"),
        ("STL-015", dates[5], 10000, "netbanking", "expected", "SYNTHETIC"),
        # Day 6
        ("STL-016", dates[6], 15000, "upi", "expected", "SYNTHETIC"),
        # Day 7
        ("STL-017", dates[7], 12000, "upi", "expected", "SYNTHETIC"),
    ]
    
    # Insert Live PG Data
    for s in live_settlements:
        execute_query("INSERT INTO settlements (id, date, amount, source, status, data_source) VALUES (?, ?, ?, ?, ?, ?)", s)
        
    # Insert Synthetic Data
    for s in synthetic_settlements:
        execute_query("INSERT INTO settlements (id, date, amount, source, status, data_source) VALUES (?, ?, ?, ?, ?, ?)", s)

    print(f"Seeded {len(live_settlements)} live Razorpay PG payments and {len(synthetic_settlements)} synthetic settlements.")

    # 2. Seed Payouts
    payouts = []
    
    # --- CRITICAL (Day 1-2) ---
    payouts.extend([
        ("PO-001", "Amit Shah (Employee)", "Monthly salary, employment contract, cannot delay", 15000, dates[1], dates[1], "IMPS"),
        ("PO-002", "Neha Gupta (Employee)", "Monthly salary, contractual obligation", 15000, dates[1], dates[1], "IMPS"),
        ("PO-003", "Suresh Kumar (Employee)", "Salary for August", 15000, dates[1], dates[1], "IMPS"),
        ("PO-004", "Riya Verma (Employee)", "Salary for August", 15000, dates[1], dates[1], "IMPS"),
        ("PO-005", "Anjali D (Employee)", "Salary for August", 15000, dates[1], dates[1], "IMPS"),
        ("PO-006", "WeWork India", "Office rent, late fee Rs500/day after due date", 35000, dates[1], dates[1], "IMPS"),
        ("PO-007", "GST Dept", "Statutory GST filing, government deadline, penalty on delay", 28000, dates[2], dates[2], "IMPS"),
        ("PO-008", "AWS India", "Cloud hosting bill, service suspension on non-payment within 48h", 47000, dates[2], dates[2], "IMPS"),
    ])
    
    # --- STANDARD (Days 2-5) ---
    standard_contexts = [
        "Supplier invoice #442, standard NET-30 terms apply",
        "Raw materials bulk order, agreed to pay within 30 days",
        "Quarterly software license renewal, normal SLA",
        "Marketing agency retainer, invoice due this week",
        "Logistics partner weekly settlement, standard priority",
        "Packaging boxes supply, B2B invoice terms",
        "Inventory restocking, standard payment window",
        "Office supplies delivery, NET-15 payment terms",
        "Consultancy fee, invoice submitted last week",
        "Legal services retainer, standard processing",
        "Internet broadband corporate plan, due date tomorrow",
        "Water delivery subscription, standard billing",
        "Pest control services, normal invoice processing",
        "Cleaning staff agency fee, monthly regular",
        "Corporate catering, standard NET-30 terms",
        "IT hardware purchase, standard 30 day SLA",
        "Printers and ink supply, regular vendor",
        "Courier and shipping charges, standard billing",
        "Social media ad spend agency fee",
        "Warehouse rent, regular monthly SLA",
        "Security guard agency, standard priority",
        "Vehicle maintenance fleet, regular invoice",
        "Air conditioning service, standard NET-30",
        "Corporate gifting vendor, regular terms",
        "Event management partial payment, standard SLA"
    ]
    
    po_id = 9
    standard_distributions = [(dates[2], 4), (dates[3], 15), (dates[4], 4), (dates[5], 2)]
    
    random.seed(42) # For reproducible amounts
    sc_idx = 0
    for dt, count in standard_distributions:
        for _ in range(count):
            amount = random.randint(30, 200) * 100 # 3000 to 20000
            payouts.append((
                f"PO-{po_id:03d}", 
                f"Vendor Supplier {po_id}", 
                standard_contexts[sc_idx], 
                amount, dt, dt, "IMPS"
            ))
            po_id += 1
            sc_idx += 1
            
    # --- FLEXIBLE (Days 3-7) ---
    flexible_contexts = [
        "Freelance logo design, no hard deadline",
        "Blog post writing, flexible timing, relationship based",
        "Photography shoot edit, told them we'll pay sometime this week",
        "Casual consulting advice, pay whenever",
        "Intern stipend, flexible up to 5 days",
        "Reimbursement for team lunch, no rush",
        "One-off UI tweak by freelancer, flexible",
        "Translation services, no strict SLA",
        "Data entry gig, happy to wait a few days",
        "Voiceover artist, agreed to flexible payout",
        "Custom illustration, no hard deadline",
        "Video editing for social, flexible terms",
        "Proofreading document, pay when convenient",
        "Research assistant hourly gig, no rush",
        "Beta testing compensation, flexible",
        "Referral bonus, no strict timeline",
        "Guest post contribution, pay anytime this week",
        "Feedback interview participant, flexible",
        "Local errand runner, no rush on payment",
        "Minor script bug fix by external dev, pay whenever"
    ]
    
    flexible_distributions = [(dates[3], 8), (dates[4], 5), (dates[5], 4), (dates[6], 3)]
    fc_idx = 0
    for dt, count in flexible_distributions:
        for _ in range(count):
            amount = random.randint(10, 80) * 100 # 1000 to 8000
            payouts.append((
                f"PO-{po_id:03d}", 
                f"Freelancer / Sub {po_id}", 
                flexible_contexts[fc_idx], 
                amount, dt, dt, "IMPS"
            ))
            po_id += 1
            fc_idx += 1
            
    # Realistic CRITICAL bill to counteract the 8 Lakh cash pile and cause a minor 17k crunch on Day 3
    payouts.append(("PO-054", "Income Tax Dept", "Q2 Advance Tax - Government Deadline, penalties on delay", 600000, dates[3], dates[3], "IMPS"))
            
    # Insert Payouts
    for p in payouts:
        execute_query(
            "INSERT INTO payouts (id, vendor_name, vendor_context, amount, due_date, original_date, original_mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
            p
        )
        
    print(f"Seeded {len(live_settlements)} live and {len(synthetic_settlements)} synthetic settlements, and {len(payouts)} payouts.")

if __name__ == "__main__":
    seed_data()
