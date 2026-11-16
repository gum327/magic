# Instructor audit: Team Magic, Checkpoint 2

**Repo:** gum327/magic · **Audited commit:** `3372c54` (2026-11-14 10:52, `main`) · **Seeds:** 2 (post-earnings drift) and 7, as revised in your `PROPOSAL.md`: does earnings-call language predict 20-session post-earnings returns beyond the surprise and the announcement reaction?

> Note from your human teacher: This review is generated with minimal supervision from Opus 5.5-high. It is thorough, but can be too generous at times and doesn't know my taste for what is "good". Grades it and I would assign are correlated, but noisy, ok? If you want additional feedback from _me_, you need to find me before/after/during class or during office hours for a guaranteed speedy reply. I will try to respond to emails and issues, but can not respond to student inquiries around the clock across the final weeks of class. Response times will be unpredictable, though during Thanksgiving week, I will do my best to respond quickly virtually, as in person options will be nil.

## Summary

The pilot on `main` is careful about the things that usually go wrong:
- a dated S&P 500 roster instead of today's list;
- the after-close rule;
- the announcement reaction kept separate from the forward window;
- a pinned LLM snapshot with a pre-cohort cutoff;
- transcript rights checked before use.

All 38 unit tests pass. My independent code reproduces the four pilot events' announcement, 5-session and 20-session returns exactly.

**Scope of this audit:** I audited the `main` branch (`3372c54`, the morning of Nov 14). I know much of your Checkpoint 2 work is on other branches and unmerged pull requests (Gus's 500-event cohort, Abby's transcript export, Michelle's dataset, Cammy's analysis plan, the integration branch), and that work is not reviewed here. Your final project repo needs to have every relevant piece on `main`, because that is what readers, the dashboard and later audits see (A1). The other gaps:
- there is no `specs_tried.md` (A2);
- a one-quarter cohort with a chronological split needs a plan for overlapping return windows (A3).

| Check | Result |
|---|---|
| Reruns from scratch | ⚠️ unit tests pass (38/38). The pilot stopped at Yahoo's earnings-date page, which is blocked in the audit environment (not your bug). An independent recomputation of the four committed events matches |
| Inputs have provenance | ⚠️ the dated roster is excellent (Wikipedia revision `1361794875`). Prices and EPS are pulled live and not saved (A4) |
| Keys unique, merges validated | ✅ manifest validation in `build_q2_2026_cohort` |
| No look-ahead / survivorship | ✅ roster fixed at 2026-06-30. Estimation window ends before the reaction session |
| LLM leakage handled | ✅ planned: `gpt-5.2-2025-12-11`, cutoff Aug 31 2025, before the Q2 2026 cohort. Not run yet |
| `specs_tried.md` complete | ❌ missing on every branch (A2) |
| Magnitudes discussed | ⚠️ not yet (pilot) |
| Hand checks | ✅ unit tests on synthetic fixtures with known answers. The auditor's recomputation below |
| Threats to validity | ✅ self-audit "Remaining threats"; README covers access and rights |
| Every number traces to `outputs/` | ✅ pilot numbers are in `outputs/pead_sample.csv` |

## What holds up

- **Independent recomputation.** My own code uses fresh yfinance prices and your committed release timestamps. It applies the after-close rule, the 252-session estimation window, the ETF proxies (SPY−BIL, IWM−SPY, IWD−IWF), and residuals summed over the sessions after the reaction. It reproduces `outputs/pead_sample.csv` for AAPL, MSFT, NVDA and TSLA:
  - Announcement, 5-session and 20-session factor-proxy CARs, and the SPY buy-and-hold 5/20/60: all match to 0.000 pp. For example, AAPL's 20-session CAR is −1.935, and MSFT's announcement-day CAR is +12.999.
  - The 60-session factor-proxy CAR differs by up to 0.18 pp (MSFT 16.516 vs 16.685). Your own `calculate_factor_proxy_returns` run on my price pull gives my numbers, so this comes from Yahoo revising its data between your 11-06 pull and mine, not from your code (see A4).
- **Seed 2, survivorship:** a dated 503-stock roster from a named Wikipedia revision, kept fixed for the cohort.
- **Seed 2, the after-close day-0 rule:** implemented in both return functions and tested.
- **Seed 7, timestamps:** fiscal period end and release timestamp are required fields in the event manifest.
- **LLM leakage:** a pinned snapshot with a published cutoff before the cohort. You also correctly say a cutoff doesn't prove absence from training.
- **Transcript rights:** documented per source; no scraping of sites whose terms prohibit it. On the unmerged branches, every transcript file I opened is metadata or clearly synthetic.

## Findings

### A1 · Major · `main` doesn't contain all of your work

