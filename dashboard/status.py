"""Data-status rules for the dashboard (presentation logic only).

Every cell the dashboard reports about an event gets exactly one of six
statuses. Missing values are never filled or zeroed; they are classified so
viewers can see *why* a value is absent.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

AVAILABLE = "Available"
MISSING = "Missing"
NOT_YET = "Not yet observable"
SYNTHETIC = "Synthetic"
RESTRICTED = "Restricted"
PENDING = "Pending"

STATUS_ORDER = [AVAILABLE, NOT_YET, RESTRICTED, SYNTHETIC, PENDING, MISSING]

# Icon + label always accompany the color so status is never color-alone.
STATUS_STYLE = {
    AVAILABLE: {"icon": "✓", "color": "#0ca30c", "ink": "#ffffff"},
    NOT_YET: {"icon": "◷", "color": "#fab219", "ink": "#0b0b0b"},
    RESTRICTED: {"icon": "⚿", "color": "#ec835a", "ink": "#0b0b0b"},
    SYNTHETIC: {"icon": "◆", "color": "#6250d6", "ink": "#ffffff"},
    PENDING: {"icon": "…", "color": "#c3c2b7", "ink": "#0b0b0b"},
    MISSING: {"icon": "✕", "color": "#d03b3b", "ink": "#ffffff"},
}

STATUS_DEFINITIONS = {
    AVAILABLE: "A value is present in a delivered, non-synthetic file.",
    NOT_YET: "The forward return window had not finished as of the data's "
    "retrieval date. Not an error; it fills in once enough sessions pass.",
    RESTRICTED: "The source exists but retention or AI-model rights are not "
    "established, so it cannot be used yet.",
    SYNTHETIC: "Generated for testing the workflow. Never a research result.",
    PENDING: "The upstream file or check has not been delivered yet.",
    MISSING: "Expected but absent in a delivered file, or confirmed unavailable "
    "at the checked source.",
}

# Weekday count ignores market holidays, so allow a small buffer before
# calling an absent forward return "Missing" instead of "Not yet observable".
HOLIDAY_BUFFER_SESSIONS = 3

EVENT_FIELDS = [
    # (display label, column, forward horizon in sessions or None)
    ("Fiscal period end", "fiscal_period_end", None),
    ("Announcement time", "earnings_timestamp", None),
    ("EPS actual", "eps_actual", None),
    ("EPS consensus", "eps_estimate", None),
    ("Announcement reaction", "factor_proxy_announcement_abnormal_return_pct", 0),
    ("5-session return", "factor_proxy_abnormal_5d_return_pct", 5),
    ("20-session return (primary)", "factor_proxy_abnormal_20d_return_pct", 20),
    ("60-session return", "factor_proxy_abnormal_60d_return_pct", 60),
]
TRANSCRIPT_FIELD = "Transcript"
FEATURE_FIELD = "Language features"
MATRIX_COLUMNS = [label for label, _, _ in EVENT_FIELDS] + [TRANSCRIPT_FIELD, FEATURE_FIELD]


def _is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    return isinstance(value, str) and value.strip() == ""


def _event_date(row) -> Optional[pd.Timestamp]:
    for column in ("earnings_date", "earnings_timestamp"):
        value = row.get(column)
        if not _is_blank(value):
            parsed = pd.to_datetime(str(value)[:10], errors="coerce")
            if not pd.isna(parsed):
                return parsed
    return None


def _as_of_date(row, fallback: Optional[pd.Timestamp]) -> Optional[pd.Timestamp]:
    for column in ("as_of_date", "retrieved_at_utc"):
        value = row.get(column)
        if not _is_blank(value):
            parsed = pd.to_datetime(str(value)[:10], errors="coerce")
            if not pd.isna(parsed):
                return parsed
    return fallback


def forward_window_status(event_date, as_of_date, horizon: int) -> str:
    """Classify an absent forward return as NOT_YET or MISSING.

    Approximation: weekdays after the event date up to the as-of date. The
    reaction session plus ``horizon`` forward sessions must have elapsed.
    """
    if event_date is None or as_of_date is None:
        return MISSING
    elapsed = int(
        np.busday_count(
            (event_date + pd.Timedelta(days=1)).date(),
            (as_of_date + pd.Timedelta(days=1)).date(),
        )
    )
    needed = horizon + 1 + HOLIDAY_BUFFER_SESSIONS
    return NOT_YET if elapsed < needed else MISSING


def classify_event_value(row, column: str, horizon: Optional[int], synthetic: bool,
                         as_of_fallback=None) -> str:
    if column not in row.index:
        return MISSING
    if _is_blank(row[column]):
        if horizon:
            return forward_window_status(_event_date(row), _as_of_date(row, as_of_fallback), horizon)
        return MISSING
    return SYNTHETIC if synthetic else AVAILABLE


def _permission_granted(value) -> bool:
    return isinstance(value, str) and value.strip().lower().startswith(("yes", "granted"))


def transcript_status(ticker: str, audit: Optional[pd.DataFrame],
                      screen: Optional[pd.DataFrame]) -> tuple:
    """Return (status, detail) for one ticker's transcript."""
    if audit is not None and "ticker" in audit.columns:
        rows = audit[audit["ticker"] == ticker]
        if not rows.empty:
            row = rows.iloc[-1]
            located = str(row.get("transcript_available", "")).strip().lower()
            if located.startswith("yes"):
                if _permission_granted(row.get("retention_permission")) and _permission_granted(
                    row.get("external_model_permission")
                ):
                    return AVAILABLE, "Located; retention and model rights recorded as granted."
                return RESTRICTED, "Located at {}; rights not established.".format(
                    row.get("transcript_source", "source")
                )
            if located.startswith("no"):
                return MISSING, str(row.get("transcript_available"))
            return PENDING, "Audit row exists but availability is unclear."
    if screen is not None and "ticker" in screen.columns and ticker in set(screen["ticker"]):
        return PENDING, "Listing lead only; not yet checked at a permitted source."
    return PENDING, "Not yet screened."


