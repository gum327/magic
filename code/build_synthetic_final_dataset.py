"""Build a SYNTHETIC final-shape dataset and run the checkpoint models on it.

Why this exists: the real event list, event-study CARs, Yahoo Finance
variables and transcript scores are not delivered yet. This script fakes one
row per earnings call in the exact shape of Cammy's analysis plan
(ANALYSIS_PLAN.md) so the dashboard can show the full analysis now. When the
real merged file arrives with the same columns, the same model code runs on it.

Everything here is invented:
- Tickers are fake (SYN001...). Sectors are drawn from the real roster's mix.
- Relationships between the variables and CAR[0,1] are PLANTED by the
  generator (see ``_simulate_car``). Any "finding" on this data only shows
  that the code recovers what was planted. It is not evidence.
- Missing values are left blank (NaN), never zero.

Outputs (all carry data_status = synthetic):
    outputs/synthetic_final_dataset.csv          one row per call
    outputs/final_dataset_variables.csv          variable dictionary
    outputs/synthetic_model_runs.csv             Run 1-3 holdout metrics
    outputs/synthetic_model_coefficients.csv     standardized OLS coefficients
    outputs/synthetic_run_predictions.csv        holdout predictions per run

Run from the repository root:
    python code/build_synthetic_final_dataset.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
ROSTER_PATH = ROOT / "inputs" / "sp500_constituents_20260630.csv"
SEED = 331
N_EVENTS = 500
GENERATED_ON = "2026-11-14"
TRAIN_SHARE = 0.60

OUTCOME = "car_0_1_pct"

# (name, group, run, definition, planned source, units)
VARIABLES = [
    ("event_id", "Key", None, "Unique ID for one company-quarter earnings call (primary key).",
     "Event list (Gus)", "text"),
    ("ticker", "Key", None, "Stock ticker; checked for consistency on merge.", "Event list (Gus)", "text"),
    ("fiscal_period_end", "Key", None, "Last day of the fiscal quarter reported; checked on merge.",
     "Event list (Gus)", "date"),
    ("call_date", "Key", None, "Date of the earnings call (event day 0).", "Event list (Gus)", "date"),
    ("sector", "Descriptive", None, "GICS sector.", "S&P 500 roster", "text"),
    ("car_0_1_pct", "Outcome (Y)", None,
     "CHECKPOINT OUTCOME. Cumulative abnormal return over the call day and the next trading day.",
     "Event Study Package", "%"),
    ("car_final_20s_pct", "Outcome (Y)", None,
     "FINAL-STUDY OUTCOME (not used in checkpoint models). Abnormal return over the 20 trading "
     "sessions after the announcement-reaction session.", "Event Study Package", "%"),
    ("eps_actual", "Run 1: Yahoo Finance", None, "Reported EPS for the quarter.", "Yahoo Finance", "$"),
    ("eps_estimate", "Run 1: Yahoo Finance", None, "Consensus EPS estimate before the call.",
     "Yahoo Finance", "$"),
    ("eps_surprise_usd", "Run 1: Yahoo Finance", 1, "EPS actual minus consensus.", "Yahoo Finance", "$"),
    ("eps_surprise_pct", "Run 1: Yahoo Finance", 1, "(Actual - consensus) / |consensus| x 100.",
     "Yahoo Finance", "%"),
    ("eps_beat", "Run 1: Yahoo Finance", None, "1 if actual EPS > consensus, else 0.", "Yahoo Finance",
     "0/1"),
    ("log_market_cap", "Run 1: Yahoo Finance", 1, "Natural log of market cap (USD), day before the call.",
     "Yahoo Finance", "log $"),
    ("price_to_book", "Run 1: Yahoo Finance", 1, "Price-to-book ratio.", "Yahoo Finance", "x"),
    ("forward_pe", "Run 1: Yahoo Finance", 1,
     "Forward P/E. Yahoo gives a current snapshot only, so flagged for look-ahead risk.",
     "Yahoo Finance", "x"),
    ("profit_margin", "Run 1: Yahoo Finance", 1, "Net profit margin, latest quarter before the call.",
     "Yahoo Finance", "share"),
    ("revenue_growth", "Run 1: Yahoo Finance", 1, "Year-over-year quarterly revenue growth.",
     "Yahoo Finance", "share"),
    ("earnings_growth", "Run 1: Yahoo Finance", 1, "Year-over-year quarterly earnings growth.",
     "Yahoo Finance", "share"),
    ("debt_to_equity", "Run 1: Yahoo Finance", 1, "Total debt / shareholders' equity.", "Yahoo Finance",
     "x"),
    ("beta", "Run 1: Yahoo Finance", 1, "Market beta.", "Yahoo Finance", "x"),
    ("price_change_52w_pct", "Run 1: Yahoo Finance", 1, "52-week price change to the day before the call.",
     "Yahoo Finance", "%"),
    ("ma50_ma200_gap_pct", "Run 1: Yahoo Finance", 1, "(50-day avg / 200-day avg - 1) x 100.",
     "Yahoo Finance", "%"),
    ("avg_daily_volume", "Run 1: Yahoo Finance", 1, "Average daily share volume (3 months).",
     "Yahoo Finance", "shares"),
    ("short_pct_float", "Run 1: Yahoo Finance", 1,
     "Short interest as % of float. Current snapshot only, so flagged for look-ahead risk.",
     "Yahoo Finance", "%"),
    ("transcript_sentiment", "Run 2: dictionary text", 2, "Overall dictionary sentiment of the call.",
     "Transcript features (Abby)", "-1 to 1"),
    ("management_prepared_sentiment", "Run 2: dictionary text", 2,
     "Dictionary sentiment of management's prepared remarks only (not Q&A).",
     "Transcript features (Abby)", "-1 to 1"),
    ("analyst_question_sentiment", "Run 2: dictionary text", 2, "Dictionary sentiment of analyst questions.",
     "Transcript features (Abby)", "-1 to 1"),
    ("sentiment_gap", "Run 2: dictionary text", None,
     "management_prepared_sentiment minus analyst_question_sentiment; blank if either is blank. "
     "Kept for description but NOT entered in the regression: it is an exact linear combination of "
     "the two sentiment columns, so OLS cannot separate the three effects.",
     "Derived", "-2 to 2"),
    ("congratulations_mentioned", "Run 2: dictionary text", 2, "1 if an analyst says 'congratulations'.",
     "Transcript features (Abby)", "0/1"),
    ("outlook_tone", "Run 3: AI-scored", 3, "AI score of management's forward-looking tone.",
     "Transcript features (Abby)", "1-5"),
    ("guidance_specificity", "Run 3: AI-scored", 3, "AI score of how concrete the guidance is.",
     "Transcript features (Abby)", "1-5"),
    ("data_status", "Metadata", None, "synthetic / pilot / cohort. Every row here is synthetic.", "Generator",
     "text"),
]

RUN_LABELS = {
    1: "Run 1: Yahoo Finance only",
    2: "Run 2: + dictionary text",
    3: "Run 3: + AI-scored text",
}


def run_features(run: int) -> list:
    """Features used in a run; each run contains the previous one."""
    return [v[0] for v in VARIABLES if v[2] is not None and v[2] <= run]


def _sectors(rng, n):
    if ROSTER_PATH.exists():
        mix = pd.read_csv(ROSTER_PATH)["GICS Sector"].value_counts(normalize=True)
        return rng.choice(mix.index.to_numpy(), size=n, p=mix.to_numpy())
    return np.full(n, "Unknown")


def _call_dates(rng, n):
    days = pd.bdate_range("2026-07-14", "2026-08-28")
    weights = np.exp(-((np.arange(len(days)) - 12) ** 2) / 120.0)  # peak in late July
    return np.sort(rng.choice(days, size=n, p=weights / weights.sum()))


def _blank(rng, values, share):
    out = pd.Series(values, dtype="float")
    out[rng.random(len(out)) < share] = np.nan
    return out


def _simulate_car(df, rng):
    """PLANTED relationships. Real data will have whatever it has."""
    surprise = df["eps_surprise_pct"].clip(-30, 30)
    return (
        0.12 * surprise
        - 0.45 * (df["log_market_cap"] - 24.5)
        + 2.0 * df["management_prepared_sentiment"].fillna(0)
        - 1.2 * df["analyst_question_sentiment"].fillna(0)
        + 0.9 * (df["outlook_tone"].fillna(3) - 3)
        + 0.3 * (df["guidance_specificity"].fillna(3) - 3)
        + rng.standard_t(4, len(df)) * 3.2
    )


def build_dataset(seed: int = SEED, n: int = N_EVENTS) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "event_id": ["SYN-FINAL-{:03d}".format(i + 1) for i in range(n)],
        "ticker": ["SYN{:03d}".format(i + 1) for i in range(n)],
        "sector": _sectors(rng, n),
    })
    df["call_date"] = pd.to_datetime(_call_dates(rng, n)).strftime("%Y-%m-%d")
    df["fiscal_period_end"] = rng.choice(["2026-06-30", "2026-05-31", "2026-04-30"], n, p=[0.8, 0.12, 0.08])

    est = np.round(np.exp(rng.normal(0.4, 0.7, n)), 2)
    surprise_share = rng.standard_t(3, n) * 0.05 + 0.03
    actual = np.round(est * (1 + surprise_share), 2)
    df["eps_estimate"], df["eps_actual"] = est, actual
    df["eps_surprise_usd"] = np.round(actual - est, 2)
    df["eps_surprise_pct"] = np.round((actual - est) / np.abs(est) * 100, 2)
    df["eps_beat"] = (actual > est).astype(int)

    df["log_market_cap"] = np.round(rng.normal(24.5, 1.0, n), 3)
    df["price_to_book"] = np.round(np.exp(rng.normal(1.3, 0.8, n)), 2)
    df["forward_pe"] = _blank(rng, np.round(np.exp(rng.normal(3.0, 0.4, n)), 1), 0.08)
    df["profit_margin"] = np.round(rng.normal(0.14, 0.10, n), 3)
    df["revenue_growth"] = np.round(rng.normal(0.06, 0.10, n), 3)
    df["earnings_growth"] = np.round(rng.normal(0.08, 0.25, n), 3)
    df["debt_to_equity"] = np.round(np.exp(rng.normal(-0.2, 0.8, n)), 2)
    df["beta"] = np.round(rng.normal(1.05, 0.3, n), 2)
    df["price_change_52w_pct"] = np.round(rng.normal(10, 25, n), 1)
    df["ma50_ma200_gap_pct"] = np.round(rng.normal(2, 6, n), 2)
    df["avg_daily_volume"] = np.round(np.exp(rng.normal(14.9, 0.9, n)), -3)
    df["short_pct_float"] = _blank(rng, np.round(np.exp(rng.normal(0.9, 0.6, n)), 2), 0.04)

    # Transcript features: ~7% of calls have no usable transcript at all.
    has_transcript = rng.random(n) > 0.07
    tone = 0.04 * surprise_share * 100 + rng.normal(0, 1, n)
    mgmt = np.tanh(0.25 + 0.35 * tone + rng.normal(0, 0.25, n))
    analyst = np.tanh(-0.05 + 0.15 * tone + rng.normal(0, 0.3, n))
    df["management_prepared_sentiment"] = np.where(has_transcript, np.round(mgmt, 3), np.nan)
    df["analyst_question_sentiment"] = np.where(has_transcript, np.round(analyst, 3), np.nan)
    df.loc[rng.random(n) < 0.02, "analyst_question_sentiment"] = np.nan  # no Q&A section
    df["transcript_sentiment"] = np.where(has_transcript, np.round(np.tanh(0.6 * np.arctanh(mgmt * 0.999) + 0.4 * np.arctanh(analyst * 0.999)
                                                    + rng.normal(0, 0.15, n)), 3), np.nan)
    df["sentiment_gap"] = (df["management_prepared_sentiment"] - df["analyst_question_sentiment"]).round(3)
    congrats = rng.random(n) < 1 / (1 + np.exp(-(tone - 0.5)))
    df["congratulations_mentioned"] = np.where(has_transcript, congrats.astype(float), np.nan)

    ai_ok = has_transcript & (rng.random(n) > 0.03)
    df["outlook_tone"] = np.where(ai_ok, np.clip(np.round(3 + 0.8 * tone + rng.normal(0, 0.6, n)), 1, 5), np.nan)
    df["guidance_specificity"] = np.where(ai_ok, rng.choice([1, 2, 3, 4, 5], n, p=[.08, .2, .35, .25, .12]),
                                          np.nan)

    df[OUTCOME] = np.round(_simulate_car(df, rng), 2)
    df.loc[rng.random(n) < 0.02, OUTCOME] = np.nan  # e.g. trading halt / missing prices
    df["car_final_20s_pct"] = np.round(0.03 * df["eps_surprise_pct"].clip(-30, 30) + rng.normal(0, 6, n), 2)

    df["data_status"] = "synthetic"
    df["generated_on"] = GENERATED_ON
    df["note"] = "Invented values with planted relationships; not research data."
    order = [v[0] for v in VARIABLES if v[0] in df.columns] + ["generated_on", "note"]
    return df[order]


# ---------------------------------------------------------------------------
# Checkpoint models (Cammy's plan): same sample, chronological 60/40, OLS.
# ---------------------------------------------------------------------------
def model_sample(df: pd.DataFrame):
    needed = [OUTCOME, "call_date"] + run_features(3)
    complete = df.dropna(subset=needed).sort_values(["call_date", "event_id"]).reset_index(drop=True)
    return complete, len(df) - len(complete)


def _ols(x_train, y_train):
    X = np.column_stack([np.ones(len(x_train)), x_train])
    beta, *_ = np.linalg.lstsq(X, y_train, rcond=None)
    resid = y_train - X @ beta
    dof = max(len(y_train) - X.shape[1], 1)
    cov = (resid @ resid / dof) * np.linalg.pinv(X.T @ X)
    return beta, np.sqrt(np.diag(cov))


def run_models(df: pd.DataFrame):
    sample, excluded = model_sample(df)
    # Split on a date boundary so one day's calls are never split; put the boundary
    # day on whichever side keeps the training share closest to 60%.
    boundary = sample["call_date"].iloc[int(round(len(sample) * TRAIN_SHARE)) - 1]
    n_before, n_through = (sample["call_date"] < boundary).sum(), (sample["call_date"] <= boundary).sum()
    target = len(sample) * TRAIN_SHARE
    in_train = (sample["call_date"] <= boundary) if abs(n_through - target) <= abs(n_before - target) \
        else (sample["call_date"] < boundary)
    train, test = sample[in_train], sample[~in_train]
    y_tr, y_te = train[OUTCOME].to_numpy(), test[OUTCOME].to_numpy()
    runs, coefs = [], []
    preds = test[["event_id", "ticker", "call_date", OUTCOME]].rename(columns={OUTCOME: "actual"}).copy()
    for run, label in RUN_LABELS.items():
        cols = run_features(run)
        mu, sd = train[cols].mean(), train[cols].std(ddof=0).replace(0, 1)
        beta, se = _ols(((train[cols] - mu) / sd).to_numpy(), y_tr)
        pred = beta[0] + ((test[cols] - mu) / sd).to_numpy() @ beta[1:]
        err = y_te - pred
        runs.append({
            "run": run, "label": label, "n_features": len(cols),
            "train_n": len(train), "test_n": len(test), "excluded_n": excluded,
            "train_cutoff": train["call_date"].max(), "test_start": test["call_date"].min(),
            "out_of_sample_r2": 1 - (err @ err) / ((y_te - y_tr.mean()) @ (y_te - y_tr.mean())),
            "mae": np.abs(err).mean(), "rmse": np.sqrt((err ** 2).mean()),
            "data_status": "synthetic",
        })
        for name, b, s in zip(cols, beta[1:], se[1:]):
            coefs.append({"run": run, "variable": name, "coef_per_sd": b, "std_error": s,
                          "ci_low": b - 1.96 * s, "ci_high": b + 1.96 * s, "data_status": "synthetic"})
        preds["pred_run{}".format(run)] = pred
    preds["data_status"] = "synthetic"
    return pd.DataFrame(runs), pd.DataFrame(coefs), preds


def variable_dictionary() -> pd.DataFrame:
    return pd.DataFrame(VARIABLES, columns=["variable", "group", "first_used_in_run", "definition",
                                            "planned_source", "units"])


def main():
    df = build_dataset()
    runs, coefs, preds = run_models(df)
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_DIR / "synthetic_final_dataset.csv", index=False)
    variable_dictionary().to_csv(OUTPUT_DIR / "final_dataset_variables.csv", index=False)
    runs.round(4).to_csv(OUTPUT_DIR / "synthetic_model_runs.csv", index=False)
    coefs.round(4).to_csv(OUTPUT_DIR / "synthetic_model_coefficients.csv", index=False)
    preds.round(3).to_csv(OUTPUT_DIR / "synthetic_run_predictions.csv", index=False)
    print(runs[["label", "train_n", "test_n", "excluded_n", "out_of_sample_r2", "mae", "rmse"]].round(3)
          .to_string(index=False))


if __name__ == "__main__":
    main()
