import streamlit as st
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.title("🏡 Home Loan Tenure Calculator with Prepayments")

# Basic Loan Inputs
loan_amount = st.number_input("Enter Loan Amount", value=5028000.0, step=100000.0)
interest_rate = st.number_input("Enter Annual Interest Rate (%)", value=8.7)
emi = st.number_input("Enter EMI Amount", value=41200.0)
start_month = st.number_input("Loan Start Month (1-12)", value=7, min_value=1, max_value=12)
start_year = st.number_input("Loan Start Year", value=2023)
start_date = datetime(int(start_year), int(start_month), 1)

# Number of Prepayments
num_prepayments = st.number_input("Number of Prepayments", min_value=0, max_value=10, value=2, step=1)

# Prepayment Inputs
prepayments = []
for i in range(num_prepayments):
    st.subheader(f"Prepayment #{i+1}")
    amount = st.number_input(f"Prepayment Amount #{i+1}", value=200000.0, step=10000.0)
    month = st.number_input(f"Prepayment Month #{i+1} (1-12)", min_value=1, max_value=12, value=8 if i==0 else 6)
    year = st.number_input(f"Prepayment Year #{i+1}", value=2024 if i==0 else 2025)
    prepayments.append({
        "amount": amount,
        "date": datetime(int(year), int(month), 1)
    })

if st.button("Calculate Remaining Tenure"):
    monthly_interest_rate = interest_rate / 12 / 100

    def remaining_principal(P, R, EMI, n):
        return P * (1 + R) ** n - EMI * ((1 + R) ** n - 1) / R

    def calculate_remaining_tenure(principal, R, EMI):
        N = -np.log(1 - (principal * R / EMI)) / np.log(1 + R)
        return int(np.ceil(N))

    principal = loan_amount
    last_prepayment_date = start_date
    total_months_paid = 0

    for prepayment in prepayments:
        months_between = (prepayment["date"].year - last_prepayment_date.year) * 12 + (prepayment["date"].month - last_prepayment_date.month)
        total_months_paid += months_between
        principal = remaining_principal(principal, monthly_interest_rate, emi, months_between)
        principal -= prepayment["amount"]
        last_prepayment_date = prepayment["date"]

    remaining_months = calculate_remaining_tenure(principal, monthly_interest_rate, emi)
    loan_closure_date = last_prepayment_date + relativedelta(months=remaining_months)

    st.success(f"📅 Remaining Tenure: {remaining_months} months")
    st.info(f"Loan will close by: {loan_closure_date.strftime('%B %Y')}")
