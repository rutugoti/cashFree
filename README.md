# 💸 CashPilot: AI Treasury Agent

**CashPilot** is an autonomous AI Treasury Agent built for the Razorpay AI Buildathon. It solves the critical cash-flow mismatch between inbound revenue (Payment Gateway) and outbound expenses (RazorpayX) to prevent bounced payouts and optimize bank fees.

## 🚨 The Problem
D2C merchants use **Razorpay Payment Gateway** to receive money (settlements) and **RazorpayX** to pay their vendors (payouts). 
The problem is a timing mismatch: Card settlements take T+2 days to arrive, but merchants often pay vendors immediately via IMPS. This causes temporary **"cash crunches"**—their RazorpayX balance drops below zero, causing payouts to bounce, leading to penalties and damaged vendor relationships.

## 🚀 The Solution
CashPilot is an AI Treasury Agent that bridges the gap between Razorpay PG and RazorpayX. It predicts cash crunches before they happen, uses **Google Gemini AI** to understand which vendors can wait, and automatically optimizes the payout schedule to prevent the account from ever going negative.

### 🏗️ Hybrid Architecture (Live API + Synthetic Projections)
To build a mathematically sound treasury forecaster, CashPilot uses a Hybrid Data Architecture:
1. **Live Inbound API:** CashPilot hits `GET /v1/payments` to pull real-time captured PG transactions.
2. **Honest T+2 Projections:** It calculates exact T+2 settlement dates for those live transactions without faking `setl_xxx` objects.
3. **Synthetic Gap-Filling:** It uses synthetic data to flesh out the 7-day cash flow curve to create predictable, deep cash crunches for the AI to solve.

## ⚙️ How It Works (The 5-Step Pipeline)

1. **Forecasting (Math):** The agent calculates a rolling 7-day cash flow based on inbound PG settlements and pending X payouts. It detects imminent cash crunches (e.g., negative balance on Day 3).
2. **Classification (Gemini AI):** Instead of using dumb keyword matching, Gemini reads the context of every invoice (e.g., *"Freelance logo design"* vs *"AWS server hosting"*) and classifies them into `CRITICAL`, `STANDARD`, or `FLEXIBLE`.
3. **Fee Optimization:** It reroutes non-critical payouts from expensive IMPS to cheaper NEFT/UPI modes, saving the merchant hundreds in bank fees.
4. **Rescheduling:** It uses a reverse-chronological greedy algorithm to delay `FLEXIBLE` payouts just enough to perfectly bridge the cash crunch, ensuring the bank account never hits zero.
5. **Live RazorpayX Execution:** It securely pushes the optimized payouts for "today" directly to the real **RazorpayX Test API**, creating live Contacts and Fund Accounts in the dashboard.

## 💻 Tech Stack
* **Language:** Python 3.12
* **AI/LLM:** Google Gemini 2.5 Flash (`google-genai` SDK)
* **APIs:** Razorpay Payment Gateway, RazorpayX Payouts
* **Database:** SQLite3
* **Frontend:** Streamlit + Plotly

## 🛠️ How to Run Locally

1. **Clone the repository and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up your environment variables:**
   Create a `.env` file based on `.env.example`:
   ```env
   RAZORPAY_KEY_ID="rzp_test_..."
   RAZORPAY_KEY_SECRET="..."
   RAZORPAYX_ACCOUNT_NUMBER="..."
   GEMINI_API_KEY="..."
   ```
3. **Run the Dashboard:**
   ```bash
   streamlit run app.py
   ```
4. **Test the Integration:**
   Click **"Reset / Reseed Data"** in the sidebar to fetch live PG payments, then click **"Run CashPilot"** to trigger the AI optimization pipeline and execute live payouts to your RazorpayX dashboard!
