import pandas as pd
import streamlit as st


def sip_planner(monthly_investment, annual_rate, years, step_up_rate):
    months = years * 12
    monthly_rate = annual_rate / 12 / 100
    balances, invested_amounts, interest_amounts = [], [], []
    balance, total_invested = 0, 0

    for month in range(1, months + 1):
        # Increase monthly investment yearly based on step-up rate
        if month % 12 == 1 and month != 1:
            monthly_investment *= (1 + step_up_rate / 100)
        
        interest = balance * monthly_rate
        balance = balance * (1 + monthly_rate) + monthly_investment
        total_invested += monthly_investment

        # Append results
        balances.append(round(balance))
        invested_amounts.append(round(total_invested))
        interest_amounts.append(round(balance - total_invested))

    return balances, invested_amounts, interest_amounts


def swp_planner(initial_investment, annual_rate, post_annual_rate, monthly_withdrawal, years, inflation_rate, retirement_age):
    months = years * 12
    balance = initial_investment
    balances, interest_earned, money_withdrawn = [], [], []
    balance_negative_month = None

    for month in range(1, months + 1):
        # Calculate dynamic percentage split
        age = retirement_age + (month // 12)
        years_after_retirement = age - retirement_age
        x = min(0.5 + 0.05 * (years_after_retirement // 5), 1)
        y = 1 - x
        #x = max(50 - (years_after_retirement * 5), 0)  # Percentage for `annual_rate` (reduces by 5% every 5 years)
        #y = 100 - x  # Percentage for `post_annual_rate`

        # Adjust monthly withdrawal for inflation yearly
        if month % 12 == 0:
            monthly_withdrawal *= (1 + inflation_rate / 100)

        # Calculate interest
        interest = balance * (y * annual_rate / 12 / 100 + x * post_annual_rate / 12 / 100)
        balance = balance + interest - monthly_withdrawal

        # Check for negative balance
        if balance < 0 and balance_negative_month is None:
            balance_negative_month = month
            break

        # Append results
        balances.append(round(balance))
        interest_earned.append(round(interest))
        money_withdrawn.append(round(monthly_withdrawal))

    # Return all results including when balance becomes negative
    return balances, interest_earned, money_withdrawn, balance_negative_month


# Streamlit UI
st.title("SIP & SWP Planner")

# Input fields
current_age = st.number_input("Current Age", min_value=28, max_value=100, value=30)
retirement_age = st.number_input("Expected Age to Retire", min_value=current_age + 1, max_value=100, value=45)
expected_death_age = st.number_input("Expected Age of Death", min_value=retirement_age + 1, max_value=120, value=90)

monthly_investment = st.number_input("Monthly SIP Installment (₹)", min_value=1000, value=30000)
step_up_rate = st.number_input("Annual Step-Up Rate (%)", min_value=0.0, value=2.0)
sip_annual_rate = st.number_input("Annual Rate of Return During SIP (%)", min_value=0.0, value=13.0)

monthly_withdrawal = st.number_input("Monthly SWP Withdrawal (₹)", min_value=1000, value=100000)
post_annual_rate = st.number_input("Post-Retirement Annual Rate of Return (%)", min_value=0.0, value=8.0)
inflation_rate = st.number_input("Annual Inflation Rate (%)", min_value=0.0, value=7.0)

# Calculations
years_to_retirement = retirement_age - current_age
years_of_withdrawal = expected_death_age - retirement_age

if st.button("Calculate"):
    # SIP calculations
    sip_balances, invested_amounts, interest_amounts = sip_planner(
        monthly_investment, sip_annual_rate, years_to_retirement, step_up_rate
    )
    sip_future_value = sip_balances[-1] if sip_balances else 0

    # SWP calculations
    swp_balances, interest_earned, money_withdrawn, balance_negative_month = swp_planner(
        sip_future_value, sip_annual_rate, post_annual_rate, monthly_withdrawal, years_of_withdrawal, inflation_rate, retirement_age
    )

    # Calculate the year when the balance goes negative
    if balance_negative_month:
        negative_year = retirement_age + (balance_negative_month // 12)
        st.error(f"SWP Balance becomes negative in year {negative_year} (at age {negative_year}).")
    else:
        st.success("SWP Balance sustains throughout the withdrawal period.")

    # Display SIP results
    st.subheader("SIP Results")
    st.line_chart(sip_balances)
    sip_data = pd.DataFrame({
        "Month": list(range(1, len(sip_balances) + 1)),
        "SIP Balance (₹)": sip_balances,
        "Invested Amount (₹)": invested_amounts,
        "Cumulative Interest (₹)": interest_amounts
    })
    st.dataframe(sip_data.style.format("{:,.0f}"))

    # Display SWP results
    st.subheader("SWP Results")
    st.line_chart(swp_balances)
    swp_data = pd.DataFrame({
        "Month": list(range(1, len(swp_balances) + 1)),
        "SWP Balance (₹)": swp_balances,
        "Interest Earned (₹)": interest_earned,
        "Money Withdrawn (₹)": money_withdrawn
    })
    st.dataframe(swp_data.style.format("{:,.0f}"))

    # Summary
    st.subheader("Summary")
    st.write(f"Total SIP Value at Retirement: ₹{sip_future_value:,.0f}")
    if swp_balances:
        st.write(f"Final SWP Balance After Withdrawals: ₹{swp_balances[-1]:,.0f}")