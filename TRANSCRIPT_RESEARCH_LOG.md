# Transcript sourcing research log

## Scope and reporting rule

This log records two specifically timed work blocks from the latest
source-verification pass. Their durations are **not** the total time spent on
the transcript investigation. Earlier source screening, browser searches,
issuer-link review, and project-file work took place across prior work periods,
but their durations were not recorded. Therefore this log cannot provide a
reliable aggregate or determine how many 3–5-hour sessions those combined
efforts represent. Do not interpret the timed blocks below as the full effort.

No transcript was transcribed, decoded, summarized, or added to the repository.
No provider credentials were available. A public link or successful HTTP
header check is not treated as license or permission.

## Session 1 — existing audit review and source verification

- **Date/time:** November 7, 2026, 21:29:22–21:31:57 EST.
- **Elapsed time:** 2 minutes 35 seconds.
- **Work:** Read the project README, status, proposal, notebook, repository
  instructions, and both existing metadata trackers. Confirmed the documented
  set of 16 companies and corrected the arithmetic from the file contents:
  the earlier audit had eight transcript PDF links plus Microsoft's transcript
  page (nine first-party links), not nine complete/cleared transcripts.
- **Checks:** Sent HTTP `HEAD` requests (headers only) to the existing company
  source URLs. The linked Alphabet, Meta, Netflix, Bank of America, JPMorgan,
  Coca-Cola, and Visa PDFs returned `200 application/pdf`; issuer event pages
  for Amazon, Mastercard, Microsoft, Goldman Sachs, Morgan Stanley, and IBM
  returned `200 text/html`. Citigroup's issuer quarterly-earnings page had
  previously been checked and lists a Q2 transcript PDF, but the direct PDF
  returned HTTP 403 to the current header request. No retry or access-control
  bypass was attempted.
- **Outcome:** The existing links remain useful source leads. Header responses
  verify link/file availability only, not full transcript completeness, rights,
  or analytical usability.

## Session 2 — source expansion and access/rights checks

- **Date/time:** November 7, 2026, 21:32:00–21:34:54 EST.
- **Elapsed time:** 2 minutes 54 seconds.
- **Work:** Expanded the screen to include AT&T and Hewlett Packard Enterprise.
  Verified both tickers against the archived June 30, 2026 roster. Verified
  direct issuer-hosted Q2 FY2026 transcript PDF links for both from issuer
  search results and checked only response headers; both returned
  `200 application/pdf`. AT&T's search result described an edited 18-page
  transcript. The fiscal-period mapping for AT&T and HPE still needs
  confirmation; HPE's call date and fiscal period-end were not established in
  this work block.
- **Access and terms:** Rechecked Seeking Alpha's terms, Quartr's API and MCP
  product/documentation pages, FactSet's Academic ID request page, and the SEC
  filing search endpoint. Seeking Alpha states use/download is solely for
  personal, non-commercial purposes and requires written permission for
  broader exploitation; no scraping was done. Quartr API terms are contract
  based and separate internal-use and redistribution agreements; the MCP
  documentation requires Quartr Pro and says student plans are not eligible.
  FactSet's page confirms an Academic ID request route only, not the team's
  entitlement or transcript rights. The SEC search endpoint returned 403 in
  this environment; no retry/bypass was attempted.
- **Retrieval boundary:** A prior attempt to fetch AT&T's public PDF returned
  raw encoded PDF bytes in the tool response. The bytes were not decoded,
  transcript text was not reviewed or saved, and no further PDF-body
  retrieval was attempted. This was not an authorization or permission check.
