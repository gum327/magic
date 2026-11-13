"""Build separate synthetic team handoff datasets and a merged dashboard fixture."""

from pathlib import Path

import numpy as np
import pandas as pd

from merge_event_datasets import merge_event_datasets

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
FIXTURE_DATE = "2026-11-13"
TRANSCRIPT_SCORE_PATH = (
    Path(__file__).resolve().parents[1]
    / "inputs"
    / "synthetic_transcript_checkpoint_claude_scores.csv"
)


def _load_transcript_scores(event_ids):
    scores = pd.read_csv(TRANSCRIPT_SCORE_PATH)
    required = {
        "id",
        "outlook_tone",
        "guidance_specificity",
        "status",
        "model",
        "effort",
        "prompt_version",
        "fixture_version",
        "run_date",
    }
    missing = required.difference(scores.columns)
    if missing:
        raise ValueError(
            "Transcript score log is missing columns: {}".format(
                ", ".join(sorted(missing))
            )
        )
    if scores["id"].duplicated().any() or set(scores["id"]) != set(event_ids):
        raise ValueError("Transcript score IDs must match the synthetic event IDs exactly.")

    scores = scores.set_index("id").loc[event_ids].reset_index()
    scores["outlook_tone"] = pd.to_numeric(scores["outlook_tone"], errors="coerce")
    scores["guidance_specificity"] = pd.to_numeric(
        scores["guidance_specificity"], errors="coerce"
    )
    allowed_statuses = {"scored", "insufficient_outlook", "incomplete_transcript"}
    if not set(scores["status"]).issubset(allowed_statuses):
        raise ValueError("Transcript score log contains an unknown status.")
    scored = scores["status"].eq("scored")
    insufficient = scores["status"].eq("insufficient_outlook")
    incomplete = scores["status"].eq("incomplete_transcript")
    if (
        scores.loc[scored, ["outlook_tone", "guidance_specificity"]].isna().any().any()
        or not scores.loc[scored, "outlook_tone"].between(-2, 2).all()
        or not scores.loc[scored, "outlook_tone"].mod(1).eq(0).all()
        or not scores.loc[scored, "guidance_specificity"].between(0, 2).all()
        or not scores.loc[scored, "guidance_specificity"].mod(1).eq(0).all()
    ):
        raise ValueError("Scored transcript rows contain invalid feature values.")
    if (
        scores.loc[insufficient, "outlook_tone"].notna().any()
        or not scores.loc[insufficient, "guidance_specificity"].eq(0).all()
        or scores.loc[incomplete, ["outlook_tone", "guidance_specificity"]]
        .notna()
        .any()
        .any()
    ):
        raise ValueError("Transcript scores violate the checkpoint status rules.")
    return scores


