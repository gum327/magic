# Project status

## Current direction

The research question is now whether earnings-call language adds predictive
value beyond EPS surprise and the immediate announcement reaction—not whether
positive surprises are followed by positive returns, a well-established PEAD
result.

The target is a fixed, dated roster of S&P 500 constituents as of June 30,
2026, for fiscal quarters ending in calendar Q2 2026. Because this is a
single-quarter, point-in-time cohort, the prior multi-year current-constituent
survivorship concern does not apply. Keep the roster fixed and retain firms
that later leave the index so membership is not selected using future
outcomes.

The 503-stock roster has been archived at
`inputs/sp500_constituents_20260630.csv` from Wikipedia revision `1361794875`
(revision time 2026-06-30 03:37:58 UTC). It is dated and usable as the team's
point-in-time roster, but is not an official S&P file; the source and this
limitation are recorded in each row.

The primary outcome is 20-session cumulative abnormal return from an
ETF-proxy three-factor model, measured after and excluding the separately
reported announcement-reaction session. Official Kenneth French factors lag recent
events, so the provisional daily proxies are SPY minus BIL for market excess
return, IWM minus SPY for size, and IWD minus IWF for value. These are
transparent ETF proxies, not the official French factors. Use 5- and
60-session windows as secondary outcomes when observable; some 60-session
windows for the Q2 cohort are not yet complete as of November 6, 2026.

## Transcript access: candidate screen, rights unresolved