**Evidence:** This audit covers `main`, which was last updated 2026-11-14 10:52. I know more of your work is on other branches. Five PRs with later CP2 work were open at the deadline:
- #5: Abby's transcript export, Nov 13;
- #9: Michelle's dataset, 10:43;
- #10: Gus's Q2 2026 event list and CAR[0,1] for 500 events, 23:12;
- #8: Cammy's `ANALYSIS_PLAN.md`, 23:31;
- #11: the team integration branch, last pushed 2026-11-15 11:03, after the deadline.

None of that work is reviewed in this audit.

**Why it matters:** The final project repo is judged by what is on `main`. Readers, the dashboard and the next audit all see `main`. Today `main` holds a four-firm pilot, while the 500-event cohort exists only on a branch.

**Fix:** Before the next checkpoint, make sure `main` contains every relevant piece: the code, the cohort data and outputs, the analysis plan, and the dashboard. Merge the integration branch into `main` after resolving conflicts, close the superseded PRs, and make `main` the place where the pipeline runs end to end.

**How to show it's fixed:** `main` contains the cohort files and runs end to end.

### A2 · Major · No `specs_tried.md`

**Evidence:** No `specs_tried.md` exists on `main` or on any branch or PR (searched all refs).

**Why it matters:** Your design is a prediction comparison: a baseline vs. a language-augmented model on a holdout. Which features, horizons and models were tried decides whether the holdout result means anything.

**Fix:** Add `specs_tried.md` now, before the holdout is ever evaluated. List:
- the pre-specified language scores,
- the baseline and augmented formulas,
- the 60/40 split rule,
- the metrics (MAE, RMSE, out-of-sample R²),
- the factor-proxy definitions.

Then log every run.

**How to show it's fixed:** The file exists with dated entries made before the first holdout evaluation.

### A3 · Major · One cohort, overlapping windows: plan the inference

**Evidence:**
- `README.md:45-61`: a single Q2 2026 cohort, sorted by release time, fit on the first 60%, evaluated on the last 40%.
- Releases cluster in late July–August 2026. The 20-session outcome windows of the training events therefore overlap in calendar time with those of the holdout events, and with each other.
- Seed 2's audit list includes "overlapping holding periods in the t-stats".

**Why it matters:** Two consequences:
- Holdout errors are correlated through common market moves, so a difference in MAE or R² between the models needs a standard error that respects that (e.g. a block bootstrap by calendar week, or a Diebold–Mariano test with HAC errors).
- Training outcomes are realized during the holdout's windows. That isn't look-ahead in the features, but say so.

**Fix:** In `specs_tried.md`, before evaluating, state how you'll judge whether the augmented model's improvement is real. Two simple options:
- a bootstrap that resamples release weeks;
- comparing the improvement against a placebo with shuffled language scores.

**How to show it's fixed:** The holdout table reports the improvement with an interval, computed as pre-specified.

### A4 · Minor · Live pulls make reruns drift, and versions aren't pinned

**Evidence:**
- `code/pead_pipeline.py` downloads earnings dates (`get_earnings_dates`, line 258) and prices (`history`, lines 312, 320, 508, 520) on every run, and saves no raw copy.
- Rerun on 2026-11-15, the 60-session factor-proxy CARs moved by up to 0.18 pp.
- `requirements.txt` lists `pandas`, `numpy`, `yfinance`, `lxml` and `streamlit` without versions.
- The tests in `tests/test_dashboard_data.py` require the committed `outputs/pead_sample.csv`. After deleting it to rerun from scratch, 2 of 38 fail until the pipeline has run again.

**Fix:** Save each pull to `data/raw/` with a pull date, and reuse it unless `--refresh` is given. Pin versions with `pip freeze`.

**How to show it's fixed:** Two consecutive runs produce byte-identical outputs.

### A5 · Minor · The forward-window alignment works by an implicit off-by-one

**Evidence:**
- In `calculate_factor_proxy_returns` (`code/pead_pipeline.py:191-249`), `event_position` is a position in `common_prices`, but the windows slice `residuals`, which is indexed by returns and therefore one row shorter.
- So `residuals.iloc[event_position:...]` starts on the session after the reaction, which is what you want, only because exactly one row (the first) is dropped by `pct_change().dropna()`.
- I confirmed the current numbers are right (above). But any change that drops another row (a missing ETF price, a different join) would silently shift every window.

**Fix:** Slice by date: `residuals.loc[residuals.index > event_session].iloc[:horizon]`. Add a unit test where the window must start exactly one session after the reaction.

**How to show it's fixed:** The new test exists and passes.

## How to respond

This audit is `audits/02_instructor_audit.md` in your repo. Fix what you can, then add `audits/03_audit_response.md`, replying to each finding ID: fixed (the commit), disputed (why), or disclosed as a limitation (where).

**Deadline: Saturday, November 21, 2026.**
