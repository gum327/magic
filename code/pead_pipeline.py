"""Build a small post-earnings-announcement-drift dataset from Yahoo Finance."""

import argparse
from datetime import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

DEFAULT_TICKERS = ("AAPL", "MSFT", "TSLA", "NVDA")
DEFAULT_BENCHMARK = "SPY"
HORIZONS = (1, 5, 20, 60)
FACTOR_PROXIES = ("SPY", "BIL", "IWM", "IWD", "IWF")
FACTOR_ESTIMATION_WINDOW = 252
Q2_2026_START = pd.Timestamp("2026-04-01")
Q2_2026_END = pd.Timestamp("2026-06-30")
EASTERN = "America/New_York"
DATA_SOURCE = "Yahoo Finance via yfinance"
FACTOR_MODEL = "ETF 3-proxy daily OLS (SPY-BIL, IWM-SPY, IWD-IWF)"
EVENT_MANIFEST_COLUMNS = [
    "ticker",
    "fiscal_period_end",
    "earnings_timestamp",
    "eps_actual",
    "eps_estimate",
    "earnings_source",
    "event_timestamp_source",
]

OUTPUT_COLUMNS = [
    "ticker",
    "fiscal_period_end",
    "earnings_timestamp",
    "earnings_date",
    "eps_actual",
    "eps_estimate",
    "eps_surprise_pct",
    "benchmark",
    "announcement_abnormal_return_pct",
    "abnormal_5d_return_pct",
    "abnormal_20d_return_pct",
    "abnormal_60d_return_pct",
    "factor_proxy_model",
    "factor_proxy_estimation_nobs",
    "factor_proxy_announcement_abnormal_return_pct",
    "factor_proxy_abnormal_5d_return_pct",
    "factor_proxy_abnormal_20d_return_pct",
    "factor_proxy_abnormal_60d_return_pct",
    "retrieved_at_utc",
    "earnings_source",
    "event_timestamp_source",
    "prices_source",
]


def calculate_eps_surprise_pct(actual, estimate):
    """Return (actual - estimate) / abs(estimate) as a percentage."""
    if pd.isna(actual) or pd.isna(estimate) or estimate == 0:
        return float("nan")
    return (actual - estimate) / abs(estimate) * 100


def _close_series(prices):
    if isinstance(prices, pd.Series):
        close = prices.copy()
    else:
        close = prices["Close"].copy()

    index = pd.DatetimeIndex(pd.to_datetime(close.index))
    if index.tz is not None:
        index = index.tz_convert(EASTERN).tz_localize(None)
    close.index = index.normalize()
    close = close[~close.index.duplicated(keep="last")].sort_index()
    return pd.to_numeric(close, errors="coerce").dropna()


def calculate_abnormal_returns(stock_prices, benchmark_prices, earnings_timestamp):
    """Compute announcement reaction and forward buy-and-hold abnormal returns.

    An after-close announcement starts from that session's close. Other or
    unknown announcement times start from the previous session's close, so
    the first tradable session captures the announcement reaction. Forward
    horizons begin at that session's close and exclude its return. Abnormal
    return is stock buy-and-hold return minus benchmark return.
    """
    stock = _close_series(stock_prices).rename("stock")
    benchmark = _close_series(benchmark_prices).rename("benchmark")
    prices = pd.concat([stock, benchmark], axis=1, join="inner").dropna()
    if prices.empty:
        raise ValueError("Stock and benchmark prices have no overlapping sessions.")

    event_time = pd.Timestamp(earnings_timestamp)
    if event_time.tzinfo is not None:
        event_time = event_time.tz_convert(EASTERN).tz_localize(None)
    event_day = event_time.normalize()
    after_close = event_time.time() >= time(16, 0)

    event_position = prices.index.searchsorted(event_day)
    has_event_session = (
        event_position < len(prices) and prices.index[event_position] == event_day
    )
    if after_close and has_event_session:
        base_position = event_position
    else:
        base_position = event_position - 1

    if base_position < 0:
        raise ValueError("No price session is available before the earnings event.")

    first_tradable_position = base_position + 1
    results = {
        "event_session": (
            prices.index[first_tradable_position]
            if first_tradable_position < len(prices)
            else pd.NaT
        )
    }
    for horizon in HORIZONS:
        if horizon == 1:
            end_position = first_tradable_position
            start_position = base_position
        else:
            start_position = first_tradable_position
            end_position = first_tradable_position + horizon
        if end_position >= len(prices):
            results[horizon] = float("nan")
            continue
        stock_return = (
            prices["stock"].iloc[end_position]
            / prices["stock"].iloc[start_position]
            - 1
        )
        benchmark_return = (
            prices["benchmark"].iloc[end_position]
            / prices["benchmark"].iloc[start_position]
            - 1
        )
        results[horizon] = (stock_return - benchmark_return) * 100
    return results