def build_datasets():
    rng = np.random.default_rng(20261113)
    size = 20
    event_ids = ["SYN-{:03d}".format(i + 1) for i in range(size)]
    tickers = ["SYN{:03d}".format(i + 1) for i in range(size)]
    fiscal_ends = pd.to_datetime(
        ["2026-04-30", "2026-05-31", "2026-06-30", "2026-06-27"] * 5
    )
    event_days = pd.date_range("2026-07-20", periods=size, freq="2D")
    timestamps = [
        "{}T{}-04:00".format(day.date(), "16:10:00" if i % 2 else "08:15:00")
        for i, day in enumerate(event_days)
    ]
    identity = {
        "event_id": event_ids,
        "ticker": tickers,
        "fiscal_period_end": fiscal_ends.strftime("%Y-%m-%d"),
    }

    estimates = np.round(rng.uniform(0.5, 6.0, size), 2)
    surprise_draw = np.round(rng.normal(0, 14, size), 2)
    actuals = np.round(estimates + surprise_draw * np.abs(estimates) / 100, 2)
    actuals[19] = np.nan
    eps_surprise = np.divide(
        actuals - estimates,
        np.abs(estimates),
        out=np.full(size, np.nan),
        where=np.isfinite(actuals) & np.isfinite(estimates) & (estimates != 0),
    ) * 100
    sectors = [
        "Information Technology",
        "Health Care",
        "Financials",
        "Industrials",
        "Consumer Discretionary",
        "Energy",
        "Utilities",
        "Consumer Staples",
        "Materials",
        "Communication Services",
    ]
    financial = pd.DataFrame(
        {
            **identity,
            "company_name": [
                "Synthetic Company {:02d}".format(i + 1) for i in range(size)
            ],
            "earnings_timestamp": timestamps,
            "earnings_date": event_days.strftime("%Y-%m-%d"),
            "eps_actual": actuals,
            "eps_estimate": estimates,
            "eps_surprise_pct": eps_surprise,
            "eps_beat": np.where(
                np.isfinite(actuals), (actuals > estimates).astype(float), np.nan
            ),
            "market_cap_usd": np.round(
                np.exp(rng.uniform(np.log(2e9), np.log(350e9), size)), 0
            ),
            "sector": [sectors[i % len(sectors)] for i in range(size)],
            "prior_20d_return_pct": np.round(rng.normal(1, 8, size), 2),
            "prior_20d_volatility_pct": np.round(rng.uniform(1, 9, size), 2),
            "eps_source": "Synthetic placeholder; no Yahoo data retrieved",
            "financial_data_source": "Synthetic placeholder; no Yahoo data retrieved",
            "financial_retrieved_at_utc": "",
            "event_timestamp_source": (
                "Synthetic placeholder; timestamp not independently verified"
            ),
            "prices_source": "Synthetic placeholder; no Yahoo prices retrieved",
        }
    )

    car_0_1 = np.round(rng.normal(0, 3.5, size), 2)
    car_0_5 = np.round(rng.normal(0, 5.5, size), 2)
    car_0_20 = np.round(rng.normal(0, 8.0, size), 2)
    car_0_1[18] = np.nan
    car_0_5[3] = np.nan
    car_0_20[16:] = np.nan
    event_study = pd.DataFrame(
        {
            **identity,
            "event_date": event_days.strftime("%Y-%m-%d"),
            "car_0_1_pct": car_0_1,
            "car_0_5_pct": car_0_5,
            "car_0_20_pct": car_0_20,
            "event_study_status": np.where(
                np.isfinite(car_0_1),
                "synthetic_placeholder",
                "synthetic_missingness_example",
            ),
            "event_study_method": (
                "Synthetic placeholder; event-study package not run"
            ),
            "event_study_source": "Synthetic fixture; no market data retrieved",
            "event_study_retrieved_at_utc": "",
        }
    )

    scores = _load_transcript_scores(event_ids)
    classic_sentiment = np.round(rng.uniform(-1, 1, size), 2)
    management_sentiment = np.round(rng.uniform(-1, 1, size), 2)
    analyst_sentiment = np.round(rng.uniform(-1, 1, size), 2)
    incomplete_rows = scores["status"].eq("incomplete_transcript").to_numpy()
    for values in (classic_sentiment, management_sentiment, analyst_sentiment):
        values[incomplete_rows] = np.nan
    congratulations = rng.integers(0, 2, size).astype(float)
    congratulations[incomplete_rows] = np.nan
    transcript = pd.DataFrame(
        {
            **identity,
            "transcript_sentiment": classic_sentiment,
            "management_sentiment": management_sentiment,
            "analyst_question_sentiment": analyst_sentiment,
            "congratulations_mentioned": congratulations,
            "language_outlook_tone": scores["outlook_tone"].to_numpy(),
            "language_guidance_specificity": scores[
                "guidance_specificity"
            ].to_numpy(),
            "transcript_score_status": scores["status"].to_numpy(),
            "transcript_sentiment_method": (
                "Synthetic placeholder; not calculated from transcript text"
            ),
            "language_model": scores["model"].to_numpy(),
            "language_effort": scores["effort"].to_numpy(),
            "language_prompt_version": scores["prompt_version"].to_numpy(),
            "language_score_run_date": scores["run_date"].to_numpy(),
            "language_fixture_version": scores["fixture_version"].to_numpy(),
            "language_score_source": TRANSCRIPT_SCORE_PATH.name,
            "transcript_input_type": "synthetic",
            "transcript_source": (
                "Synthetic mock calls; raw text excluded from dashboard data"
            ),
            "transcript_retrieved_at_utc": "",
        }
    )
    return financial, event_study, transcript


def write_checkpoint_datasets():
    financial, event_study, transcript = build_datasets()
    components = {
        "synthetic_yahoo_finance_variables.csv": financial,
        "synthetic_event_study_results.csv": event_study,
        "synthetic_transcript_features.csv": transcript,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, data in components.items():
        data.to_csv(OUTPUT_DIR / filename, index=False)

    merged = merge_event_datasets(financial, event_study, transcript)
    merged["record_type"] = "synthetic"
    merged["fixture_generated_date"] = FIXTURE_DATE
    merged["fixture_note"] = (
        "Generated placeholders; blanks demonstrate missing-data handling."
    )
    output_path = OUTPUT_DIR / "synthetic_checkpoint_dataset.csv"
    merged.to_csv(output_path, index=False)
    print("Wrote 3 component fixtures and {} merged synthetic rows.".format(len(merged)))


if __name__ == "__main__":
    write_checkpoint_datasets()
