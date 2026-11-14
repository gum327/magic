"""Contract tests for the synthetic final-shape dataset and checkpoint runs."""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

import build_synthetic_final_dataset as b  # noqa: E402


class SyntheticFinalDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = b.build_dataset()
        cls.runs, cls.coefs, cls.preds = b.run_models(cls.df)

    def test_every_planned_variable_is_present(self):
        for name in b.variable_dictionary()["variable"]:
            self.assertIn(name, self.df.columns)

    def test_rows_are_synthetic_with_fake_tickers_and_unique_ids(self):
        self.assertTrue((self.df["data_status"] == "synthetic").all())
        self.assertTrue(self.df["ticker"].str.startswith("SYN").all())
        self.assertTrue(self.df["event_id"].is_unique)

    def test_missing_scores_are_null_not_zero(self):
        no_transcript = self.df["management_prepared_sentiment"].isna()
        self.assertGreater(no_transcript.sum(), 0)
        self.assertTrue(self.df.loc[no_transcript, "transcript_sentiment"].isna().all())

    def test_sentiment_gap_is_null_if_either_input_is_null(self):
        either = self.df["management_prepared_sentiment"].isna() | self.df["analyst_question_sentiment"].isna()
        self.assertTrue(self.df.loc[either, "sentiment_gap"].isna().all())
        both = ~either
        diff = self.df.loc[both, "management_prepared_sentiment"] - self.df.loc[both, "analyst_question_sentiment"]
        pd.testing.assert_series_equal(self.df.loc[both, "sentiment_gap"], diff.round(3), check_names=False)

    def test_runs_are_nested_and_share_one_sample(self):
        self.assertEqual(self.runs["train_n"].nunique(), 1)
        self.assertEqual(self.runs["test_n"].nunique(), 1)
        sizes = [len(b.run_features(r)) for r in (1, 2, 3)]
        self.assertEqual(sizes, sorted(sizes))
        self.assertTrue(set(b.run_features(1)) < set(b.run_features(2)) < set(b.run_features(3)))
        sample, excluded = b.model_sample(self.df)
        self.assertEqual(len(sample) + excluded, len(self.df))

    def test_split_is_chronological(self):
        first = self.runs.iloc[0]
        self.assertLessEqual(first["train_cutoff"], first["test_start"])

    def test_no_exact_linear_combination_enters_a_run(self):
        self.assertNotIn("sentiment_gap", b.run_features(3))
        sample, _ = b.model_sample(self.df)
        X = sample[b.run_features(3)].to_numpy(dtype=float)
        X = (X - X.mean(0)) / X.std(0)
        self.assertEqual(np.linalg.matrix_rank(X), X.shape[1])

    def test_outcomes_are_not_predictors(self):
        for run in (1, 2, 3):
            self.assertNotIn("car_0_1_pct", b.run_features(run))
            self.assertNotIn("car_final_20s_pct", b.run_features(run))


if __name__ == "__main__":
    unittest.main()