- **Outcome:** The screen now has 18 company candidates and 11 potential
  first-party transcript links (10 PDF links plus Microsoft's page). Rights
  for retention and external AI input remain unestablished. The pilot dataset
  therefore contains zero eligible transcript records.

## Earlier documented work carried forward (duration not recorded)

The prior investigation reviewed the project plan/status/proposal and notebook,
screened 16 initial companies, searched issuer and third-party transcript
leads, and recorded event pages that listed only webcasts or releases as well
as unresolved leads for Apple and Intel. It also checked transcript-page
availability and source terms, including Seeking Alpha restrictions and
possible FactSet/Quartr access routes. The existing trackers report that
Microsoft transcript text was not saved and only an initial preview was
viewed. This earlier work is carried forward as project-file evidence, but
its elapsed time was not captured. The current pass expanded the candidate
screen to 18 companies and 11 potential first-party links as of November 7.

## Session 3 — event alignment and lead verification

- **Date:** November 10, 2026. **Elapsed time:** not recorded.
- **Work:** Rechecked unresolved cohort dates and source leads using issuer
  pages and search-result excerpts. Apple's issuer release confirms fiscal Q3
  ended June 27 and its call was July 30; Intel's official results listing
  confirms Q2 ended June 27 and its call was July 23. The official result
  materials surfaced for both did not provide a verified full transcript.
  AT&T's quarterly index confirms a Q2 transcript with Q&A and prepared
  remarks for its June 30 period end. HPE's issuer listing confirms its fiscal
  Q2 ended April 30, so its PDF is outside the calendar-Q2 cohort. Wells
  Fargo's IR quarterly page and a targeted official-domain search did not
  verify the GuruFocus transcript lead.
- **Retrieval boundary:** No transcript text was retrieved, reviewed, or
  retained during this follow-up. No access-control bypass was attempted.
- **Outcome:** The candidate tracker now has 19 company rows. Ten potential
  first-party transcript locations align to the cohort (nine issuer PDF links
  and Microsoft's IR page); HPE's link is recorded but excluded. Wells Fargo
  remains an unverified third-party lead.

## Session 4 — Hilton and Expedia reconciliation, institutional route

- **Date/time:** November 10, 2026, 11:47:33 EST to about 11:55 EST
  (assisted pass; start and intermediate timestamps from the shell clock).
- **Elapsed time:** about 8 minutes. This is not a 3–5-hour session, and it
  does not complete either requested session.
- **Hilton (HLT):** The roster row is present. Hilton's official
  quarterly-results page lists a Q2 2026 Earnings Call Transcript (PDF). That
  listed URL returned `200 application/pdf` to a HEAD request. An older
  `~/media` URL from search results returned 404 and was not retried. The SEC
  10-Q header (accession 0001585689-26-000043) gives a conformed period of
  2026-06-30 and a fiscal year end of 12/31. The issuer release covers the
  three months ended June 30, 2026 and sets the call for July 28, 2026 at
  9:00 a.m. ET. Cohort-aligned.
- **Expedia (EXPE):** The roster row is present. Expedia's official Q2 2026
  earnings-call event page links a transcript PDF on its IR CDN, which
  returned `200 application/pdf` to HEAD. The fiscal quarter end was verified
  from authoritative sources. The SEC 10-Q header (accession
  0001324424-26-000053, filed 2026-08-06) gives a conformed period of
  2026-06-30 and a fiscal year end of 12/31. The 8-K earnings-release exhibit
  states that the second quarter ended June 30, 2026 and sets the call for
  August 5, 2026 at 1:30 p.m. PT. Cohort-aligned.
- **Terms:** Hilton's IR disclaimer has only an all-rights-reserved notice.
  The hilton.com Site Usage Agreement (October 2025) prohibits copying or
  reproducing site material, and it does not explicitly name ir.hilton.com.
  Expedia Group's website terms (last modified July 22, 2026) limit use to
  personal or internal business use and bar copying. They do not mention AI
  and do not explicitly name ir.expediagroup.com. Neither set of terms grants
  study retention or external-model input.
- **Institutional route:** Lehigh library guides list Bloomberg, Thomson One,
  and WRDS through the Financial Services Lab. None is described there as
  carrying transcripts. Capital IQ, FactSet, and LSEG were not found on the
  checked pages. No database was accessed.
- **Retrieval boundary:** Transcript PDF bodies were not opened. One WebFetch
  of Expedia's earnings-release PDF (not a transcript) cached the binary
  release file in the local tool-results folder outside the repository. Its
  text was not readable, and nothing was added to the repository.
- **Tracker hygiene:** Marked the stale 2026-11-07 Intel row in
  `TRANSCRIPT_SOURCE_AUDIT.csv` as superseded so Intel is counted once.

## Current result

- Candidate companies recorded: **21**.
- Potential first-party transcript locations aligned to the cohort: **12**
  (11 PDFs, including Hilton and Expedia, and Microsoft's transcript page);
  HPE's PDF is outside the cohort. These are posted transcripts, not verified
  complete ones.
- Transcript content verified complete by inspecting the full transcript:
  **0**.
- Transcripts with explicit permission for study retention: **0**.
- Transcripts with explicit permission for external AI input: **0**.
- Authorized pilot records: **0**.
- Aggregate time across earlier research and the first November 10 follow-up:
  **not recorded**. Timed blocks total about 13 minutes (Sessions 1, 2, and 4).
  Neither requested 3–5-hour session is documented as completed.

Supporting details are in [TRANSCRIPT_SOURCE_AUDIT.csv](./TRANSCRIPT_SOURCE_AUDIT.csv)
and [TRANSCRIPT_PILOT.csv](./TRANSCRIPT_PILOT.csv).
