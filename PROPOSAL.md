# Beyond the Earnings Surprise
## Can AI help explain post-earnings stock returns?

**A research proposal by Team Magic**  
Abby Fischler · Gus Maass · Cammy Marks · Michelle Orloff

---

### Investment question

When a public company reports earnings that differ from expectations, do its
shares continue to earn abnormal returns in the following weeks? And, if
reliable earnings-call transcripts are available, can language about outlook,
guidance, and uncertainty help explain which firms keep rising and which
reverse?

### Executive summary

This project will test for post-earnings announcement drift (PEAD), the
possibility that stock prices continue moving in the direction of an earnings
surprise after the initial announcement. We will build an event-level dataset
that links quarterly earnings announcements to subsequent benchmark-adjusted
stock returns. The baseline analysis will compare future returns across
earnings-surprise groups and test whether surprise magnitude predicts
subsequent returns.

If sufficient, time-aligned transcripts can be obtained, we will extend the
analysis with consistently defined measures of management sentiment, guidance,
and uncertainty. This extension will be treated as a separate test, not a
substitute for the baseline: transcripts may be incomplete, and generated
scores must not use information that became available after the call.

The deliverable will be a reproducible research pipeline and an interactive
dashboard that explains the sample, methods, results, and limitations. A
four-company Yahoo Finance pilot demonstrates the proposed event-level output
and dashboard flow; it is a feasibility check, not evidence that PEAD exists.

## Why this question matters

Markets react to both reported numbers and investors' expectations. A company
can exceed its consensus earnings estimate while management describes weaker
demand or cautious guidance. If prices adjust gradually, that mismatch may
help explain why some positive surprises are followed by stronger returns
than others.

The project connects course concepts in return measurement, event studies,
benchmark adjustment, statistical inference, predictive modeling, and
out-of-sample evaluation. It also examines a practical question about
responsible AI use in finance: whether text-derived signals improve
predictions beyond information already contained in quantitative earnings
data.

Our primary question is deliberately testable without AI:

> **Do stocks earn abnormal returns after earnings surprises, and does the
> size or direction of the surprise relate to subsequent returns?**

Our secondary, conditional question is:

> **Among announcements with comparable earnings surprises, do
> pre-specified measures of earnings-call sentiment, guidance, or uncertainty
> add out-of-sample predictive value?**

## Hypotheses

1. **Drift:** Firms with more positive earnings surprises will, on average,
   have higher subsequent abnormal returns than firms with more negative
   surprises.
2. **Information in the call (conditional):** If transcript coverage is
   sufficient, call signals will improve out-of-sample predictions beyond an
   earnings-surprise-only baseline.

These are hypotheses to test, not assumed findings. Results may be weak,
unstable, or absent in the proposed sample.

## Data design

### Unit of observation

One row represents **one firm's quarterly earnings announcement**. Each row
links the announcement timestamp and earnings surprise to returns measured
over specified trading sessions after the information became public.

### Proposed sample

- **Period:** Announcements from January 2021 through the latest date for
  which the full 60-trading-session forward-return window is observable.
- **Universe:** Approximately 100 publicly traded U.S. firms, subject to data
  availability. We will define the universe using historical membership or a
  documented point-in-time selection rule where possible, rather than only
  current index constituents.
- **Pilot:** A small convenience sample of AAPL, MSFT, TSLA, and NVDA used to
  validate collection, event timing, return construction, and dashboard
  behavior. The pilot is not representative and will not be used to claim
  statistical significance.

An event is included in the baseline analysis if the firm was publicly traded,
the earnings date and actual and expected EPS can be identified, stock and
benchmark prices are available around the event, and all required forward
return windows can be calculated. Events with a missing or zero EPS estimate
will be excluded from the percentage-surprise measure and counted in the
coverage audit. For the AI extension, a time-aligned transcript must also be
available.

### Proposed final dataset

