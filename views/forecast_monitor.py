"""Forecast monitor: accuracy and bias by segment, with alerts."""
import numpy as np
import pandas as pd
import streamlit as st

st.title("Forecast monitor: accuracy and bias by segment")
st.caption("Synthetic flights. A forecast can look accurate on average and still be "
           "consistently biased in one market or booking window.")

with st.sidebar:
    st.header("Inputs")
    seed = st.number_input("Random seed", 0, 9999, 7)
    inject = st.slider("Bias injected into one market", -0.4, 0.4, -0.2, 0.05,
                       help="Negative means the forecast is too high in that market.")
    noise = st.slider("Random forecast noise", 0.05, 0.40, 0.15, 0.05)
    threshold = st.slider("Bias alert threshold", 0.02, 0.20, 0.08, 0.01)

@st.cache_data
def make_data(seed, inject, noise):
    rng = np.random.default_rng(seed)
    markets = ["Short-haul A", "Short-haul B", "Long-haul C", "Long-haul D"]
    windows = ["0-7 days", "8-30 days", "31+ days"]
    rows = []
    for m in markets:
        for w in windows:
            base_bias = inject if (m == "Long-haul C" and w == "8-30 days") else 0.0
            actual = rng.normal(80, 15, 60).clip(20)
            forecast = actual * (1 + base_bias) * (1 + rng.normal(0, noise, 60))
            rows += [(m, w, a, f) for a, f in zip(actual, forecast)]
    return pd.DataFrame(rows, columns=["Market", "Window", "Actual", "Forecast"])

d = make_data(seed, inject, noise)
d["Error"] = d["Forecast"] - d["Actual"]

def summarise(g):
    return pd.Series({
        "WAPE": g["Error"].abs().sum() / g["Actual"].sum(),
        "Bias": g["Error"].sum() / g["Actual"].sum(),
        "Flights": len(g),
    })

overall = summarise(d)
c1, c2, c3 = st.columns(3)
c1.metric("Overall WAPE", f"{100 * overall['WAPE']:.1f}%")
c2.metric("Overall bias", f"{100 * overall['Bias']:+.1f}%",
          help="Positive = forecast above actual (over-forecast).")
c3.metric("Flights", f"{int(overall['Flights'])}")

seg = d.groupby(["Market", "Window"]).apply(summarise, include_groups=False).reset_index()
seg["Alert"] = np.where(seg["Bias"].abs() > threshold, "CHECK", "ok")

st.subheader("Bias by market and booking window")
heat = seg.pivot(index="Market", columns="Window", values="Bias")
st.dataframe((heat * 100).round(1).style.format("{:+.1f}%")
             .background_gradient(cmap="RdBu_r", vmin=-25, vmax=25), width="stretch")

st.subheader("Segments flagged for review")
flagged = seg[seg["Alert"] == "CHECK"].copy()
if flagged.empty:
    st.success("No segment exceeds the bias threshold.")
else:
    flagged["WAPE"] = (100 * flagged["WAPE"]).round(1)
    flagged["Bias"] = (100 * flagged["Bias"]).round(1)
    st.dataframe(flagged[["Market", "Window", "Bias", "WAPE", "Flights"]]
                 .rename(columns={"Bias": "Bias %", "WAPE": "WAPE %"}), width="stretch")

with st.expander("Method and limitations"):
    st.markdown("""
- WAPE = sum of absolute errors / sum of actuals. Bias = sum of signed errors / sum of actuals.
- Bias is the key calibration signal: a persistent over-forecast makes an optimiser protect too many high-fare seats (see the seat protection page).
- Bias is injected into one segment so the monitor has something to find; the overall figures hide it.
- In practice, add tests that account for sample size per segment and track bias over time, not just a snapshot.
""")
