"""Regenerate the SYNTHETIC dashboard test fixtures.

Every value written here is random noise from a fixed seed. Tickers are
``SYN01``..``SYN40`` so they cannot be mistaken for real companies, and every
row carries ``data_status = synthetic``. These files exist only so the
dashboard's Findings tab can be built and tested before real outputs exist.
They are NOT research data and must never be copied into ``outputs/``.

Run from the repository root:

    python tests/fixtures/make_synthetic_fixtures.py

The metrics come from the team's existing (unmodified)
``compare_chronological_predictions`` helper so the fixture has the same
shape as the real output will.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
from pead_pipeline import compare_chronological_predictions  # noqa: E402

OUT = Path(__file__).resolve().parent
SEED = 331
N_EVENTS = 40
LANGUAGE_FEATURES = ["lang_synthetic_tone", "lang_synthetic_uncertainty"]


def main():
    rng = np.random.default_rng(SEED)
    tickers = ["SYN{:02d}".format(i + 1) for i in range(N_EVENTS)]
    days = np.sort(rng.integers(0, 50, N_EVENTS))
    timestamps = [
        (pd.Timestamp("2026-07-13 16:00", tz="America/New_York") + pd.Timedelta(days=int(d))).isoformat()
        for d in days
    ]
    events = pd.DataFrame(
        {
            "ticker": tickers,
            "fiscal_period_end": "2026-06-30",
            "earnings_timestamp": timestamps,
            "eps_surprise_pct": rng.normal(0, 8, N_EVENTS).round(3),
            "factor_proxy_announcement_abnormal_return_pct": rng.normal(0, 5, N_EVENTS).round(3),
            "factor_proxy_abnormal_20d_return_pct": rng.normal(0, 6, N_EVENTS).round(3),
            "data_status": "synthetic",
        }
    )
    features = events[["ticker", "fiscal_period_end", "earnings_timestamp"]].copy()
    for name in LANGUAGE_FEATURES:
        features[name] = rng.uniform(-1, 1, N_EVENTS).round(4)
    features["model_id"] = "none (synthetic random values)"
    features["prompt_version"] = "synthetic-fixture"
    features["scored_at_utc"] = "1970-01-01T00:00:00+00:00"
    features["data_status"] = "synthetic"

    merged = events.merge(features, on=["ticker", "fiscal_period_end", "earnings_timestamp"])
    result = compare_chronological_predictions(merged, LANGUAGE_FEATURES)

    metrics = pd.DataFrame(
        [
            {
                "model": model,
                **values,
                "train_n": result["train_n"],
                "test_n": result["test_n"],
                "train_cutoff": result["train_cutoff"].isoformat(),
                "test_start": result["test_start"].isoformat(),
                "outcome": "factor_proxy_abnormal_20d_return_pct",
                "baseline_features": "eps_surprise_pct;factor_proxy_announcement_abnormal_return_pct",
                "language_features": ";".join(LANGUAGE_FEATURES) if model == "with_language" else "",
                "data_status": "synthetic",
            }
            for model, values in result["metrics"].items()
        ]
    )
    holdout = result["holdout_predictions"].copy()
    holdout["earnings_timestamp"] = holdout["earnings_timestamp"].map(lambda t: t.isoformat())
    holdout["data_status"] = "synthetic"

    events.to_csv(OUT / "synthetic_events.csv", index=False)
    features.to_csv(OUT / "synthetic_transcript_features.csv", index=False)
    metrics.to_csv(OUT / "synthetic_model_comparison_metrics.csv", index=False, float_format="%.6f")
    holdout.to_csv(OUT / "synthetic_holdout_predictions.csv", index=False, float_format="%.6f")
    print("Wrote synthetic fixtures to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
