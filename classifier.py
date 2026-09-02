import json
from google import genai
from google.genai import types
from database import fetch_all, execute_query
from config import GEMINI_API_KEY, GEMINI_MODEL
import logging

logging.basicConfig(level=logging.INFO)

def fallback_classify(payout: dict) -> dict:
    context = payout["vendor_context"].lower()
    if any(w in context for w in ["payroll", "salary", "rent", "tax", "gst", "emi", "statutory", "cannot delay"]):
        return {"id": payout["id"], "urgency": "CRITICAL", "reason": "[FALLBACK] Critical keyword found"}
    if any(w in context for w in ["no rush", "flexible", "whenever", "no deadline", "no hard deadline"]):
        return {"id": payout["id"], "urgency": "FLEXIBLE", "reason": "[FALLBACK] Flexible keyword found"}
    return {"id": payout["id"], "urgency": "STANDARD", "reason": "[FALLBACK] Standard SLA assumed"}

def classify_payouts():
    payouts = fetch_all("SELECT id, vendor_name, vendor_context, amount, due_date FROM payouts WHERE urgency IS NULL")
    if not payouts:
        return []
        
    if not GEMINI_API_KEY:
        logging.warning("No GEMINI_API_KEY found, using fallback classifier.")
        results = [fallback_classify(p) for p in payouts]
    else:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            prompt = """
            You are a financial operations AI for an Indian SME.
            Classify each vendor payout urgency.

            Rules:
            - CRITICAL: Payroll, rent, statutory taxes, loan EMIs, services that disconnect on non-payment. Cannot be delayed.
            - STANDARD: Regular vendor invoices with contractual SLA (e.g. NET-30). Can flex ±2 days if needed.
            - FLEXIBLE: Freelancers with no deadline, flexible timing, low-priority services. Can flex ±5 days.

            Respond with a JSON array where each object has:
            {"id": "PO-XXX", "urgency": "CRITICAL" | "STANDARD" | "FLEXIBLE", "reason": "One line explanation"}
            """
            
            payload = [{"id": p["id"], "vendor": p["vendor_name"], "context": p["vendor_context"], "amount": p["amount"], "due": p["due_date"]} for p in payouts]
            
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt, json.dumps(payload)],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            results = json.loads(response.text)
            
        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            logging.info("Falling back to rule-based classification.")
            results = [fallback_classify(p) for p in payouts]
            
    # Update Database
    # Handle case where API might return slightly wrong structure
    validated_results = []
    for r in results:
        urg = r.get("urgency", "STANDARD").upper()
        if urg not in ["CRITICAL", "STANDARD", "FLEXIBLE"]:
            urg = "STANDARD"
        validated_results.append((urg, r.get("reason", ""), r.get("id")))

    for urg, reason, pid in validated_results:
        if pid:
            execute_query("UPDATE payouts SET urgency = ?, urgency_reason = ? WHERE id = ?", (urg, reason, pid))
            from audit import log_audit
            log_audit("classified", f"Classified as {urg}: {reason}", pid, 0.0)
        
    return validated_results

if __name__ == "__main__":
    res = classify_payouts()
    print(f"Classified {len(res)} payouts.")

