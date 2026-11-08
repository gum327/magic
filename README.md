# Team Magic: Earnings Calls and Post-Earnings Returns

## Project question

For S&P 500 companies reporting fiscal quarters that ended in calendar Q2
2026, do pre-specified signals from earnings-call language improve
chronological holdout prediction of 20-trading-session factor-proxy-adjusted
returns beyond EPS surprise and the announcement reaction?

Post-earnings announcement drift (PEAD) is established in prior research, so
the project is not premised on rediscovering that positive surprises predict
positive returns. The contribution we will test is whether information in
management commentary adds useful predictive value beyond conventional
earnings data.

## Scope and design

- **Observation:** One company-quarter earnings announcement.
- **Universe:** S&P 500 constituents as of June 30, 2026, using a dated
  constituent list. The archived [snapshot CSV](inputs/sp500_constituents_20260630.csv)
  contains 503 listed stocks from the Wikipedia revision made June 30, 2026
  (revision `1361794875`); this is a point-in-time research roster, not an
  official S&P file. Keep that roster fixed for the cohort.
- **Earnings cohort:** Fiscal-quarter end dates from April 1 through June 30,
  2026, with the corresponding earnings calls and announcements. Record both
  the fiscal period end and public announcement timestamp.
- **Primary outcome:** Cumulative abnormal return over the 20 full trading
  sessions after the announcement-reaction session, estimated with three
  ETF-based factor proxies. Keep the announcement reaction separate from
  those forward sessions. The pipeline now computes these proxies for the
  four-company pilot; that convenience sample is still not the target study.
- **Later outcomes:** Report 5- and 60-session estimates as secondary results
  when complete forward windows are available. Do not treat not-yet-observed
  returns as zero or silently drop them.
