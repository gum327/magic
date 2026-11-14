# Local transcript feature pipeline

This pipeline computes dictionary-based transcript variables locally. It
makes no Claude, OpenAI, Expected Parrot, or other external AI/API calls.
The inputs are the 20 fictional mini-call excerpts in
`inputs/synthetic_transcript_text_feature_checkpoint.jsonl`; their metadata
is in `inputs/synthetic_transcript_text_feature_manifest.csv`. They are not
real earnings calls or full-length transcripts. All 20 fixture excerpts are
complete for the speaker sections this pipeline measures. Unit tests
separately verify that incomplete and missing inputs keep feature values
null. This local-scoring fixture is separate from the synthetic Claude-prompt
fixture used in `TRANSCRIPT_CHECKPOINT.md`.

## Run

Download the Loughran–McDonald Master Dictionary 1993–2025 CSV from the
[official Notre Dame page](https://sraf.nd.edu/loughranmcdonald-master-dictionary/)
and save it outside Git-tracked files. The authors state that the dictionary
is free for academic research. The dictionary file is not committed here.

From the repository root:

```bash
python code/extract_transcript_features.py \
  --input-jsonl inputs/synthetic_transcript_text_feature_checkpoint.jsonl \
  --manifest-csv inputs/synthetic_transcript_text_feature_manifest.csv \
  --dictionary-csv /path/to/Loughran-McDonald_MasterDictionary_1993-2025.csv \
  --dictionary-retrieved-date 2026-11-13 \
  --output outputs/synthetic_transcript_text_features.csv
```

The output is one row per manifest event, keyed by `event_id`, and includes
`ticker`, `fiscal_period_end`, `company_name`, `call_date`, `fiscal_quarter`,
and `transcript_id`. It contains no transcript text. For approved future
transcripts, keep the text in the authorized local location, create a
metadata-only manifest, and normalize each call to the speaker labels
`Operator`, `CEO`, `CFO`, and `Analyst` before running the extractor. Source-
specific transcript parsing and permission checks are not implemented here.
Unrecognized speaker labels are recorded as a section issue and are never
guessed to be management or analysts; overall sentiment remains available
while speaker-specific scores and analyst-question counts are null.
The manifest records the transcript source and UTC retrieval timestamp; the
dictionary retrieval date is required by the command.

The parser treats management speech before the first `Analyst:` turn as
prepared remarks and management speech after it as Q&A. A section-status
column flags missing or unlabeled sections; it never converts a missing
section to a zero score. Inputs absent from the transcript JSONL remain as
rows with `missing_transcript` status and null features. Duplicate or
unmanifested IDs fail explicitly.
The shared event merger also coalesces `company_name` when more than one
component supplies it and rejects conflicts; the event keys remain
`event_id`, `ticker`, and `fiscal_period_end`.
`analyst_question_count` counts literal question marks in analyst-labeled
turns, not the number of analyst speaker turns. It is a reproducible
punctuation-based proxy, not semantic question segmentation.

## Reproducibility

The output records the dictionary version, official source, retrieval date,
and SHA-256 hash of the local CSV. Tokenization uses ASCII alphabetic word
tokens, uppercase exact dictionary matching, no stemming, and no negation or
phrase handling. The formulae and column definitions are in
[`data_dictionary.md`](data_dictionary.md). Synthetic-only tests run with:

```bash
python -m unittest discover -s tests -p test_transcript_features.py
```

## Checkpoint scope

This validates a local feature-extraction workflow on 20 invented excerpts,
not accuracy on actual calls and not prediction of returns. For any real transcript, verify the provider's retention and research-use
terms before local processing. Under current project instructions, do not send
real transcript text to any external model. AI scoring remains a separate
optional workflow and is disabled in this pipeline.
