# Transcript access and licensing report

## Bottom line

The source investigation found promising first-party locations, but not a
transcript dataset that is verified complete and licensed for this study.
Nineteen candidate companies are tracked. Ten possible first-party transcript
locations are event-aligned to the calendar-Q2 cohort: nine PDF links and
Microsoft's issuer page. HPE has another issuer PDF, but its quarter ended
April 30 and is outside the cohort. The PDF contents were not reviewed for
completeness, speaker coverage, or omission of sections.
No written license or terms reviewed explicitly authorize retaining the
transcript text for this study and submitting it to an external AI model.
Accordingly, **the number of verified, complete, use-authorized transcripts
is zero**, and no transcript text belongs in the pilot dataset.

## Provider/source comparison

| Route | What was verified | Access/cost status | Retention and external AI |
|---|---|---|---|
| Company investor-relations (IR) pages | Nine calendar-Q2-aligned PDF links remain in scope across Alphabet, AT&T, Bank of America, Citigroup, Coca-Cola, JPMorganChase, Meta, Netflix, and Visa. Microsoft displays transcript text on its IR event page. HPE's issuer PDF is excluded because its fiscal quarter ended April 30. Apple and Intel are aligned events, but official result materials do not provide a verified full transcript. | Ten issuer PDF endpoints were checked: nine returned PDF headers and Citi's file returned 403. The successful group includes HPE, whose event is outside the cohort. No price was listed for the checked materials. | Public listing is not a reuse license. No explicit study retention or external-model permission was established for any issuer source. Obtain written authorization or have counsel/library confirm applicable terms. |
| Seeking Alpha | Public transcript listings were considered as leads; no transcript text was scraped or collected. | Account/paywall/access status for each target call was not tested. No institutional academic entitlement was identified. | Current terms restrict use to personal, non-commercial use and call for written permission for broader exploitation. The terms do not establish this project's transcript retention or external AI rights. Do not scrape. |
| Quartr mobile app | Product advertises transcripts and in-app AI functionality. No transcript was accessed for this project. | The app is advertised as free; that does not imply a research license. | Reviewed consumer terms do not establish project retention or submission to an external model; data-mining and third-party use restrictions apply. |
| Quartr API | Product page advertises first-party live/historical transcripts, speaker identification, filings, and structured data. Terms page separates internal-use and redistribution contracts. | Commercial scoping/demo/contract process; public price not confirmed. No API credentials or team contract were available. | Rights depend on the negotiated contract. A written grant must specifically cover educational research, storage/retention, and external AI/model processing. Not established. |
| Quartr Pro MCP | Documentation offers transcript/document access through an MCP interface. | Requires Quartr Pro; docs say student plans are not eligible. No subscription or login was available. | Individual access does not establish team research retention or permission to send content to another AI provider. Not established. |
| FactSet Academic | An Academic ID request page exists. It does not show the team's transcript entitlement. | University/library access, package coverage, student eligibility, and cost are unknown. No credentials were available. | Transcript-specific and external-model use terms are unknown. Ask the library and FactSet to confirm in writing. |
| SEC EDGAR | Filing-search route investigated. SEC filings may contain earnings releases, 8-K exhibits, presentations, or links; they are not a systematic call-transcript repository. | The search endpoint returned HTTP 403 in this environment. No retry or bypass was attempted. | Do not treat a filing, press release, or webcast as a full earnings-call transcript. Terms and content rights depend on the actual filing/exhibit. |
| Company webcast/audio | Event pages for several issuers link live or replay audio. | A webcast link/replay may require a browser or registration and may expire; access was not tested for transcript content. | Audio availability is not a transcript and does not by itself grant rights to transcribe, retain, or use external speech-to-text/model services. |
| Third-party transcript aggregators | Existing leads mention Motley Fool, AlphaStreet, Decode Investing, Fortune, GuruFocus, Benzinga, Yahoo Finance/Quartr, and other sites. Destination pages and completeness were not systematically verified. | Access, account requirements, academic access, and fees are unknown. | No aggregator's terms were verified as authorizing this study's reuse and external AI input. Check each provider directly before use. |

## Source audit interpretation

`TRANSCRIPT_SOURCE_AUDIT.csv` is one row per investigated company or
provider/access route. “PDF link verified” means only that the issuer-linked
URL responded as a PDF (or was listed by the issuer). It does not mean the PDF
was read, is a complete call transcript, contains all Q&A, is event-aligned,
or can be stored or sent to a model.

The 19 tracked companies are present in the archived June 30, 2026 roster.
Apple and Intel fiscal quarters ended June 27, 2026; AT&T ended June 30, so
these align with calendar Q2. HPE fiscal Q2 ended April 30 and is excluded.
Visa and Microsoft use fiscal-quarter labels other than calendar Q2, but their
stated quarter ends are June 30; preserve fiscal label and period-end
separately. Wells Fargo was added as a company candidate, but only a
third-party transcript search lead was found; its destination is unverified.

## Selection and survivorship limitations

- Companies publishing issuer-hosted transcripts may differ systematically
  from those that publish only audio. A transcript-only sample could select
  for disclosure practice and investor-relations resources.
- Free/public source coverage is incomplete and is not a random subset of the
  S&P roster. Provider licensing may further narrow coverage.
- Large firms and firms with readily indexed English transcripts may be
  overrepresented. Keep the dated roster denominator, all missing cases, and
  source-specific exclusions.
- Fiscal calendars differ. A quarter named Q2 is not necessarily a quarter
  ending in calendar Q2; verify exact period-end dates from issuer filings.
- “Full transcript” should be checked for prepared remarks and Q&A, speaker
  labels, corrected/edited status, and missing pages. Current screening did
  not inspect transcript bodies, so no such completeness claim is possible.
- Use the same transcript-covered events for baseline and augmented models;
  otherwise source availability itself changes the comparison sample.

## Decision

The project is **not ready for AI sentiment analysis**. Continue the
quantitative PEAD baseline and defer transcript scoring until both (1)
event-aligned full transcripts are verified and (2) written terms permit
storage and external AI input. The first operational step is a library/course
lead inquiry about FactSet or another institutional provider; no login
credentials should be sent in chat.
