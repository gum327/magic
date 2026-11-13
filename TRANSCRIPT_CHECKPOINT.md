# Transcript-feature checkpoint

## Scope and safeguards

This is a low-cost workflow check, not the final research scoring protocol or
evidence about the S&P 500 cohort. Use synthetic transcripts or, subject to
the safeguard below, up to 20 real transcripts from the professor-provided
licensed dataset.

Professor Bowen's November 13 email permits a checkpoint using fake transcripts
or up to 20 real transcripts from the licensed dataset, with non-Enterprise
Claude, provided queries are not used for training. If using real transcripts,
use only that professor-provided subset, confirm the account's no-training
setting, and send text directly to Claude. Do not use Expected Parrot. Keep raw
files in the authorized location and out of GitHub. If the account setting
cannot be confirmed, continue with synthetic text only.

The final study's proposed model remains the pinned checkpoint documented in
`PROPOSAL.md`; this exploratory Claude checkpoint does not replace it.

## Features for this checkpoint

Score only management's forward-looking statements, not analysts' questions,
historical results, external facts, or market reaction.

- `outlook_tone`: integer from -2 to +2. Use -2 for materially worsening,
  -1 for somewhat worsening, 0 for stable or mixed, +1 for somewhat improving,
  and +2 for materially improving expectations. Use `null` when the transcript
  has no usable management outlook.
- `guidance_specificity`: integer from 0 to 2. Use 0 when management gives no
  forward guidance, 1 for qualitative or directional guidance (even if a
  future period is named), and 2 for numerical guidance such as a target or
  range tied to a period.

`status` is `scored`, `insufficient_outlook`, or `incomplete_transcript`.
For a complete transcript with no usable outlook, return a null tone, zero
guidance specificity, and `insufficient_outlook`. If the transcript is
incomplete or unreadable, return null for both scores and
`incomplete_transcript`. Missing information must not be converted to a
neutral score.

## Prompt (version 1.2)

Use one transcript per request and ask for both scores in that single request.
For a real-data checkpoint, use Claude Haiku directly, not Expected Parrot.
Turn off reasoning or use the lowest setting; if the interface exposes an
output-token limit, start at 128 and increase only if valid JSON is truncated.

```text
Score the management outlook in the single earnings-call transcript below.
Use only this transcript. Do not use outside knowledge, browse, infer stock
returns, or use information learned after the call. Score management
statements, not analysts' views. Do not quote the transcript or include
explanations.

outlook_tone: -2 materially worsening, -1 somewhat worsening, 0 stable or
mixed, +1 somewhat improving, +2 materially improving. Use null if there is
no usable management outlook.

guidance_specificity: 0 no forward guidance, 1 qualitative or directional
guidance even if a future period is named, 2 numerical guidance such as a
target or range tied to a period.

status: scored if outlook can be assessed; insufficient_outlook if there is
no usable management outlook; incomplete_transcript if the transcript is
incomplete or unreadable. For insufficient_outlook, use null for
outlook_tone and 0 for guidance_specificity. For incomplete_transcript, use
null for both scores.

Return exactly one JSON object with these keys and no other text:
{"outlook_tone": <integer or null>,
 "guidance_specificity": <integer or null>,
 "status": "<scored|insufficient_outlook|incomplete_transcript>"}
Use standard ASCII double quotes, not typographic quotes, so the response is
valid JSON. Do not wrap it in a Markdown code fence.

Transcript:
<PASTE ONE SYNTHETIC OR AUTHORIZED TRANSCRIPT HERE>
```

## Single-excerpt dry run

The following invented example is SYN-001 in the 20-excerpt fixture. It is
synthetic and not based on an issuer transcript.

> Management: Customer demand has strengthened for three consecutive months.
> We now expect full-year revenue growth of 6% to 8%, up from our prior
> expectation of 3% to 5%. We are confident in that range, although currency
> movements may create some volatility.

Claude Haiku 5.5 (Low effort) was run twice on November 13, 2026 with the
synthetic example above, first with prompt version 1.0 and then 1.1. Both
runs returned `outlook_tone=2`, `guidance_specificity=2`, and `status=scored`.
The Claude web interface did not expose a maximum-output-token setting. Its
displayed response used typographic quotes even with version 1.1's ASCII-only
instruction, so strict JSON parseability remains unverified. Before a larger
run, manually verify copied output or record the three values directly in the
run log.

Expected scores and status:

```json
{
  "outlook_tone": 2,
  "guidance_specificity": 2,
  "status": "scored"
}
```

Claude Haiku 5.5 (Low effort) was run twice on November 13, 2026 with this
synthetic example, first using prompt version 1.0 and then 1.1. Both runs
returned the expected scores and status. The Claude web interface did not
expose a maximum-output-token setting. Its displayed response used
typographic quotes even with version 1.1's ASCII-only instruction, so strict
JSON parseability remains unverified.

## Twenty-mini-call batch check

The JSONL file contains 20 fictional mini-calls, including improving, stable,
worsening, no-outlook, and explicitly incomplete cases. They can be scored
together in one request as a low-cost format experiment. This batch approach
applies only to these synthetic mini-calls; use one transcript per request for
real transcripts. The mock calls are much shorter than real full-length calls,
so this tests scoring and output format but not real-call token cost.

The first batch exposed ambiguity between qualitative outlooks that name a
future period and numerical guidance. Prompt version 1.2 clarifies that a
period alone does not make qualitative guidance specific. Paste the JSONL
records after this prompt. Do not include
`inputs/synthetic_transcript_expected_scores.csv`.

```text
Score each synthetic call excerpt independently using only its own text.
Apply these definitions: outlook_tone is -2 to +2 or null;
guidance_specificity is 0 for no forward guidance, 1 for qualitative or
directional guidance even if a future period is named, and 2 for numerical
guidance such as a target or range tied to a period; status is scored,
insufficient_outlook, or incomplete_transcript. For a complete excerpt with
no usable outlook, return null, 0, insufficient_outlook. For an explicitly
incomplete excerpt, return null, null, incomplete_transcript.

Return exactly one TSV header and one row per ID, with these columns:
id<TAB>outlook_tone<TAB>guidance_specificity<TAB>status
Use null for null values. Do not use quotes, code fences, explanations, or
extra rows.

Synthetic excerpts:
<PASTE THE CONTENTS OF inputs/synthetic_transcript_checkpoint.jsonl HERE>
```

Compare Claude's rows with the separate expected-score CSV. Record
disagreements, incorrect IDs, missing rows, and output-format errors. Agreement
on invented excerpts is not evidence of predictive validity.

On November 13, 2026, Claude Haiku 5.5 at Low effort scored all 20 expanded
mock calls using prompt version 1.2. The output is saved in
`inputs/synthetic_transcript_checkpoint_claude_scores.csv` and matches all 20
reference rows. The rubric and two reference labels were clarified after the
earlier short-excerpt batch, then the same examples were expanded and run
again; this 20/20 agreement is a prompt-debugging result, not an independent
accuracy estimate. The web interface did not expose a maximum-output-token
setting.

## Minimal run log

Keep the run log separate from transcript text. Record the event identifier,
whether the transcript was synthetic or authorized, model/version shown by the
client (and exact API model identifier if available), prompt version, run date,
no-training confirmation for real inputs, status, scores, and any error. Do
not save transcript text, quotations, or model explanations in the log.
Preserve incomplete and failed records as such.

Do not interpret this checkpoint as a predictive test. A 20-call exercise is
only a workflow and coverage feasibility check; the final study requires
authorized coverage, a pinned model and rubric, and the planned chronological
comparison on a shared sample.
