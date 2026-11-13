"""Exploratory dashboard for the PEAD sample."""

from pathlib import Path

import pandas as pd
import streamlit as st

from data_contract import coverage_table, quality_summary, validate_required_columns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PILOT_PATH = PROJECT_ROOT / "outputs" / "pead_sample.csv"
SYNTHETIC_PATH = PROJECT_ROOT / "outputs" / "synthetic_checkpoint_dataset.csv"

st.set_page_config(page_title="Earnings Drift Explorer", layout="wide")
st.title("Earnings Surprise and Post-Announcement Returns")
source = st.sidebar.selectbox(
    "Dataset",
    ("Synthetic checkpoint (20 events)", "Yahoo Finance pilot (4 events)"),
)
is_synthetic = source.startswith("Synthetic")
data_path = SYNTHETIC_PATH if is_synthetic else PILOT_PATH

if not data_path.exists():
    if is_synthetic:
        st.warning("The synthetic checkpoint dataset has not been generated yet.")
        st.code("python code/build_synthetic_checkpoint.py", language="bash")
    else:
        st.warning("The Yahoo Finance pilot dataset has not been generated yet.")
        st.code("python code/pead_pipeline.py", language="bash")
    st.stop()

data = pd.read_csv(data_path)
try:
    validate_required_columns(data)
except ValueError as error:
    st.error(str(error))
    st.stop()

for date_column in ("earnings_date", "earnings_timestamp", "fiscal_period_end"):
    if date_column in data.columns:
        data[date_column] = pd.to_datetime(data[date_column], errors="coerce")

if is_synthetic:
    st.caption(
        "Synthetic checkpoint only; separate financial, event-study, and transcript "
        "fixtures are merged by event_id."
    )
    st.warning(
        "Every row is generated for dashboard testing. Synthetic values are not "
        "observations, model results, or evidence about the S&P 500 cohort."
    )
else:
    st.caption("Four-company Yahoo Finance pilot; not the S&P 500 Q2 2026 study")
    st.warning(
        "This is a small convenience sample, not a statistically representative test "
        "or a result for the S&P 500 Q2 2026 cohort."
    )
    if "fiscal_period_end" not in data:
        st.info(
            "The existing pilot has no verified fiscal-period-end field. Its "
            "dashboard checks use ticker and earnings date only; it is not ready "
            "to join to the target cohort schema."
        )

quality = quality_summary(data)
coverage = coverage_table(data)
coverage_by_field = coverage.set_index("field")
c1, c2, c3 = st.columns(3)
c1.metric("Firm-event observations", len(data))
c2.metric("Firms", data["ticker"].nunique())
c3.metric("EPS + primary outcome rows", quality["primary_data_complete_rows"])
c4, c5 = st.columns(2)
c4.metric(
    "EPS surprise coverage",
    "{:.0f}%".format(coverage_by_field.loc["eps_surprise_pct", "coverage_pct"]),
)
c5.metric(
    "Usable tone-score coverage",
    "{:.0f}%".format(
        coverage_by_field.loc["language_outlook_tone", "coverage_pct"]
    ),
)

outcome_options = {
    "Event-study CAR [0,1] (%)": "car_0_1_pct",
    "Event-study CAR [0,5] (%)": "car_0_5_pct",
    "Event-study CAR [0,20] (%)": "car_0_20_pct",
    "ETF-proxy CAR (20 sessions)": "factor_proxy_abnormal_20d_return_pct",
    "ETF-proxy CAR (5 sessions)": "factor_proxy_abnormal_5d_return_pct",
    "ETF-proxy CAR (60 sessions)": "factor_proxy_abnormal_60d_return_pct",
    "SPY buy-and-hold abnormal return (20 sessions)": "abnormal_20d_return_pct",
}
available_outcomes = {
    label: column
    for label, column in outcome_options.items()
    if column in data.columns and data[column].notna().any()
}
st.subheader("Earnings surprise vs. abnormal return")
if not available_outcomes or "eps_surprise_pct" not in data:
    st.info("No complete EPS/outcome pair is available to plot.")
else:
    selected_outcome = st.selectbox("Outcome", tuple(available_outcomes))
    return_column = available_outcomes[selected_outcome]
    color_column = "sector" if is_synthetic and "sector" in data else "ticker"
    chart_columns = ["eps_surprise_pct", return_column, color_column]
    chart_data = data[chart_columns].dropna(
        subset=["eps_surprise_pct", return_column]
    )
    st.caption(
        "Plot includes {} of {} events with both selected variables observed.".format(
            len(chart_data), len(data)
        )
    )
    if chart_data.empty:
        st.info("No complete observations are available for this plot.")
    else:
        st.scatter_chart(
            chart_data,
            x="eps_surprise_pct",
            y=return_column,
            color=color_column,
            x_label="EPS surprise (%)",
            y_label=selected_outcome,
        )

