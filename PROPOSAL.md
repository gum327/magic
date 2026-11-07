# Beyond the Earnings Surprise
## Do earnings-call signals improve predictions of post-earnings returns?

**A research proposal by Team Magic**  
Abby Fischler · Gus Maass · Cammy Marks · Michelle Orloff

## Research question

For S&P 500 constituents as of June 30, 2026, do pre-specified signals from
management's earnings-call language improve chronological holdout prediction
of 20-trading-session factor-proxy-adjusted returns beyond EPS surprise and
the announcement reaction for fiscal quarters ending in calendar Q2 2026?

Post-earnings announcement drift (PEAD) is well established. The project is
not framed as asking whether positive earnings surprises tend to be followed
by positive returns. Instead, we will test whether contemporaneous management
commentary adds predictive value over a quantitative baseline. The surprise-
only model is necessary as a comparator, not the novel result.

## Hypotheses

1. EPS surprise and the announcement reaction contain information about
   subsequent abnormal returns, providing a benchmark model.
2. Among events with authorized, usable transcripts, pre-specified call
   language measures improve chronological holdout prediction over the same
   baseline events.

The second hypothesis is conditional on transcript coverage, reuse rights, and
reproducible model scoring. We will report null or negative results and will
not treat these hypotheses as established outcomes.

## Sample and unit of observation

One row represents one S&P 500 company earnings announcement for a fiscal
quarter ending from April 1 through June 30, 2026. The target universe is the
dated constituent roster as of June 30, 2026, archived in
`inputs/sp500_constituents_20260630.csv`. Retain firms that leave the index
after the roster date. Since this is one recent cohort rather than a multi-year
sample selected from current constituents, the earlier long-horizon
survivorship-bias concern does not apply to the target design.

Record each company's fiscal-quarter end separately from the public earnings
release and call dates. Include an event in the quantitative sample when the
company, earnings data, release timing, and required price/factor data can be
verified. Record exclusions and missingness by reason. The transcript
extension uses only events with authorized, time-aligned transcripts; do not
silently compare it with a different sample.

The existing AAPL/MSFT/TSLA/NVDA sample is a four-company pipeline
demonstration using Yahoo Finance. It is not representative, is not the target
sample, and must not be used to claim evidence for either hypothesis.

## Data and provenance

| Data | Intended use | Status / constraint |
|---|---|---|
| June 30, 2026 S&P 500 roster | Define a fixed point-in-time universe | Archived Wikipedia revision `1361794875` (503 stocks); not an official S&P file |
| Fiscal quarter, actual and consensus EPS | Define event and surprise | Audit coverage, definitions, revisions, and source |
| Earnings release/call timestamp | Align the information event to trading sessions | Verify with a second source where possible |
| Adjusted daily prices | Stock and ETF returns | The current pilot uses Yahoo Finance; validate before scale-up |
| SPY, BIL, IWM, IWD, IWF adjusted prices | Provisional daily factor proxies | ETF proxies, not official Kenneth French factors |
| Earnings-call transcript | Construct text measures | Not acquired; access and reuse rights must be confirmed |
| Model version and rubric | Reproduce transcript measures | Proposed pinned checkpoint `gpt-5.2-2025-12-11`; verify transcript/API terms |

Store source name, retrieval time, source URL or identifier, definitions,
adjustment settings, and missing-data decisions for each dataset. Do not
commit licensed data, restricted transcript text, or credentials. Public
visibility of a transcript does not establish a right to download, retain, or
use it for model input.

### Transcript feasibility

Seeking Alpha's transcript index is publicly viewable. Its current terms of
use limit site content to personal, non-commercial use and prohibit automated
retrieval, scraping, and data mining. The team has not downloaded transcripts
or confirmed project-scale reuse permission. Do not scrape Seeking Alpha.
Request written authorization or verify an institutional license/another
explicitly permitted source before collecting text. Then audit 10–20 Q2 2026
calls for coverage, event alignment, and usable content. This audit is a
feasibility check only, not a sufficient predictive-analysis sample. If
rights or broader cohort coverage fail, complete the quantitative baseline
and defer AI sentiment.

