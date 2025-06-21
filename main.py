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
start_date = datetime(int(start_year), int(start_month), 1)

# Section: Prepayment Details
st.header("2️⃣ Prepayment Details")
num_prepayments = st.number_input("🔁 Number of Prepayments", min_value=0, max_value=10, value=2, step=1)

prepayments = []
for i in range(num_prepayments):
    st.subheader(f"🔹 Prepayment #{i+1}")
    amount = st.number_input(f"💰 Amount for Prepayment #{i+1}", value=200000.0, step=10000.0)
    month = st.number_input(f"📅 Month of Prepayment #{i+1} (1-12)", min_value=1, max_value=12, value=8 if i == 0 else 6)
    year = st.number_input(f"📅 Year of Prepayment #{i+1}", value=2024 if i == 0 else 2025)
    prepayments.append({
        "amount": amount,
        "date": datetime(int(year), int(month), 1)
    })

# Calculation Logic
if st.button("📊 Calculate Remaining Tenure"):

    # Monthly interest rate
    monthly_interest_rate = interest_rate / 12 / 100

    def remaining_principal(P, R, EMI, n):
        """Calculate remaining principal after n EMIs"""
        return P * (1 + R) ** n - EMI * ((1 + R) ** n - 1) / R

    def calculate_remaining_tenure(principal, R, EMI):
        """Calculate months needed to repay the remaining loan"""
        if EMI <= principal * R:
            return float("inf")  # EMI too small to cover interest
        N = -np.log(1 - (principal * R / EMI)) / np.log(1 + R)
        return int(np.ceil(N))

    # Process prepayments
    principal = loan_amount
    last_payment_date = start_date
    total_months_paid = 0

    for prepayment in prepayments:
        months_between = (prepayment["date"].year - last_payment_date.year) * 12 + (prepayment["date"].month - last_payment_date.month)
        total_months_paid += months_between
        principal = remaining_principal(principal, monthly_interest_rate, emi, months_between)
        principal -= prepayment["amount"]
        last_payment_date = prepayment["date"]

    # Final tenure calculation
    remaining_months = calculate_remaining_tenure(principal, monthly_interest_rate, emi)
    loan_closure_date = last_payment_date + relativedelta(months=remaining_months)

    # Display results
    st.write("---")
    st.subheader("✅ Result")
    st.write(f"📌 Tenure calculation starts from: **{last_payment_date.strftime('%B %Y')}**")
    st.success(f"📅 Remaining Tenure: **{remaining_months} months**")
    st.info(f"🎯 Expected Loan Closure: **{loan_closure_date.strftime('%B %Y')}**")
