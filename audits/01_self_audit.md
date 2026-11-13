# Self-audit: PEAD pilot and revised study

## Current pilot

The pilot covers AAPL, MSFT, TSLA, and NVDA using one latest event per ticker
with a complete 20-trading-session forward window. It retrieves earnings
dates, reported and consensus EPS, and auto-adjusted daily closing prices from
Yahoo Finance through `yfinance`; SPY is the comparison benchmark. Run
`python code/pead_pipeline.py --as-of 2026-11-06` from the repository root to
regenerate `outputs/pead_sample.csv`. Yahoo may revise historical estimates
and coverage, and the CSV is not a permanent source archive.

The output contains two methods. The SPY comparison is the arithmetic
difference between adjusted stock and SPY buy-and-hold returns. The new
factor-proxy method regresses stock excess returns on market excess
(SPY-BIL), size (IWM-SPY), and value (IWD-IWF) using 252 pre-event daily
observations. Its announcement reaction is the residual for the first
tradable session; forward horizons start on the next session and sum daily
residuals. These are ETF proxies, not official French factors. The four-row
snapshot retrieved November 6, 2026 has complete 20-session outcomes and one
incomplete 60-session factor outcome, which remains blank rather than being
discarded or imputed.

## Revised target study

The target is a dated S&P 500 roster as of June 30, 2026, with fiscal-quarter
ends in calendar Q2 2026. This is a fixed, recent cohort rather than a
multi-year sample selected from current index members, so the earlier
long-horizon survivorship criticism does not describe the intended design.
Use the dated roster, retain departures after the roster date, and document
any unavailable events. The pilot remains a convenience sample and cannot
support conclusions about this cohort.

The primary outcome is a 20-session cumulative abnormal return after and
excluding the separately measured announcement-reaction session, estimated
with ETF proxies for market excess, size, and value; the official Kenneth
French data lag the newest events. This estimator is implemented and tested
on the pilot, but not yet run on the target S&P 500 cohort. The proxies
(SPY-BIL, IWM-SPY, and IWD-IWF) are not official factor portfolios. Use 5- and
60-session windows as secondary outcomes only when fully observed.

## Transcript and model access

The Seeking Alpha transcript index is publicly viewable, but its current
terms limit content to personal, non-commercial use and prohibit automated
retrieval, scraping, and data mining. Do not scrape it. A metadata screen
started November 7 and was updated November 10, 2026; it now has 21
candidate-company rows, not verified transcripts or cleared coverage. Twelve
potential first-party transcript locations align to the cohort: 11 PDF
links for Alphabet, AT&T, Bank of America, Citigroup, Coca-Cola, Expedia,
Hilton, JPMorganChase, Meta, Netflix, and Visa, plus Microsoft's transcript
page. Hilton and Expedia June 30 period ends are confirmed by SEC 10-Q headers.
HPE's issuer PDF is excluded because its fiscal Q2 ended April 30, outside
the cohort. Apple and Intel fiscal quarters ended June 27 and their calls
were July 30 and July 23; official result materials do not provide a
verified full transcript. AT&T's period end is confirmed as June 30.

The source links were checked, but transcript text was not retained and
reuse/model rights remain unknown. Microsoft's Investor Relations page
displays transcript text; only an initial preview was viewed and no text was
saved or analyzed. Its website terms do not establish research-retention or
external-model rights. Citi's [official quarterly earnings page](https://www.citigroup.com/global/investors/quarterly-earnings)
links its [July 14 Q2 transcript PDF](https://www.citigroup.com/rcs/citigpa/storage/public/2026psqtr2-transcript.pdf);
only PDF metadata was inspected, and the direct file returned 403 to a
metadata-only request. It was not retried or bypassed. Official event pages
for Amazon, Mastercard, Goldman Sachs, Morgan Stanley, and IBM list no
transcript. Wells Fargo's official quarterly page lists earnings materials,
while its GuruFocus transcript result remains an unverified lead. Third-party
leads for Apple, Intel, GS, MS, IBM, and Wells Fargo remain unverified. See
`inputs/transcript_candidate_screen_q2_2026.csv` and
`inputs/transcript_access_audit_template.csv`. No full transcript has been
checked for completeness, no source has confirmed retention or external-AI
permission, and the audit does not establish 10–20-call coverage.
Public visibility is not evidence of reuse rights; obtain written permission
or a suitable institutional/explicitly permitted source before collecting or
scoring text.

FactSet has an [Academic ID request page](https://support.factset.com/academic/),
which is a plausible institution-mediated access route. The page itself does
not establish access to transcripts, coverage, or AI-use rights. The
course lead/library must verify those entitlements; no rights-cleared
transcripts have been collected and the 10–20-call audit is incomplete.

Quartr's [B2C terms PDF dated November 27, 2025](https://a.storyblok.com/f/182663/x/49876bbd8f/terms-of-service-quartr-b2c-version-2025-11-27.pdf)
prohibits data-mining tools and limits its
service content to internal use; third-party furnishing requires written
approval or another permission provided under the terms. Permission to retain
transcript text for this project or submit it to an external model is not
established. Log only coverage and rights metadata in
`inputs/transcript_access_audit_template.csv` until permission is verified.

Before any AI extension, audit at least 10–20 authorized Q2 2026 calls for
transcript coverage, event alignment, and usable text. This is a feasibility
check, not a sufficient prediction sample. Document the model version and its
provider-documented cutoff; do not claim that the cohort was absent from
training data based on a published cutoff alone. Keep subsequent returns and
post-call information out of the scoring process.

## Remaining threats and checks

- The Homework 8 dashboard includes three reproducible 20-row synthetic
  component fixtures and their event-ID outer merge. They exist only to check
  handoff, display, and missing-data behavior; generated EPS, firm
  characteristics, transcript features, and CAR values are not real data or
  model results, and the Event Study Package has not been run on them. The
  four-company Yahoo pilot remains a separate convenience sample.
- Verify point-in-time S&P 500 membership and retain post-roster removals.
- Independently verify event timestamps and EPS actual/consensus definitions.
- Account for announcement timing, confounding same-day news, overlapping
  return windows, and incomplete forward outcomes.
- If rights and broader transcript coverage are established, compare
  performance on the same events using an earlier-60%/later-40% chronological
  split; report transcript coverage and uncertainty, not only a score or
  p-value. Otherwise, defer the AI predictive comparison.
- Do not infer strategy profitability from statistical association; the pilot
  has no transaction-cost model and is not an investment recommendation.
