# Transcript sourcing research log

## Scope and reporting rule

This log records the current, short research work blocks separately. The
professor's requested two 3–5-hour sessions have **not** been completed. The
durations below are the observed elapsed time for these work blocks, not an
estimate of prior unscheduled research. Earlier screening facts are carried
forward from the existing dated project trackers; their time spent was not
recorded and is not included in the durations below.

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

## Earlier documented work carried forward

The existing November 7 tracker recorded metadata-only screens for the 16
initial companies, including official event pages with no transcript link for
Amazon, Mastercard, Goldman Sachs, Morgan Stanley, and IBM; unresolved leads
for Apple and Intel; and unknown text-use rights for the located issuer
materials. The prior tracker states Microsoft transcript text was not saved
and only an initial preview was viewed. These statements are carried forward
as project-file evidence; the time for that earlier work was not captured.

## Current result

- Candidate companies recorded: **18**.
- Potential first-party transcript links located: **11**.
- Transcript content verified complete by inspecting the full transcript:
  **0**.
- Transcripts with explicit permission for study retention: **0**.
- Transcripts with explicit permission for external AI input: **0**.
- Authorized pilot records: **0**.
- Professor-requested 3–5-hour sessions completed: **0 of 2**.

Supporting details are in [TRANSCRIPT_SOURCE_AUDIT.csv](./TRANSCRIPT_SOURCE_AUDIT.csv)
and [TRANSCRIPT_PILOT.csv](./TRANSCRIPT_PILOT.csv).
