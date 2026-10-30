"""Overbooking: how many seats to sell above capacity given no-shows."""
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import binom

st.title("Overbooking: selling above capacity")
st.caption("Some passengers do not show up. Selling extra seats fills them, but too many "
           "means denied boardings. Synthetic inputs.")

with st.sidebar:
    st.header("Inputs")
    capacity = st.slider("Seats on the flight", 50, 300, 100, 10)
    fare = st.number_input("Average fare", 50, 3000, 450, 10)
    show_rate = st.slider("Show-up rate", 0.70, 1.00, 0.92, 0.01)
    db_mult = st.slider("Denied-boarding cost (multiple of fare)", 0.5, 6.0, 2.5, 0.5,
                        help="Compensation plus rebooking and goodwill cost per denied passenger.")

def evaluate(limit):
    k = np.arange(0, limit + 1)
    pmf = binom.pmf(k, limit, show_rate)       # passengers who actually show
    flown = np.minimum(k, capacity)
    denied = np.maximum(0, k - capacity)
    revenue = (pmf * (fare * flown - db_mult * fare * denied)).sum()
    return revenue, (pmf * denied).sum(), (pmf * np.maximum(0, capacity - k)).sum()

limits = np.arange(capacity, int(capacity * 1.3) + 1)
rows = [(L, *evaluate(L)) for L in limits]
df = pd.DataFrame(rows, columns=["Booking limit", "Expected revenue",
                                 "Expected denied boardings", "Expected empty seats"]).set_index("Booking limit")
best = df["Expected revenue"].idxmax()
base = df.loc[capacity, "Expected revenue"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Best booking limit", f"{best}", f"{best - capacity:+d} seats over capacity")
c2.metric("Expected revenue", f"{df.loc[best, 'Expected revenue']:,.0f}",
          f"{100 * (df.loc[best, 'Expected revenue'] / base - 1):+.1f}% vs no overbooking")
c3.metric("Expected denied boardings", f"{df.loc[best, 'Expected denied boardings']:.2f}")
c4.metric("Expected empty seats", f"{df.loc[best, 'Expected empty seats']:.1f}")

st.subheader("Expected revenue by booking limit")
st.line_chart(df[["Expected revenue"]])
st.subheader("The trade-off: empty seats vs denied boardings")
st.line_chart(df[["Expected denied boardings", "Expected empty seats"]])

with st.expander("Method and limitations"):
    st.markdown("""
- Passengers show independently with probability equal to the show-up rate, so shows are Binomial(booking limit, show rate).
- Revenue = fare x passengers flown - denied-boarding cost x passengers denied. Demand is assumed high enough to sell the limit.
- Real systems vary the show rate by market, fare class and booking window, and model cancellations over time. This is the single-parameter version.
""")
