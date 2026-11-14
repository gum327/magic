# Shared data contract: PROPOSAL (not yet agreed)

**Status:** Draft for team review. Drafted by Michelle (dashboard) on
2026-11-13. Nothing here is final until Gus, Cammy, and the transcript-features
lead approve it. The transcript-features lead coordinates the shared dataset
format, so their decisions override this draft.

**Purpose:** The dashboard needs these files so it can show real results
without being redesigned. It reads them only through
`dashboard/data_registry.py`, so if the team picks different paths or names,
only that file needs to change.

## General conventions

- **Format:** CSV, UTF-8, with a header row. Save it in `outputs/` and run
  everything from the repo root.
- **Event key:** `ticker` + `fiscal_period_end`.
  - `ticker` is uppercase and matches `Symbol` in
    `inputs/sp500_constituents_20260630.csv`.
  - `fiscal_period_end` is formatted `YYYY-MM-DD`.
- **Timestamps:** ISO 8601 with a UTC offset (e.g.
  `2026-07-29T16:00:00-04:00`). Use `*_utc` columns for retrieval or scoring
  times.
- **Returns and surprises:** in **percent** (e.g. `6.88` means 6.88%), as the
  pipeline already does.
- **Missing values:** leave the cell blank. Never write `0`, `-999`, or `NA`
  strings. If you know *why* a value is missing, put it in a status or notes
  column.
- **`data_status` column** (required in every new output). Allowed values:

  | Value | Meaning |
  |---|---|
  | `synthetic` | Generated for testing (e.g. synthetic transcripts) |
  | `pilot` | The convenience-sample check |
  | `cohort` | Target Q2 2026 cohort output |

  The dashboard labels any view that contains even one `synthetic` row as
  synthetic.
- **No restricted content:** no transcript text, licensed raw data, or
  credentials (see `AGENTS.md`).

## Gus: quantitative pipeline

### 1. `outputs/q2_2026_cohort.csv` (already defined by the pipeline)

Use the existing `OUTPUT_COLUMNS` in `code/pead_pipeline.py`. Nothing new is
needed except the additions marked *proposed*.

| Column | Type | Notes |
|---|---|---|
| `ticker`, `fiscal_period_end`, `earnings_timestamp`, `earnings_date` | text/date | Event identity and timing |
| `eps_actual`, `eps_estimate`, `eps_surprise_pct` | number | Surprise in % |
| `factor_proxy_announcement_abnormal_return_pct` | number | Day-0 reaction (baseline feature) |
| `factor_proxy_abnormal_{5,20,60}d_return_pct` | number | 20d is the primary outcome; leave blank if the window is incomplete |
| `announcement_abnormal_return_pct`, `abnormal_{5,20,60}d_return_pct` | number | SPY buy-and-hold robustness check |
| `factor_proxy_model`, `factor_proxy_estimation_nobs` | text/int | Model metadata |
| `retrieved_at_utc`, `earnings_source`, `event_timestamp_source`, `prices_source` | text | Provenance |
| `as_of_date` *(proposed)* | date | Date that forward windows are judged against |
| `outcome_{5,20,60}d_status` *(proposed)* | `complete` / `incomplete_window` / `missing_data` | Replaces the dashboard's weekday estimate of "not yet observable" |
| `data_status` *(proposed)* | `cohort` | |

**Also requested:** regenerate `outputs/pead_sample.csv` with the current
schema. It currently lacks `fiscal_period_end` and `event_timestamp_source`.

### 2. `outputs/q2_2026_exclusions.csv` *(proposed, new)*

One row per roster stock that is **not** in the cohort, so the coverage funnel
can explain the gaps.

| Column | Type | Notes |
|---|---|---|
| `ticker` | text | Roster symbol |
| `reason` | text | Short category, e.g. `fiscal_end_not_in_q2_2026`, `no_verified_eps`, `no_timestamp`, `insufficient_price_history` |
| `detail` | text | Optional free text |

## Transcript features and data coordination

### 3. `outputs/transcript_features.csv` *(proposed, new)*

One row per scored event, including events scored from synthetic transcripts.

| Column | Type | Notes |
|---|---|---|
| `ticker`, `fiscal_period_end`, `earnings_timestamp` | key | Must join to the cohort file |
| `lang_<name>` | number | One column per pre-specified score. The `lang_` prefix is how the dashboard finds them. Document each score's scale. |
| `model_id` | text | Pinned snapshot, e.g. `gpt-5.2-2025-12-11` |
| `prompt_version` | text | Versioned rubric/prompt identifier |
| `scored_at_utc` | timestamp | |
| `transcript_source` | text | Source label only; no text |
| `data_status` | `synthetic` / `cohort` | **Required.** Synthetic transcripts must be `synthetic`. |

The existing metadata logs stay as they are:
`inputs/transcript_access_audit_template.csv` and
`inputs/transcript_candidate_screen_q2_2026.csv`. The dashboard counts a
transcript as rights-cleared only when both `retention_permission` and
`external_model_permission` begin with `yes`. Please confirm that wording
convention.

## Cammy: statistical analysis

`compare_chronological_predictions` already returns everything below, but only
in memory. Proposal: save its output to two files.

### 4. `outputs/model_comparison_metrics.csv` *(proposed, new)*

One row per model.

| Column | Type | Notes |
|---|---|---|
| `model` | `baseline` / `with_language` | Exact values the dashboard expects |
| `mae`, `rmse`, `out_of_sample_r2` | number | From `result["metrics"]` |
| `train_n`, `test_n` | int | |
| `train_cutoff`, `test_start` | timestamp | |
| `outcome` | text | e.g. `factor_proxy_abnormal_20d_return_pct` |
| `baseline_features`, `language_features` | text | Semicolon-separated column names |
| `data_status` | `synthetic` / `cohort` | |

### 5. `outputs/holdout_predictions.csv` *(proposed, new)*

This is `result["holdout_predictions"]` plus a status column. Columns:
`ticker`, `earnings_timestamp`, `actual`, `baseline_prediction`,
`language_model_prediction`, `data_status`.

### Open questions for Cammy

- **Small-holdout threshold:** the dashboard labels results **Exploratory**
  when `test_n` < 30. This is a placeholder; what threshold should we use?
- **Uncertainty:** should we add a file for it (e.g. bootstrap intervals for
  the error difference)? If so, agree its columns here first.

## Reference example

`tests/fixtures/` contains **synthetic** examples of files 3–5, generated by
`tests/fixtures/make_synthetic_fixtures.py` using the unmodified pipeline
helper. Use them to check the column layout only. Their values are random and
are not results.
