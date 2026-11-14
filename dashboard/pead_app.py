"""Team Magic research dashboard: earnings calls and post-earnings returns.

Run from the repository root:

    streamlit run dashboard/pead_app.py

Presentation only. Data collection and estimation live in the pipeline and
statistics workstreams; this app reads their files through
``data_registry.py`` and never fills, zeroes, or invents values.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import charts  # noqa: E402
from data_registry import (  # noqa: E402
    DATASETS,
    PILOT,
    REPO_ROOT,
    STATUS_LABELS,
    SYNTHETIC,
    language_feature_columns,
    load_dataset,
)
from status import (  # noqa: E402
    MATRIX_COLUMNS,
    STATUS_DEFINITIONS,
    STATUS_ORDER,
    STATUS_STYLE,
    build_status_matrix,
    coverage_funnel,
    sector_representation,
)

# Proposed (not team-agreed) holdout size below which results are labelled
# exploratory. Confirm with the statistics workstream.
MIN_HOLDOUT_FOR_CONFIRMATORY = 30

st.set_page_config(
    page_title="Earnings Calls & Post-Earnings Returns",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>
.block-container {padding-top: 2rem; max-width: 1400px;}
.status-chip {display:inline-block; padding:2px 10px; border-radius:999px;
  font-size:0.85rem; font-weight:600; margin:2px 6px 2px 0;}
.lede {font-size:1.05rem; line-height:1.55;}
.small-muted {color:#898781; font-size:0.85rem;}
</style>
""",
    unsafe_allow_html=True,
)


def status_chip(status: str) -> str:
    style = STATUS_STYLE[status]
    return '<span class="status-chip" style="background:{};color:{}">{} {}</span>'.format(
        style["color"], style["ink"], style["icon"], status
    )


def synthetic_banner(what: str = "This section"):
    st.error(
        "**SYNTHETIC TEST DATA: NOT RESEARCH RESULTS.** {} uses synthetic inputs "
        "generated to test the layout. Tickers starting with SYN are fake. Real "
        "outputs will replace them automatically when delivered.".format(what),
        icon="🧪",
    )


def pilot_banner():
    st.warning(
        "**PILOT DATA.** Four-company convenience sample (AAPL, MSFT, NVDA, TSLA) "
        "used to check the pipeline. It is not representative and is not evidence "
        "about the S&P 500 Q2 2026 cohort.",
        icon="⚠️",
    )


def awaiting(owner: str, what: str, items: list, files: list):
    with st.container(border=True):
        st.markdown("#### ⏳ Awaiting {}".format(owner))
        st.markdown(what)
        st.markdown("**What will appear here:**\n" + "\n".join("- " + i for i in items))
        st.markdown(
            "<span class='small-muted'>Expected file(s): {}. See "
            "<code>docs/DATA_CONTRACT_PROPOSAL.md</code>.</span>".format(
                ", ".join("<code>{}</code>".format(f) for f in files)
            ),
            unsafe_allow_html=True,
        )


def fmt_count(value):
    return "Pending" if value is None or pd.isna(value) else "{:,}".format(int(value))


# --------------------------------------------------------------------------
# Sidebar and data loading
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Team Magic · FIN331")
    st.caption("Earnings calls and post-earnings returns")
    use_fixtures = st.toggle(
        "Preview with synthetic test fixtures",
        value=False,
        key="use_fixtures",
        help="Fills the Findings tab with random SYNTHETIC data from tests/fixtures "
        "so the layout can be reviewed. Real files always take priority.",
    )

data = {key: load_dataset(key, allow_fixture=use_fixtures) for key in DATASETS}
cohort, pilot = data["cohort"], data["pilot"]
if cohort.available:
    events_ds = cohort
else:
    events_ds = pilot
events = events_ds.frame if events_ds.available else None
events_is_synthetic = events_ds.status == SYNTHETIC
roster = data["roster"].frame if data["roster"].available else None
audit = data["transcript_audit"].frame if data["transcript_audit"].available else None
screen = data["transcript_screen"].frame if data["transcript_screen"].available else None

