"""Altair chart builders. Presentation only: inputs are already-computed data.

Colors follow a validated reference palette: categorical slot 1 (blue) and
slot 2 (orange) for two-series comparisons, and a fixed status palette that
is always paired with an icon and text label.
"""

from __future__ import annotations

import altair as alt
import pandas as pd

from status import MATRIX_COLUMNS, STATUS_ORDER, STATUS_STYLE

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
MUTED = "#898781"
LABEL = "#898781"  # mid-gray readable on both light and dark Streamlit themes
BASELINE = "#c3c2b7"

STATUS_SCALE = alt.Scale(
    domain=STATUS_ORDER, range=[STATUS_STYLE[s]["color"] for s in STATUS_ORDER]
)


def _zero_rule(axis: str):
    data = pd.DataFrame({"v": [0]})
    enc = {"x": "v:Q"} if axis == "x" else {"y": "v:Q"}
    return alt.Chart(data).mark_rule(color=BASELINE, strokeWidth=1).encode(**enc)


def coverage_funnel_chart(funnel: pd.DataFrame) -> alt.Chart:
    df = funnel.copy()
    df["label"] = df.apply(
        lambda r: "{:,}".format(int(r["count"])) if pd.notna(r["count"]) else "Pending: {}".format(r["owner"]),
        axis=1,
    )
    df["plot_count"] = df["count"].astype("float")
    order = list(df["stage"])
    y = alt.Y("stage:N", sort=order, title=None, axis=alt.Axis(labelLimit=260))
    tooltip = [
        alt.Tooltip("stage:N", title="Stage"),
        alt.Tooltip("label:N", title="Count"),
        alt.Tooltip("owner:N", title="Owner"),
        alt.Tooltip("note:N", title="Definition"),
    ]
    base = alt.Chart(df).encode(y=y, tooltip=tooltip)
    bars = base.transform_filter("isValid(datum.plot_count)").mark_bar(
        color=BLUE, cornerRadiusEnd=4, height=22
    ).encode(x=alt.X("plot_count:Q", title="Events / stocks", scale=alt.Scale(domainMin=0)))
    counts = base.transform_filter("isValid(datum.plot_count)").mark_text(
        align="left", dx=6, fontWeight="bold", color=LABEL
    ).encode(x="plot_count:Q", text="label:N")
    pending = base.transform_filter("!isValid(datum.plot_count)").mark_text(
        align="left", dx=4, color=MUTED, fontStyle="italic"
    ).encode(x=alt.datum(0), text="label:N")
    return (bars + counts + pending).properties(height=alt.Step(40))