def feature_status(ticker: str, fiscal_period_end, features: Optional[pd.DataFrame]) -> tuple:
    if features is None:
        return PENDING, "Features file not delivered."
    rows = features[features["ticker"] == ticker]
    if not _is_blank(fiscal_period_end) and "fiscal_period_end" in features.columns:
        rows = rows[rows["fiscal_period_end"].astype(str) == str(fiscal_period_end)]
    if rows.empty:
        return MISSING, "No feature row for this event."
    status = str(rows.iloc[0].get("data_status", "")).lower()
    if status == "synthetic":
        return SYNTHETIC, "Scored from a synthetic transcript."
    return AVAILABLE, "Scored."


def build_status_matrix(events: pd.DataFrame, events_synthetic: bool,
                        audit: Optional[pd.DataFrame] = None,
                        screen: Optional[pd.DataFrame] = None,
                        features: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Long table: one row per (event, field) with status and detail."""
    records = []
    for _, row in events.iterrows():
        ticker = row["ticker"]
        fpe = row.get("fiscal_period_end")
        for label, column, horizon in EVENT_FIELDS:
            status = classify_event_value(row, column, horizon, events_synthetic)
            if column not in events.columns:
                detail = "Column not present in the delivered file."
            elif status == NOT_YET:
                detail = "Window incomplete as of retrieval date."
            else:
                detail = ""
            records.append((ticker, fpe, label, status, detail))
        t_status, t_detail = transcript_status(ticker, audit, screen)
        records.append((ticker, fpe, TRANSCRIPT_FIELD, t_status, t_detail))
        f_status, f_detail = feature_status(ticker, fpe, features)
        records.append((ticker, fpe, FEATURE_FIELD, f_status, f_detail))
    return pd.DataFrame(records, columns=["ticker", "fiscal_period_end", "field", "status", "detail"])


def status_counts(matrix: pd.DataFrame) -> pd.DataFrame:
    counts = (
        matrix.groupby(["field", "status"]).size().rename("n").reset_index()
        if not matrix.empty
        else pd.DataFrame(columns=["field", "status", "n"])
    )
    return counts


def coverage_funnel(roster, cohort, audit, features, metrics) -> pd.DataFrame:
    """Coverage stages. ``count`` is None (shown as Pending) when the stage's
    source has not been delivered; a real zero stays zero."""

    def n(frame):
        return None if frame is None else len(frame)

    complete_20d = None
    if cohort is not None and "factor_proxy_abnormal_20d_return_pct" in cohort.columns:
        complete_20d = int(cohort["factor_proxy_abnormal_20d_return_pct"].notna().sum())

    located = cleared = None
    if audit is not None:
        located_mask = audit["transcript_available"].astype(str).str.lower().str.startswith("yes")
        located = int(located_mask.sum())
        cleared = int(
            (
                located_mask
                & audit["retention_permission"].map(_permission_granted)
                & audit["external_model_permission"].map(_permission_granted)
            ).sum()
        )

    scored = None
    if features is not None:
        real = features["data_status"].astype(str).str.lower() != "synthetic"
        scored = int(real.sum())

    model_n = None
    if metrics is not None and not metrics.empty:
        real_metrics = metrics[metrics["data_status"].astype(str).str.lower() != "synthetic"]
        if not real_metrics.empty:
            first = real_metrics.iloc[0]
            model_n = int(first["train_n"]) + int(first["test_n"])

    stages = [
        ("Roster stocks (June 30, 2026)", n(roster), "Shared input",
         "Fixed point-in-time universe."),
        ("Verified Q2 2026 events", n(cohort), "Gus",
         "Fiscal quarter ending Apr 1 – Jun 30, 2026, with sourced EPS and timestamp."),
        ("Complete 20-session outcome", complete_20d, "Gus",
         "Primary outcome observed for the full window."),
        ("Transcript located", located, "Transcript coordination",
         "From the access log; locating a transcript is not permission to use it."),
        ("Transcript rights cleared", cleared, "Transcript coordination",
         "Retention and external-model permission both recorded."),
        ("Events with language features", scored, "Transcript coordination",
         "Non-synthetic scored events only."),
        ("Model sample (train + holdout)", model_n, "Cammy",
         "Shared complete-case sample used by both models."),
    ]
    return pd.DataFrame(stages, columns=["stage", "count", "owner", "note"])


def sector_representation(roster: pd.DataFrame, groups: dict) -> pd.DataFrame:
    """Share of each GICS sector in the roster versus in each ticker group.

    ``groups`` maps a group label to an iterable of tickers.
    """
    sector_of = roster.set_index("Symbol")["GICS Sector"]
    frames = [
        roster["GICS Sector"].value_counts(normalize=True).rename("share").to_frame().assign(group="Roster")
    ]
    for label, tickers in groups.items():
        sectors = sector_of.reindex(list(tickers)).dropna()
        if sectors.empty:
            continue
        frames.append(sectors.value_counts(normalize=True).rename("share").to_frame().assign(group=label))
    out = pd.concat(frames).rename_axis("sector").reset_index()
    out["share_pct"] = out["share"] * 100
    counts = {"Roster": len(roster)}
    for label, tickers in groups.items():
        counts[label] = int(sector_of.reindex(list(tickers)).notna().sum())
    out["group_n"] = out["group"].map(counts)
    return out
