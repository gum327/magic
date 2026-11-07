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

A focused metadata screen on November 7, 2026 identified 16 S&P-roster
candidate listings in `inputs/transcript_candidate_screen_q2_2026.csv`.
These are not 16 verified or rights-cleared transcripts. Eight first-party
transcript PDFs have been located through issuer IR/Q4CDN pages or indexed
first-party links: Alphabet, Bank of America, Coca-Cola, JPMorganChase, Meta,
Netflix, Visa, and Citigroup. [Citi's official quarterly earnings page](https://www.citigroup.com/global/investors/quarterly-earnings)
links its [July 14 Q2 transcript PDF](https://www.citigroup.com/rcs/citigpa/storage/public/2026psqtr2-transcript.pdf);
only the PDF metadata was inspected, with no
transcript text extracted, reviewed, or retained. The Visa IR event page links
its July 28 Q3 PDF directly. Transcript text from the other PDFs was not
reviewed or retained; retention and external-model rights remain unknown.
Microsoft IR displays its Q4 call transcript; only the initial preview was
viewed and no text saved. Thus nine first-party source links are identified,
but zero are cleared for
retention/model input. Amazon's and
Mastercard's official event pages confirm their Q2 calls but list no
transcript; third-party listings remain leads only. Official Goldman Sachs,
Morgan Stanley, and IBM event pages confirm Q2 calls but list no transcript.
The metadata audit now has one row for each of the 16 screened companies.
AAPL and Intel remain unverified at the issuer/source level. Third-party
transcript leads for GS, MS, and IBM are also unverified, although their
issuer call pages were checked. A targeted GS search returned a Yahoo
Finance/Quartr result snippet, but not a verified transcript destination; a
separate Goldman Sachs BDC result was excluded as a different issuer.
The Microsoft Investor Relations page for [FY26 Q4](https://www.microsoft.com/en-us/Investor/events/FY-2026/earnings-fy-2026-q4)
confirms a July 29, 2026 call and displays transcript text; only the initial
preview was viewed, and no transcript text was saved or analyzed. Microsoft's
[website terms](https://www.microsoft.com/en-us/legal/terms-of-use) generally
restrict copying and do not establish permission to retain this transcript or
submit it to an external model. Intel search results identify a Seeking Alpha
transcript listing, but no transcript source page was opened and no text was
retained. Candidate listings and first-party materials are itemized in the
screen and metadata audit files. The attached
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
