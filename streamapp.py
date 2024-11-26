import pandas as pd
import streamlit as st


def sip_planner(monthly_investment, annual_rate, years, step_up_rate):
    months = years * 12
    monthly_rate = annual_rate / 12 / 100
    balances, invested_amounts, interest_amounts, monthly_invested, monthly_interests = [], [], [], [], []
    balance, total_invested = 0, 0
    for month in range (1, months + 1):
        if month % 12 == 1 and month != 1:
            monthly_investment *= (1 + step_up_rate / 100)
            interest = balance * monthly_rate
            balance = balance * (1 + monthly_rate) + monthly_investment
            total_invested += monthly_investment
            balances.append(round(balance))
            invested_amounts.append(round(total_invested))
            interest_amounts.append(round(balance - total_invested))
            monthly_invested.append(round(monthly_investment))
            monthly_interests.append(round(interest))
    return balances, invested_amounts, interest_amounts, monthly_invested, monthly_interests

def swp_planner(initial_investment, post_annual_rate, annual_rate, monthly_withdrawal, years, inflation_rate, retirement_age):
    months = years * 12
    balance = initial_investment
    balances, interest_earned, money_withdrawn = [], [], []
    for month in range(months):
        age = retirement_age + month // 12
        years_after_retirement = age - retirement_age
        rate_8 = min(0.50 + 0.05 * (years_after_retirement // 5), 1)
        rate_13 = 1 - rate_8
        interest = balance * (rate_8 * post_annual_rate / 12 / 100 + rate_13 * annual_rate / 12 / 100)
        if month % 12 == 0 and month != 0:
            monthly_withdrawal *= (1 + inflation_rate / 100)
        balance = balance + interest - monthly_withdrawal
        balances.append(round(balance))
        interest_earned.append(round(interest))
        money_withdrawn.append(round(monthly_withdrawal))
    return balances, interest_earned, money_withdrawn

def find_minimum_monthly_investment(annual_rate, post_annual_rate, monthly_withdrawal, years_to_retirement, years_of_withdrawal, step_up_rate, inflation_rate, retirement_age):
    monthly_investment, tolerance, max_investment = 0, 1, 100000
    while monthly_investment <= max_investment:
        sip_balances, *_ = sip_planner(monthly_investment, annual_rate, years_to_retirement, step_up_rate)
        sip_future_value = sip_balances[-1]
        swp_balances, *_ = swp_planner(sip_future_value, post_annual_rate, annual_rate, monthly_withdrawal, years_of_withdrawal, inflation_rate, retirement_age)
        if abs(swp_balances[-1]) <= tolerance:
            return monthly_investment
        monthly_investment += 500
        return None

st.title('SIP & SWP Planner')
monthly_investment = st.number_input('Monthly Investment', value=50000)
monthly_withdrawal = st.number_input('Monthly Withdrawal', value=50000)
annual_rate = st.number_input('Annual Rate (%)', value = 14)
post_annual_rate = st.number_input('Post Annual Rate (%)', value = 8)
current_age = st.number_input('Current Age', value=28)
retirement_age = st.number_input('Retirement Age', value=45)
expected_death_age = st.number_input('Expected Death Age', value=90)
step_up_rate = st.number_input('Step-Up Rate (%)', value=2)
inflation_rate = st.number_input('Inflation Rate (%)', value = 7)
years_to_retirement = retirement_age - current_age
years_of_withdrawal = expected_death_age - retirement_age

if st.button('Calculate'):
    sip_balances, sip_invested_amounts, sip_interest_amounts, monthly_invested, monthly_interests = sip_planner(monthly_investment, annual_rate, years_to_retirement, step_up_rate)
    sip_future_value = sip_balances[-1]
    swp_balances, interest_earned, money_withdrawn = swp_planner(sip_future_value, post_annual_rate, annual_rate, monthly_withdrawal, years_of_withdrawal, inflation_rate, retirement_age)
    minimum_monthly_investment = find_minimum_monthly_investment(annual_rate, post_annual_rate, monthly_withdrawal, years_to_retirement, years_of_withdrawal, step_up_rate, inflation_rate, retirement_age)

    st.subheader('SIP Balances')
    st.line_chart([round(balance) for balance in sip_balances])
    st.subheader('SWP Balances')
    st.line_chart([round(balance) for balance in swp_balances])

    if minimum_monthly_investment is not None:
        st.success(f"The bare minimum monthly investment required is: {minimum_monthly_investment:,}")
    else:
        st.error ("No suitable monthly investment found within the limit.")

    sip_data = {
        'Year': [month // 12 for month in range(1, years_to_retirement * 12 + 1)],
        'Month': list(range(1, years_to_retirement * 12 + 1)),
        'Monthly invested' : monthly_invested,
        'Invested Amount': sip_invested_amounts,
        'Monthly Interest': monthly_interests,
        'Cumulative Interest Amount': sip_interest_amounts,
        'SIP Balance': sip_balances
    }

    swp_data = {
        'Year': [month // 12 for month in range(1, years_to_retirement * 12 + 1)],
        'Month': list(range(1, years_to_retirement * 12 + 1)),
        'Interest Earned': interest_earned,
        'Money Withdrawn': money_withdrawn,
        'SWP Balance': swp_balances
    }

    sip_df, swp_df = pd.DataFrame(sip_data), pd.DataFrame(swp_data)
    st.subheader('SIP Data Frame')
    st.dataframe(sip_df.style.format("(:,.0f)"))
    st.subheader('SWP Data Frame')
    st.dataframe(swp_df.style.format("{:,.0f}"))