with st.sidebar:
    st.divider()
    st.markdown("**Data sources**")
    for key, ds in data.items():
        if key == "synthetic_events" and ds.source == "absent":
            continue
        if ds.error or ds.missing_columns:
            icon, note = "❌", "problem loading; see Data quality tab"
        elif ds.source == "absent":
            icon, note = "⏳", "awaiting {}".format(ds.spec.owner)
        elif ds.status == SYNTHETIC:
            icon, note = "🧪", "{} rows · synthetic".format(ds.n_rows)
        elif ds.status == PILOT:
            icon, note = "⚠️", "{} rows · pilot".format(ds.n_rows)
        else:
            icon, note = "✅", "{} rows · {}".format(ds.n_rows, STATUS_LABELS[ds.status].lower())
        st.markdown("{} **{}**  \n<span class='small-muted'>{}</span>".format(icon, ds.spec.label, note),
                    unsafe_allow_html=True)
    if events is not None and "retrieved_at_utc" in events.columns:
        st.divider()
        st.caption("Event data retrieved: {}".format(str(events["retrieved_at_utc"].dropna().max())[:10]))

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.title("Earnings Calls and Post-Earnings Returns")
st.markdown(
    "<p class='lede'>Do signals from earnings-call language help predict a stock's "
    "return over the 20 trading sessions after an earnings announcement, "
    "<b>beyond</b> what the EPS surprise and the day-of reaction already tell us?</p>",
    unsafe_allow_html=True,
)
if events_ds is pilot:
    pilot_banner()
if use_fixtures:
    st.info(
        "Synthetic fixture preview is **on**. Affected sections carry a red "
        "SYNTHETIC banner. Turn it off in the sidebar before presenting.",
        icon="🧪",
    )

tabs = st.tabs(
    ["Overview", "Data coverage", "Data quality & gaps", "Event explorer", "Findings", "Methods & limitations"]
)