def calculate_factor_proxy_returns(
    stock_prices,
    factor_prices,
    earnings_timestamp,
    estimation_window=FACTOR_ESTIMATION_WINDOW,
    horizons=(5, 20, 60),
):
    """Estimate ETF-proxy abnormal returns after the announcement reaction.

    Factor loadings are fitted on daily returns ending before the first
    tradable session. The announcement reaction is reported separately; each
    forward horizon starts on the following trading session.
    """
    missing_proxies = set(FACTOR_PROXIES).difference(factor_prices)
    if missing_proxies:
        raise ValueError(
            "Missing factor proxy price series: {}".format(
                ", ".join(sorted(missing_proxies))
            )
        )
    if estimation_window < 4:
        raise ValueError("estimation_window must be at least 4.")
    if any(horizon < 1 for horizon in horizons):
        raise ValueError("All return horizons must be positive.")

    prices = {"stock": _close_series(stock_prices)}
    prices.update(
        {symbol: _close_series(factor_prices[symbol]) for symbol in FACTOR_PROXIES}
    )
    common_prices = pd.concat(prices, axis=1, join="inner").dropna()
    if common_prices.empty:
        raise ValueError("Stock and ETF prices have no overlapping sessions.")

    returns = common_prices.pct_change(fill_method=None).dropna()
    factor_returns = pd.DataFrame(
        {
            "stock_excess": returns["stock"] - returns["BIL"],
            "market": returns["SPY"] - returns["BIL"],
            "size": returns["IWM"] - returns["SPY"],
            "value": returns["IWD"] - returns["IWF"],
        },
        index=returns.index,
    ).dropna()

    event_time = pd.Timestamp(earnings_timestamp)
    if event_time.tzinfo is not None:
        event_time = event_time.tz_convert(EASTERN).tz_localize(None)
    event_day = event_time.normalize()
    event_position = common_prices.index.searchsorted(event_day)
    has_event_session = (
        event_position < len(common_prices)
        and common_prices.index[event_position] == event_day
    )
    after_close = event_time.time() >= time(16, 0)
    if after_close and has_event_session:
        event_position += 1
    if event_position >= len(common_prices):
        raise ValueError("No tradable price session is available after the event.")

    event_session = common_prices.index[event_position]
    estimation = factor_returns.loc[factor_returns.index < event_session].tail(
        estimation_window
    )
    if len(estimation) < estimation_window:
        raise ValueError(
            "Only {} pre-event returns are available; {} are required.".format(
                len(estimation), estimation_window
            )
        )

    design = np.column_stack(
        [
            np.ones(len(estimation)),
            estimation[["market", "size", "value"]].to_numpy(),
        ]
    )
    if np.linalg.matrix_rank(design) < design.shape[1]:
        raise ValueError("Pre-event ETF factor design matrix is rank deficient.")
    coefficients, _, _, _ = np.linalg.lstsq(
        design, estimation["stock_excess"].to_numpy(), rcond=None
    )

    event_design = np.column_stack(
        [
            np.ones(len(factor_returns)),
            factor_returns[["market", "size", "value"]].to_numpy(),
        ]
    )
    residuals = factor_returns["stock_excess"].to_numpy() - (
        event_design @ coefficients
    )
    residuals = pd.Series(residuals, index=factor_returns.index)
    if event_session not in residuals.index:
        raise ValueError("Factor proxy returns are missing the event session.")

    result = {
        "factor_proxy_model": FACTOR_MODEL,
        "factor_proxy_estimation_nobs": len(estimation),
        "factor_proxy_announcement_abnormal_return_pct": (
            residuals.loc[event_session] * 100
        ),
    }
    for horizon in horizons:
        start = event_position
        end = start + horizon
        horizon_residuals = residuals.iloc[start:end]
        result[horizon] = (
            horizon_residuals.sum() * 100
            if len(horizon_residuals) == horizon
            else float("nan")
        )
    return result


