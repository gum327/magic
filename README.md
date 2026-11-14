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
retrieval, scraping, and data mining. Do not scrape it. A metadata screen
started November 7 and updated November 10, 2026 found 21 candidate-company
rows; see
`inputs/transcript_candidate_screen_q2_2026.csv`. These are not 21 verified or
rights-cleared transcripts. Twelve potential first-party transcript locations
have been identified within the calendar-Q2 cohort: PDF links for Alphabet,
AT&T, Bank of America, Citigroup, Coca-Cola, Expedia, Hilton, JPMorganChase,
Meta, Netflix, and Visa, plus Microsoft's transcript page. Hilton and Expedia
fiscal quarters ended June 30, 2026, confirmed by their SEC 10-Q headers. HPE's issuer PDF is outside the
cohort because fiscal Q2 ended April 30, 2026. Transcript text was not
reviewed or retained and reuse/model rights remain unverified. Apple and
Intel are event-aligned, with fiscal quarters ended June 27, but their
official results materials do not provide a verified full transcript.
AT&T's Q2 event ending June 30 is confirmed. Microsoft IR displays its Q4
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
or submitting transcript text to any model. Twelve potential first-party
transcript locations remain in the cohort (11 PDF links and Microsoft's
transcript page); HPE's located PDF is excluded because its quarter ended
April 30. AT&T's fiscal period alignment is confirmed. Apple and Intel are
calendar-Q2 aligned but their official materials do not provide a verified
full transcript. Wells Fargo is a newly recorded third-party lead only; its
transcript destination is not verified. No source is cleared for this study's
retention or model use. The metadata audit has 21 company candidates, but it does
not establish usable 10–20-call coverage; leads for GS, MS, IBM, and WFC
remain unverified.
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

## Homework 8 dashboard fixture and shared row contract

For the checkpoint, the dashboard merges three separate 20-row handoff
fixtures. They use fictional `SYN` identifiers and are generated locally by
`code/build_synthetic_checkpoint.py`; none contains real issuer, Yahoo, or
event-study package observations. The transcript handoff uses the existing
Claude scores on fictional mini-calls only. Classic sentiment values and
congratulations flags are placeholders, not computed from text. Some blanks
deliberately test coverage display. No transcript text is stored in the merged
dashboard data.

The normalized merge key is `event_id`, with `ticker` and `fiscal_period_end`
checked across all sources. Each source is one row per company-quarter event;
the outer merge keeps events absent from a component and adds a
`*_record_present` flag. For real data, agree on the event ID across team
handoffs before merging. Dashboard fields:

The separate local text-feature pipeline is documented in
[`docs/transcript_features/README.md`](docs/transcript_features/README.md).
It calculates Loughran–McDonald dictionary features on the 20 fictional
speaker-labeled excerpts and writes
`outputs/synthetic_transcript_text_features.csv`, keyed by the same `event_id`.
This output is separate from the dashboard fixture: the latter's classic
sentiment columns remain synthetic placeholders until the team agrees to
replace them with extracted features. The local pipeline makes no external
AI/API calls.

| Group | Shared columns and meaning |
|---|---|
| Event | `event_id`, `ticker`, `fiscal_period_end`, timezone-aware `earnings_timestamp`; one call per row |
| Yahoo-finance X | `eps_actual`, `eps_estimate`, `eps_surprise_pct` = `(actual - estimate) / abs(estimate) * 100`, `eps_beat`, `market_cap_usd`, `sector`, and pre-call return/volatility fields |
| Event-study Y | Normalized checkpoint fields `car_0_1_pct`, `car_0_5_pct`, `car_0_20_pct`; Gus should map the package output and confirm its event-day convention |
| Transcript X | Placeholder classic fields `transcript_sentiment`, `management_sentiment`, `analyst_question_sentiment`, `congratulations_mentioned`; Claude-scored synthetic-call fields `language_outlook_tone`, `language_guidance_specificity`, and `transcript_score_status` |
| Provenance | Per-source source/retrieval fields; synthetic input is labeled, retrieval dates are blank, and Claude model, effort, prompt, and run date are recorded |

`transcript_sentiment`, manager/analyst sentiment, and the congratulations
flag are synthetic UI values, not scores derived from text. The existing
transcript checkpoint rubric covers outlook tone and guidance specificity
only. Those fields in the fixture are the Claude Haiku 5.5 Low outputs from
the 20 fictional development calls under prompt version 1.2; the same set was
used for prompt tuning, so its 20/20 reference agreement is not an independent
accuracy estimate. The separate 10-call synthetic validation is documented in
`TRANSCRIPT_CHECKPOINT.md`. The exact Yahoo fields should be reconciled with
Gus's myGPT list, and Kami should approve the explanatory/predictive variables
and whether to use regression, predictive ML, or both. The dashboard does not
fit models.

