import unittest
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from pead_pipeline import calculate_abnormal_returns, calculate_eps_surprise_pct


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


if __name__ == "__main__":
    unittest.main()
