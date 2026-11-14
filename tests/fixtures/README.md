# Synthetic dashboard fixtures — NOT research data

Every file in this folder is **synthetic**: random numbers from a fixed seed,
fake tickers (`SYN01`–`SYN40`), and `data_status = synthetic` on every row.
They exist only to build and test the dashboard's Findings tab before the
real outputs from the statistics and transcript-feature workstreams exist.

- Do not copy these files into `outputs/` or cite them anywhere.
- The dashboard loads them only when the sidebar toggle
  **"Preview with synthetic test fixtures"** is switched on, and then labels
  every affected view as synthetic.
- A real file at the registered `outputs/` path always takes priority, so
  integration needs no change here.

Regenerate with `python tests/fixtures/make_synthetic_fixtures.py`.
