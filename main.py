import streamlit as st
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Home Loan Calculator", page_icon="🏡")
st.title("🏡 Home Loan Tenure Calculator with Prepayments")

# Section: Loan Details
st.header("1️⃣ Basic Loan Details")
loan_amount = st.number_input("🏦 Loan Amount (₹)", value=5028000.0, step=100000.0)
interest_rate = st.number_input("📈 Annual Interest Rate (%)", value=8.7)
emi = st.number_input("💸 Monthly EMI (₹)", value=41200.0)

start_month = st.number_input("📅 Loan Start Month (1-12)", value=7, min_value=1, max_value=12)
start_year = st.number_input("📅 Loan Start Year (e.g. 2023)", value=2023)
original_loan_years = st.number_input("📆 Original Loan Tenure (Years)", value=25, min_value=1, max_value=40)

start_date = datetime(int(start_year), int(start_month), 1)
original_loan_months = original_loan_years * 12

# Section: Prepayment Details
st.header("2️⃣ Prepayment Details")
num_prepayments = st.number_input("🔁 Number of Prepayments", min_value=0, max_value=10, value=1, step=1)

prepayments = []
for i in range(num_prepayments):
    st.subheader(f"🔹 Prepayment #{i+1}")
    amount = st.number_input(f"💰 Amount for Prepayment #{i+1}", value=200000.0, step=10000.0, key=f"amount_{i}")
    month = st.number_input(f"📅 Month of Prepayment #{i+1} (1-12)", min_value=1, max_value=12, value=8 if i == 0 else 6, key=f"month_{i}")
    year = st.number_input(f"📅 Year of Prepayment #{i+1}", value=2024 if i == 0 else 2025, key=f"year_{i}")
    prepayments.append({
        "amount": amount,
        "date": datetime(int(year), int(month), 1)
    })

# --- Calculation Logic ---
if st.button("📊 Calculate Remaining Tenure"):

    monthly_interest_rate = interest_rate / 12 / 100

    def remaining_principal(P, R, EMI, n):
        """Remaining principal after n EMIs"""
        return P * (1 + R) ** n - EMI * ((1 + R) ** n - 1) / R

    def calculate_remaining_tenure(principal, R, EMI):
        """Calculate tenure needed to repay remaining principal"""
        if EMI <= principal * R:
            return float("inf")
        N = -np.log(1 - (principal * R / EMI)) / np.log(1 + R)
        return int(np.ceil(N))

    # Initial setup
    principal = loan_amount
    last_payment_date = start_date
    total_months_paid = 0

    for i, prepayment in enumerate(prepayments):
        months_between = (prepayment["date"].year - last_payment_date.year) * 12 + (prepayment["date"].month - last_payment_date.month)
        total_months_paid += months_between
        principal = remaining_principal(principal, monthly_interest_rate, emi, months_between)

        # 📢 Show remaining principal before prepayment
        st.info(f"💼 Remaining Principal *before* Prepayment #{i+1} on {prepayment['date'].strftime('%B %Y')}: ₹{principal:,.2f}")

        principal -= prepayment["amount"]
        last_payment_date = prepayment["date"]

    # Calculate new remaining tenure
    remaining_months = calculate_remaining_tenure(principal, monthly_interest_rate, emi)
    total_tenure_after_prepayment = total_months_paid + remaining_months
    new_closure_date = start_date + relativedelta(months=total_tenure_after_prepayment)

    # Show results
    st.write("---")
    st.subheader("✅ Result")
    st.write(f"📌 Tenure calculation starts from: **{start_date.strftime('%B %Y')}**")
    st.write(f"💳 Total EMIs paid till last prepayment: **{total_months_paid} months**")
    st.success(f"📅 Remaining Tenure *after* prepayments: **{remaining_months} months**")
    st.info(f"🎯 Expected Loan Closure: **{new_closure_date.strftime('%B %Y')}**")

    # Extra: Tenure saved
    original_closure_date = start_date + relativedelta(months=original_loan_months)
    months_saved = original_loan_months - total_tenure_after_prepayment
    if months_saved > 0:
        st.success(f"🎉 Tenure Reduced by: **{months_saved} months**")
        st.caption(f"Original closure date would have been: {original_closure_date.strftime('%B %Y')}")
    else:
        st.warning("❗ EMI or prepayment is too small to impact tenure meaningfully.")
