"""Build separate synthetic team handoff datasets and a merged dashboard fixture."""

from pathlib import Path

import numpy as np
import pandas as pd

from merge_event_datasets import merge_event_datasets

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
FIXTURE_DATE = "2026-11-13"


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
            "event_study_method": (
                "Synthetic placeholder; event-study package not run"
            ),
            "event_study_source": "Synthetic fixture; no market data retrieved",
            "event_study_retrieved_at_utc": "",
        }
    )

    tone = np.array(
        [2, 1, 0, -2, -1, 0, 1, -1, 2, 0, 1, -2, np.nan, 1, np.nan, np.nan, np.nan, -1, np.nan, 2]
    )
    specificity = np.array(
        [2, 1, 2, 2, 1, 2, 0, 1, 2, 1, 1, 2, 0, 1, 0, np.nan, np.nan, 1, np.nan, 2]
    )
    outlook_status = [
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "scored",
        "insufficient_outlook",
        "scored",
        "insufficient_outlook",
        "incomplete_transcript",
        "not_available",
        "scored",
        "incomplete_transcript",
        "scored",
    ]
    classic_sentiment = np.round(rng.uniform(-1, 1, size), 2)
    management_sentiment = np.round(rng.uniform(-1, 1, size), 2)
    analyst_sentiment = np.round(rng.uniform(-1, 1, size), 2)
    for values in (classic_sentiment, management_sentiment, analyst_sentiment):
        values[[15, 16, 18]] = np.nan
    congratulations = rng.integers(0, 2, size).astype(float)
    congratulations[[15, 16, 18]] = np.nan
    transcript = pd.DataFrame(
        {
            **identity,
            "transcript_sentiment": classic_sentiment,
            "management_sentiment": management_sentiment,
            "analyst_question_sentiment": analyst_sentiment,
            "congratulations_mentioned": congratulations,
            "language_outlook_tone": tone,
            "language_guidance_specificity": specificity,
            "transcript_score_status": outlook_status,
            "transcript_sentiment_method": (
                "Synthetic placeholder; not calculated from transcript text"
            ),
            "language_model": "Synthetic placeholder; not LLM-generated",
            "language_prompt_version": "not_applicable",
            "transcript_source": "Synthetic fixture; no transcript text retained",
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
