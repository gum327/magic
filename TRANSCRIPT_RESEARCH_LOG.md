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

## Current result

- Candidate companies recorded: **19**.
- Potential first-party transcript locations aligned to the cohort: **10**
  (nine PDFs and Microsoft's transcript page); HPE's PDF is outside the
  cohort.
- Transcript content verified complete by inspecting the full transcript:
  **0**.
- Transcripts with explicit permission for study retention: **0**.
- Transcripts with explicit permission for external AI input: **0**.
- Authorized pilot records: **0**.
- Aggregate time across earlier research and the November 10 follow-up: **not
  recorded**; session-duration compliance cannot be determined from this log.

Supporting details are in [TRANSCRIPT_SOURCE_AUDIT.csv](./TRANSCRIPT_SOURCE_AUDIT.csv)
and [TRANSCRIPT_PILOT.csv](./TRANSCRIPT_PILOT.csv).