For the checkpoint, the comparison can be staged as (1) Yahoo variables only,
(2) Yahoo plus classic transcript sentiment, and (3) those variables plus
additional transcript/AI features. Because `CAR[0,1]` includes the event day
and following day, do not use a same-window announcement return as a
predictor. This checkpoint fixture does not change the final study design in
`PROPOSAL.md`, which has a separate ETF-proxy outcome plan.

The generated files are:

- `outputs/synthetic_yahoo_finance_variables.csv`
- `outputs/synthetic_event_study_results.csv`
- `outputs/synthetic_transcript_features.csv`
- `outputs/synthetic_checkpoint_dataset.csv` — outer-merged dashboard input

Regenerate all four with `python code/build_synthetic_checkpoint.py`. For
other compatible handoffs, the shared merger is
`code/merge_event_datasets.py`. Choose the synthetic checkpoint in the
dashboard's Dataset menu to inspect overview, coverage, quality checks, and
limitations; the existing Yahoo pilot remains available in that menu.

## Repository guide

- `Magic_TeamProposal.ipynb` — project proposal and revised research design.
- `PROPOSAL.md` — detailed sample, methods, and validation plan.
- `STATUS.md` — decisions, completed work, and open dependencies.
- `code/pead_pipeline.py` — current small Yahoo Finance pilot pipeline.
- `code/build_synthetic_checkpoint.py` — deterministic synthetic-only
  three-source dashboard fixture generator.
- `code/extract_transcript_features.py` — local, dictionary-based transcript
  feature extractor; no external model calls.
- `docs/transcript_features/README.md` and
  `docs/transcript_features/data_dictionary.md` — run instructions, feature
  definitions, and provenance.
- `inputs/synthetic_transcript_manifest.csv` and
  `outputs/synthetic_transcript_text_features.csv` — synthetic event metadata
  and local dictionary scores; no transcript text in the output.
- `code/merge_event_datasets.py` — validated outer merge on shared event IDs.
- `outputs/synthetic_yahoo_finance_variables.csv`,
  `outputs/synthetic_event_study_results.csv`, and
  `outputs/synthetic_transcript_features.csv` — separate 20-row synthetic
  team handoff fixtures.
- `outputs/synthetic_checkpoint_dataset.csv` — 20-row synthetic dashboard
  merge; no real issuers, returns, or transcript text; AI scores use fictional
  calls only.
- `outputs/pead_sample.csv` — four-firm pilot output; not the final sample.
- `inputs/q2_2026_events_template.csv` — required verified event-manifest
  columns; currently unpopulated.
- `inputs/transcript_access_audit_template.csv` — metadata-only transcript
  coverage and rights log; do not store transcript text here.
- `inputs/transcript_candidate_screen_q2_2026.csv` — preliminary, metadata-only
  screen of transcript listing leads; not verified coverage or permission.
- `TRANSCRIPT_CHECKPOINT.md` — synthetic-first prompt and scoring rubric for
  the transcript-feature checkpoint; not the final study protocol.
- `inputs/synthetic_transcript_checkpoint.jsonl` — 20 invented mini-call
  transcripts for prompt testing; not company or market data.
- `inputs/synthetic_transcript_expected_scores.csv` — reference scores for
  those invented excerpts; do not send this file to a model.
- `inputs/synthetic_transcript_checkpoint_claude_scores.csv` — Claude scores
  for the synthetic checkpoint run; not study data.
- `inputs/synthetic_transcript_validation.jsonl` — separate 10-call synthetic
  validation set; do not treat as real event data.
- `inputs/synthetic_transcript_validation_expected.csv` — blinded reference
  scores; do not send this file to a model.
- `inputs/synthetic_transcript_validation_claude_scores.csv` — Claude scores
  from the frozen-prompt validation run; not study data.
- `dashboard/pead_app.py` — pilot and synthetic checkpoint dashboard.
- `dashboard/data_contract.py` — shared event schema, coverage summary, and
  dashboard quality checks.
- `audits/01_self_audit.md` — current pilot limitations and validation needs.
- `tests/test_pead_pipeline.py` — pipeline unit tests.

## Run the pilot

Run commands from the repository root:

```bash
pip install -r requirements.txt
python code/pead_pipeline.py --as-of 2026-11-06
python code/build_synthetic_checkpoint.py
python code/extract_transcript_features.py \
  --input-jsonl inputs/synthetic_transcript_checkpoint.jsonl \
  --manifest-csv inputs/synthetic_transcript_manifest.csv \
  --dictionary-csv /path/to/Loughran-McDonald_MasterDictionary_1993-2025.csv \
  --dictionary-retrieved-date 2026-11-13 \
  --output outputs/synthetic_transcript_text_features.csv
python code/merge_event_datasets.py \
  --financial outputs/synthetic_yahoo_finance_variables.csv \
  --event-study outputs/synthetic_event_study_results.csv \
  --transcript outputs/synthetic_transcript_features.csv \
  --output outputs/synthetic_checkpoint_dataset.csv
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
