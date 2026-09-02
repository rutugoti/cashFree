# 💸 CashPilot - AI Treasury Agent

CashPilot connects Razorpay Payment Gateway settlements (inflows) with RazorpayX payouts (outflows) to predict cash flow, classify vendor payout urgency, and autonomously optimize payment timing and routing (IMPS vs NEFT vs UPI).

Built for the **Razorpay AI Buildathon (Open Track)**.

## 🚀 The Problem
Indian SMEs face hidden cash crunches because inbound settlements arrive on staggered T+1 to T+3 cycles, while vendor payouts are often executed manually using expensive IMPS rails without cash-flow awareness. Section 43B(h) makes proper vendor payout timing a compliance necessity.

## 🧠 The Solution
CashPilot uses a hybrid AI architecture:
- **Deterministic Code**: Predicts 7-day cash flow balances, validates constraints (never drop below zero), and computes fees. 
- **Gemini 2.5 Flash**: Contextually classifies unstructured vendor payout urgency (e.g. "Logo design, no rush" vs "Payroll") and generates explainable audit trail reports.
- **RazorpayX Test API**: Executes real payouts across multiple routing rails.

## 🛠️ Setup & Run

1. **Install Dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and add your keys:
   - `GEMINI_API_KEY`
   - `RAZORPAY_KEY_ID` (Optional - simulates if omitted)
   - `RAZORPAY_KEY_SECRET` (Optional - simulates if omitted)

3. **Start the Agent Dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Demo Flow**
   - Click **Reset / Reseed Data** on the sidebar to load the engineered 53-payout scenario with a hidden cash crunch.
   - Go to **Run CashPilot** and hit `▶️ Run CashPilot`.
   - Watch the AI eliminate the crunch, generate fee savings, and execute RazorpayX payouts in real-time!

