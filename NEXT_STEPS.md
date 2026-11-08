# Next steps for transcript access

## Required before any transcript text is collected or scored

1. **Ask the course lead/library to check institutional access.** Specifically
   ask whether the school has FactSet, LSEG/Refinitiv, Bloomberg, Capital IQ,
   or another service with full historical Q2 2026 earnings-call transcripts.
   Ask for the applicable license terms, not just confirmation that a webpage
   opens.
2. **Get written permission for the intended actions.** Confirm whether the
   team may (a) retrieve full text, (b) retain it during the project, (c) share
   it among team members, and (d) submit it to the named external AI provider
   for analysis. Ask whether outputs/derived scores may be retained and
   reported. Store the written answer/licensing evidence in the project
   records; do not put transcript text or credentials in Git.
3. **Prioritize issuer links already located.** Begin with the issuer-hosted
   sources in `TRANSCRIPT_SOURCE_AUDIT.csv`, while remembering that public
   visibility is not permission. Resolve the fiscal period-end/date gaps for
   Apple, Intel, AT&T, and HPE. Citi's official page lists a PDF, but its
   direct link returned 403 to a metadata-only request; use only the ordinary
   issuer page/browser route if authorized, and do not bypass the response.
4. **If issuer or library permissions are insufficient, request a provider
   license.** Ask Quartr API or another provider for a written educational
   research quote/license that explicitly allows project storage and external
   model input. Quartr Pro MCP's student-plan exclusion means it is not the
   assumed student route. Do not scrape Seeking Alpha.

## Once access and rights are confirmed

5. **Run a metadata-first coverage screen** of 10–20 issuer events from the
   fixed June 30, 2026 S&P roster and calendar-Q2 fiscal period ends. Record
   each event's actual fiscal period end, call date/time, source, transcript
   format, and rights evidence before obtaining text.
6. **Test several authorized records manually.** Confirm that the document
   matches the issuer, fiscal quarter, and call date; check prepared remarks
   and Q&A, speaker labels, page/document completeness, corrected/edited
   labeling, and whether the content is a transcript rather than a summary or
   earnings release.
7. **Document a reproducible retrieval recipe** for the approved source:
   authorized login/API route; query fields (ticker, event date, quarter);
   retrieval date; version/identifier; file format; and validation checks.
   Use official API/UI mechanisms and their documented rate limits. Do not
   automate a consumer interface or store content outside the license scope.
8. **Store only authorized material.** If the license permits retained text,
   keep it in a protected, access-controlled location outside version control.
   Track source IDs, retrieval timestamps, hashes, document version, and
   rights evidence in metadata. If only ephemeral/model-processed use is
   allowed, do not persist raw text and document that constraint.
9. **Create the pilot dataset only from eligible events.** Add a row to
   `TRANSCRIPT_PILOT.csv` only after event alignment, full-call completeness,
   retention permission, and external-AI permission are all verified. If
   fewer than 10 are eligible, report the shortfall and why; do not fill gaps
   with summaries or unauthorized content.
10. **Audit selection bias and analysis feasibility.** Compare included and
    excluded names against all 18+ candidates and the full dated roster;
    report missing transcript rates by source/sector/size where data permit.
    A 10–20 call feasibility pilot is not enough on its own for a stable
    predictive comparison or a 60/40 holdout.

## Until then

- Do not send transcript text to any model.
- Do not claim that a public PDF link is a usable licensed transcript.
- Continue the quantitative return/EPS baseline and preserve transcript
  outcomes as missing/deferred, not zero.
- Record additional source searches and actual time spent in
  `TRANSCRIPT_RESEARCH_LOG.md`.
