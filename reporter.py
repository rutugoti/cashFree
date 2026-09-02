import os
from google import genai
from google.genai import types
from database import fetch_all
from config import GEMINI_API_KEY, GEMINI_MODEL
import logging

logging.basicConfig(level=logging.INFO)

def generate_summary(opt_result: dict) -> str:
    if not GEMINI_API_KEY:
        logging.warning("No GEMINI_API_KEY. Using fallback text.")
        return f"Processed payouts successfully. Crunches prevented: {opt_result.get('crunches_prevented', 0)}. Payouts rerouted: {opt_result.get('rerouted_count', 0)}. Payouts rescheduled: {opt_result.get('rescheduled_count', 0)}. Total fee savings: Rs.{opt_result.get('fee_saved', 0)}."

    prompt = f"""
    You are CashPilot, an AI treasury assistant.
    Write a 4-6 sentence executive summary of the recent optimization run.

    Results:
    - Crunches prevented: {opt_result.get('crunches_prevented', 0)}
    - Shortfall avoided: Rs.{opt_result.get('shortfall_avoided', 0)}
    - Payouts rerouted: {opt_result.get('rerouted_count', 0)}
    - Payouts rescheduled: {opt_result.get('rescheduled_count', 0)}
    - Total fee savings: Rs.{opt_result.get('fee_saved', 0)}

    Write a concise, professional summary for the business owner. Do not use asterisks or bold text, just plain sentences.
    """

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return "Summary could not be generated due to an AI service error."

if __name__ == "__main__":
    res = generate_summary({"crunches_prevented": 1, "shortfall_avoided": 10200, "rerouted_count": 18, "rescheduled_count": 7, "fee_saved": 5400})
    print(res)

