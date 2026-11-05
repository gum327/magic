# Self-audit: PEAD v0

## Scope and reproducibility

The pilot covers AAPL, MSFT, TSLA, and NVDA, using the latest available earnings
event per ticker with a complete 60-trading-session forward window. The pipeline
retrieves earnings dates, reported and consensus EPS, and auto-adjusted daily
closing prices from Yahoo Finance through `yfinance`; SPY is the market
benchmark. Retrieval time and source labels are included in each output row.
Run `python code/pead_pipeline.py` from the repository root to regenerate
`outputs/pead_sample.csv`. Yahoo Finance can revise historical estimates and
coverage, so the CSV records this pull but is not a permanent source archive.

## Timing and return construction

The observation is a firm-earnings announcement. EPS surprise is
`(reported EPS - consensus EPS) / abs(consensus EPS) * 100`; zero or missing
estimates are excluded. Adjusted buy-and-hold returns are measured against SPY
over one, five, twenty, and sixty subsequent trading sessions. Abnormal return
is the stock return minus the benchmark return, not a factor-model alpha. For
announcements timestamped at or after 4:00 p.m. Eastern, the baseline is that
session's close; for earlier or unknown times, the baseline is the prior
trading session's close. The first post-announcement session is therefore
included in each forward window. Events lacking a complete 60-session window
are skipped.

## Threats to validity and next checks

Four well-known firms are a demonstration sample, not a historical universe;
they introduce severe selection and survivorship bias and cannot support
statistical conclusions. Yahoo's earnings-date history and consensus EPS
coverage may be incomplete or revised, and its displayed event timestamps
should be independently checked before a larger study. The pilot does not
include Kenneth French factor returns, transaction costs, market
capitalization controls, or the announced-period abnormal-return series needed
for a full event study. No transcripts were collected and no AI sentiment
scores were generated, so the proposed AI extension remains untested. Before
inference, expand to a historically appropriate universe, verify dates and EPS
against a second source, add factor-based abnormal returns and out-of-sample
testing, and audit point-in-time transcript availability.