st.subheader("Data coverage")
st.dataframe(
    coverage.drop(columns="field_present"),
    hide_index=True,
    width="stretch",
    column_config={
        "coverage_pct": st.column_config.ProgressColumn(
            "Coverage (%)", min_value=0, max_value=100, format="%.0f%%"
        )
    },
)
if (~coverage["field_present"]).any():
    st.info(
        "Fields absent from the selected source are displayed as 0% coverage; "
        "they are not imputed."
    )

st.subheader("Data quality")
q1, q2, q3, q4 = st.columns(4)
q1.metric("Duplicate event rows", quality["duplicate_event_rows"])
q2.metric("Rows with missing event keys", quality["missing_event_keys"])
q3.metric("EPS surprise mismatches", quality["eps_surprise_mismatches"])
q4.metric("Out-of-range transcript scores", quality["invalid_language_scores"])
q5, q6 = st.columns(2)
q5.metric("Baseline-ready rows", quality["baseline_complete_rows"])
q6.metric("Outlook-feature-complete rows", quality["outlook_feature_complete_rows"])

st.subheader("Event-level results")
display_columns = [
    column
    for column in (
        "event_id",
        "ticker",
        "company_name",
        "fiscal_period_end",
        "earnings_timestamp",
        "eps_actual",
        "eps_estimate",
        "eps_surprise_pct",
        "eps_beat",
        "market_cap_usd",
        "sector",
        "prior_20d_return_pct",
        "prior_20d_volatility_pct",
        "car_0_1_pct",
        "car_0_5_pct",
        "car_0_20_pct",
        "factor_proxy_announcement_abnormal_return_pct",
        "factor_proxy_abnormal_5d_return_pct",
        "factor_proxy_abnormal_20d_return_pct",
        "factor_proxy_abnormal_60d_return_pct",
        "abnormal_20d_return_pct",
        "language_outlook_tone",
        "language_sentiment_score",
        "language_guidance_specificity",
        "transcript_sentiment",
        "management_sentiment",
        "analyst_question_sentiment",
        "congratulations_mentioned",
        "transcript_score_status",
        "record_type",
    )
    if column in data.columns
]
st.dataframe(data[display_columns], hide_index=True, width="stretch")

st.subheader("Limitations and definitions")
st.markdown(
    """
- Each row is one firm's quarterly earnings announcement.
- EPS surprise is `(reported EPS - consensus EPS) / abs(consensus EPS) * 100`.
- `car_0_1_pct` is the proposed checkpoint-normalized CAR[0,1] field for the
  event day and following day; the course event-study package has not been run
  on this synthetic fixture. Confirm its date convention with Gus.
- SPY buy-and-hold abnormal return is the firm's adjusted buy-and-hold return
  minus SPY's return over the same sessions.
- ETF-proxy abnormal returns use market excess (SPY-BIL), size (IWM-SPY), and
  value (IWD-IWF) daily returns. The announcement reaction is reported
- separately in the existing Yahoo pilot; these values are not in the
  Event Study Package fixture. ETF proxies are not official Kenneth French
  factors.
- Synthetic EPS, firm characteristics, textual features, and all return
  values are fabricated placeholders; no model or event study was estimated.
- `transcript_sentiment`, `management_sentiment`,
  `analyst_question_sentiment`, and `congratulations_mentioned` are also
  synthetic UI fields. Their extraction methods require team agreement.
- `language_outlook_tone` and `language_guidance_specificity` use the
  synthetic transcript checkpoint rubric; no Claude outputs are included.
- Missing values remain missing. Coverage percentages describe only the
  currently selected dataset, not the 500-company target cohort.
- The proposed sequence is Yahoo-only variables, then classic transcript
  sentiment, then additional transcript/AI variables. The dashboard does not
  fit regressions or predictive models. Do not use a same-window announcement
  return as a predictor of CAR[0,1]; it would overlap the outcome.
- Confirm Yahoo variables with Gus and model inputs/method with Kami before
  real-data integration.

See `PROPOSAL.md`, `STATUS.md`, and `audits/01_self_audit.md` for the
documented study design and remaining access, provenance, and sample limits.
"""
)
