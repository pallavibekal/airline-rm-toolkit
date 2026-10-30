"""Revenue management toolkit: entry point and navigation."""
import streamlit as st

st.set_page_config(page_title="Airline RM Toolkit", layout="wide")

pages = [
    st.Page("views/seat_protection.py", title="Seat protection (EMSR-b)", default=True),
    st.Page("views/overbooking.py", title="Overbooking"),
    st.Page("views/forecast_monitor.py", title="Forecast monitor"),
    st.Page("views/parameter_test.py", title="Parameter A/B test"),
]
st.navigation(pages).run()
st.sidebar.caption("Synthetic data. Portfolio project by Pallavi Krishna.")