Quartr's free mobile app advertises transcripts and in-app AI chat; its
transcript API and MCP offerings require paid access, and the MCP docs state
student plans are not eligible. The published
[mobile-app terms](https://quartr.com/terms-and-conditions) prohibit data
mining and limit service content to internal use; furnishing it to a third
party requires prior written approval or other permission under the terms.
Permission to retain text for this study or send it to an external model is
not established. Use
`inputs/transcript_access_audit_template.csv` to log metadata-only coverage
checks; do not copy transcript text until the applicable rights are confirmed.
FactSet's Academic ID request process is another route to ask the course
lead/library about, but transcript access and text-use rights have not been
confirmed.

The proposed model checkpoint is `gpt-5.2-2025-12-11`. OpenAI's
[model documentation](https://developers.openai.com/api/docs/models/gpt-5.2)
lists a fixed snapshot dated December 11, 2025 and an August 31, 2025
knowledge cutoff, both before the Q2 2026 cohort. Use the exact snapshot, not a
floating model alias; record the model ID, API date, prompts, and output
schema. A published knowledge cutoff is not a complete audit of training
data, so preserve the snapshot documentation and do not claim stronger
provenance than the provider states. The model cutoff is distinct from the
statistical holdout; it does not establish that the LLM's predictions or
training process are valid for this study.

## Variables and outcomes

### Earnings surprise

The pilot defines percentage EPS surprise as
`(reported EPS - consensus EPS) / abs(consensus EPS) * 100`. Near-zero
consensus can make this ratio unstable; report coverage and use a
pre-specified scaled-surprise alternative when a reliable denominator is
available. Preserve original actual and consensus values and their sources.

### Event time

Use the first trading session in which the public information could be acted
on. Pre-market releases map to that day's session; after-close releases map to
the next trading session. Use a documented market-hours convention for
during-session announcements. Flag ambiguous or unverified times and exclude
them from the primary analysis, with a sensitivity check under conservative
timing. Retain the release timestamp and assigned first tradable session.
Measure the announcement reaction as the close-to-close return ending on that
first tradable session. The forward 5-, 20-, and 60-session windows begin on
the following session, so the baseline's announcement-reaction predictor does
not overlap the return outcome.

### ETF-proxy factor-adjusted return

The official Kenneth French factor data have a publication lag for the most
recent events. The provisional daily proxies are:

- Market excess: SPY total return minus BIL total return.
- Size (SMB-like): IWM total return minus SPY total return.
- Value (HML-like): IWD total return minus IWF total return.

These are not the official Fama-French portfolios. Use distribution-adjusted
daily returns and fit each firm's exposure on 252 pre-event trading-session
returns ending before the first tradable session. For each post-reaction day,
calculate abnormal return as stock excess return minus the fitted intercept
and factor component:

`r_stock - r_BIL - alpha - beta_mkt*(r_SPY-r_BIL) - beta_size*(r_IWM-r_SPY) - beta_value*(r_IWD-r_IWF)`

Sum daily abnormal returns over the 20 sessions after the announcement-
reaction session. The 5- and 60-session estimates use the same convention and
are secondary. The current pilot's arithmetic difference between adjusted
stock and SPY buy-and-hold returns is a transparent pipeline/robustness
reference, not the factor-adjusted outcome. Record ETF symbols, price source,
estimation window, and observations used for every fit.

As of November 6, 2026, some 60-session windows for the Q2 cohort are not yet
observable. Keep these outcomes missing until the full window exists; do not
replace them with zero or require 60 sessions for the 20-session primary
analysis.

## Analysis plan

1. Validate the dated constituent roster, fiscal quarter ends, EPS fields,
   event timestamps, prices, and source coverage before estimating results.
2. Compute the announcement reaction and 5-, 20-, and 60-session factor-proxy
   abnormal returns under the same event-time rules.
3. Describe the sample, exclusions, missingness, EPS-surprise distribution,
   transcript coverage, and outcome availability.
4. Fit a baseline prediction model using EPS surprise, announcement reaction,
   and only pre-specified available controls.
5. If transcript access and coverage are adequate, score each call with a
   fixed rubric for sentiment, forward guidance, and uncertainty. Record
   transcript identifiers, model/checkpoint, prompt or scoring rubric, and
   score version. The model must not receive later returns or post-call
   information.
6. If authorized transcript coverage is adequate, sort events by public
   announcement timestamp, fit ordinary least squares on the earlier 60%,
   and evaluate once on the later 40%. The baseline uses EPS surprise and the
   announcement reaction; the augmented model adds the pre-specified
   language scores. Compare the models on the same transcript-covered events;
   do not randomly mix later events into training or tune on the holdout.
7. Report held-out performance differences, uncertainty, sample size, and
   coverage changes, including mean absolute error, root mean squared error,
   and out-of-sample R-squared relative to the training-set outcome mean. The
   10–20-call feasibility audit is not by itself enough to establish
   predictive performance. If the usable cohort or holdout is too small for
   stable inference, label results exploratory or defer them.
8. Test sensitivity to event timing, alternative return windows, proxy-factor
   choices, and sample exclusions. Discuss overlapping return windows and
   contemporaneous confounding news.

No trading strategy or profitability claim follows from a predictive
association. A trading interpretation would require a separately specified
portfolio, costs, and implementation assumptions.

## Output and dashboard

The deliverable is a reproducible dataset, analysis, and research dashboard
that makes the sample, factor-proxy definitions, transcript coverage, model
comparison, and limitations visible. The current Streamlit app is only a
four-row pilot explorer. It can now display the pilot's ETF-proxy estimates,
but those four convenience-sample rows are not results for the S&P 500 cohort.
Do not display placeholder sample sizes.

## Current implementation and next steps

The Yahoo Finance pilot pipeline now computes EPS surprise, SPY
buy-and-hold abnormal returns, and ETF-proxy factor-adjusted returns with
252 pre-event observations. It also includes a tested chronological OLS
comparison helper. The refreshed four-company CSV has complete 20-session
outcomes and preserves an incomplete 60-session value as missing. The event
manifest is still empty, so no S&P 500 Q2 cohort output or transcript scores
exist. FactSet provides an
[Academic ID request page](https://support.factset.com/academic/), but course
access to transcripts and associated text-use rights remain unverified.

Next:

1. Use the archived June 30, 2026 roster in
   `inputs/sp500_constituents_20260630.csv`; validate its symbols against the
   chosen event sources.
2. Ask the course lead/library to check FactSet Academic access and transcript
   reuse rights, or obtain written permission from another source.
3. If access is confirmed, audit 10–20 Q2 2026 transcripts and record
   coverage. Treat this as a feasibility check, not a sufficient model
   sample; otherwise defer transcript scoring.
4. Audit EPS, timestamps, stock returns, and ETF coverage for the fixed
   cohort.
5. Apply the tested factor-proxy outcome to the verified target cohort. If
   transcript rights and cohort coverage are adequate, implement the
   pre-specified chronological 60/40 holdout comparison; otherwise report
   the AI extension as deferred or exploratory.
6. Proceed with transcript scoring only if rights, coverage, alignment, and
   model training cutoff are verified.

See `STATUS.md` for current decisions and open dependencies, and
`audits/01_self_audit.md` for the pilot's limitations.