def _fetch_events(ticker, start_date, as_of):
    events = yf.Ticker(ticker).get_earnings_dates(limit=100)
    if events is None or events.empty:
        raise ValueError("Yahoo Finance returned no earnings dates for {}.".format(ticker))

    required = {"EPS Estimate", "Reported EPS"}
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(
            "Yahoo Finance earnings data for {} is missing {}.".format(
                ticker, ", ".join(sorted(missing))
            )
        )

    events = events.dropna(subset=["EPS Estimate", "Reported EPS"]).copy()
    index = pd.DatetimeIndex(pd.to_datetime(events.index))
    if index.tz is None:
        index = index.tz_localize(EASTERN)
    else:
        index = index.tz_convert(EASTERN)
    events.index = index

    start = pd.Timestamp(start_date).normalize().tz_localize(EASTERN)
    cutoff = pd.Timestamp(as_of)
    if cutoff.tzinfo is None:
        cutoff = cutoff.tz_localize(EASTERN)
    else:
        cutoff = cutoff.tz_convert(EASTERN)
    return events.loc[(events.index >= start) & (events.index <= cutoff)].sort_index(
        ascending=False
    )


def build_dataset(
    tickers=DEFAULT_TICKERS,
    benchmark=DEFAULT_BENCHMARK,
    start_date="2021-01-01",
    events_per_ticker=1,
    as_of=None,
):
    """Fetch earnings and returns, requiring complete 20-session outcomes."""
    if events_per_ticker < 1:
        raise ValueError("events_per_ticker must be at least 1.")

    now = pd.Timestamp.now(tz=EASTERN) if as_of is None else pd.Timestamp(as_of)
    if now.tzinfo is None:
        now = now.tz_localize(EASTERN)
    else:
        now = now.tz_convert(EASTERN)

    history_start = (
        pd.Timestamp(start_date).normalize()
        - pd.Timedelta(days=FACTOR_ESTIMATION_WINDOW * 2)
    )
    history_end = now.normalize() + pd.Timedelta(days=1)
    benchmark_history = yf.Ticker(benchmark).history(
        start=history_start, end=history_end, auto_adjust=True
    )
    if benchmark_history.empty or "Close" not in benchmark_history:
        raise ValueError("Yahoo Finance returned no prices for benchmark {}.".format(benchmark))
    benchmark_prices = benchmark_history["Close"]
    factor_histories = {}
    for symbol in FACTOR_PROXIES:
        history = yf.Ticker(symbol).history(
            start=history_start, end=history_end, auto_adjust=True
        )
        if history.empty or "Close" not in history:
            raise ValueError(
                "Yahoo Finance returned no prices for factor proxy {}.".format(symbol)
            )
        factor_histories[symbol] = history["Close"]

    retrieved_at = pd.Timestamp.now(tz="UTC").isoformat()
    rows = []
    skipped_incomplete_20d = 0

    for ticker in tickers:
        instrument = yf.Ticker(ticker)
        events = _fetch_events(ticker, start_date, now)
        history = instrument.history(
            start=history_start,
            end=history_end,
            auto_adjust=True,
        )
        if history.empty or "Close" not in history:
            raise ValueError("Yahoo Finance returned no prices for {}.".format(ticker))

        accepted = 0
        for timestamp, event in events.iterrows():
            if accepted >= events_per_ticker:
                break

            actual = float(event["Reported EPS"])
            estimate = float(event["EPS Estimate"])
            surprise = calculate_eps_surprise_pct(actual, estimate)
            if pd.isna(surprise):
                continue

            returns = calculate_abnormal_returns(
                history["Close"], benchmark_prices, timestamp
            )
            factor_returns = calculate_factor_proxy_returns(
                history["Close"], factor_histories, timestamp
            )
            if pd.isna(returns[20]) or pd.isna(factor_returns[20]):
                skipped_incomplete_20d += 1
                continue

            rows.append(
                {
                    "ticker": ticker,
                    "fiscal_period_end": pd.NA,
                    "earnings_timestamp": timestamp.isoformat(),
                    "earnings_date": timestamp.date().isoformat(),
                    "eps_actual": actual,
                    "eps_estimate": estimate,
                    "eps_surprise_pct": surprise,
                    "benchmark": benchmark,
                    "announcement_abnormal_return_pct": returns[1],
                    "abnormal_5d_return_pct": returns[5],
                    "abnormal_20d_return_pct": returns[20],
                    "abnormal_60d_return_pct": returns[60],
                    "factor_proxy_model": factor_returns["factor_proxy_model"],
                    "factor_proxy_estimation_nobs": factor_returns[
                        "factor_proxy_estimation_nobs"
                    ],
                    "factor_proxy_announcement_abnormal_return_pct": factor_returns[
                        "factor_proxy_announcement_abnormal_return_pct"
                    ],
                    "factor_proxy_abnormal_5d_return_pct": factor_returns[5],
                    "factor_proxy_abnormal_20d_return_pct": factor_returns[20],
                    "factor_proxy_abnormal_60d_return_pct": factor_returns[60],
                    "retrieved_at_utc": retrieved_at,
                    "earnings_source": DATA_SOURCE,
                    "event_timestamp_source": DATA_SOURCE,
                    "prices_source": DATA_SOURCE,
                }
            )
            accepted += 1

    if not rows:
        raise ValueError(
            "No complete earnings observations found. Check source coverage, "
            "start date, and whether 60 forward trading sessions are available."
        )

    dataset = pd.DataFrame(rows, columns=OUTPUT_COLUMNS).sort_values(
        ["ticker", "earnings_date"]
    )
    required_outputs = [
        "ticker",
        "earnings_timestamp",
        "earnings_date",
        "eps_actual",
        "eps_estimate",
        "eps_surprise_pct",
        "factor_proxy_model",
        "factor_proxy_estimation_nobs",
        "factor_proxy_announcement_abnormal_return_pct",
        "factor_proxy_abnormal_20d_return_pct",
    ]
    assert dataset[required_outputs].notna().all().all(), (
        "Dataset contains missing required 20-session outputs."
    )
    assert not dataset.duplicated(["ticker", "earnings_date"]).any(), (
        "Dataset contains duplicate ticker/earnings-date observations."
    )
    print(
        "Built {} observations; skipped {} events without complete 20-session windows.".format(
            len(dataset), skipped_incomplete_20d
        )
    )
    return dataset.reset_index(drop=True)