| Field | Definition | Status |
|---|---|---|
| `ticker` | Firm identifier | Required |
| `earnings_timestamp` | Announcement date and time, with time zone | Required |
| `eps_actual` | Reported quarterly EPS | Required |
| `eps_estimate` | Consensus EPS estimate for the same quarter | Required |
| `eps_surprise_pct` | `(actual - estimate) / abs(estimate) * 100` | Required |
| `announcement_abnormal_return_pct` | Benchmark-adjusted return for the announcement reaction | Required |
| `abnormal_5d_return_pct` | Benchmark-adjusted return over five post-event sessions | Required |
| `abnormal_20d_return_pct` | Benchmark-adjusted return over 20 post-event sessions | Required |
| `abnormal_60d_return_pct` | Benchmark-adjusted return over 60 post-event sessions | Required |
| `benchmark` | Benchmark or factor model used | Required |
| `market_cap`, `industry` | Firm controls and grouping variables | Desired |
| `transcript_id`, `sentiment_score` | Transcript reference and reproducible score | Conditional |
| `guidance_score`, `uncertainty_score` | Rubric-based management language measures | Conditional |
| `source`, `retrieved_at` | Provenance and retrieval timestamp | Required |

The team will also retain event-level raw inputs, including original EPS
records, price histories, benchmark or factor returns, timestamp evidence, and
transcripts where permitted. Processed data and analysis outputs will be
separate from raw inputs so that transformations can be reviewed and
reproduced.

### Sources and collection plan

The pilot uses Yahoo Finance through `yfinance` for earnings dates, EPS
estimates and reports, and adjusted daily prices. This provides a rapid
prototype, but its historical coverage, consensus definitions, and event
timestamps need to be independently checked before making research claims.

For the larger study, we will audit coverage and seek the most consistent
available sources for historical earnings surprises and announcement times.
Potential sources include licensed academic/financial databases available
through the course or institution, company investor-relations releases, and
other documented public datasets. We will use the Kenneth French Data Library
for market and risk-factor returns if those factors are selected for the
abnormal-return model. We will record each field's source, retrieval date,
definition, and known gaps. We will not imply that data access is secured
before confirming it.

### Raw-input organization

```text
data/
├── raw/
│   ├── company_universe/
│   ├── earnings/
│   ├── prices/
│   ├── factors/
│   └── transcripts/       # only where access and terms permit
├── processed/
│   ├── events.csv
│   └── event_returns.csv
└── sample/
    └── pilot_events.csv
outputs/
├── tables/
└── figures/
audits/
code/
dashboard/
```

Large or licensed raw files will not be committed to the repository. The
project will document retrieval and transformation steps so authorized users
can reproduce the data without redistributing restricted materials.

## Empirical plan

### 1. Validate and construct events

Normalize dates and time zones, match each earnings release to the correct
trading session, and retain an auditable event record. An announcement after
the market close is assigned to the next trading session as the first session
in which investors can trade on the information. Earlier announcements use
that same session. Unknown or ambiguous release times will be flagged and
excluded from the primary timing-sensitive analysis, with a sensitivity
analysis using conservative timing assumptions.

### 2. Measure earnings surprises and returns

The pilot computes percentage EPS surprise as
`(reported EPS - consensus EPS) / abs(consensus EPS)`. Because percentage
surprises can be unstable when expected EPS is near zero, the larger study
will report coverage and test a scaled-surprise alternative where data permit.

The pilot reports adjusted buy-and-hold stock return minus SPY buy-and-hold
return over the same sessions. For the main study, we will compare this
transparent benchmark-adjusted measure with a factor-adjusted event-study
measure, estimated using daily market/factor returns over a pre-event window.
The announcement reaction and subsequent 5-, 20-, and 60-session windows will
be kept distinct and consistently defined.

### 3. Test for drift

- Sort events into earnings-surprise quintiles and plot average cumulative
  abnormal returns by group.
- Compare returns between the highest- and lowest-surprise groups with
  confidence intervals and appropriate tests of mean differences.
- Estimate regressions of subsequent abnormal returns on surprise magnitude,
  adding pre-specified firm and time controls when data support them.
