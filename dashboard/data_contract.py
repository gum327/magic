"""Presentation-side schema and quality checks for event datasets."""

import numpy as np
import pandas as pd

EVENT_KEY = ("ticker", "fiscal_period_end")
REQUIRED_COLUMNS = ("ticker",)
OUTCOME_COLUMNS = (
    "car_0_1_pct",
    "factor_proxy_abnormal_20d_return_pct",
    "abnormal_20d_return_pct",
)

COVERAGE_GROUPS = {
    "Event identifiers": (
        "event_id",
        "ticker",
        "fiscal_period_end",
        "earnings_timestamp",
        "event_date",
    ),
    "Financial predictors": (
        "eps_actual",
        "eps_estimate",
        "eps_surprise_pct",
        "eps_beat",
        "eps_source",
        "market_cap_usd",
        "sector",
        "prior_20d_return_pct",
        "prior_20d_volatility_pct",
    ),
    "Event-study outcomes": (
        "car_0_1_pct",
        "car_0_5_pct",
        "car_0_20_pct",
        "event_study_method",
        "announcement_abnormal_return_pct",
        "abnormal_5d_return_pct",
        "abnormal_20d_return_pct",
        "abnormal_60d_return_pct",
        "factor_proxy_announcement_abnormal_return_pct",
        "factor_proxy_abnormal_5d_return_pct",
        "factor_proxy_abnormal_20d_return_pct",
        "factor_proxy_abnormal_60d_return_pct",
    ),
    "Transcript predictors": (
        "transcript_sentiment",
        "management_sentiment",
        "analyst_question_sentiment",
        "congratulations_mentioned",
        "language_outlook_tone",
        "language_sentiment_score",
        "language_guidance_specificity",
        "transcript_score_status",
    ),
    "Provenance": (
        "earnings_source",
        "event_timestamp_source",
        "prices_source",
        "financial_data_source",
        "event_study_source",
        "transcript_sentiment_method",
        "transcript_source",
        "financial_retrieved_at_utc",
        "event_study_retrieved_at_utc",
        "transcript_retrieved_at_utc",
        "language_model",
        "language_prompt_version",
    ),
    "Component records": (
        "financial_record_present",
        "event_study_record_present",
        "transcript_record_present",
    ),
}


def validate_required_columns(data):
    missing = sorted(set(REQUIRED_COLUMNS).difference(data.columns))
    if missing:
        raise ValueError("Dataset is missing required columns: {}".format(", ".join(missing)))
def coverage_table(data):
    rows = []
    for group, columns in COVERAGE_GROUPS.items():
        for column in columns:
            present = column in data.columns
            observed = int(data[column].notna().sum()) if present else 0
            total = len(data)
            rows.append(
                {
                    "group": group,
                    "field": column,
                    "observed": observed,
                    "total": total,
                    "coverage_pct": 100 * observed / total if total else 0.0,
                    "field_present": present,
                }
            )
    return pd.DataFrame(rows)


def quality_summary(data):
    if "event_id" in data:
        key_columns = ("event_id",)
    elif all(column in data for column in EVENT_KEY):
        key_columns = EVENT_KEY
    elif "earnings_date" in data:
        key_columns = ("ticker", "earnings_date")
    else:
        key_columns = ("ticker",)
    missing_keys = int(data[list(key_columns)].isna().any(axis=1).sum())
    duplicate_keys = int(data.duplicated(list(key_columns), keep=False).sum())

    def numeric_column(column):
        if column not in data:
            return pd.Series(np.nan, index=data.index, dtype=float)
        return pd.to_numeric(data[column], errors="coerce")

    actual = numeric_column("eps_actual")
    estimate = numeric_column("eps_estimate")
    surprise = numeric_column("eps_surprise_pct")
    valid_eps = actual.notna() & estimate.notna() & estimate.ne(0) & surprise.notna()
    expected_surprise = (actual[valid_eps] - estimate[valid_eps]) / estimate[valid_eps].abs() * 100
    mismatch = int(
        (~np.isclose(surprise[valid_eps], expected_surprise, rtol=1e-5, atol=1e-5)).sum()
    )

    invalid_language = 0
    if "language_outlook_tone" in data:
        values = pd.to_numeric(data["language_outlook_tone"], errors="coerce").dropna()
        invalid_language += int((~values.between(-2, 2) | values.mod(1).ne(0)).sum())
    if "language_guidance_specificity" in data:
        values = pd.to_numeric(
            data["language_guidance_specificity"], errors="coerce"
        ).dropna()
        invalid_language += int((~values.between(0, 2) | values.mod(1).ne(0)).sum())
    if "language_sentiment_score" in data:
        values = pd.to_numeric(data["language_sentiment_score"], errors="coerce").dropna()
        invalid_language += int((~values.between(-1, 1)).sum())
    if "transcript_score_status" in data:
        tone_values = pd.to_numeric(
            data.get("language_outlook_tone", pd.Series(index=data.index, dtype=float)),
            errors="coerce",
        )
        specificity_values = pd.to_numeric(
            data.get(
                "language_guidance_specificity",
                pd.Series(index=data.index, dtype=float),
            ),
            errors="coerce",
        )
        statuses = data["transcript_score_status"]
        invalid_language += int(
            (
                statuses.eq("insufficient_outlook")
                & (tone_values.notna() | specificity_values.ne(0))
            ).sum()
        )
        invalid_language += int(
            (
                statuses.eq("incomplete_transcript")
                & (tone_values.notna() | specificity_values.notna())
            ).sum()
        )
        invalid_language += int(
            (
                statuses.eq("scored")
                & (tone_values.isna() | specificity_values.isna())
            ).sum()
        )
        invalid_language += int(
            (
                statuses.eq("not_available")
                & (tone_values.notna() | specificity_values.notna())
            ).sum()
        )

    primary_outcome = next(
        (column for column in OUTCOME_COLUMNS if column in data), None
    )
    complete_columns = ["eps_surprise_pct"]
    if primary_outcome:
        complete_columns.append(primary_outcome)
    return {
        "missing_event_keys": missing_keys,
        "duplicate_event_rows": duplicate_keys,
        "eps_surprise_mismatches": mismatch,
        "invalid_language_scores": invalid_language,
        "primary_data_complete_rows": int(
            data.reindex(columns=complete_columns).notna().all(axis=1).sum()
        ),
        "outlook_feature_complete_rows": int(
            data.reindex(
                columns=complete_columns
                + ["language_outlook_tone", "language_guidance_specificity"]
            )
            .notna()
            .all(axis=1)
            .sum()
        ),
    }