def build_q2_2026_cohort(events, universe=None, as_of=None):
    """Build returns for manually verified Q2 2026 events from an event manifest.

    Required event dates and EPS sources are supplied in the manifest because
    Yahoo's earnings-date history does not identify a reliable fiscal period.
    """
    missing_columns = set(EVENT_MANIFEST_COLUMNS).difference(events.columns)
    if missing_columns:
        raise ValueError(
            "Event manifest is missing columns: {}".format(
                ", ".join(sorted(missing_columns))
            )
        )
    if events.empty:
        raise ValueError("Event manifest contains no events.")

    cohort = events[EVENT_MANIFEST_COLUMNS].copy()
    cohort["ticker"] = cohort["ticker"].astype(str).str.strip().str.upper()
    if cohort["ticker"].eq("").any():
        raise ValueError("Event manifest contains an empty ticker.")
    if cohort[EVENT_MANIFEST_COLUMNS].isna().any().any():
        raise ValueError("Event manifest contains missing required values.")
    source_columns = ["earnings_source", "event_timestamp_source"]
    if cohort[source_columns].apply(
        lambda column: column.astype(str).str.strip().eq("")
    ).any().any():
        raise ValueError("Event manifest contains an empty source reference.")
    cohort["fiscal_period_end"] = pd.to_datetime(
        cohort["fiscal_period_end"], errors="raise"
    ).dt.normalize()
    if not cohort["fiscal_period_end"].between(Q2_2026_START, Q2_2026_END).all():
        raise ValueError("Fiscal period ends must fall in calendar Q2 2026.")
    cohort["earnings_timestamp"] = pd.to_datetime(
        cohort["earnings_timestamp"], errors="raise"
    )
    cohort["eps_actual"] = pd.to_numeric(cohort["eps_actual"], errors="raise")
    cohort["eps_estimate"] = pd.to_numeric(cohort["eps_estimate"], errors="raise")
    if not np.isfinite(cohort[["eps_actual", "eps_estimate"]].to_numpy()).all():
        raise ValueError("EPS actuals and estimates must be finite numbers.")
    if (cohort["eps_estimate"] == 0).any():
        raise ValueError("EPS estimates cannot be zero for percentage surprises.")
    if cohort.duplicated(["ticker", "fiscal_period_end"]).any():
        raise ValueError("Event manifest contains duplicate ticker/period rows.")

    if universe is not None:
        if "Symbol" not in universe.columns:
            raise ValueError("Universe file must contain a Symbol column.")
        members = set(universe["Symbol"].astype(str).str.strip().str.upper())
        out_of_universe = sorted(set(cohort["ticker"]).difference(members))
        if out_of_universe:
            raise ValueError(
                "Events are outside the supplied universe: {}".format(
                    ", ".join(out_of_universe)
                )
            )

    now = pd.Timestamp.now(tz=EASTERN) if as_of is None else pd.Timestamp(as_of)
    if now.tzinfo is None:
        now = now.tz_localize(EASTERN)
    else:
        now = now.tz_convert(EASTERN)
    event_times = pd.DatetimeIndex(cohort["earnings_timestamp"])
    if event_times.tz is None:
        localized_event_times = event_times.tz_localize(EASTERN)
    else:
        localized_event_times = event_times.tz_convert(EASTERN)
    if (localized_event_times > now).any():
        raise ValueError("Event manifest includes an event after the as-of date.")

    history_start = (
        localized_event_times.min().normalize()
        - pd.Timedelta(days=FACTOR_ESTIMATION_WINDOW * 2)
    )
    history_end = now.normalize() + pd.Timedelta(days=1)
    factor_histories = {}
    for symbol in FACTOR_PROXIES:
        history = yf.Ticker(symbol).history(
            start=history_start, end=history_end, auto_adjust=True
        )
        if history.empty or "Close" not in history:
            raise ValueError(
                "Yahoo Finance returned no prices for factor proxy {}.".format(symbol)
            )
        factor_histories[symbol] = history["Close"]

    retrieved_at = pd.Timestamp.now(tz="UTC").isoformat()
    rows = []
    for ticker, firm_events in cohort.groupby("ticker", sort=True):
        history = yf.Ticker(ticker).history(
            start=history_start, end=history_end, auto_adjust=True
        )
        if history.empty or "Close" not in history:
            raise ValueError("Yahoo Finance returned no prices for {}.".format(ticker))
        for event in firm_events.itertuples(index=False):
            returns = calculate_abnormal_returns(
                history["Close"],
                factor_histories["SPY"],
                event.earnings_timestamp,
            )
            factor_returns = calculate_factor_proxy_returns(
                history["Close"], factor_histories, event.earnings_timestamp
            )
            rows.append(
                {
                    "ticker": ticker,
                    "fiscal_period_end": event.fiscal_period_end.date().isoformat(),
                    "earnings_timestamp": pd.Timestamp(
                        event.earnings_timestamp
                    ).isoformat(),
                    "earnings_date": pd.Timestamp(
                        event.earnings_timestamp
                    ).date().isoformat(),
                    "eps_actual": float(event.eps_actual),
                    "eps_estimate": float(event.eps_estimate),
                    "eps_surprise_pct": calculate_eps_surprise_pct(
                        event.eps_actual, event.eps_estimate
                    ),
                    "benchmark": "SPY",
                    "announcement_abnormal_return_pct": returns[1],
                    "abnormal_5d_return_pct": returns[5],
                    "abnormal_20d_return_pct": returns[20],
                    "abnormal_60d_return_pct": returns[60],
                    "factor_proxy_model": factor_returns["factor_proxy_model"],
                    "factor_proxy_estimation_nobs": factor_returns[
                        "factor_proxy_estimation_nobs"
                    ],
                    "factor_proxy_announcement_abnormal_return_pct": factor_returns[
                        "factor_proxy_announcement_abnormal_return_pct"
                    ],
                    "factor_proxy_abnormal_5d_return_pct": factor_returns[5],
                    "factor_proxy_abnormal_20d_return_pct": factor_returns[20],
                    "factor_proxy_abnormal_60d_return_pct": factor_returns[60],
                    "retrieved_at_utc": retrieved_at,
                    "earnings_source": event.earnings_source,
                    "event_timestamp_source": event.event_timestamp_source,
                    "prices_source": DATA_SOURCE,
                }
            )
    dataset = pd.DataFrame(rows, columns=OUTPUT_COLUMNS).sort_values(
        ["ticker", "fiscal_period_end"]
    )
    assert not dataset.duplicated(["ticker", "fiscal_period_end"]).any(), (
        "Dataset contains duplicate firm-quarter observations."
    )
    assert dataset[
        [
            "eps_surprise_pct",
            "factor_proxy_estimation_nobs",
            "factor_proxy_announcement_abnormal_return_pct",
        ]
    ].notna().all().all(), "Dataset is missing required EPS or announcement outputs."
    return dataset.reset_index(drop=True)


