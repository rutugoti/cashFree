from seed_data import seed_data
from forecaster import get_forecast
from database import fetch_all

# 1. Verify the financial math
seed_data()
fc = get_forecast()

print('=== FINANCIAL VERIFICATION ===')
total_settlements = sum(s['amount'] for s in fetch_all('SELECT amount FROM settlements'))
total_payouts = sum(p['amount'] for p in fetch_all('SELECT amount FROM payouts'))
print(f'Total settlements (7 days): Rs.{total_settlements:,.0f}')
print(f'Total payouts (53 vendors): Rs.{total_payouts:,.0f}')
print(f'Starting balance: Rs.180,000')
print(f'Net position: Rs.{180000 + total_settlements - total_payouts:,.0f}')
print()

# 2. Verify crunch scenario
print('=== DAY-BY-DAY FORECAST (Before Optimization) ===')
for i, r in enumerate(fc):
    marker = ' <<<< CRUNCH' if r[7] == 1 else ''
    print(f'Day {i+1}: In={r[2]:>8,.0f}  Out={r[3]:>8,.0f}  Close={r[5]:>10,.0f}{marker}')
print()

# 3. Verify vendor contexts are diverse enough for AI
payouts = fetch_all('SELECT id, vendor_name, vendor_context FROM payouts LIMIT 10')
print('=== SAMPLE VENDOR CONTEXTS (what Gemini sees) ===')
for p in payouts:
    print(f"{p['id']}: {p['vendor_name']} -> '{p['vendor_context']}'")
print()

# 4. Count unique vendor contexts
contexts = set(p['vendor_context'] for p in fetch_all('SELECT vendor_context FROM payouts'))
print(f'Unique vendor_context strings: {len(contexts)}')
for c in contexts:
    count = len(fetch_all('SELECT id FROM payouts WHERE vendor_context = ?', (c,)))
    print(f'  "{c[:60]}" x{count}')