- Account for repeated observations per firm and common event dates in
  inference; document the selected standard-error method.
- Report effect sizes and uncertainty, not only statistical significance.

### 4. Evaluate the AI extension

If transcript coverage is verified, use a fixed rubric to score sentiment,
forward guidance, and uncertainty from the original call text. Preserve
transcript source, call date, and scoring version. A model or human reviewer
must not use later stock returns or post-announcement information when
assigning scores.

Compare a baseline model using earnings surprises and pre-specified controls
with a model adding transcript measures. Evaluate both chronologically
out-of-sample using the same events and report performance differences and
coverage changes. If transcript access or timestamp reliability is inadequate,
defer this extension rather than fill gaps with invented or selectively
available scores.

### 5. Robustness and limitations

We will test alternative return windows and abnormal-return specifications,
inspect sensitivity to event timing, and report how missing observations alter
the sample. We will discuss overlapping return windows, confounding firm news,
survivorship and selection bias, measurement error in consensus expectations,
and the limits of daily prices for isolating the immediate announcement
reaction. Any strategy interpretation will be separated from statistical
association and will not be presented as an investment recommendation.

## Dashboard concept

The dashboard is a research explainer, not a trading tool. It will let users
inspect the sample and methods before exploring the estimated relationships.

```text
┌─────────────────────────────────────────────────────────────────────┐
│ BEYOND THE EARNINGS SURPRISE                         Methods | Data │
│ Do earnings surprises predict post-announcement returns?           │
├──────────────────┬──────────────────┬───────────────────────────────┤
│ Events in sample │ Firms             │ Return model                 │
│ 1,000*            │ ~100*             │ Factor adjusted*             │
├──────────────────┴──────────────────┴───────────────────────────────┤
│ FILTERS: date range [2021–latest]  firm [All]  horizon [20 days]    │
├─────────────────────────────────────┬───────────────────────────────┤
│ Cumulative abnormal return          │ Surprise vs. future return    │
│ by earnings-surprise quintile       │ scatter + fitted relationship │
│                                     │                               │
│       [line chart with CI bands]     │       [event-level points]    │
├─────────────────────────────────────┴───────────────────────────────┤
│ Event explorer: ticker | date | surprise | 5d | 20d | 60d | source  │
├─────────────────────────────────────────────────────────────────────┤
│ AI extension (if available) | Model comparison | Limitations        │
│ Data coverage, timestamp rules, definitions, download/repro steps   │
└─────────────────────────────────────────────────────────────────────┘
```

`*` Values shown here are layout placeholders, not results. The pilot
dashboard currently displays four event rows and an event-level scatter plot;
the quintile chart and model-comparison panel are for the larger-sample
analysis.

## Feasibility, milestones, and decisions

The four-firm pilot has produced complete event-level rows for the latest
events with observable 60-session windows. It demonstrates that the pipeline
and dashboard can be run end to end. Four newer events were skipped because a
full 60-session forward window was not yet available at retrieval. The pilot's
Yahoo data have not been independently validated.

The next work is to confirm a suitable larger-sample data source and
historical universe, audit event-time and EPS coverage, then expand the
pipeline and analysis. Transcript collection and AI scoring remain conditional
on coverage, access, and a defensible point-in-time process.

Key decisions for the project lead are:

1. Which licensed or public source should be the authoritative source for
   historical actual/consensus EPS and announcement timestamps?
2. Is an institutionally accessible historical firm universe available to
   reduce survivorship bias?
3. Should the primary abnormal-return model be a factor model, with SPY
   benchmark-adjusted returns reported as a robustness check?
4. Are transcripts accessible and permitted for this project, or should the
   AI extension be formally deferred?

## Reproducibility

The pilot pipeline, its tests, dashboard, and self-audit are maintained in the
repository. From the repository root:

```bash
python code/pead_pipeline.py
streamlit run dashboard/pead_app.py
```

The pilot file is `outputs/pead_sample.csv`. Its small and convenience-based
nature must be kept visible in any presentation of its values.
