import unittest
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from pead_pipeline import (
    FACTOR_PROXIES,
    calculate_abnormal_returns,
    calculate_eps_surprise_pct,
    calculate_factor_proxy_returns,
    build_q2_2026_cohort,
    compare_chronological_predictions,
)
import pead_pipeline


class EarningsSurpriseTests(unittest.TestCase):
    def test_surprise_uses_absolute_estimate_denominator(self):
        self.assertAlmostEqual(calculate_eps_surprise_pct(1.2, 1.0), 20.0)
        self.assertAlmostEqual(calculate_eps_surprise_pct(-1.2, -1.0), -20.0)

    def test_zero_estimate_is_missing(self):
        self.assertTrue(np.isnan(calculate_eps_surprise_pct(1.0, 0.0)))


class AbnormalReturnTests(unittest.TestCase):
    def setUp(self):
        self.dates = pd.bdate_range("2025-01-01", periods=70)
        self.stock = pd.Series(100 * (1.01 ** np.arange(70)), index=self.dates)
        self.market = pd.Series(100.0, index=self.dates)

    def test_after_close_announcement_starts_from_that_close(self):
        result = calculate_abnormal_returns(
            self.stock, self.market, pd.Timestamp(self.dates[5], tz="America/New_York")
            + pd.Timedelta(hours=16)
        )
        self.assertAlmostEqual(result[5], ((1.01 ** 5) - 1) * 100)

    def test_pre_market_announcement_uses_previous_close(self):
        event = pd.Timestamp(self.dates[5], tz="America/New_York") + pd.Timedelta(hours=8)
        result = calculate_abnormal_returns(self.stock, self.market, event)
        self.assertAlmostEqual(result[1], 1.0)
        self.assertAlmostEqual(result[5], ((1.01 ** 5) - 1) * 100)

    def test_incomplete_forward_window_is_missing(self):
        result = calculate_abnormal_returns(
            self.stock.iloc[:15],
            self.market.iloc[:15],
            pd.Timestamp(self.dates[10], tz="America/New_York")
            + pd.Timedelta(hours=16),
        )
        self.assertTrue(np.isnan(result[20]))
        self.assertTrue(np.isnan(result[60]))


class FactorProxyReturnTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(42)
        self.dates = pd.bdate_range("2025-01-01", periods=330)
        market = rng.normal(0.0004, 0.008, len(self.dates))
        size = rng.normal(0.0001, 0.003, len(self.dates))
        value = rng.normal(0.0001, 0.003, len(self.dates))
        risk_free = np.full(len(self.dates), 0.00005)
        self.residuals = np.zeros(len(self.dates))

        returns = {
            "BIL": risk_free,
            "SPY": risk_free + market,
            "IWM": risk_free + market + size,
            "IWF": risk_free + market,
            "IWD": risk_free + market + value,
            "stock": risk_free + 0.001 + 0.8 * market + 0.3 * size + 0.2 * value,
        }
        returns["stock"] = returns["stock"] + self.residuals
        self.prices = {
            symbol: pd.Series(
                100 * np.cumprod(1 + daily_returns),
                index=self.dates,
            )
            for symbol, daily_returns in returns.items()
        }
        self.factor_prices = {
            symbol: self.prices[symbol] for symbol in FACTOR_PROXIES
        }

    def test_event_reaction_is_separate_from_forward_horizons(self):
        event_position = 270
        self.residuals[event_position + 1] = 0.02
        self.residuals[event_position + 2 : event_position + 7] = [
            0.001,
            -0.002,
            0.003,
            -0.001,
            0.002,
        ]
        stock_returns = (
            self.prices["stock"].pct_change().fillna(0).to_numpy()
            + self.residuals
        )
        self.prices["stock"] = pd.Series(
            100 * np.cumprod(1 + stock_returns), index=self.dates
        )

        result = calculate_factor_proxy_returns(
            self.prices["stock"],
            self.factor_prices,
            pd.Timestamp(self.dates[event_position], tz="America/New_York")
            + pd.Timedelta(hours=16),
            horizons=(5,),
        )

        self.assertAlmostEqual(
            result["factor_proxy_announcement_abnormal_return_pct"], 2.0, places=6
        )
        self.assertAlmostEqual(result[5], 0.3, places=6)
        self.assertEqual(result["factor_proxy_estimation_nobs"], 252)

    def test_forward_horizon_is_missing_until_fully_observed(self):
        result = calculate_factor_proxy_returns(
            self.prices["stock"],
            self.factor_prices,
            pd.Timestamp(self.dates[-3], tz="America/New_York"),
            horizons=(5,),
        )
        self.assertTrue(np.isnan(result[5]))

    def test_rejects_missing_proxy_series(self):
        with self.assertRaisesRegex(ValueError, "Missing factor proxy"):
            calculate_factor_proxy_returns(
                self.prices["stock"],
                {"SPY": self.prices["SPY"]},
                pd.Timestamp(self.dates[270], tz="America/New_York"),
            )


