"""Build a small post-earnings-announcement-drift dataset from Yahoo Finance."""

import argparse
from datetime import time
from pathlib import Path

import pandas as pd
import yfinance as yf

DEFAULT_TICKERS = ("AAPL", "MSFT", "TSLA", "NVDA")
DEFAULT_BENCHMARK = "SPY"
HORIZONS = (1, 5, 20, 60)
EASTERN = "America/New_York"
DATA_SOURCE = "Yahoo Finance via yfinance"

OUTPUT_COLUMNS = [
    "ticker",
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
    "retrieved_at_utc",
    "earnings_source",
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
    """Compute announcement-day and forward buy-and-hold abnormal returns.

    An after-close announcement starts from that session's close. Other or
    unknown announcement times start from the previous session's close, so
    the first post-announcement trading session is included conservatively.
    Abnormal return is stock buy-and-hold return minus benchmark return.
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

    results = {"event_session": prices.index[base_position + 1] if base_position + 1 < len(prices) else pd.NaT}
    for horizon in HORIZONS:
        end_position = base_position + horizon
        if end_position >= len(prices):
            results[horizon] = float("nan")
            continue
        stock_return = prices["stock"].iloc[end_position] / prices["stock"].iloc[base_position] - 1
        benchmark_return = (
            prices["benchmark"].iloc[end_position]
            / prices["benchmark"].iloc[base_position]
            - 1
        )
        results[horizon] = (stock_return - benchmark_return) * 100
    return results


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
    """Fetch earnings and adjusted prices, keeping only complete 60-day rows."""
    if events_per_ticker < 1:
        raise ValueError("events_per_ticker must be at least 1.")

    now = pd.Timestamp.now(tz=EASTERN) if as_of is None else pd.Timestamp(as_of)
    if now.tzinfo is None:
        now = now.tz_localize(EASTERN)
    else:
        now = now.tz_convert(EASTERN)

    benchmark_history = yf.Ticker(benchmark).history(
        start=start_date, end=(now.normalize() + pd.Timedelta(days=1)), auto_adjust=True
    )
    if benchmark_history.empty or "Close" not in benchmark_history:
        raise ValueError("Yahoo Finance returned no prices for benchmark {}.".format(benchmark))
    benchmark_prices = benchmark_history["Close"]

    retrieved_at = pd.Timestamp.now(tz="UTC").isoformat()
    rows = []
    skipped_incomplete = 0

    for ticker in tickers:
        instrument = yf.Ticker(ticker)
        events = _fetch_events(ticker, start_date, now)
        history = instrument.history(
            start=start_date,
            end=(now.normalize() + pd.Timedelta(days=1)),
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
            if any(pd.isna(returns[horizon]) for horizon in HORIZONS):
                skipped_incomplete += 1
                continue

            rows.append(
                {
                    "ticker": ticker,
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
                    "retrieved_at_utc": retrieved_at,
                    "earnings_source": DATA_SOURCE,
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
    assert dataset[OUTPUT_COLUMNS].notna().all().all(), "Dataset contains missing outputs."
    assert not dataset.duplicated(["ticker", "earnings_date"]).any(), (
        "Dataset contains duplicate ticker/earnings-date observations."
    )
    print(
        "Built {} observations; skipped {} events without complete 60-session windows.".format(
            len(dataset), skipped_incomplete
        )
    )
    return dataset.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickers", nargs="+", default=list(DEFAULT_TICKERS))
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK)
    parser.add_argument("--start-date", default="2021-01-01")
    parser.add_argument("--events-per-ticker", type=int, default=1)
    parser.add_argument("--output", default="outputs/pead_sample.csv")
    args = parser.parse_args()

    dataset = build_dataset(
        tickers=args.tickers,
        benchmark=args.benchmark,
        start_date=args.start_date,
        events_per_ticker=args.events_per_ticker,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output, index=False)
    print("Wrote {} rows to {}".format(len(dataset), output))
    print(dataset[["ticker", "earnings_date", "eps_surprise_pct", "abnormal_20d_return_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
