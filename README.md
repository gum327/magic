Beyond the Earnings Surprise: Can AI Predict Post-Earnings Stock Returns?

Team Magic: Abby Fischler, Gus Maass, Cammy Marks, Michelle Orloff FIN 331: Data Science & AI for Finance, Lehigh University, Fall 2026

Dashboard: <link to Streamlit app or GitHub Page>
Dashboard code: dashboard/app.py
Presentation: presentation/

Status: v0 (Checkpoint 2). The pipeline runs end to end on a small sample. Numbers in outputs/ are preliminary until Checkpoint 3 (full sample).

The question

Do stocks keep drifting in the direction of an earnings surprise after the announcement (post-earnings announcement drift, or PEAD), and does an AI reading of the earnings call predict those returns better than the surprise alone?

Hypotheses

Positive EPS (earnings per share) surprises are followed by positive abnormal returns over the next 5, 20, and 60 trading days; negative surprises by negative ones.
AI-scored management tone adds predictive power. A beat with cautious commentary (e.g. lowered guidance) should drift less than a beat with confident commentary.
The output: one row per firm-earnings announcement

code/05_build_dataset.py writes outputs/final_dataset.csv. This column list is the contract between the data, analysis, and dashboard code. Do not rename or drop a column without updating this table first.

column	meaning
ticker	company ticker
fiscal_qtr	fiscal quarter reported (e.g. 2025Q1)
announce_ts	announcement timestamp (US/Eastern)
timing	BMO (before market open) or AMC (after market close)
day0	first trading day the market could react: same day if BMO, next trading day if AMC
eps_actual, eps_est	reported EPS and consensus estimate as of the announcement
surprise_pct	(eps_actual − eps_est) / abs(eps_est)
surprise_quintile	1 (worst) to 5 (best), sorted within each calendar quarter
car_ann	cumulative abnormal return, days −1 to +1 (the announcement reaction)
car_5, car_20, car_60	cumulative abnormal return, day +2 through +6, +21, +61 (the drift)
mktcap	market cap on day −2, in $ millions
ai_sentiment, ai_guidance, ai_uncertainty	AI scores from the call transcript (blank if no transcript)

Abnormal return = stock return − market return (SPY). Fama-French factor-adjusted returns are a robustness check.

data/sample/final_dataset_FAKE.csv has the same columns with made-up numbers so the dashboard can be built before real data exists.

How to run it
bash
pip install -r requirements.txt
python run_all.py              # rebuilds every file in data/processed/ and outputs/ from scratch
streamlit run dashboard/app.py # opens the dashboard at localhost:8501

run_all.py runs the scripts in code/ in order:

step	script	reads	writes
1	01_get_data.py	data/raw/tickers.csv	data/raw/prices.csv, earnings.csv, factors.csv
2	02_clean_data.py	data/raw/	data/processed/earnings_clean.csv
3	03_calculate_returns.py	data/processed/, data/raw/prices.csv	data/processed/car.csv
4	04_ai_sentiment.py	data/raw/transcripts/	data/processed/ai_scores.csv
5	05_build_dataset.py	data/processed/	outputs/final_dataset.csv
6	06_analysis.py	outputs/final_dataset.csv	outputs/tables/, outputs/figures/

Step 4 calls an AI model and needs an API key in .env (never committed). If no key is set, it skips scoring and loads the saved scores in data/processed/ai_scores.csv, so the rest of the pipeline still reruns.

Data sources
data	source	retrieved
Stock prices, earnings dates, EPS actual and estimate	Yahoo Finance via yfinance	<date>
Market and factor returns	Kenneth French Data Library	<date>
Earnings call transcripts	<source>	<date>
Company universe	<e.g. S&P 100 constituents as of Jan 2021>	<date>

Sample: about 100 large U.S. firms, announcements from 2021 through the last date with a complete 60-day forward window (roughly mid-August 2026).

Method
Assign each announcement to day0 using its BMO/AMC timing.
Compute abnormal returns around and after day0.
Sort announcements into surprise quintiles; compare average drift (car_5, car_20, car_60) across quintiles. PEAD shows up as quintile 5 minus quintile 1 > 0.
Regress drift on surprise, then on surprise + AI scores, with standard errors clustered by announcement date.
Test out of sample: fit on 2021–2024, predict 2025–2026. Compare against the surprise-only model.
Check whether a long-short strategy survives transaction costs.

Every specification we run, including the ones that fail, is logged in specs_tried.md.

Threats to validity
Look-ahead bias. An AMC announcement can't be traded until the next day. Mitigation: day0 uses the timestamp; drift windows start at day +2.
Survivorship bias. Using today's index members drops firms that fell out since 2021. Mitigation: build the universe from constituents as of the start of the sample.
Stale or revised EPS estimates. Yahoo's consensus may not be the estimate available on the announcement day, and coverage is uneven. Mitigation: spot-check a sample against company releases; report coverage in audits/.
Small denominators. surprise_pct explodes when the estimate is near $0. Mitigation: winsorize at 1%/99%; robustness check scaling by share price instead.
LLM leakage. The AI model may already "know" how the stock did after the call. Mitigation: remove ticker, company name, and dates from transcripts before scoring; score with a fixed prompt and rubric saved in the repo.
Factor data lag. The French library updates with a delay, so the latest months may be missing. Mitigation: market-adjusted returns are the main measure; factor-adjusted only where data exists.
Overlapping windows and clustering. Many firms report the same week, so observations are not independent. Mitigation: cluster standard errors by date.
P-hacking. Many windows × many scores = something will look significant by chance. Mitigation: windows and hypotheses fixed in the proposal; every spec logged in specs_tried.md.
Statistical vs. economic significance. A 0.3% drift may vanish after trading costs. Mitigation: report returns net of an assumed cost.
Limited transcripts. The AI test may cover fewer firms or years than the PEAD test. Mitigation: report both samples' sizes and rerun PEAD on the transcript subsample.
Repository layout
text
magic/
├── README.md            # this file
├── STATUS.md            # Checkpoint 1 memo
├── specs_tried.md       # every specification run
├── run_all.py           # rebuilds everything
├── requirements.txt
├── AGENTS.md            # rules for humans and coding agents
├── data/
│   ├── raw/             # downloads (large files git-ignored; 01_get_data.py recreates them)
│   ├── processed/       # cleaned and merged intermediate files
│   └── sample/          # fake and small test data
├── code/                # 01–06 pipeline scripts
├── outputs/
│   ├── final_dataset.csv
│   ├── tables/
│   └── figures/
├── dashboard/app.py
├── audits/              # self-audits and responses to instructor audits
├── presentation/
└── dev/                 # scratch work and the old WACC exercise
Who does what
Role	Name	GitHub	Owns
CEO	Gus	gum327	README, reviewing and merging every pull request, 04_ai_sentiment.py
Developer	Michelle	michelleorloff	02–03, 05–06, run_all.py
Product manager	Cammy	cammymarks	dashboard/app.py
Analyst	Abby	abbyfischler	01_get_data.py, data sources, specs_tried.md

Rules for working in the repo (branches, pull requests, no API keys): see AGENTS.md.

References
Ball, R., & Brown, P. (1968). An empirical evaluation of accounting income numbers. Journal of Accounting Research, 6(2), 159–178.
Bernard, V. L., & Thomas, J. K. (1989). Post-earnings-announcement drift: Delayed price response or risk premium? Journal of Accounting Research, 27, 1–36.
Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. Journal of Financial Economics, 33(1), 3–56.