class Q2CohortValidationTests(unittest.TestCase):
    def setUp(self):
        self.events = pd.DataFrame(
            [
                {
                    "ticker": "AAPL",
                    "fiscal_period_end": "2026-06-30",
                    "earnings_timestamp": "2026-07-30T16:00:00-04:00",
                    "eps_actual": 2.0,
                    "eps_estimate": 1.9,
                    "earnings_source": "verified source",
                    "event_timestamp_source": "verified source",
                }
            ]
        )

    def test_requires_fiscal_period_and_source_manifest(self):
        with self.assertRaisesRegex(ValueError, "missing columns"):
            build_q2_2026_cohort(self.events.drop(columns=["fiscal_period_end"]))

    def test_rejects_non_q2_fiscal_period(self):
        self.events.loc[0, "fiscal_period_end"] = "2026-07-01"
        with self.assertRaisesRegex(ValueError, "calendar Q2 2026"):
            build_q2_2026_cohort(self.events)

    def test_rejects_events_after_as_of_date(self):
        with self.assertRaisesRegex(ValueError, "after the as-of date"):
            build_q2_2026_cohort(self.events, as_of="2026-07-01")

    def test_rejects_events_outside_the_supplied_universe(self):
        with self.assertRaisesRegex(ValueError, "outside the supplied universe"):
            build_q2_2026_cohort(
                self.events,
                universe=pd.DataFrame({"Symbol": ["MSFT"]}),
            )

    def test_rejects_duplicate_firm_quarters(self):
        duplicate = pd.concat([self.events, self.events], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "duplicate ticker/period"):
            build_q2_2026_cohort(duplicate)

    def test_rejects_empty_source_references(self):
        self.events.loc[0, "earnings_source"] = " "
        with self.assertRaisesRegex(ValueError, "empty source reference"):
            build_q2_2026_cohort(self.events)

    def test_builds_cohort_from_verified_manifest(self):
        dates = pd.bdate_range("2025-01-01", "2026-11-30")
        rng = np.random.default_rng(42)
        returns = {
            symbol: rng.normal(0.0002, 0.008, len(dates))
            for symbol in ["BIL", "SPY", "IWM", "IWD", "IWF"]
        }
        returns["AAPL"] = (
            returns["BIL"]
            + 0.0003
            + 0.8 * (returns["SPY"] - returns["BIL"])
            + 0.2 * (returns["IWM"] - returns["SPY"])
            - 0.1 * (returns["IWD"] - returns["IWF"])
            + rng.normal(0, 0.003, len(dates))
        )
        prices = {
            symbol: pd.Series(100 * np.cumprod(1 + values), index=dates)
            for symbol, values in returns.items()
        }

        class FakeTicker:
            def __init__(self, symbol):
                self.symbol = symbol

            def history(self, **kwargs):
                return pd.DataFrame({"Close": prices[self.symbol]})

        with patch.object(pead_pipeline.yf, "Ticker", side_effect=FakeTicker):
            dataset = build_q2_2026_cohort(
                self.events,
                universe=pd.DataFrame({"Symbol": ["AAPL"]}),
                as_of="2026-11-30",
            )

        self.assertEqual(len(dataset), 1)
        self.assertEqual(dataset.loc[0, "ticker"], "AAPL")
        self.assertEqual(dataset.loc[0, "factor_proxy_estimation_nobs"], 252)
        self.assertTrue(np.isfinite(dataset.loc[0, "factor_proxy_abnormal_20d_return_pct"]))
        self.assertEqual(dataset.loc[0, "earnings_source"], "verified source")


class ChronologicalPredictionTests(unittest.TestCase):
    def setUp(self):
        size = 30
        self.events = pd.DataFrame(
            {
                "ticker": ["T{:03d}".format(i) for i in range(size)],
                "earnings_timestamp": pd.date_range(
                    "2026-07-01", periods=size, freq="D", tz="UTC"
                ),
                "eps_surprise_pct": np.linspace(-2, 2, size),
                "factor_proxy_announcement_abnormal_return_pct": np.sin(
                    np.arange(size)
                ),
                "language_tone": np.cos(np.arange(size)),
            }
        )
        self.events["factor_proxy_abnormal_20d_return_pct"] = (
            1
            + 0.3 * self.events["eps_surprise_pct"]
            - 0.5
            * self.events["factor_proxy_announcement_abnormal_return_pct"]
            + 1.2 * self.events["language_tone"]
        )

    def test_compares_both_models_on_same_chronological_holdout(self):
        result = compare_chronological_predictions(
            self.events, language_features=["language_tone"]
        )

        self.assertEqual(result["train_n"], 18)
        self.assertEqual(result["test_n"], 12)
        self.assertLess(result["train_cutoff"], result["test_start"])
        self.assertEqual(len(result["holdout_predictions"]), 12)
        self.assertLess(
            result["metrics"]["with_language"]["mae"],
            result["metrics"]["baseline"]["mae"],
        )

    def test_rejects_missing_prediction_values(self):
        self.events.loc[0, "language_tone"] = np.nan
        with self.assertRaisesRegex(ValueError, "missing required values"):
            compare_chronological_predictions(
                self.events, language_features=["language_tone"]
            )

    def test_rejects_rank_deficient_training_features(self):
        self.events["duplicate_tone"] = self.events["language_tone"]
        with self.assertRaisesRegex(ValueError, "rank deficient"):
            compare_chronological_predictions(
                self.events,
                language_features=["language_tone", "duplicate_tone"],
            )


if __name__ == "__main__":
    unittest.main()