def sector_share_chart(sectors: pd.DataFrame) -> alt.Chart:
    groups = list(dict.fromkeys(sectors["group"]))
    palette = [BLUE, ORANGE, AQUA][: len(groups)]
    sector_order = (
        sectors[sectors["group"] == "Roster"].sort_values("share", ascending=False)["sector"].tolist()
    )
    return (
        alt.Chart(sectors)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y("sector:N", sort=sector_order, title=None, axis=alt.Axis(labelLimit=200)),
            yOffset=alt.YOffset("group:N", sort=groups),
            x=alt.X("share_pct:Q", title="Share of group (%)"),
            color=alt.Color(
                "group:N",
                scale=alt.Scale(domain=groups, range=palette),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=[
                alt.Tooltip("group:N", title="Group"),
                alt.Tooltip("group_n:Q", title="Stocks in group"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("share_pct:Q", title="Share (%)", format=".1f"),
            ],
        )
        .properties(height=alt.Step(12 if len(groups) > 2 else 14))
    )


def status_grid_chart(matrix: pd.DataFrame) -> alt.Chart:
    df = matrix.copy()
    df["icon"] = df["status"].map(lambda s: STATUS_STYLE[s]["icon"])
    df["ink"] = df["status"].map(lambda s: STATUS_STYLE[s]["ink"])
    tickers = list(dict.fromkeys(df["ticker"]))
    tooltip = [
        alt.Tooltip("ticker:N", title="Event"),
        alt.Tooltip("field:N", title="Field"),
        alt.Tooltip("status:N", title="Status"),
        alt.Tooltip("detail:N", title="Detail"),
    ]
    base = alt.Chart(df).encode(
        x=alt.X("field:N", sort=MATRIX_COLUMNS, title=None, scale=alt.Scale(paddingInner=0.06),
                axis=alt.Axis(labelAngle=-35, labelLimit=180, orient="top", labelOverlap=False,
                              domain=False, ticks=False)),
        y=alt.Y("ticker:N", sort=tickers, title=None, scale=alt.Scale(paddingInner=0.12),
                axis=alt.Axis(domain=False, ticks=False)),
        tooltip=tooltip,
    )
    cells = base.mark_rect(cornerRadius=4).encode(
        color=alt.Color("status:N", scale=STATUS_SCALE,
                        legend=alt.Legend(title="Status", orient="bottom", columns=6))
    )
    icons = base.mark_text(fontSize=14, fontWeight="bold").encode(
        text="icon:N", color=alt.Color("ink:N", scale=None)
    )
    return (cells + icons).properties(height=alt.Step(34))


def status_count_chart(matrix: pd.DataFrame) -> alt.Chart:
    counts = matrix.groupby(["field", "status"]).size().rename("n").reset_index()
    counts["order"] = counts["status"].map(STATUS_ORDER.index)
    return (
        alt.Chart(counts)
        .mark_bar(cornerRadius=2)
        .encode(
            y=alt.Y("field:N", sort=MATRIX_COLUMNS, title=None, axis=alt.Axis(labelLimit=200)),
            x=alt.X("n:Q", stack="normalize", title="Share of events", axis=alt.Axis(format="%")),
            color=alt.Color("status:N", scale=STATUS_SCALE, legend=None),
            order=alt.Order("order:Q"),
            tooltip=[
                alt.Tooltip("field:N", title="Field"),
                alt.Tooltip("status:N", title="Status"),
                alt.Tooltip("n:Q", title="Events"),
            ],
        )
        .properties(height=alt.Step(26))
    )


def timeline_chart(events: pd.DataFrame) -> alt.Chart:
    df = events.copy()
    df["date"] = pd.to_datetime(df["earnings_timestamp"].astype(str).str[:10], errors="coerce")
    df = df.dropna(subset=["date"])
    if len(df) <= 25:
        base = alt.Chart(df).encode(
            x=alt.X("date:T", title="Announcement date", axis=alt.Axis(format="%b %d")),
            y=alt.Y("ticker:N", sort=alt.EncodingSortField("date"), title=None),
            tooltip=[alt.Tooltip("ticker:N"), alt.Tooltip("date:T", title="Date", format="%Y-%m-%d")],
        )
        dots = base.mark_circle(size=140, color=BLUE, stroke="white", strokeWidth=2, opacity=1)
        labels = base.mark_text(align="left", dx=10, color=MUTED).encode(
            text=alt.Text("date:T", format="%b %d")
        )
        return (dots + labels).properties(height=alt.Step(32))
    return (
        alt.Chart(df)
        .mark_bar(color=BLUE, cornerRadiusEnd=4)
        .encode(
            x=alt.X("yearweek(date):T", title="Week of announcement"),
            y=alt.Y("count():Q", title="Events"),
            tooltip=[alt.Tooltip("yearweek(date):T", title="Week of"), alt.Tooltip("count():Q", title="Events")],
        )
        .properties(height=260)
    )


def surprise_scatter(events: pd.DataFrame, y_col: str, y_title: str) -> alt.Chart:
    df = events.dropna(subset=["eps_surprise_pct", y_col])
    base = alt.Chart(df).encode(
        x=alt.X("eps_surprise_pct:Q", title="EPS surprise (%)"),
        y=alt.Y("{}:Q".format(y_col), title=y_title),
        tooltip=[
            alt.Tooltip("ticker:N", title="Ticker"),
            alt.Tooltip("eps_surprise_pct:Q", title="EPS surprise (%)", format=".2f"),
            alt.Tooltip("{}:Q".format(y_col), title=y_title, format=".2f"),
        ],
    )
    dots = base.mark_circle(size=160, color=BLUE, stroke="white", strokeWidth=2, opacity=1)
    labels = base.mark_text(align="left", dx=10, dy=-8, fontWeight="bold", color=LABEL).encode(text="ticker:N")
    return (_zero_rule("x") + _zero_rule("y") + dots + labels).properties(height=380)


def reaction_vs_forward_chart(events: pd.DataFrame, reaction_col: str, forward_col: str,
                              forward_label: str) -> alt.Chart:
    long = events[["ticker", reaction_col, forward_col]].melt(
        id_vars="ticker", var_name="measure", value_name="value"
    )
    names = {reaction_col: "Announcement reaction (day 0)", forward_col: forward_label}
    long["measure"] = long["measure"].map(names)
    long["shown"] = long["value"].map(lambda v: "not yet observable / missing" if pd.isna(v) else "{:.2f}%".format(v))
    domain = list(names.values())
    base = alt.Chart(long).encode(
        x=alt.X("ticker:N", title=None, axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("measure:N", sort=domain),
        tooltip=[
            alt.Tooltip("ticker:N", title="Ticker"),
            alt.Tooltip("measure:N", title="Measure"),
            alt.Tooltip("shown:N", title="Abnormal return"),
        ],
    )
    bars = base.transform_filter("isValid(datum.value)").mark_bar(cornerRadius=4).encode(
        y=alt.Y("value:Q", title="Abnormal return (%)"),
        color=alt.Color("measure:N", scale=alt.Scale(domain=domain, range=[BLUE, ORANGE]),
                        legend=alt.Legend(title=None, orient="top", labelLimit=320)),
    )
    gaps = base.transform_filter("!isValid(datum.value)").mark_text(
        text="n/a", color=MUTED, dy=-6, fontStyle="italic"
    ).encode(y=alt.datum(0))
    return (_zero_rule("y") + bars + gaps).properties(height=340)


MODEL_NAMES = {"baseline": "Baseline", "with_language": "Baseline + language"}


def metric_comparison_chart(metrics: pd.DataFrame) -> alt.Chart:
    df = metrics.copy()
    df["model_label"] = df["model"].map(MODEL_NAMES).fillna(df["model"])
    long = df.melt(id_vars=["model_label"], value_vars=["mae", "rmse"], var_name="metric", value_name="value")
    long["metric"] = long["metric"].str.upper()
    domain = [MODEL_NAMES["baseline"], MODEL_NAMES["with_language"]]
    return (
        alt.Chart(long)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=alt.Y("metric:N", title=None),
            yOffset=alt.YOffset("model_label:N", sort=domain),
            x=alt.X("value:Q", title="Holdout error (percentage points, lower is better)"),
            color=alt.Color("model_label:N", scale=alt.Scale(domain=domain, range=[BLUE, ORANGE]),
                            legend=alt.Legend(title=None, orient="top", labelLimit=320)),
            tooltip=[
                alt.Tooltip("model_label:N", title="Model"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("value:Q", title="Value", format=".3f"),
            ],
        )
        .properties(height=alt.Step(26))
    )


def predicted_vs_actual_chart(holdout: pd.DataFrame) -> alt.Chart:
    long = holdout.melt(
        id_vars=["ticker", "actual"],
        value_vars=["baseline_prediction", "language_model_prediction"],
        var_name="model",
        value_name="predicted",
    )
    long["model"] = long["model"].map(
        {"baseline_prediction": MODEL_NAMES["baseline"], "language_model_prediction": MODEL_NAMES["with_language"]}
    )
    lo = float(min(long["actual"].min(), long["predicted"].min()))
    hi = float(max(long["actual"].max(), long["predicted"].max()))
    diag = alt.Chart(pd.DataFrame({"a": [lo, hi], "b": [lo, hi]})).mark_line(
        color=BASELINE, strokeDash=[4, 4], strokeWidth=2
    ).encode(x="a:Q", y="b:Q")
    domain = [MODEL_NAMES["baseline"], MODEL_NAMES["with_language"]]
    dots = alt.Chart(long).mark_point(size=90, filled=True, opacity=0.9, stroke="white", strokeWidth=1.5).encode(
        x=alt.X("predicted:Q", title="Predicted 20-session return (%)"),
        y=alt.Y("actual:Q", title="Actual 20-session return (%)"),
        color=alt.Color("model:N", scale=alt.Scale(domain=domain, range=[BLUE, ORANGE]),
                        legend=alt.Legend(title=None, orient="top", labelLimit=320)),
        shape=alt.Shape("model:N", scale=alt.Scale(domain=domain, range=["circle", "triangle-up"]),
                        legend=alt.Legend(title=None, orient="top", labelLimit=320)),
        tooltip=[
            alt.Tooltip("ticker:N", title="Event"),
            alt.Tooltip("model:N", title="Model"),
            alt.Tooltip("predicted:Q", title="Predicted", format=".2f"),
            alt.Tooltip("actual:Q", title="Actual", format=".2f"),
        ],
    )
    return (diag + dots).properties(height=380)


def feature_scatter(df: pd.DataFrame, feature: str, outcome: str, outcome_title: str) -> alt.Chart:
    data = df.dropna(subset=[feature, outcome])
    dots = alt.Chart(data).mark_circle(size=90, color=BLUE, opacity=0.85, stroke="white", strokeWidth=1.5).encode(
        x=alt.X("{}:Q".format(feature), title=feature),
        y=alt.Y("{}:Q".format(outcome), title=outcome_title),
        tooltip=[
            alt.Tooltip("ticker:N", title="Event"),
            alt.Tooltip("{}:Q".format(feature), format=".3f"),
            alt.Tooltip("{}:Q".format(outcome), title=outcome_title, format=".2f"),
        ],
    )
    return (_zero_rule("y") + dots).properties(height=340)


# --------------------------------------------------------------------------
# Checkpoint results (three nested runs on CAR[0,1])
# --------------------------------------------------------------------------
RUN_COLORS = [MUTED, BLUE, ORANGE]


def run_metrics_chart(runs: pd.DataFrame) -> alt.Chart:
    labels = list(runs.sort_values("run")["label"])
    titles = {"out_of_sample_r2": "Holdout R² (higher = better)", "mae": "MAE, pp (lower = better)",
              "rmse": "RMSE, pp (lower = better)"}
    long = runs.melt(id_vars=["run", "label"], value_vars=list(titles), var_name="metric", value_name="value")
    long["metric"] = long["metric"].map(titles)
    long["shown"] = long.apply(lambda r: ("{:.3f}" if "R²" in r["metric"] else "{:.2f}").format(r["value"]), axis=1)
    base = alt.Chart(long).encode(
        y=alt.Y("label:N", sort=labels, title=None, axis=alt.Axis(labelLimit=220)),
        x=alt.X("value:Q", title=None, axis=alt.Axis(tickCount=4)),
        tooltip=[alt.Tooltip("label:N", title="Run"), alt.Tooltip("metric:N", title="Metric"),
                 alt.Tooltip("shown:N", title="Value")],
    )
    bars = base.mark_bar(cornerRadiusEnd=4, height=22).encode(
        color=alt.Color("label:N", scale=alt.Scale(domain=labels, range=RUN_COLORS), legend=None))
    text = base.mark_text(align="left", dx=6, fontWeight="bold", color=LABEL).encode(text="shown:N")
    return (
        alt.layer(bars, text, data=long)
        .properties(width=150, height=alt.Step(34))
        .facet(column=alt.Column("metric:N", sort=list(titles.values()), title=None,
                                 header=alt.Header(labelFontWeight="bold", labelFontSize=13)))
        .resolve_scale(x="independent")
    )


def coefficient_chart(coefs: pd.DataFrame, names: dict) -> alt.Chart:
    df = coefs.copy()
    df["name"] = df["variable"].map(names).fillna(df["variable"])
    df["side"] = df.apply(lambda r: "Clearly above 0" if r["ci_low"] > 0 else
                          ("Clearly below 0" if r["ci_high"] < 0 else "Interval includes 0"), axis=1)
    order = list(df.sort_values("coef_per_sd")["name"])
    domain = ["Clearly above 0", "Interval includes 0", "Clearly below 0"]
    base = alt.Chart(df).encode(
        y=alt.Y("name:N", sort=order, title=None, axis=alt.Axis(labelLimit=260)),
        tooltip=[alt.Tooltip("name:N", title="Variable"),
                 alt.Tooltip("coef_per_sd:Q", title="Effect of +1 SD (pp)", format=".2f"),
                 alt.Tooltip("ci_low:Q", title="95% low", format=".2f"),
                 alt.Tooltip("ci_high:Q", title="95% high", format=".2f")],
    )
    color = alt.Color("side:N", scale=alt.Scale(domain=domain, range=[BLUE, BASELINE, ORANGE]),
                      legend=alt.Legend(title=None, orient="bottom", labelLimit=200))
    bars = base.mark_rule(strokeWidth=3).encode(x=alt.X("ci_low:Q", title="Change in CAR[0,1] per +1 SD (pp)"),
                                                x2="ci_high:Q", color=color)
    dots = base.mark_circle(size=90, opacity=1).encode(x="coef_per_sd:Q", color=color)
    return (_zero_rule("x") + bars + dots).properties(height=alt.Step(22))


def binned_relationship_chart(df: pd.DataFrame, x: str, x_title: str, y: str, y_title: str) -> alt.Chart:
    data = df.dropna(subset=[x, y])
    dots = alt.Chart(data).mark_circle(size=40, color=BLUE, opacity=0.35).encode(
        x=alt.X("{}:Q".format(x), title=x_title),
        y=alt.Y("{}:Q".format(y), title=y_title),
        tooltip=[alt.Tooltip("ticker:N", title="Event"), alt.Tooltip("{}:Q".format(x), title=x_title, format=".2f"),
                 alt.Tooltip("{}:Q".format(y), title=y_title, format=".2f")],
    )
    fit = alt.Chart(data).transform_regression(x, y).mark_line(color=ORANGE, strokeWidth=3).encode(
        x="{}:Q".format(x), y="{}:Q".format(y))
    return (_zero_rule("y") + dots + fit).properties(height=360)


def group_mean_chart(df: pd.DataFrame, group: str, y: str, y_title: str) -> alt.Chart:
    data = df.dropna(subset=[group, y])
    base = alt.Chart(data).encode(x=alt.X("{}:N".format(group), title=None, axis=alt.Axis(labelAngle=0)))
    bars = base.mark_bar(color=BLUE, cornerRadiusEnd=4, size=48).encode(
        y=alt.Y("mean({}):Q".format(y), title="Average " + y_title),
        tooltip=[alt.Tooltip("{}:N".format(group), title="Group"),
                 alt.Tooltip("mean({}):Q".format(y), title="Average", format=".2f"),
                 alt.Tooltip("count():Q", title="Events")])
    err = base.mark_errorbar(extent="ci", color=LABEL).encode(y="{}:Q".format(y))
    return (_zero_rule("y") + bars + err).properties(height=300)


def run_predictions_chart(preds: pd.DataFrame, run_col: str, run_label: str) -> alt.Chart:
    data = preds.dropna(subset=["actual", run_col])
    lo = float(min(data["actual"].min(), data[run_col].min()))
    hi = float(max(data["actual"].max(), data[run_col].max()))
    diag = alt.Chart(pd.DataFrame({"a": [lo, hi], "b": [lo, hi]})).mark_line(
        color=BASELINE, strokeDash=[4, 4], strokeWidth=2).encode(x="a:Q", y="b:Q")
    dots = alt.Chart(data).mark_circle(size=60, color=BLUE, opacity=0.6).encode(
        x=alt.X("{}:Q".format(run_col), title="Predicted CAR[0,1] (%), " + run_label),
        y=alt.Y("actual:Q", title="Actual CAR[0,1] (%)"),
        tooltip=[alt.Tooltip("ticker:N", title="Event"), alt.Tooltip("call_date:N", title="Call date"),
                 alt.Tooltip("{}:Q".format(run_col), title="Predicted", format=".2f"),
                 alt.Tooltip("actual:Q", title="Actual", format=".2f")])
    return (diag + dots).properties(height=360)
