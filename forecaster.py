from database import fetch_all, execute_query
from razorpay_client import RazorpayClient

# Cache the balance in memory so we don't spam the API during the optimization loop
_cached_balance = None

def clear_cache():
    global _cached_balance
    _cached_balance = None

def get_forecast():
    global _cached_balance
    if _cached_balance is None:
        _cached_balance = RazorpayClient().get_balance()
        
    # Get settlements grouped by date
    settlements = fetch_all("SELECT date, SUM(amount) as total FROM settlements GROUP BY date ORDER BY date")
    inflows_by_date = {s['date']: s['total'] for s in settlements}
    
    # Before Optimization: group by original_date
    payouts_before = fetch_all("SELECT original_date, SUM(amount) as total FROM payouts GROUP BY original_date")
    outflows_before_dict = {p['original_date']: p['total'] for p in payouts_before}
    
    # After Optimization: group by scheduled_date (fallback to original_date if not set)
    payouts_after = fetch_all("SELECT COALESCE(scheduled_date, original_date) as exec_date, SUM(amount) as total FROM payouts GROUP BY exec_date")
    outflows_after_dict = {p['exec_date']: p['total'] for p in payouts_after}
    
    # Get unique dates sorted
    all_dates = sorted(list(set(
        list(inflows_by_date.keys()) + 
        list(outflows_before_dict.keys()) + 
        list(outflows_after_dict.keys())
    )))
    
    balance_before = _cached_balance
    balance_after = _cached_balance
    
    execute_query("DELETE FROM cash_forecast")
    
    forecasts = []
    
    for date in all_dates:
        inflows = inflows_by_date.get(date, 0.0)
        
        outflows_before = outflows_before_dict.get(date, 0.0)
        outflows_after = outflows_after_dict.get(date, 0.0)
        
        closing_before = balance_before + inflows - outflows_before
        closing_after = balance_after + inflows - outflows_after
        
        is_crunch = 1 if closing_before < 0 else 0
        is_crunch_after = 1 if closing_after < 0 else 0
        
        forecast = (date, balance_before, inflows, outflows_before, outflows_after, closing_before, closing_after, is_crunch, is_crunch_after)
        execute_query('''
        INSERT INTO cash_forecast 
        (date, opening_balance, inflows, outflows_before, outflows_after, closing_before, closing_after, is_crunch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, balance_before, inflows, outflows_before, outflows_after, closing_before, closing_after, is_crunch))
        
        # Keep list as tuple for backwards compatibility with existing returns (date, open, in, out_b, out_a, close_b, close_a, crunch)
        forecasts.append(forecast)
        
        balance_before = closing_before
        balance_after = closing_after
        
    return forecasts

if __name__ == "__main__":
    res = get_forecast()
    print("7-Day Forecast:")
    for r in res:
        print(f"{r[0]} | In: {r[2]:.2f} | Out(B): {r[3]:.2f} | Close(B): {r[5]:.2f} | Out(A): {r[4]:.2f} | Close(A): {r[6]:.2f} | Crunch: {'YES' if r[7] else 'NO'}")
