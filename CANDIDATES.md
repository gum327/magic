# Research design decisions

The project has moved from a broad PEAD question to a specific test of whether
earnings-call language adds predictive information beyond standard earnings
metrics.

## Selected design

- **Question:** Among S&P 500 constituents as of June 30, 2026, do
  pre-specified earnings-call language signals improve chronological holdout
  prediction of 20-session factor-proxy-adjusted returns beyond EPS surprise
  and the announcement reaction for fiscal quarters ending in calendar Q2
  2026?
- **Unit:** One firm-quarter announcement.
- **Sample:** The archived June 30, 2026 Wikipedia revision (`1361794875`,
  503 stocks; not an official S&P file) and one Q2 2026
  reporting cohort, subject to verified source coverage. This short,
  point-in-time cohort avoids the long-horizon current-constituent
  survivorship problem; keep firms that leave the index after the roster date.
- **Primary outcome:** Twenty-session cumulative abnormal return after and
  excluding the separately measured announcement-reaction session, from a
  three-factor regression using ETF proxies. Report 5- and 60-session windows
  only when complete.
- **Baseline:** EPS surprise, announcement reaction, and pre-specified
  controls.
- **Extension:** Add fixed, reproducible transcript-language scores only if
  lawful access and adequate cohort coverage are established. The 10–20-call
  audit is a feasibility check, not the predictive-analysis sample.
  Proposed snapshot: `gpt-5.2-2025-12-11` (published before the cohort, with
  provider-documented August 31, 2025 knowledge cutoff); verify terms and
  preserve the exact model/version documentation.
- **Main comparison:** Fit on the earlier 60% of transcript-covered events
  and evaluate once on the later 40%; compare models on the same events and
  report coverage differences. Treat results as exploratory if the holdout is
  too small.

## Return model

The official Kenneth French files lag the newest events. The provisional
daily ETF proxies are SPY minus BIL (market excess), IWM minus SPY
(size/SMB-like), and IWD minus IWF (value/HML-like). Estimate factor loadings
from the 252 trading sessions ending before the first tradable session. Report
the announcement reaction separately; aggregate daily residuals only over
forward sessions after that reaction session. Call these ETF proxies, not
official French factors. The pipeline now emits both this estimate and the
SPY buy-and-hold pilot comparison.

## Transcript sourcing decision

Seeking Alpha exposes a public transcript index, but its current terms prohibit
automated retrieval and restrict content to personal, non-commercial use.
Project-scale collection or model use is not authorized by public visibility
alone. Obtain written permission or use a licensed/explicitly permitted
provider before collecting. If access is not confirmed, defer AI sentiment
and complete the quantitative baseline without it.

## Why the question changed

Whether PEAD exists is not the project's novel contribution. The quantitative
surprise-only model is a necessary benchmark; the project asks whether
management's contemporaneous call language improves held-out predictions
beyond that benchmark.
