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
  forward guidance, 1 for qualitative or directional guidance, and 2 for
  quantitative or time-bounded guidance.

`status` is `scored`, `insufficient_outlook`, or `incomplete_transcript`.
For a complete transcript with no usable outlook, return a null tone, zero
guidance specificity, and `insufficient_outlook`. If the transcript is
incomplete or unreadable, return null for both scores and
`incomplete_transcript`. Missing information must not be converted to a
neutral score.

## Prompt (version 1.0)

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
guidance, 2 quantitative or time-bounded guidance.

status: scored if outlook can be assessed; insufficient_outlook if there is
no usable management outlook; incomplete_transcript if the transcript is
incomplete or unreadable. For insufficient_outlook, use null for
outlook_tone and 0 for guidance_specificity. For incomplete_transcript, use
null for both scores.

Return exactly one JSON object with these keys and no other text:
{"outlook_tone": <integer or null>,
 "guidance_specificity": <integer or null>,
 "status": "<scored|insufficient_outlook|incomplete_transcript>"}

Transcript:
<PASTE ONE SYNTHETIC OR AUTHORIZED TRANSCRIPT HERE>
```

## Synthetic dry run

The following invented example is for checking the prompt and output shape
only. It is not a Claude response and is not based on an issuer transcript.

> Management: Customer demand has strengthened for three consecutive months.
> We now expect full-year revenue growth of 6% to 8%, up from our prior
> expectation of 3% to 5%. We are confident in that range, although currency
> movements may create some volatility.

Illustrative expected output:

```json
{
  "outlook_tone": 2,
  "guidance_specificity": 2,
  "status": "scored"
}
```

## Minimal run log

Keep the run log separate from transcript text. Record the event identifier,
whether the transcript was synthetic or authorized, exact model identifier,
prompt version, run date, account no-training confirmation, status, scores,
and any error. Do not save transcript text, quotations, or model explanations
in the log. Preserve incomplete and failed records as such.

Do not interpret this checkpoint as a predictive test. A 20-call exercise is
only a workflow and coverage feasibility check; the final study requires
authorized coverage, a pinned model and rubric, and the planned chronological
comparison on a shared sample.
