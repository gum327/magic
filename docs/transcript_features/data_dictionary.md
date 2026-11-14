# Transcript feature data dictionary

Output: `outputs/synthetic_transcript_text_features.csv`

Each row is one earnings-call event. `event_id` is the primary merge key; the
synthetic IDs match the existing 20-row checkpoint fixtures. The 20 rows are
fictional mini-call excerpts, not real companies or complete calls.

## Identity and quality fields

| Column | Type | Definition |
|---|---|---|
| `event_id` | string | Shared event-level join key. |
| `transcript_id` | string | Identifier for the input transcript record. |
| `ticker` | string | Synthetic ticker in this fixture; use the verified event ticker for authorized data. |
| `company_name` | string | Synthetic company label; not an issuer name. |
| `call_date` | ISO date | Synthetic call date from the existing checkpoint fixture. |
| `fiscal_quarter` | string | Synthetic fiscal-quarter label (`2026Q2`). |
| `fiscal_period_end` | ISO date | Synthetic quarter-end date; not a verified company fiscal period. |
| `transcript_status` | category | `complete`, `incomplete_transcript`, or `missing_transcript`. `complete` means the supplied input is complete for its stated scope; in this fixture it means a complete mini-call excerpt with the required speaker sections, not a full issuer transcript. A leading explicit incomplete marker overrides a manifest value of `complete`. Non-complete rows have null feature values. |
| `transcript_input_type` | category | `synthetic` for all rows in this checkpoint. |
| `transcript_source` | string | Synthetic input description; future data should record its authorized source. |
| `transcript_retrieved_at_utc` | string | `not_applicable_synthetic` in the fixture; future data should record the source retrieval timestamp in UTC. |
| `section_status` | category | `complete`, the non-complete transcript status, or semicolon-separated parser flags such as missing sections, unlabeled prefix, or unrecognized speaker labels. Missing sections and any unrecognized speaker identity keep speaker-specific features null. |

## Numeric features

All proportions and sentiment scores are fractions, not percentages. For a
section with `N` alphabetic tokens, a positive proportion is
`positive_word_count / N`; negative and uncertainty proportions use the same
denominator. `transcript_sentiment` is
`(positive_word_count - negative_word_count) / N`, bounded by -1 and +1.
This is a dictionary-based net sentiment density per alphabetic token, not a
positive-versus-negative ratio over dictionary hits and not the separate
management-outlook tone score in the AI-scoring fixture.
Category counts use the Loughran–McDonald 1993–2025 master dictionary
membership columns. A positive flag means a word belongs to the category;
zero and negative-year removal markers do not count as membership.

| Column | Type | Definition |
|---|---|---|
| `transcript_word_count` | integer | ASCII alphabetic tokens across all speaker turns, including operator and Q&A. |
| `positive_word_count` | integer | Tokens flagged positive by the dictionary. |
| `positive_word_proportion` | float | Positive tokens divided by all transcript tokens. |
| `negative_word_count` | integer | Tokens flagged negative by the dictionary. |
| `negative_word_proportion` | float | Negative tokens divided by all transcript tokens. |
| `uncertainty_word_count` | integer | Tokens flagged uncertainty by the dictionary. |
| `uncertainty_word_proportion` | float | Uncertainty tokens divided by all transcript tokens. |
| `sentiment_word_count` | integer | Positive plus negative token counts; helps distinguish no dictionary hits from offsetting counts. |
| `transcript_sentiment` | float | Overall net financial sentiment: `(positive - negative) / transcript_word_count`. |
| `management_prepared_word_count` | integer | Tokens spoken by CEO/CFO before the first analyst turn. |
| `management_prepared_sentiment` | float | `(positive - negative) / section word count` for management prepared remarks. |
| `management_qa_word_count` | integer | Tokens spoken by CEO/CFO after the first analyst turn. |
| `management_qa_sentiment` | float | `(positive - negative) / section word count` for management Q&A responses. |
| `management_word_count` | integer | Tokens across management prepared remarks and Q&A. |
| `management_sentiment` | float | Net financial sentiment across management turns. |
| `analyst_question_word_count` | integer | Tokens in turns labeled `Analyst`. |
| `analyst_question_sentiment` | float | Net financial sentiment in analyst turns. |
| `analyst_question_count` | nullable integer | Punctuation-based question-count proxy: number of question-mark characters (`?`) in analyst-labeled turns, not semantic question segmentation; null if the analyst section is missing or any speaker label is unrecognized. |
| `congratulations_mentioned` | nullable integer | 1 if the exact word “congratulations” appears, otherwise 0; null for incomplete/missing transcripts. |

A score is null for an empty or unavailable section, not zero. A zero score
for a nonempty section means positive and negative dictionary counts balance;
it does not imply that the language is truly neutral. No stemming, negation,
sarcasm, phrase-level context, or speaker-level attribution beyond the
normalized labels is modeled. Unknown speaker names are not guessed to be
management or analysts: overall text sentiment can still be calculated, but
speaker-specific features are null and `section_status` records the issue.

## Team handoff proposal (not yet approved)

The current extractor output has `event_id`, `ticker`, and
`fiscal_period_end`, plus documented `transcript_*` feature names. The
repository's synthetic merger uses `event_id` as the join key and verifies
`ticker` and `fiscal_period_end`. Michelle's dashboard contract in PR #6 is
explicitly a draft: it proposes the composite key, a required `data_status`,
and `lang_*` feature names. The current extractor CSV does not satisfy that
dashboard registry directly.

Recommended minimum shared contract:

- Keep a stable `event_id` as the primary join key in each component, and
  retain uppercase `ticker` plus ISO `fiscal_period_end` as cross-source
  validation fields.
- Keep the public, timezone-aware `earnings_timestamp` from the financial
  event source authoritative; do not derive it from transcript `call_date`.
  The merged event table must carry it.
- Include `data_status` (`synthetic`, `pilot`, or `cohort`) in each handoff,
  leaving synthetic rows explicitly labeled.
- Preserve the extractor's documented `transcript_*` feature names, or add
  an explicit dashboard adapter that maps them to `lang_*`; do not maintain
  two undocumented names for the same measure.

This is a proposal, not a schema change. Until the team approves a contract
and Michelle's registry is adapted, the synthetic event-ID merge is verified,
but direct dashboard loading of this extractor's CSV is not.

## Provenance fields

| Column | Type | Definition |
|---|---|---|
| `dictionary_version` | string | Version label for the local dictionary (default: Loughran–McDonald Master Dictionary 1993–2025). |
| `dictionary_source` | URL | Official dictionary landing page. |
| `dictionary_retrieved_date` | ISO date/string | User-supplied retrieval date for the local dictionary file. |
| `dictionary_sha256` | hex string | Hash of the exact dictionary CSV used. |
| `transcript_feature_method` | string | Declares the normalized positive-minus-negative count formula. |

## References

The dictionary version and category flags are documented on the
[official Notre Dame Loughran–McDonald page](https://sraf.nd.edu/loughranmcdonald-master-dictionary/).
See Loughran and McDonald (2011), “When is a Liability not a Liability?
Textual Analysis, Dictionaries, and 10-Ks,” *The Journal of Finance* 66(1),
35–65, for the financial-dictionary method. The authors state that their
dictionary is free for academic research; the raw CSV is therefore obtained
locally and not committed in this repository.
