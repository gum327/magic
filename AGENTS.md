# Repository instructions

Read `README.md`, `STATUS.md`, and the relevant proposal/audit before changing
the research design or data pipeline. README is the project plan; the
event-level output is not considered final until its definitions and sources
are documented there and in the audit.

## Scope and data integrity

- Keep changes limited to the earnings-event study; do not revive the old WACC
  application or treat its files as project inputs.
- Preserve the pilot as a clearly labeled pipeline check. Do not present its
  four convenience-sample observations as representative findings.
- The target sample is the S&P 500 roster dated June 30, 2026, with fiscal
  quarters ending in calendar Q2 2026. Never substitute current constituents
  without documenting the date and selection rule.
- Distinguish the existing SPY buy-and-hold abnormal returns from the planned
  ETF-proxy factor-adjusted outcome. Do not label ETF proxies as official
  Kenneth French factors.
- Preserve missing, incomplete, or inaccessible observations explicitly;
  never turn them into zero or silently imply full coverage.
- Record sources, retrieval dates, timestamp assumptions, units, and
  transformations. Do not invent data, access, or permissions.

## Transcripts and restricted data

- Do not scrape Seeking Alpha or bypass access controls. Its current terms
  prohibit automated retrieval and restrict reuse; obtain written permission
  before project-scale use.
- For any other transcript provider, check the applicable user/API terms
  before copying, retaining, or sending transcript text to a separate model.
- Do not commit transcript text, licensed data, credentials, or other
  restricted raw material. Store only data the team is authorized to retain.
- Keep AI scoring reproducible: version the model and prompt/rubric, document
  its training-data cutoff, and prevent later information or returns from
  entering the score.

## Development

- Work on the assigned feature branch; never commit directly to `main`, force
  push, or rewrite shared history without approval.
- Run all commands from the repository root and use relative paths.
- Keep the dashboard presentation-only: data collection and estimation belong
  in the pipeline, not in Streamlit code.
- Add assertions or tests for data contracts and silent failure risks.
- Run the smallest relevant test suite after a change. The pilot tests run
  with `python -m unittest discover -s tests`.
- The supported dashboard entry point is
  `streamlit run dashboard/pead_app.py`.
