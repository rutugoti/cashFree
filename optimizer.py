from database import fetch_all, execute_query
from config import FEES, MAX_RESCHEDULE_DAYS
from forecaster import get_forecast
from datetime import datetime, timedelta
from audit import log_audit

def date_diff_days(d1_str: str, d2_str: str) -> int:
    d1 = datetime.strptime(d1_str, "%Y-%m-%d")
    d2 = datetime.strptime(d2_str, "%Y-%m-%d")
    return (d1 - d2).days

def add_days(d_str: str, days: int) -> str:
    d = datetime.strptime(d_str, "%Y-%m-%d")
    return (d + timedelta(days=days)).strftime("%Y-%m-%d")

def optimize_payouts():
    payouts = fetch_all("SELECT * FROM payouts WHERE status = 'pending'")
    if not payouts:
        return {"rerouted_count": 0, "rescheduled_count": 0, "fee_saved": 0.0, "crunches_left": 0}

    # Step 3a: Mode Selection (Fee Optimization)
    rerouted = 0
    total_fee_saved = 0.0
    
    for p in payouts:
        mode = "IMPS" # default fallback
        urgency = p["urgency"]
        amount = p["amount"]
        
        if urgency == "CRITICAL":
            mode = "IMPS"
        elif amount <= 5000:
            mode = "UPI"
        elif urgency in ["FLEXIBLE", "STANDARD"]:
            mode = "NEFT"
            
        fee_original = FEES.get(p["original_mode"], 150.0)
        fee_optimized = FEES.get(mode, 150.0)
        fee_saved = max(0.0, fee_original - fee_optimized)
        
        if mode != p["original_mode"]:
            rerouted += 1
            log_audit("rerouted", f"Rerouted from {p['original_mode']} to {mode} saving Rs.{fee_saved}", p["id"], fee_saved)
            
        total_fee_saved += fee_saved
        
        # Initially scheduled_date = original_date
        execute_query('''
            UPDATE payouts 
            SET optimized_mode = ?, scheduled_date = original_date, 
                fee_original = ?, fee_optimized = ?, fee_saved = ?
            WHERE id = ?
        ''', (mode, fee_original, fee_optimized, fee_saved, p["id"]))

    # Step 3b: Rescheduling (Crunch Prevention)
    rescheduled = 0
    
    # We allow moving multiple payouts, up to a sensible limit to prevent infinite loops
    for _ in range(50): 
        forecasts = get_forecast()
        crunches = [f for f in forecasts if f[8] == 1]
        
        if not crunches:
            break
            
        crunch_day = crunches[0]
        crunch_date = crunch_day[0]
        
        # Find FLEXIBLE payouts scheduled for this day
        flex_payouts = fetch_all("SELECT * FROM payouts WHERE scheduled_date = ? AND urgency = 'FLEXIBLE' ORDER BY amount DESC", (crunch_date,))
        
        if not flex_payouts:
            # Try standard
            std_payouts = fetch_all("SELECT * FROM payouts WHERE scheduled_date = ? AND urgency = 'STANDARD' ORDER BY amount DESC", (crunch_date,))
            for p in std_payouts:
                if date_diff_days(crunch_date, p["original_date"]) < 2:
                    flex_payouts.append(p)
                    
        if not flex_payouts:
            print(f"Cannot resolve crunch on {crunch_date} - no movable payouts.")
            break
            
        p_to_move = flex_payouts[0]
        new_date = add_days(crunch_date, 1)
        
        if date_diff_days(new_date, p_to_move["original_date"]) > MAX_RESCHEDULE_DAYS:
            print(f"Cannot move {p_to_move['id']} further than {MAX_RESCHEDULE_DAYS} days.")
            # Remove from list of movable for this iteration by marking it somehow (in this simple script we might get stuck, so let's just break for MVP or pick the next one)
            if len(flex_payouts) > 1:
                p_to_move = flex_payouts[1]
            else:
                break
                
        execute_query("UPDATE payouts SET scheduled_date = ? WHERE id = ?", (new_date, p_to_move["id"]))
        rescheduled += 1
        
        # Calculate new forecast to show impact
        new_forecasts = get_forecast()
        new_crunch_day = [f for f in new_forecasts if f[0] == crunch_date][0]
        new_balance = new_crunch_day[5] # closing_before of that day after this move
        
        msg = f"Rescheduled Rs.{p_to_move['amount']} from {crunch_date} to {new_date}. Helped prevent {crunch_date} shortfall. New balance: Rs.{new_balance}"
        log_audit("rescheduled", msg, p_to_move["id"], 0.0)
        print(f"Rescheduled {p_to_move['id']} ({p_to_move['vendor_name']}, Rs.{p_to_move['amount']}) from {crunch_date} to {new_date}")

    final_forecasts = get_forecast()
    crunches_left = sum([1 for f in final_forecasts if f[8] == 1])
    
    return {
        "rerouted_count": rerouted,
        "rescheduled_count": rescheduled,
        "fee_saved": total_fee_saved,
        "crunches_left": crunches_left
    }

if __name__ == "__main__":
    res = optimize_payouts()
    print("Optimization Results:")
    print(res)
    fc = get_forecast()
    for r in fc:
        print(f"{r[0]} | Close: {r[5]:.2f} | Crunch: {'YES' if r[7] else 'NO'}")