def compare_chronological_predictions(
    events,
    language_features,
    outcome="factor_proxy_abnormal_20d_return_pct",
    timestamp="earnings_timestamp",
    baseline_features=(
        "eps_surprise_pct",
        "factor_proxy_announcement_abnormal_return_pct",
    ),
    train_fraction=0.6,
):
    """Compare baseline and language-augmented OLS on a chronological holdout.

    All models use the same complete-case sample. Features are fit only on the
    earlier portion of the event-time-sorted sample; the later portion is used
    once for evaluation.
    """
    language_features = tuple(language_features)
    baseline_features = tuple(baseline_features)
    if not language_features:
        raise ValueError("At least one language feature is required.")
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")
    all_features = baseline_features + language_features
    if len(set(all_features)) != len(all_features):
        raise ValueError("Baseline and language features must be distinct.")
    if not baseline_features:
        raise ValueError("At least one baseline feature is required.")

    required = [timestamp, outcome, *all_features]
    if "ticker" in events.columns:
        required.append("ticker")
    missing_columns = set(required).difference(events.columns)
    if missing_columns:
        raise ValueError(
            "Prediction data is missing columns: {}".format(
                ", ".join(sorted(missing_columns))
            )
        )
    if events.empty:
        raise ValueError("Prediction data contains no events.")

    sample = events[required].copy()
    if sample[required].isna().any().any():
        raise ValueError("Prediction data contains missing required values.")
    sample[timestamp] = pd.to_datetime(sample[timestamp], errors="raise", utc=True)
    for column in [outcome, *all_features]:
        sample[column] = pd.to_numeric(sample[column], errors="raise")
    if not np.isfinite(sample[[outcome, *all_features]].to_numpy(dtype=float)).all():
        raise ValueError("Prediction data contains non-finite numeric values.")
    sample = sample.sort_values(timestamp, kind="stable").reset_index(drop=True)

    train_n = int(np.floor(len(sample) * train_fraction))
    test_n = len(sample) - train_n
    if train_n == 0 or test_n == 0:
        raise ValueError("Not enough events for chronological train and holdout sets.")

    train = sample.iloc[:train_n]
    test = sample.iloc[train_n:]
    train_mean = train[outcome].mean()
    actual = test[outcome].to_numpy(dtype=float)

    def fit_and_predict(features):
        design = np.column_stack(
            [np.ones(train_n), train[list(features)].to_numpy(dtype=float)]
        )
        if np.linalg.matrix_rank(design) < design.shape[1]:
            raise ValueError("Training design matrix is rank deficient.")
        if train_n <= design.shape[1]:
            raise ValueError("Training sample must exceed the number of model parameters.")
        coefficients, _, _, _ = np.linalg.lstsq(
            design, train[outcome].to_numpy(dtype=float), rcond=None
        )
        test_design = np.column_stack(
            [np.ones(test_n), test[list(features)].to_numpy(dtype=float)]
        )
        return test_design @ coefficients

    predictions = {
        "baseline": fit_and_predict(baseline_features),
        "with_language": fit_and_predict(all_features),
    }

    metrics = {}
    for model_name, predicted in predictions.items():
        errors = actual - predicted
        baseline_error = actual - train_mean
        denominator = np.square(baseline_error).sum()
        metrics[model_name] = {
            "mae": float(np.abs(errors).mean()),
            "rmse": float(np.sqrt(np.square(errors).mean())),
            "out_of_sample_r2": (
                float(1 - np.square(errors).sum() / denominator)
                if denominator > 0
                else float("nan")
            ),
        }

    prediction_columns = [timestamp, outcome]
    if "ticker" in test.columns:
        prediction_columns.insert(0, "ticker")
    holdout = test[prediction_columns].rename(
        columns={outcome: "actual", timestamp: "earnings_timestamp"}
    ).copy()
    holdout["baseline_prediction"] = predictions["baseline"]
    holdout["language_model_prediction"] = predictions["with_language"]
    return {
        "train_n": train_n,
        "test_n": test_n,
        "train_cutoff": train[timestamp].iloc[-1],
        "test_start": test[timestamp].iloc[0],
        "metrics": metrics,
        "holdout_predictions": holdout,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickers", nargs="+", default=list(DEFAULT_TICKERS))
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK)
    parser.add_argument("--start-date", default="2021-01-01")
    parser.add_argument("--events-per-ticker", type=int, default=1)
    parser.add_argument(
        "--as-of",
        help="Include events and prices only through this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--events-csv",
        help=(
            "Build the Q2 2026 cohort from a verified event manifest; requires "
            ", ".join(EVENT_MANIFEST_COLUMNS)
        ),
    )
    parser.add_argument(
        "--universe-csv",
        help="Optional constituent CSV with a Symbol column to validate event tickers.",
    )
    parser.add_argument("--output", default="outputs/pead_sample.csv")
    args = parser.parse_args()

    if args.events_csv:
        events = pd.read_csv(args.events_csv)
        universe = pd.read_csv(args.universe_csv) if args.universe_csv else None
        dataset = build_q2_2026_cohort(events, universe=universe, as_of=args.as_of)
    else:
        dataset = build_dataset(
            tickers=args.tickers,
            benchmark=args.benchmark,
            start_date=args.start_date,
            events_per_ticker=args.events_per_ticker,
            as_of=args.as_of,
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output, index=False)
    print("Wrote {} rows to {}".format(len(dataset), output))
    print(
        dataset[
            [
                "ticker",
                "earnings_date",
                "eps_surprise_pct",
                "factor_proxy_abnormal_20d_return_pct",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
