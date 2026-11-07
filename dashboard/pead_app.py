"""Exploratory dashboard for the PEAD sample."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parents[1] / "outputs" / "pead_sample.csv"

st.set_page_config(page_title="Earnings Drift Explorer", layout="wide")
st.title("Earnings Surprise and Post-Announcement Returns")
st.caption("Four-company pilot; not the S&P 500 Q2 2026 study")

if not DATA_PATH.exists():
    st.warning("The sample dataset has not been generated yet.")
    st.code("python code/pead_pipeline.py", language="bash")
    st.stop()

data = pd.read_csv(DATA_PATH, parse_dates=["earnings_date"])
required = {
    "ticker",
    "earnings_date",
    "eps_surprise_pct",
    "abnormal_5d_return_pct",
    "abnormal_20d_return_pct",
    "abnormal_60d_return_pct",
}
missing = required.difference(data.columns)
if missing:
    st.error("Dataset is missing required columns: {}".format(", ".join(sorted(missing))))
    st.stop()

st.warning(
    "This is a small convenience sample, not a statistically representative test "
    "or a result for the S&P 500 Q2 2026 cohort."
)

factor_return = "factor_proxy_abnormal_20d_return_pct"
has_factor_returns = factor_return in data.columns
return_column = factor_return if has_factor_returns else "abnormal_20d_return_pct"
c1, c2, c3 = st.columns(3)
c1.metric("Firm-event observations", len(data))
c2.metric("Firms", data["ticker"].nunique())
c3.metric(
    "Return method",
    "ETF factor proxies" if has_factor_returns else ", ".join(data["benchmark"].dropna().unique()),
)

st.subheader("Earnings surprise vs. 20-session abnormal return")
st.scatter_chart(
    data,
    x="eps_surprise_pct",
    y=return_column,
    color="ticker",
    x_label="EPS surprise (%)",
    y_label=(
        "20-session ETF-proxy abnormal return (%)"
        if has_factor_returns
        else "20-session SPY buy-and-hold abnormal return (%)"
    ),
)

st.subheader("Event-level results")
st.dataframe(data, hide_index=True, width="stretch")

st.subheader("How to read this pilot")
st.markdown(
    """
- Each row is one firm's quarterly earnings announcement.
- EPS surprise is `(reported EPS - consensus EPS) / abs(consensus EPS)`.
- SPY buy-and-hold abnormal return is the firm's adjusted buy-and-hold return
  minus SPY's return over the same sessions.
- ETF-proxy abnormal returns use market excess (SPY-BIL), size (IWM-SPY), and
  value (IWD-IWF) daily returns. The announcement reaction is reported
  separately; forward horizons start at the following close.
- ETF proxies are not official Kenneth French factors. See
  `audits/01_self_audit.md` for assumptions and limitations.
"""
)