Seeking Alpha's transcript index is publicly viewable and lists earnings-call
transcripts. Its [current terms of use](https://about.seekingalpha.com/terms)
state that content is for personal, non-commercial use and prohibit robots,
scraping, data mining, or similar automated retrieval. No transcripts were
downloaded or retained from Seeking Alpha, and project-scale reuse permission
has not been confirmed. Do not scrape it. A legitimate access route to check is
[FactSet's Academic ID request page](https://support.factset.com/academic/).
The page confirms an academic access request process, but does not confirm
that our course has access to transcripts or permission for AI use. Ask the
course lead/library to verify that entitlement or request a written license
from a transcript provider.

The metadata screen began on November 7 and was updated November 10, 2026.
It now has 21 company candidates in
`inputs/transcript_candidate_screen_q2_2026.csv`, including Wells Fargo,
which was added as a lead. Twelve potential first-party transcript locations
are event-aligned to the calendar-Q2 cohort: 11 PDF links (Alphabet,
AT&T, Bank of America, Citigroup, Coca-Cola, Expedia, Hilton, JPMorganChase,
Meta, Netflix, and Visa) plus Microsoft's transcript page. Hilton's
quarterly-results page and Expedia's Q2 event page each list a transcript
PDF; SEC 10-Q headers confirm both quarters ended June 30, 2026 (calls July
28 and August 5). Both are posted transcripts, not verified complete ones:
their contents were not opened, and Hilton's site-usage agreement and
Expedia's website terms restrict copying and do not grant study-retention or
external-model rights. HPE has a located issuer PDF,
but its fiscal Q2 ended April 30, so it is outside the cohort. Apple and
Intel fiscal quarters ended June 27 and their calls were July 30 and July 23,
respectively; official result materials do not provide a verified full
transcript. AT&T's fiscal period alignment is confirmed at June 30.

The Citi PDF returned 403 to a metadata-only request; it was not retried or
bypassed. Transcript text was not retained. The 11 PDF contents were not
reviewed for completeness, and no transcript source has confirmed permission
for project retention or external AI input. Microsoft's
[FY26 Q4 page](https://www.microsoft.com/en-us/Investor/events/FY-2026/earnings-fy-2026-q4)
displays transcript text, but only the initial preview was viewed and no text
was saved or analyzed; its [website terms](https://www.microsoft.com/en-us/legal/terms-of-use)
do not establish project-retention or external-model permission. Official
event pages for Amazon, Mastercard, Goldman Sachs, Morgan Stanley, and IBM
list no transcript. Wells Fargo's official quarterly page lists earnings
materials, while its transcript result is only a GuruFocus search lead whose
destination and rights are unverified. Third-party leads for GS, MS, IBM,
Apple, and Intel also remain unverified. No full transcript has been checked
for completeness; the pilot remains empty.

The attached
[Quartr B2C terms PDF](https://a.storyblok.com/f/182663/x/49876bbd8f/terms-of-service-quartr-b2c-version-2025-11-27.pdf)
is the November 27, 2025 version; as already noted, its terms do not establish
permission to retain transcripts for this study or send them to an external
model. This is not a completed 10–20-call coverage audit: no rights-cleared
transcript has been collected and no provider license has been established.
The two requested 3–5-hour work sessions have not been completed or
represented as complete.

[Quartr's free mobile app](https://quartr.com/products/mobile-app) advertises
access to transcripts and an in-app AI chat. Its published
[consumer terms](https://quartr.com/terms-and-conditions) prohibit data-mining
tools and say service content is for internal use; furnishing that content to
a third party requires prior written approval or another permission provided
under the terms. The terms do not establish permission to retain transcript
text for this study or submit it to an external model. Its separate
[API](https://quartr.com/products/quartr-api) advertises historical transcripts
but requires a commercial scoping/demo process; the
[MCP documentation](https://mcp.quartr.com/docs) says a Quartr Pro subscription
is required and student plans are not eligible. A manual metadata-only
coverage check might be possible, but the terms do not clearly authorize a
systematic audit. We have not accessed or copied transcripts from Quartr. Use
`inputs/transcript_access_audit_template.csv` to record source, availability,
and rights-check status without storing transcript text.

AI sentiment remains conditional on that transcript audit and rights check.
The proposed pinned scoring checkpoint is `gpt-5.2-2025-12-11`. The
[provider docs](https://developers.openai.com/api/docs/models/gpt-5.2) date
the snapshot before the cohort and list an August 31, 2025 knowledge cutoff.
Use the immutable snapshot rather than a floating alias, and preserve the
model documentation. A knowledge cutoff is not a complete audit of the model's
training data. The language model must not receive post-call returns or
subsequent information. The 10–20-call audit is only a feasibility check, not
enough on its own to support a predictive model comparison. Quartr's consumer
terms have now been reviewed; they do not establish retention or external-model
use rights. The Microsoft terms have also been reviewed and do not establish
those rights.

For the November 13 checkpoint, use synthetic transcripts only with external
AI. Professor Bowen's current instruction prohibits uploading licensed
transcript text to GitHub or sending it to external AI services; do not use
Claude, Expected Parrot, or another external service with real transcript
text. The synthetic-only prompt and two-feature scoring rubric are in
`TRANSCRIPT_CHECKPOINT.md`. No real transcript text has been processed here,
and this checkpoint does not replace the proposed final model or support
predictive claims. The synthetic example was run twice with Claude Haiku 5.5
at Low effort and returned the expected scores. The web interface did not
expose a maximum-token setting, and strict JSON parseability remains
unverified for the single-transcript JSON prompt.

Twenty expanded synthetic mini-calls were batch-scored with Claude Haiku 5.5
at Low effort, using prompt version 1.2. All 20 matched the reference labels
after the rubric was clarified and two labels were corrected; because the same
examples were used for prompt tuning, this is not an independent accuracy
estimate. The mock calls test scoring and output format, not real-call token
cost. See
`inputs/synthetic_transcript_checkpoint_claude_scores.csv`.

A separate 10-call synthetic validation set was scored once with the prompt
frozen at version 1.2. Its reference labels were not sent to Claude and were
not changed after scoring; all 10 model outputs matched. This is a synthetic
consistency check only, not validation on real transcripts or evidence of
predictive accuracy. See
`inputs/synthetic_transcript_validation_claude_scores.csv`.

## Homework 8 dashboard checkpoint

The dashboard defaults to a 20-row, three-source synthetic checkpoint and
can switch to the existing four-row Yahoo pilot. The synthetic handoffs are
`synthetic_yahoo_finance_variables.csv`,
`synthetic_event_study_results.csv`, and
`synthetic_transcript_features.csv`; they outer-merge on `event_id`, verify
`ticker` and `fiscal_period_end`, and preserve component presence flags. The
dashboard shows `CAR[0,1]` and secondary synthetic CAR windows, alongside the
pilot's separately named ETF-proxy/SPY outcomes.

Financial values, CARs, and classic sentiment fields are generated
placeholders, not actual Yahoo Finance data, Event Study Package results, or
scores calculated from text. The two rubric features in the transcript
handoff reuse Claude Haiku 5.5 Low outputs on the 20 fictional development
calls (prompt 1.2); metadata is recorded and no transcript text is included.
Those same calls were used for prompt tuning, so 20/20 label agreement is not
an independent accuracy estimate. A separate 10-call synthetic validation
set matched 10/10 references once. Source fields identify synthetic inputs,
retrieval fields remain blank, and deliberate missing values stay null. The
dashboard displays overview, coverage, quality checks, and limitations; it
does not estimate returns or fit models.

A separate local-only transcript feature extractor now scores the 20
fictional speaker-labeled mini-call excerpts with the Loughran–McDonald
1993–2025 Master Dictionary. It outputs one event-keyed row per manifest
record, including sentiment, word counts/proportions, management/analyst
sections, and explicit completeness flags. All 20 synthetic fixture excerpts
are scored; separate tests cover incomplete and missing inputs. The
dictionary file is not committed; the extractor
records its version, source, retrieval date, and checksum. This output is not
yet merged into the dashboard handoff, and it is not evidence about real
transcripts or return prediction.

The suggested checkpoint comparison is Yahoo-only, then Yahoo plus classic
sentiment, then additional transcript/AI features. The exact Yahoo fields
should be checked against Gus's myGPT list; Kami should confirm model inputs
and whether the project uses regression, predictive ML, or both. Do not use
a return overlapping `CAR[0,1]` as a predictor. The standardized checkpoint
schema does not replace the longer-horizon final design in `PROPOSAL.md`.
Regenerate all fixtures with `python code/build_synthetic_checkpoint.py`.
No 500-company sample or real transcript-feature merge has been built.

### Synthetic final-shape dataset and Results tab (Nov 14, 2026)

`code/build_synthetic_final_dataset.py` generates 500 invented calls
(`SYN001`-`SYN500`) with every variable in `ANALYSIS_PLAN.md`, writes the
variable dictionary, and runs the plan's three nested OLS models on
`CAR[0,1]` (same complete-case sample, chronological ~60/40 split on a date
boundary). The dashboard's **Results (checkpoint)** tab displays those outputs
under a synthetic banner. Relationships are planted by the generator, so the
results show the analysis layout only. `car_final_20s_pct` (the final-study
outcome) is in the file but not used by the checkpoint models.
`sentiment_gap` stays in the dataset but is excluded from the regressions,
because it equals management minus analyst sentiment exactly (perfect
collinearity). The real merged file should replace
`outputs/synthetic_final_dataset.csv` with the same columns.

## Existing implementation

The four-firm AAPL/MSFT/TSLA/NVDA Yahoo Finance pilot, CSV, dashboard, audit,
and 18 unit tests validate pipeline behavior only. The pipeline now
computes the SPY buy-and-hold comparison and ETF-proxy abnormal returns using
252 pre-event observations. It reports the announcement reaction separately
and starts forward windows after that session. A tested OLS helper now
compares baseline and language-augmented models on the same chronological
60/40 split; it has not been run on real cohort data. The refreshed CSV
contains four complete 20-session pilot rows; one 60-session ETF-proxy
horizon is still missing and is retained as missing. The event manifest is
empty, so the pilot is not the S&P 500 Q2 cohort and no transcript scores are
included.

## Next actions

1. Ask the course lead/library to check FactSet Academic access and transcript
   reuse rights; alternatively request written permission from a provider.
   Quartr's mobile-app terms do not by themselves authorize retention or
   external-model input.
2. Populate `inputs/q2_2026_events_template.csv` from verified fiscal-quarter
   period-end, EPS, and timestamp sources. Do not treat Yahoo's report date as
   a verified fiscal-quarter end.
3. Ask the course lead/library for written guidance on Microsoft transcript
   retention/model-input rights, and verify any institutional license. Continue
   the 10–20-call audit only through a permitted access route; distinguish
   candidate listings from verified usable coverage. Treat the audit as a
   feasibility check, not a sufficient prediction sample. If broader coverage
   and text-use rights are authorized, pass the same transcript-covered events
   and language-score columns to `compare_chronological_predictions`;
   otherwise defer the AI comparison.
4. If access or coverage cannot be verified, complete and report the
   quantitative baseline and defer AI scoring.
