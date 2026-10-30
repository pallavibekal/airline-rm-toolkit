"""Parameter A/B test: how long to test a change to optimiser settings."""
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import norm

st.title("Testing a parameter change safely")
st.caption("Before rolling out a new optimiser setting, test it on a subset of flights "
           "with a control group. How long does the test need to run?")

with st.sidebar:
    st.header("Inputs")
    mean_rev = st.number_input("Mean revenue per flight", 5000, 200000, 50000, 1000)
    sd_rev = st.number_input("Std dev of revenue per flight", 500, 100000, 9000, 500)
    uplift = st.slider("Uplift you expect (%)", 0.2, 5.0, 3.0, 0.1)
    flights_per_week = st.slider("Flights per week in each group", 10, 500, 150, 10)
    alpha = st.slider("Significance level", 0.01, 0.10, 0.05, 0.01)
    power = st.slider("Power", 0.60, 0.95, 0.80, 0.05)

delta = mean_rev * uplift / 100
z_a, z_b = norm.ppf(1 - alpha / 2), norm.ppf(power)
n_per_group = int(np.ceil(2 * ((z_a + z_b) * sd_rev / delta) ** 2))
weeks = n_per_group / flights_per_week

c1, c2, c3 = st.columns(3)
c1.metric("Flights needed per group", f"{n_per_group:,}")
c2.metric("Weeks to run", f"{weeks:.1f}")
c3.metric("Smallest effect detectable in 4 weeks",
          f"{100 * (z_a + z_b) * sd_rev * np.sqrt(2 / (4 * flights_per_week)) / mean_rev:.2f}%")

st.subheader("Power vs test duration")
w = np.arange(1, 25)
n = w * flights_per_week
se = sd_rev * np.sqrt(2 / n)
pw = norm.cdf(delta / se - z_a) + norm.cdf(-delta / se - z_a)
st.line_chart(pd.DataFrame({"Power": pw}, index=pd.Index(w, name="Weeks")))

st.subheader("What a failed or unclear test looks like")
st.markdown(f"If you only run the test for **2 weeks**, power is about "
            f"**{100 * pw[1]:.0f}%**, so a real {uplift:.1f}% uplift would be missed "
            f"roughly {100 * (1 - pw[1]):.0f}% of the time.")

with st.expander("Method and limitations"):
    st.markdown("""
- Two-sample comparison of mean revenue per flight, normal approximation: n = 2 x ((z_alpha/2 + z_power) x sd / effect)^2 per group.
- Assumes flights are independent and comparable between groups. In practice match test and control on route, season and day of week, and watch for demand shocks.
- Revenue per flight is noisy, so small uplifts need long tests. Track load factor, overrides and forecast bias alongside revenue.
""")