# --------------------------------------------------------------------------
# 1. Overview
# --------------------------------------------------------------------------
with tabs[0]:
    funnel = coverage_funnel(
        roster,
        cohort.frame if cohort.available else None,
        audit,
        data["features"].frame if data["features"].available and data["features"].source == "real" else None,
        data["metrics"].frame if data["metrics"].available and data["metrics"].source == "real" else None,
    )
    stage = dict(zip(funnel["stage"], funnel["count"]))
    m = st.columns(4)
    m[0].metric("Roster stocks", fmt_count(stage["Roster stocks (June 30, 2026)"]), border=True,
                help="S&P 500 constituents on the archived June 30, 2026 list.")
    m[1].metric("Verified Q2 2026 events", fmt_count(stage["Verified Q2 2026 events"]), border=True,
                help="Pending until the verified event manifest and cohort output are delivered.")
    located, cleared = stage["Transcript located"], stage["Transcript rights cleared"]
    m[2].metric("Transcripts rights-cleared", fmt_count(cleared), border=True,
                delta=None if pd.isna(located) else "{} located, rights unknown".format(
                    int(located) - int(0 if pd.isna(cleared) else cleared)),
                delta_color="off", delta_arrow="off",
                help="Locating a transcript is not permission to retain it or send it to a model.")
    m[3].metric("Model comparison", "Pending" if not (data["metrics"].available and data["metrics"].source == "real")
                else "Delivered", border=True)

    st.subheader("How the study works")
    steps = st.columns(4)
    step_text = [
        ("1 · Sample", "One observation = one company's quarterly earnings announcement. "
         "Universe: the S&P 500 list as of **June 30, 2026**, for fiscal quarters ending "
         "April 1 – June 30, 2026."),
        ("2 · Outcome", "The **abnormal return** over the 20 trading sessions *after* the "
         "announcement-day reaction, i.e. the return not explained by market, size and value "
         "moves (measured with ETF proxies)."),
        ("3 · Baseline model", "Predict that outcome from what is already known: the **EPS "
         "surprise** and the **announcement-day reaction**. This captures classic "
         "post-earnings drift."),
        ("4 · Language test", "Add pre-specified **earnings-call language scores**. Fit on the "
         "earliest 60% of events, test once on the latest 40%. Does prediction error fall?"),
    ]
    for col, (head, body) in zip(steps, step_text):
        with col.container(border=True, height="stretch"):
            st.markdown("**{}**".format(head))
            st.markdown(body)

    st.subheader("Workstream status")
    rows = []
    for key in ["roster", "pilot", "cohort", "exclusions", "transcript_screen", "transcript_audit",
                "features", "metrics", "holdout"]:
        ds = data[key]
        if ds.source == "absent":
            state = "⏳ Awaiting delivery"
        elif ds.error or ds.missing_columns:
            state = "❌ Delivered with problems"
        elif ds.source == "fixture":
            state = "🧪 Synthetic fixture (preview)"
        else:
            state = "✅ Delivered"
        rows.append({
            "Dataset": ds.spec.label,
            "Owner": ds.spec.owner,
            "State": state,
            "Data status": STATUS_LABELS[ds.status] if ds.source != "absent" else "—",
            "Rows": "—" if ds.n_rows is None else "{:,}".format(ds.n_rows),
            "What it is": ds.spec.description,
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True,
                 column_config={"What it is": st.column_config.TextColumn(width="large")})

    with st.expander("Glossary for readers new to the project"):
        st.markdown(
            """
- **EPS surprise:** `(reported EPS − consensus EPS) / |consensus EPS|`, in percent.
- **Announcement reaction:** the abnormal return on the first trading session that could react to the news.
- **Abnormal return:** the part of a stock's return not explained by a benchmark model.
- **ETF factor proxies:** market excess (SPY − BIL), size (IWM − SPY), value (IWD − IWF). These
  stand in for the Kenneth French factors, which lag recent events. *They are not the official French factors.*
- **SPY buy-and-hold abnormal return:** stock return minus SPY return over the same sessions; a simpler robustness check.
- **Post-earnings announcement drift (PEAD):** the documented tendency of prices to keep moving
  in the direction of an earnings surprise. The project does not try to rediscover it; it asks whether call language adds to it.
- **Chronological holdout:** the model is fit on earlier announcements and evaluated once on later ones, so it never "sees the future".
- **Out-of-sample R²:** improvement over simply predicting the training-set average. Below 0 means worse than that average.
"""
        )

# --------------------------------------------------------------------------
# 2. Data coverage
# --------------------------------------------------------------------------
with tabs[1]:
    st.subheader("From universe to usable observations")
    st.caption(
        "Each bar is a stage the data must pass. A stage reads **Pending** until its owner "
        "delivers the file; it is never filled with a placeholder number. A real zero is shown as 0."
    )
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.altair_chart(charts.coverage_funnel_chart(funnel), width="stretch")
    with right:
        with st.container(border=True):
            st.markdown("**What share of the intended sample do we have?**")
            n_events = stage["Verified Q2 2026 events"]
            if pd.isna(n_events):
                st.markdown(
                    "Not yet measurable. The intended sample is every roster company whose "
                    "fiscal quarter ended in calendar Q2 2026. That is **not automatically all "
                    "503** (e.g. Apple's and Visa's fiscal quarters are offset), so the "
                    "denominator comes from Gus's verified event manifest and exclusion log."
                )
            else:
                excl = data["exclusions"]
                st.metric("Cohort events vs. roster", "{:.0%}".format(n_events / stage["Roster stocks (June 30, 2026)"]))
                if excl.available:
                    st.dataframe(excl.frame["reason"].value_counts().rename_axis("Exclusion reason")
                                 .reset_index(name="Stocks"), hide_index=True)
                else:
                    st.caption("Exclusion log not delivered, so excluded firms cannot yet be explained.")
            if pilot.available:
                st.markdown(
                    "<span class='small-muted'>The {} pilot events are a separate pipeline check "
                    "and are not counted in this funnel.</span>".format(len(pilot.frame)),
                    unsafe_allow_html=True,
                )

    st.subheader("Is transcript coverage representative across sectors?")
    if roster is not None:
        groups = {}
        if screen is not None:
            groups["Transcript listing leads"] = screen["ticker"].unique()
        if cohort.available:
            groups["Cohort events"] = cohort.frame["ticker"].unique()
        sectors = sector_representation(roster, groups)
        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            st.altair_chart(charts.sector_share_chart(sectors), width="stretch")
        with c2:
            if "Transcript listing leads" in groups:
                wide = sectors.pivot_table(index="sector", columns="group", values="share_pct").fillna(0)
                gap = (wide["Transcript listing leads"] - wide["Roster"]).sort_values()
                st.markdown(
                    "Bars compare each sector's share of the **roster** with its share of the "
                    "{} **transcript listing leads** screened so far.".format(len(groups["Transcript listing leads"]))
                )
                st.markdown(
                    "- Most over-represented: **{}** ({:+.0f} pp)\n"
                    "- Most under-represented: **{}** ({:+.0f} pp)".format(gap.index[-1], gap.iloc[-1],
                                                                       gap.index[0], gap.iloc[0])
                )
                st.caption(
                    "Leads came from a quick screen of large, widely covered firms, not a random draw. "
                    "If the language analysis only uses such firms, results may not generalise to the full index."
                )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("When did announcements happen?")
        st.caption("Matters because the holdout split is chronological: later announcements form the test set.")
        if events is not None:
            if events_ds is pilot:
                st.caption("Showing **pilot** events.")
            st.altair_chart(charts.timeline_chart(events), width="stretch")
    with c2:
        st.subheader("Transcript access log")
        st.caption("Metadata only. No transcript text is stored in this project.")
        if audit is not None:
            show = audit[["ticker", "transcript_available", "transcript_source",
                          "retention_permission", "external_model_permission", "screened_at_utc"]]
            st.dataframe(show, hide_index=True, column_config={
                "ticker": "Ticker",
                "transcript_available": "Transcript located?",
                "transcript_source": "Source",
                "retention_permission": "May we retain it?",
                "external_model_permission": "May we send it to an AI model?",
                "screened_at_utc": "Checked on",
            })
        if screen is not None:
            st.caption("{} further tickers appear only as listing leads in the candidate screen.".format(
                len(set(screen["ticker"]) - set(audit["ticker"] if audit is not None else []))))

# --------------------------------------------------------------------------
# 3. Data quality and gaps
# --------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Where are the gaps?")
    st.markdown("Every cell is classified into exactly one status. Missing values are never filled or treated as zero.")
    legend_cols = st.columns(3)
    for i, s in enumerate(STATUS_ORDER):
        with legend_cols[i % 3]:
            st.markdown("{}<br><span class='small-muted'>{}</span>".format(status_chip(s), STATUS_DEFINITIONS[s]),
                        unsafe_allow_html=True)

    problems = [ds for ds in data.values() if ds.error or ds.missing_columns]
    for ds in problems:
        st.error("**{}** ({}) could not be used: {}".format(
            ds.spec.label, ds.spec.path,
            ds.error or "missing required columns " + ", ".join(ds.missing_columns)))

    if events is None:
        awaiting("Gus (pipeline)", "No event-level file is available yet.", ["Status grid per event and field"],
                 [DATASETS["cohort"].path])
    else:
        features_ds = data["features"]
        features = features_ds.frame if features_ds.available and features_ds.source == "real" else None
        matrix = build_status_matrix(events, events_is_synthetic, audit, screen, features)
        if events_ds is pilot:
            st.caption("Showing the **pilot** events (the cohort output has not been delivered yet).")

        f1, f2 = st.columns([2, 3])
        only_gaps = f1.toggle("Show only events with a gap", value=False)
        tickers = sorted(matrix["ticker"].unique())
        chosen = f2.multiselect("Events", tickers, default=tickers if len(tickers) <= 30 else tickers[:30])
        view = matrix[matrix["ticker"].isin(chosen)]
        if only_gaps:
            gap_tickers = view.loc[view["status"] != "Available", "ticker"].unique()
            view = view[view["ticker"].isin(gap_tickers)]

        if view.empty:
            st.info("No events match the current filters.")
        else:
            st.altair_chart(charts.status_grid_chart(view), width="stretch")

        st.markdown("**Status mix by field (all events)**")
        st.altair_chart(charts.status_count_chart(matrix), width="stretch")

        missing_cols = [c for c in ("fiscal_period_end", "event_timestamp_source") if c not in events.columns]
        if missing_cols and events_ds is pilot:
            st.info(
                "The pilot file predates the pipeline's current output schema and lacks: "
                "{}. Regenerating it is a pipeline task (Gus).".format(", ".join(missing_cols)),
                icon="ℹ️",
            )

        wide = matrix.pivot_table(index="ticker", columns="field", values="status", aggfunc="first")
        wide = wide.reindex(columns=MATRIX_COLUMNS)
        with st.expander("Status table (download)"):
            st.dataframe(wide)
            st.download_button("Download status table (CSV)", wide.to_csv().encode(), "data_status_matrix.csv",
                               mime="text/csv")
        st.caption(
            "\"Not yet observable\" is estimated from weekdays between the announcement and the data's "
            "retrieval date (with a 3-session holiday buffer). An explicit pipeline flag would replace this "
            "approximation; see the data contract proposal."
        )

# --------------------------------------------------------------------------
# 4. Event explorer
# --------------------------------------------------------------------------
with tabs[3]:
    if events is None:
        awaiting("Gus (pipeline)", "No event-level file is available yet.",
                 ["EPS surprise vs. abnormal return", "Announcement reaction vs. forward drift"],
                 [DATASETS["cohort"].path])
    else:
        if events_ds is pilot:
            pilot_banner()
        df = events.copy()
        if roster is not None:
            df = df.merge(roster[["Symbol", "Security", "GICS Sector"]].rename(
                columns={"Symbol": "ticker", "Security": "company", "GICS Sector": "sector"}), on="ticker", how="left")
        c1, c2, c3 = st.columns([2, 1, 2])
        method = c1.segmented_control(
            "Return method",
            ["ETF factor proxies (primary)", "SPY buy-and-hold (robustness)"],
            default="ETF factor proxies (primary)", required=True,
        )
        horizon = c2.selectbox("Forward window", [20, 5, 60], format_func=lambda h: "{} sessions".format(h))
        tick_opts = sorted(df["ticker"].unique())
        picked = c3.multiselect("Companies", tick_opts, default=tick_opts)
        df = df[df["ticker"].isin(picked)]

        prefix = "factor_proxy_" if method.startswith("ETF") else ""
        fwd_col = "{}abnormal_{}d_return_pct".format(prefix, horizon)
        react_col = "{}announcement_abnormal_return_pct".format(prefix)
        method_short = "ETF-proxy" if prefix else "SPY buy-and-hold"
        fwd_title = "{}-session {} abnormal return (%)".format(horizon, method_short)

        if fwd_col not in df.columns or react_col not in df.columns:
            st.warning("This file does not contain {} / {}.".format(react_col, fwd_col))
        elif df.empty:
            st.info("Select at least one company.")
        else:
            n_missing = int(df[fwd_col].isna().sum())
            a, b = st.columns(2, gap="large")
            with a:
                st.markdown("**EPS surprise vs. {}**".format(fwd_title.lower()))
                st.altair_chart(charts.surprise_scatter(df, fwd_col, fwd_title), width="stretch")
            with b:
                st.markdown("**Day-0 reaction vs. the {}-session window that follows**".format(horizon))
                st.altair_chart(charts.reaction_vs_forward_chart(
                    df, react_col, fwd_col, "{}-session forward window".format(horizon)), width="stretch")
            if n_missing:
                st.caption("{} of {} events have no {}-session value (window incomplete or missing); "
                           "they are left out of the scatter, not set to zero.".format(n_missing, len(df), horizon))

            st.markdown("**Event-level data**")
            cols = [c for c in ["ticker", "company", "sector", "fiscal_period_end", "earnings_timestamp",
                                "eps_actual", "eps_estimate", "eps_surprise_pct", react_col,
                                "{}abnormal_5d_return_pct".format(prefix), "{}abnormal_20d_return_pct".format(prefix),
                                "{}abnormal_60d_return_pct".format(prefix), "earnings_source", "prices_source"]
                    if c in df.columns]
            num = st.column_config.NumberColumn
            st.dataframe(df[cols].sort_values("earnings_timestamp"), hide_index=True, column_config={
                "ticker": "Ticker",
                "company": "Company",
                "sector": "Sector",
                "fiscal_period_end": "Fiscal period end",
                "earnings_timestamp": "Announcement time",
                "eps_actual": num("EPS actual", format="%.2f"),
                "eps_estimate": num("EPS consensus", format="%.2f"),
                "eps_surprise_pct": num("EPS surprise", format="%.2f%%"),
                react_col: num("Day-0 reaction", format="%.2f%%"),
                "{}abnormal_5d_return_pct".format(prefix): num("5-session", format="%.2f%%"),
                "{}abnormal_20d_return_pct".format(prefix): num("20-session", format="%.2f%%"),
                "{}abnormal_60d_return_pct".format(prefix): num("60-session", format="%.2f%%"),
                "earnings_source": "Earnings source",
                "prices_source": "Price source",
            })

        with st.expander("How these numbers are computed"):
            st.markdown(
                """
- **ETF-proxy abnormal return:** each stock's daily excess return is regressed on SPY−BIL, IWM−SPY
  and IWD−IWF over the 252 sessions before the event. The day-0 residual is the announcement reaction;
  forward windows sum the residuals of the following sessions.
- **SPY buy-and-hold:** stock buy-and-hold return minus SPY's over the same sessions.
- Blank cells mean the value is unavailable or the window has not finished. They are never treated as zero.
- See `audits/01_self_audit.md` for the pilot's assumptions and limitations.
"""
            )

# --------------------------------------------------------------------------
# 5. Findings
# --------------------------------------------------------------------------
with tabs[4]:
    metrics_ds, holdout_ds, features_ds = data["metrics"], data["holdout"], data["features"]
    st.subheader("Does call language improve prediction?")
    st.markdown(
        "Both models are fit on the **earliest 60%** of events and evaluated once on the **latest 40%** "
        "(the holdout), using the same events. Lower error and higher out-of-sample R² mean better predictions."
    )
    if not metrics_ds.available:
        awaiting(
            "Cammy (statistics)",
            "The model comparison has not been delivered. No results are shown until it is.",
            ["Holdout MAE, RMSE and out-of-sample R² for the baseline vs. the language-augmented model",
             "Training and holdout sample sizes and the date of the split",
             "Predicted vs. actual returns for each holdout event",
             "An automatic **Exploratory** label if the holdout is small"],
            [DATASETS["metrics"].path, DATASETS["holdout"].path],
        )
        if not use_fixtures:
            st.caption("To review the layout now, switch on *Preview with synthetic test fixtures* in the sidebar.")
    else:
        if metrics_ds.status == SYNTHETIC:
            synthetic_banner("The model comparison below")
        mt = metrics_ds.frame.set_index("model")
        if not {"baseline", "with_language"}.issubset(mt.index):
            st.error("Metrics file must contain rows for models 'baseline' and 'with_language'.")
        else:
            base, lang = mt.loc["baseline"], mt.loc["with_language"]
            test_n, train_n = int(base["test_n"]), int(base["train_n"])
            if test_n < MIN_HOLDOUT_FOR_CONFIRMATORY:
                st.warning(
                    "**Exploratory:** the holdout has {} events (proposed minimum {}). Differences this "
                    "small-sample are not reliable evidence either way.".format(test_n, MIN_HOLDOUT_FOR_CONFIRMATORY),
                    icon="🔎",
                )
            k = st.columns(4)
            k[0].metric("Training / holdout events", "{} / {}".format(train_n, test_n), border=True)
            k[1].metric("Holdout RMSE, baseline", "{:.2f} pp".format(base["rmse"]), border=True)
            k[2].metric("Holdout RMSE, with language", "{:.2f} pp".format(lang["rmse"]),
                        delta="{:+.3f} pp vs. baseline".format(lang["rmse"] - base["rmse"]),
                        delta_color="inverse", border=True)
            k[3].metric("Out-of-sample R², with language", "{:.3f}".format(lang["out_of_sample_r2"]),
                        delta="{:+.3f} vs. baseline ({:.3f})".format(
                            lang["out_of_sample_r2"] - base["out_of_sample_r2"], base["out_of_sample_r2"]),
                        border=True, help="Below 0 means worse than predicting the training-set average.")
            if "train_cutoff" in mt.columns:
                st.caption("Training events up to {}; holdout from {}.".format(
                    str(base["train_cutoff"])[:10], str(base.get("test_start", ""))[:10]))
            a, b = st.columns(2, gap="large")
            with a:
                st.markdown("**Holdout prediction error**")
                st.altair_chart(charts.metric_comparison_chart(metrics_ds.frame), width="stretch")
            with b:
                st.markdown("**Predicted vs. actual (holdout)**")
                if holdout_ds.available:
                    if holdout_ds.status == SYNTHETIC and metrics_ds.status != SYNTHETIC:
                        synthetic_banner("This chart")
                    st.altair_chart(charts.predicted_vs_actual_chart(holdout_ds.frame), width="stretch")
                    st.caption("Points on the dashed line are perfect predictions.")
                else:
                    st.info("Holdout predictions file not delivered.")

    st.divider()
    st.subheader("Language features and later returns")
    st.markdown("A descriptive look at each language score against the 20-session outcome. "
                "This is an association plot, not the predictive test above.")
    if not features_ds.available:
        awaiting("the transcript-features workstream", "No language features have been delivered.",
                 ["Scatter of each pre-specified language score against the 20-session abnormal return",
                  "Coverage of scored events, with synthetic-transcript scores labelled"],
                 [DATASETS["features"].path])
    else:
        feats = features_ds.frame
        if features_ds.status == SYNTHETIC:
            synthetic_banner("This feature view")
        outcome_col = "factor_proxy_abnormal_20d_return_pct"
        if features_ds.source == "fixture":
            ev = data["synthetic_events"].frame
        else:
            ev = cohort.frame if cohort.available else None
        lang_cols = language_feature_columns(feats)
        if ev is None:
            st.info("Features are delivered, but there is no cohort output to join them to yet.")
        elif not lang_cols:
            st.error("Features file has no columns starting with 'lang_'.")
        else:
            joined = feats.merge(ev[["ticker", "fiscal_period_end", outcome_col]],
                                 on=["ticker", "fiscal_period_end"], how="left")
            c1, c2 = st.columns([1, 3])
            feature = c1.selectbox("Language score", lang_cols)
            c1.metric("Scored events", len(feats))
            c1.metric("Joined to an outcome", int(joined[outcome_col].notna().sum()))
            for meta in ["model_id", "prompt_version"]:
                if meta in feats.columns:
                    c1.caption("{}: `{}`".format(meta, feats[meta].dropna().iloc[0] if feats[meta].notna().any() else "—"))
            with c2:
                st.altair_chart(charts.feature_scatter(joined, feature, outcome_col,
                                                       "20-session ETF-proxy abnormal return (%)"), width="stretch")

# --------------------------------------------------------------------------
# 6. Methods and limitations
# --------------------------------------------------------------------------
LIMITATIONS = {
    "Sample and selection": [
        ("Single reporting cohort",
         "Only fiscal quarters ending in calendar Q2 2026. Results describe one quarter's market "
         "environment and may not hold in other periods.", "README, STATUS"),
        ("Roster is not an official S&P file",
         "The June 30, 2026 list is an archived Wikipedia revision (1361794875). It is dated and "
         "fixed, but not a licensed index-provider record.", "README"),
        ("Fiscal calendars differ",
         "Some firms (e.g. Apple, Visa) have offset fiscal years; a reporting date does not imply a "
         "calendar-Q2 fiscal end. Each event's period end must be verified.", "README"),
        ("Transcript coverage may be skewed",
         "Transcript leads so far are large, heavily covered firms. A language sample limited to "
         "them may not represent the index.", "Data coverage tab"),
        ("Pilot is a convenience sample",
         "The four pilot firms were hand-picked to test the pipeline and carry no evidential weight.",
         "AGENTS, audit"),
    ],
    "Measurement": [
        ("ETF proxies are not French factors",
         "Market, size and value are proxied with SPY−BIL, IWM−SPY and IWD−IWF because official "
         "factor files lag. Proxy choice can change abnormal returns.", "README, audit"),
        ("EPS consensus and timestamps need verification",
         "Yahoo Finance does not preserve point-in-time consensus or reliable fiscal period ends. "
         "Cohort EPS and announcement times require documented sources.", "README, audit"),
        ("Announcement timing",
         "Before-open vs. after-close releases change which session is day 0. Errors shift returns "
         "between the reaction and the forward window.", "audit"),
    ],
    "Timing and confounding": [
        ("Incomplete forward windows",
         "Some 60-session windows were not finished as of November 6, 2026. They are reported as "
         "not yet observable, never as zero.", "STATUS, audit"),
        ("Overlapping windows and shared news",
         "Many firms report within weeks of each other, so their return windows overlap and share "
         "market news; events are not fully independent.", "audit"),
        ("Same-day confounding news",
         "Other news released with earnings (guidance, M&A, macro data) can drive returns.", "audit"),
    ],
    "Transcripts and AI scoring": [
        ("Rights not yet established",
         "No transcript is rights-cleared for retention or external-model use. Public visibility "
         "is not permission; scraping restricted sites is not allowed.", "README, STATUS"),
        ("Model training-data cutoff",
         "The proposed scoring model's documented cutoff (Aug 31, 2025) predates the cohort, but a "
         "published cutoff does not prove specific events were absent from training data.", "README"),
        ("Leakage controls",
         "Scores must be fixed and reproducible (pinned model, versioned prompt) and must not see "
         "later returns or post-call information.", "AGENTS"),
        ("Synthetic transcripts",
         "Early feature work uses synthetic transcripts to test the workflow. Their scores say "
         "nothing about real calls.", "Team plan"),
    ],
    "Inference and interpretation": [
        ("Small holdout",
         "A 40% holdout of a transcript-covered subset may be small; differences between models "
         "can be noise. Small samples are labelled exploratory.", "README"),
        ("Prediction ≠ profit",
         "A predictive association is not a trading strategy: no transaction costs, capacity or "
         "implementation are modelled. Nothing here is investment advice.", "STATUS, audit"),
    ],
}

with tabs[5]:
    st.subheader("What could make these results wrong?")
    st.markdown("Limitations grouped by where they enter the study. Sources point to the project documents "
                "that track each one (`README.md`, `STATUS.md`, `audits/01_self_audit.md`, `AGENTS.md`).")
    cols = st.columns(2, gap="large")
    for i, (group, items) in enumerate(LIMITATIONS.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown("#### {}".format(group))
                for title, body, source in items:
                    st.markdown("**{}**: {}  \n<span class='small-muted'>Source: {}</span>".format(
                        title, body, source), unsafe_allow_html=True)

    st.subheader("Data provenance")
    prov = []
    for key, ds in data.items():
        if ds.source == "absent":
            continue
        retrieved = ""
        if ds.frame is not None:
            for c in ("retrieved_at_utc", "screened_at_utc", "search_result_checked", "roster_date", "scored_at_utc"):
                if c in ds.frame.columns and ds.frame[c].notna().any():
                    retrieved = str(ds.frame[c].dropna().astype(str).max())[:10]
                    break
        prov.append({"Dataset": ds.spec.label, "File": str(ds.path.relative_to(REPO_ROOT)) if ds.path else "",
                     "Data status": STATUS_LABELS[ds.status], "Dated": retrieved,
                     "Notes": ds.spec.description})
    st.dataframe(pd.DataFrame(prov), hide_index=True,
                 column_config={"Notes": st.column_config.TextColumn(width="large")})
