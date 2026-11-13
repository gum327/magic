import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT / "code"))

from data_contract import coverage_table, quality_summary, validate_required_columns
from build_synthetic_checkpoint import build_datasets
from merge_event_datasets import merge_event_datasets


class DashboardDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.synthetic = pd.read_csv(ROOT / "outputs" / "synthetic_checkpoint_dataset.csv")
        cls.pilot = pd.read_csv(ROOT / "outputs" / "pead_sample.csv")
        cls.components = tuple(
            pd.read_csv(ROOT / "outputs" / filename)
            for filename in (
                "synthetic_yahoo_finance_variables.csv",
                "synthetic_event_study_results.csv",
                "synthetic_transcript_features.csv",
            )
        )

    def test_synthetic_dataset_matches_event_schema_and_is_labeled(self):
        validate_required_columns(self.synthetic)
        self.assertEqual(len(self.synthetic), 20)
        self.assertEqual(self.synthetic["ticker"].nunique(), 20)
        self.assertTrue(self.synthetic["ticker"].str.startswith("SYN").all())
        self.assertEqual(set(self.synthetic["record_type"]), {"synthetic"})
        self.assertTrue(self.synthetic["financial_record_present"].all())
        self.assertTrue(self.synthetic["event_study_record_present"].all())
        self.assertTrue(self.synthetic["transcript_record_present"].all())
        self.assertEqual(quality_summary(self.synthetic)["invalid_language_scores"], 0)

    def test_synthetic_eps_surprise_uses_pipeline_definition(self):
        valid = self.synthetic.dropna(subset=["eps_actual", "eps_estimate"])
        expected = (
            (valid["eps_actual"] - valid["eps_estimate"])
            / valid["eps_estimate"].abs()
            * 100
        )
        np.testing.assert_allclose(valid["eps_surprise_pct"], expected)

    def test_missing_values_are_preserved_and_counted(self):
        coverage = coverage_table(self.synthetic).set_index("field")
        self.assertEqual(coverage.loc["eps_surprise_pct", "observed"], 19)
        self.assertEqual(
            coverage.loc["car_0_1_pct", "observed"], 19
        )
        self.assertEqual(coverage.loc["car_0_20_pct", "observed"], 16)
        self.assertTrue(self.synthetic["car_0_20_pct"].isna().any())

    def test_quality_checks_detect_invalid_scores_and_duplicate_event_keys(self):
        data = self.synthetic.copy()
        data.loc[0, "language_outlook_tone"] = 3
        data.loc[1, "event_id"] = data.loc[0, "event_id"]
        quality = quality_summary(data)
        self.assertEqual(quality["invalid_language_scores"], 1)
        self.assertEqual(quality["duplicate_event_rows"], 2)

    def test_pilot_without_language_columns_reports_zero_language_coverage(self):
        validate_required_columns(self.pilot)
        coverage = coverage_table(self.pilot).set_index("field")
        self.assertEqual(coverage.loc["language_outlook_tone", "observed"], 0)
        self.assertFalse(coverage.loc["language_outlook_tone", "field_present"])
        quality = quality_summary(self.pilot)
        self.assertEqual(quality["missing_event_keys"], 0)

    def test_merge_preserves_rows_missing_from_a_component(self):
        financial, event_study, transcript = self.components
        transcript = transcript[transcript["event_id"] != "SYN-002"]
        merged = merge_event_datasets(financial, event_study, transcript)
        row = merged.set_index("event_id").loc["SYN-002"]
        self.assertEqual(len(merged), 20)
        self.assertFalse(row["transcript_record_present"])
        self.assertTrue(pd.isna(row["transcript_sentiment"]))

    def test_merge_rejects_duplicate_or_conflicting_event_ids(self):
        financial, event_study, transcript = self.components
        duplicate = pd.concat([event_study, event_study.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "duplicate event IDs"):
            merge_event_datasets(financial, duplicate, transcript)

        conflict = event_study.copy()
        conflict.loc[0, "ticker"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "Conflicting ticker"):
            merge_event_datasets(financial, conflict, transcript)

        mismatched_id = event_study.copy()
        mismatched_id.loc[0, "event_id"] = "DIFFERENT-ID"
        with self.assertRaisesRegex(ValueError, "multiple event IDs"):
            merge_event_datasets(financial, mismatched_id, transcript)

    def test_fixture_generator_is_reproducible(self):
        first = build_datasets()
        second = build_datasets()
        for first_component, second_component in zip(first, second):
            pd.testing.assert_frame_equal(first_component, second_component)


if __name__ == "__main__":
    unittest.main()
