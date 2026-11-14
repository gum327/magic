# Analysis Plan: Earnings Calls and Abnormal Returns

Team Magic

This plan sets out how we will test whether earnings-call language helps explain abnormal stock returns beyond what conventional earnings data already tell us, for S&P 500 companies reporting for the quarter ending in calendar Q2 2026. It covers the outcome, the sample, the three model runs and their variables, and how the models will be evaluated.

## Outcome

For this checkpoint, the outcome (Y) is **CAR[0,1]**: the cumulative abnormal return over the earnings call day and the following day, relative to what a factor model predicts. It is produced by the event study package from the list of tickers and call dates.

This is distinct from the project's final outcome, the cumulative abnormal return over the 20 trading sessions after the announcement-reaction session, which the full analysis will use. At this checkpoint, CAR[0,1] captures the immediate reaction around the call.

## Sample and data

- **Observation:** one company-quarter earnings call.
- **Universe:** S&P 500 constituents as of June 30, 2026, from a dated roster file saved in the repo.
- **Period:** companies with fiscal quarters ending April 1 through June 30, 2026.
- **Same sample in every run:** all three runs use exactly the same events. Events missing any variable are dropped, and we report how many. A missing score is recorded as null, not zero, because zero would be read as a neutral score.
- **Inputs:** (1) the event study dataset, built from tickers and call dates, which supplies CAR[0,1]; (2) Yahoo Finance variables measured as of the call date; (3) a transcript dataset with one row per call. The three are merged on a shared event ID (event ID, ticker, and fiscal period end).

## Approach: three runs, each adding information

We run the same analysis three times on the same sample, adding variables each time. Because each run contains the previous one, any improvement can be credited to the variables added.

### Run 1: Yahoo Finance variables only

We model CAR[0,1] using the earnings surprise and firm characteristics available from Yahoo Finance. Every variable is measured as of the last trading day before the call, using price history through that date and the most recent quarterly financials reported before it.

- **Earnings news:** EPS surprise in dollars and as a percentage (actual minus consensus). Markets price in expectations, so the gap between actual and expected earnings is what should move the stock.
- **Size and valuation:** log market cap, price-to-book, forward P/E. Smaller and higher-valuation firms tend to react differently to the same news, since less is known about them or more is expected of them.
- **Profitability and quality:** profit margin, revenue growth, quarterly earnings growth. Steadier, faster-growing firms may get more credit for a surprise.
- **Leverage:** debt-to-equity. Leveraged firms have more fragile earnings, so news can move them more.
- **Risk and momentum:** beta, 52-week price change, gap between the 50-day and 200-day averages. A stock's usual volatility and prior run-up affect how much of the news is already priced in.
- **Attention and positioning:** average daily volume, short interest as a percentage of float. Liquidity and short interest affect how quickly and how sharply a stock responds.

We exclude announcement-day prices and volumes, which overlap with the outcome. Forward P/E and short interest are available from Yahoo mostly as current snapshots, so they are flagged as limitations and may be dropped.

### Run 2: Run 1 plus basic text measures (no AI)

We add measures computed from the call transcript without AI:

- Overall transcript sentiment
- Management sentiment (prepared remarks)
- Analyst question sentiment
- Sentiment gap (management minus analyst questions), calculated from the two columns above
- Whether "congratulations" is mentioned (yes or no)

Sentiment is intended to be dictionary-based. The scoring method will be documented in the dataset when real transcripts are used. This run shows how much standard text analysis adds beyond the Yahoo Finance baseline.

### Run 3: Run 2 plus AI-extracted measures

We add two variables scored by a language model:

- **Outlook tone:** how positive or negative management's forward-looking statements are
- **Guidance specificity:** how concrete the guidance is

This run shows whether AI-based reading of the call adds predictive power beyond Runs 1 and 2.

## Method

- **Primary method: OLS regression.** It shows which variables matter, in which direction, and by how much. It is also easy to explain, and it suits a sample of this size.
- **Robustness check: a regularized or tree-based model** (ridge regression or random forest) to test whether the added variables improve pure prediction.
- **Evaluation:** sort events by announcement date, fit on the earlier 60%, and evaluate once on the later 40%. For each run we report out-of-sample R-squared, mean absolute error, and root mean squared error.

We fix the variables, models, and the 60/40 split before viewing any results, and we evaluate the later 40% only once. No variables are added or dropped after seeing holdout performance.

## Pipeline sketch

1. Build the event list: tickers and call dates for the sample.
2. Compute CAR[0,1] for each event with the event study package.
3. Collect the Run 1 variables as of the last trading day before each call.
4. Merge in the transcript variables (Runs 2 and 3) by event ID.
5. Sort events by call date and fit each run on the earlier 60%.
6. Evaluate each run once on the later 40% and compare out-of-sample R-squared, MAE, and RMSE.

## Data caveats

- **Synthetic text in v0.** The transcript variables are currently computed on sample and synthetic transcripts to test the pipeline. They are not evidence for the research question. Real transcripts will replace them once access and usage rights are confirmed.
- **Look-ahead bias.** Yahoo Finance reports some fields only as current values. Variables must be rebuilt as of the day before each call, and any that cannot be are dropped or flagged.
- **LLM leakage.** For the AI-extracted variables, the scoring process must not use what the model may already know about how the stock reacted. The prompt and model version are recorded with every score.