- **Transcript/AI extension:** Compare a surprise-and-reaction baseline with
  a model adding pre-specified call-language scores. The proposed scoring
  checkpoint is `gpt-5.2-2025-12-11`, published before the cohort; its
  [official documentation](https://developers.openai.com/api/docs/models/gpt-5.2)
  lists an August 31, 2025 knowledge cutoff. Use this pinned snapshot, not a
  floating alias, and verify provider availability and transcript/API terms
  before use. A 10–20-call audit is only a feasibility check, not enough by
  itself to support the predictive comparison. Include the extension only if
  rights and adequate coverage are verified.

### Prediction test

The target is one reporting cohort, so the planned holdout is chronological
within that cohort: sort eligible events by public earnings timestamp, fit on
the earlier 60%, and evaluate once on the later 40%. Use the same
transcript-covered events for the baseline and language-augmented model; do
not tune on the holdout. If transcript coverage or the resulting samples are
too small for a meaningful comparison, report the language analysis as
exploratory or defer it. A model's published knowledge cutoff does not prove
that specific events were absent from its training data.

Use ordinary least squares for both models. The baseline uses EPS surprise
and the announcement reaction; the augmented model adds the pre-specified
language scores. Compare mean absolute error, root mean squared error, and
out-of-sample R-squared relative to the training-set outcome mean. The helper
`compare_chronological_predictions` in `code/pead_pipeline.py` enforces a
shared complete-case sample and returns holdout predictions and metrics.

### Provisional ETF factor proxies

The official Kenneth French factor files are not current enough for the newest
events. Until those files become available, the proposed daily proxy series
are:

- Market excess return: SPY total return minus BIL total return.
- Size (SMB-like): IWM total return minus SPY total return.
- Value (HML-like): IWD total return minus IWF total return.

These are ETF-based proxies, not Kenneth French factors. Estimate event-level
loadings on the 252 trading sessions before each announcement-reaction
session, then sum daily regression residuals over the subsequent outcome
window. The announcement reaction is reported separately. Record the ETF
series, estimation window, and missing-data rules; report SPY buy-and-hold
abnormal returns as a robustness comparison.

## Data and access

The existing four-company Yahoo Finance sample validates event timing, return
construction, and the dashboard only. It is not representative and is not
evidence for the research question. Larger-sample sources for point-in-time
index membership, EPS actuals/consensus, event timestamps, prices, and ETF
returns still require coverage checks and source documentation.

The dated S&P 500 roster is saved in `inputs/sp500_constituents_20260630.csv`.
Yahoo Finance's earnings-date history does not reliably identify fiscal
period ends or provide a preserved point-in-time consensus record. Build the
target cohort from the verified event manifest
`inputs/q2_2026_events_template.csv`; each event needs a fiscal period end,
release timestamp, actual/consensus EPS, and source references. Do not infer
that a reporting date automatically corresponds to a calendar Q2 fiscal end.

Seeking Alpha's transcript index is publicly viewable, but its current terms
limit use to personal, non-commercial purposes and prohibit automated
retrieval, scraping, and data mining. Do not scrape it. A November 7, 2026
metadata screen found 18 candidate-company rows; see
`inputs/transcript_candidate_screen_q2_2026.csv`. These are not 18 verified or
rights-cleared transcripts. Ten potential first-party transcript PDF links
have been identified for Alphabet, AT&T, Bank of America, Citigroup,
Coca-Cola, HPE, JPMorganChase, Meta, Netflix, and Visa, plus Microsoft's
transcript page. Link availability was checked, but transcript text was not
reviewed or retained and reuse/model rights remain unverified. AT&T and HPE
fiscal-period alignment also remains unverified. Microsoft IR displays its Q4
FY2026 transcript; only the initial preview was viewed and no text was saved.
[Amazon's official event page](https://ir.aboutamazon.com/events/event-details/2026/Q2-2026-Amazoncom-Inc-Earnings-Conference-Call/default.aspx)
and [Mastercard's official event page](https://investor.mastercard.com/events-and-presentations/events/event-details/2026/Q2-2026-Mastercard-Inc-Earnings-Conference-Call/default.aspx)
confirm their Q2 calls but list no transcript. Microsoft's
[website terms](https://www.microsoft.com/en-us/legal/terms-of-use) generally
restrict copying and do not establish project-retention or external-model
permission. Seeking Alpha's public transcript listings are not a lawful
permission substitute; do not scrape or retain its content.
Quartr's [mobile-app terms](https://a.storyblok.com/f/182663/x/49876bbd8f/terms-of-service-quartr-b2c-version-2025-11-27.pdf)
prohibit data-mining tools and restrict service content to internal use;
furnishing it to a third party requires prior written approval or another
express permission in the terms. Whether an external model or this course
research is permitted has not been confirmed. Visa's IR event page links the transcript PDF for its July 28 Q3 2026 event;
the PDF was not opened and rights remain unknown. Citigroup's official
quarterly earnings page links its July 14 Q2 transcript PDF; only the PDF
metadata was inspected, not transcript text, and retention/model rights remain
unresolved. Official Goldman Sachs,
Morgan Stanley, and IBM event pages confirm Q2 calls but list no transcript.
Intel search results identify a third-party transcript listing, but neither
an Intel transcript page nor the destination transcript page was verified.
FactSet provides an
[Academic ID request page](https://support.factset.com/academic/), but actual
institutional transcript access and reuse terms are unknown. Get written
authorization or verify an institutional license before obtaining, retaining,
or submitting transcript text to any model. Eleven potential first-party
source links are identified (ten transcript PDF links and Microsoft's
transcript page), including Citi's Q2 and Visa's Q3 2026 PDFs linked from
their IR pages. The AT&T and HPE fiscal-period alignment is unverified. No
source is cleared for this study's retention or model use. The metadata audit
has 18 candidate-company rows, but it does not establish 10–20-call transcript
coverage: AAPL and Intel remain unverified at the issuer/source level; third-
party transcript leads for GS, MS, and IBM remain unverified even though their
issuer call pages have been checked.
Track coverage and rights checks in
`inputs/transcript_access_audit_template.csv`; record metadata only until
permission is established. Do not commit transcript text or other restricted
raw data.

[Quartr's mobile app](https://quartr.com/products/mobile-app) advertises
transcripts and in-app AI chat at no cost on mobile, while its transcript API
and MCP require paid or Pro access. The published app terms do not establish
permission to retain transcript text or send it to a separate model. This is a
possible source to ask about, but neither a systematic coverage audit nor
research use is confirmed by the published terms.

## Repository guide

- `Magic_TeamProposal.ipynb` — project proposal and revised research design.
- `PROPOSAL.md` — detailed sample, methods, and validation plan.
- `STATUS.md` — decisions, completed work, and open dependencies.
- `code/pead_pipeline.py` — current small Yahoo Finance pilot pipeline.
- `outputs/pead_sample.csv` — four-firm pilot output; not the final sample.
- `inputs/q2_2026_events_template.csv` — required verified event-manifest
  columns; currently unpopulated.
- `inputs/transcript_access_audit_template.csv` — metadata-only transcript
  coverage and rights log; do not store transcript text here.
- `inputs/transcript_candidate_screen_q2_2026.csv` — preliminary, metadata-only
  screen of transcript listing leads; not verified coverage or permission.
- `dashboard/pead_app.py` — pilot Streamlit dashboard.
- `audits/01_self_audit.md` — current pilot limitations and validation needs.
- `tests/test_pead_pipeline.py` — pipeline unit tests.

## Run the pilot

Run commands from the repository root:

```bash
pip install -r requirements.txt
python code/pead_pipeline.py --as-of 2026-11-06
python -m unittest discover -s tests
streamlit run dashboard/pead_app.py
```

The output contains both SPY buy-and-hold abnormal returns and ETF-proxy
factor-adjusted returns. It remains a four-company pilot; it is not the S&P
500 Q2 2026 analysis.

After verifying source data, construct the cohort with:

```bash
python code/pead_pipeline.py \
  --events-csv inputs/q2_2026_events.csv \
  --universe-csv inputs/sp500_constituents_20260630.csv \
  --as-of 2026-11-06 \
  --output outputs/q2_2026_cohort.csv
```

`q2_2026_events.csv` must follow the header in the template. The pipeline
validates that fiscal period ends fall in Q2 2026 and tickers belong to the
dated roster. It computes returns but does not validate the truth or license
of source EPS/timestamp data.
