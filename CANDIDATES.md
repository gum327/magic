# Candidate research designs

These are three versions of the question already in the team proposal. Example
rows from the proposal are hypothetical; the selected design also has a
separate real-data pilot in `outputs/pead_sample.csv`.

## 1. PEAD baseline, then an optional AI extension — selected

- **Question:** Do firms with larger positive EPS surprises earn higher
  benchmark-adjusted returns over the next 5, 20, and 60 trading sessions?
  If transcript coverage permits, do earnings-call signals add predictive
  value?
- **One final-dataset row:** AAPL, 2026-07-30, actual EPS 2.02, estimate 1.89,
  surprise +6.88%, 5-session abnormal return -9.93%, 20-session -9.54%,
  60-session +1.66% (pilot observation; Yahoo Finance).
- **Inputs:** Earnings dates, actual and consensus EPS, adjusted daily stock
  prices, and SPY returns; transcripts and AI scores are optional follow-on
  inputs.
- **Chart sketch:** Average cumulative abnormal returns by earnings-surprise
  quintile; for the small pilot, show event-level surprise versus 20-session
  abnormal return instead of implying meaningful quintiles.
- **First auditor attack:** Survivorship bias and look-ahead from incorrect
  announcement timing, revised consensus data, or AI scores generated with
  information not available at the event.

## 2. Do AI call signals add predictive value?

- **Question:** Among announcements with similar EPS surprises, do call
  sentiment, guidance, or uncertainty scores improve out-of-sample forecasts
  of 20-session abnormal returns?
- **One final-dataset row:** AAPL, 2025 Q1, EPS surprise +8.2%, hypothetical AI
  sentiment 0.75, hypothetical 5-session return +2.1%, 20-session +4.3%, and
  60-session +6.5% (the proposal's illustrative row, not observed data).
- **Inputs:** Candidate 1's inputs plus time-stamped transcripts and a
  documented, reproducible scoring rubric.
- **Chart sketch:** Chronological out-of-sample predicted versus realized
  abnormal returns for a surprise-only model and a surprise-plus-AI model.
- **First auditor attack:** Transcript selection bias, scoring inconsistency,
  and leakage if the model sees later stock performance or future information.

## 3. Announcement-period reaction to surprise magnitude

- **Question:** Does the sign or size of an EPS surprise explain the immediate
  market-adjusted return around the earnings announcement?
- **One final-dataset row:** AAPL, 2026-07-30, EPS surprise +6.88%, and
  announcement-period abnormal return -8.07% (pilot observation; Yahoo
  Finance).
- **Inputs:** Actual and consensus EPS, verified release dates and times, and
  daily or intraday stock and benchmark prices.
- **Chart sketch:** Announcement-period abnormal return by surprise decile,
  with a zero-return reference line.
- **First auditor attack:** Imprecise release timestamps can assign the price
  response to the wrong session; other same-day news can confound the reaction.

## Selection

Candidate 1 is the primary design because it directly tests the proposal's
post-earnings-drift hypothesis and can be built with price and EPS data before
transcript access is confirmed. Candidate 2 remains conditional on reliable
transcript coverage. Candidate 3 is a useful near-term comparison, but does not
answer whether any drift persists after the announcement.
