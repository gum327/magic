"""Tests for the Abby event handoff and Michelle dashboard contracts."""

import shutil
import sys
import tempfile
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
from extract_transcript_features import build_dashboard_feature_export
import data_registry as reg  # noqa: E402
import status as st_rules  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"


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

    def test_transcript_handoff_uses_existing_claude_scores_without_text(self):
        transcript = pd.read_csv(
            ROOT / "outputs" / "synthetic_transcript_features.csv"
        )
        scores = pd.read_csv(
            ROOT / "inputs" / "synthetic_transcript_checkpoint_claude_scores.csv"
        )
        merged = transcript.merge(
            scores,
            left_on="event_id",
            right_on="id",
            validate="one_to_one",
        )
        np.testing.assert_allclose(
            merged["language_outlook_tone"],
            merged["outlook_tone"],
            equal_nan=True,
        )
        np.testing.assert_allclose(
            merged["language_guidance_specificity"],
            merged["guidance_specificity"],
            equal_nan=True,
        )
        self.assertTrue(merged["transcript_score_status"].equals(merged["status"]))
        self.assertEqual(set(transcript["language_model"]), {"Claude Haiku 5.5"})
        self.assertEqual(set(transcript["language_effort"]), {"Low"})
        self.assertEqual(set(transcript["language_prompt_version"]), {1.2})
        self.assertEqual(set(transcript["transcript_input_type"]), {"synthetic"})
        self.assertTrue(transcript["language_score_run_date"].notna().all())
        self.assertTrue(transcript["language_fixture_version"].notna().all())
        self.assertTrue(
            transcript["language_score_source"].eq(
                "synthetic_transcript_checkpoint_claude_scores.csv"
            ).all()
        )
        self.assertFalse(any("text" in column.lower() for column in transcript.columns))

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
        data.loc[2, "eps_beat"] = 1 - data.loc[2, "eps_beat"]
        quality = quality_summary(data)
        self.assertEqual(quality["invalid_language_scores"], 1)
        self.assertEqual(quality["duplicate_event_rows"], 2)
        self.assertEqual(quality["eps_beat_mismatches"], 1)

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


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "outputs").mkdir()
        (self.tmp / "tests" / "fixtures").mkdir(parents=True)
        for f in FIXTURES.glob("synthetic_*.csv"):
            shutil.copy(f, self.tmp / "tests" / "fixtures" / f.name)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_absent_file_never_raises(self):
        ds = reg.load_dataset("metrics", root=self.tmp)
        self.assertEqual(ds.source, "absent")
        self.assertFalse(ds.available)
        self.assertIsNone(ds.frame)

    def test_fixtures_load_only_when_allowed_and_are_synthetic(self):
        self.assertEqual(reg.load_dataset("metrics", root=self.tmp).source, "absent")
        ds = reg.load_dataset("metrics", allow_fixture=True, root=self.tmp)
        self.assertEqual(ds.source, "fixture")
        self.assertEqual(ds.status, reg.SYNTHETIC)
        self.assertTrue(ds.available)

    def test_real_file_takes_priority_over_fixture(self):
        frame = pd.read_csv(FIXTURES / "synthetic_model_comparison_metrics.csv")
        frame["data_status"] = "cohort"
        frame.to_csv(self.tmp / "outputs" / "model_comparison_metrics.csv", index=False)
        ds = reg.load_dataset("metrics", allow_fixture=True, root=self.tmp)
        self.assertEqual(ds.source, "real")
        self.assertEqual(ds.status, reg.COHORT)

    def test_fixture_is_synthetic_even_if_relabelled(self):
        path = self.tmp / "tests" / "fixtures" / "synthetic_model_comparison_metrics.csv"
        frame = pd.read_csv(path)
        frame["data_status"] = "cohort"
        frame.to_csv(path, index=False)
        ds = reg.load_dataset("metrics", allow_fixture=True, root=self.tmp)
        self.assertEqual(ds.status, reg.SYNTHETIC)

    def test_any_synthetic_row_makes_dataset_synthetic(self):
        frame = pd.read_csv(FIXTURES / "synthetic_transcript_features.csv")
        frame.loc[0, "data_status"] = "cohort"
        frame.to_csv(self.tmp / "outputs" / "transcript_features.csv", index=False)
        self.assertEqual(reg.load_dataset("features", root=self.tmp).status, reg.SYNTHETIC)

    def test_abby_feature_adapter_loads_with_dashboard_registry(self):
        features = pd.read_csv(
            ROOT / "outputs" / "synthetic_transcript_text_features.csv"
        )
        export = build_dashboard_feature_export(features, "synthetic")
        export.to_csv(self.tmp / "outputs" / "transcript_features.csv", index=False)
        loaded = reg.load_dataset("features", root=self.tmp)
        self.assertTrue(loaded.available, loaded.missing_columns)
        self.assertEqual(len(loaded.frame), 20)
        self.assertEqual(loaded.status, reg.SYNTHETIC)
        self.assertIn(
            "lang_lm_transcript_sentiment",
            reg.language_feature_columns(loaded.frame),
        )

    def test_missing_required_columns_are_reported(self):
        pd.DataFrame({"model": ["baseline"]}).to_csv(self.tmp / "outputs" / "model_comparison_metrics.csv",
                                                     index=False)
        ds = reg.load_dataset("metrics", root=self.tmp)
        self.assertFalse(ds.available)
        self.assertIn("rmse", ds.missing_columns)

    def test_malformed_file_reports_error(self):
        (self.tmp / "outputs" / "holdout_predictions.csv").write_bytes(b"")
        ds = reg.load_dataset("holdout", root=self.tmp)
        self.assertFalse(ds.available)
        self.assertIsNotNone(ds.error)

    def test_fixture_only_dataset_has_no_real_path(self):
        self.assertIsNone(reg.DATASETS["synthetic_events"].path)
        self.assertEqual(reg.load_dataset("synthetic_events", root=self.tmp).source, "absent")


class FixtureSafetyTests(unittest.TestCase):
    def test_every_fixture_row_is_labelled_synthetic_with_fake_tickers(self):
        files = list(FIXTURES.glob("synthetic_*.csv"))
        self.assertEqual(len(files), 4)
        for path in files:
            frame = pd.read_csv(path)
            self.assertTrue((frame["data_status"] == "synthetic").all(), path.name)
            if "ticker" in frame.columns:
                self.assertTrue(frame["ticker"].str.match(r"^SYN\d{2}$").all(), path.name)

    def test_fixtures_match_registered_contract(self):
        for key, spec in reg.DATASETS.items():
            if spec.fixture:
                frame = pd.read_csv(FIXTURES / spec.fixture)
                missing = set(spec.required_columns) - set(frame.columns)
                self.assertFalse(missing, "{} fixture missing {}".format(key, missing))


class RealInputContractTests(unittest.TestCase):
    """The committed shared inputs must satisfy the dashboard's contract."""

    def test_current_repo_inputs_load(self):
        for key in ("roster", "pilot", "transcript_screen", "transcript_audit"):
            ds = reg.load_dataset(key)
            self.assertTrue(ds.available, "{}: {} {}".format(key, ds.missing_columns, ds.error))


class StatusRuleTests(unittest.TestCase):
    def test_forward_window_not_yet_vs_missing(self):
        event = pd.Timestamp("2026-08-26")
        as_of = pd.Timestamp("2026-11-06")
        self.assertEqual(st_rules.forward_window_status(event, as_of, 60), st_rules.NOT_YET)
        self.assertEqual(st_rules.forward_window_status(event, as_of, 20), st_rules.MISSING)
        self.assertEqual(st_rules.forward_window_status(None, as_of, 20), st_rules.MISSING)

    def test_blank_is_never_available(self):
        row = pd.Series({"ticker": "X", "eps_actual": float("nan"), "earnings_date": "2026-07-01",
                         "retrieved_at_utc": "2026-11-06"})
        self.assertEqual(st_rules.classify_event_value(row, "eps_actual", None, False), st_rules.MISSING)
        self.assertEqual(st_rules.classify_event_value(row, "absent_column", None, False), st_rules.MISSING)

    def test_synthetic_events_never_show_available(self):
        row = pd.Series({"ticker": "SYN01", "eps_actual": 1.0})
        self.assertEqual(st_rules.classify_event_value(row, "eps_actual", None, True), st_rules.SYNTHETIC)

    def test_transcript_rights(self):
        audit = pd.DataFrame({
            "ticker": ["A", "B", "C"],
            "transcript_available": ["yes", "yes", "no transcript listed"],
            "transcript_source": ["IR", "IR", "IR"],
            "retention_permission": ["unknown", "yes - written", "n/a"],
            "external_model_permission": ["unknown", "yes - written", "n/a"],
        })
        screen = pd.DataFrame({"ticker": ["D"]})
        self.assertEqual(st_rules.transcript_status("A", audit, screen)[0], st_rules.RESTRICTED)
        self.assertEqual(st_rules.transcript_status("B", audit, screen)[0], st_rules.AVAILABLE)
        self.assertEqual(st_rules.transcript_status("C", audit, screen)[0], st_rules.MISSING)
        self.assertEqual(st_rules.transcript_status("D", audit, screen)[0], st_rules.PENDING)
        self.assertEqual(st_rules.transcript_status("E", audit, screen)[0], st_rules.PENDING)

    def test_pilot_nvda_60d_is_not_yet_observable(self):
        pilot = reg.load_dataset("pilot").frame
        matrix = st_rules.build_status_matrix(pilot, False)
        cell = matrix[(matrix["ticker"] == "NVDA") & (matrix["field"] == "60-session return")]
        self.assertEqual(cell["status"].iloc[0], st_rules.NOT_YET)
        self.assertEqual(len(matrix), len(pilot) * len(st_rules.MATRIX_COLUMNS))

    def test_funnel_pending_is_none_and_real_zero_is_zero(self):
        roster = reg.load_dataset("roster").frame
        audit = reg.load_dataset("transcript_audit").frame
        funnel = st_rules.coverage_funnel(roster, None, audit, None, None).set_index("stage")["count"]
        self.assertEqual(funnel["Roster stocks (June 30, 2026)"], len(roster))
        self.assertTrue(pd.isna(funnel["Verified Q2 2026 events"]))
        self.assertEqual(funnel["Transcript rights cleared"], 0)

    def test_funnel_ignores_synthetic_features_and_metrics(self):
        feats = pd.read_csv(FIXTURES / "synthetic_transcript_features.csv")
        metrics = pd.read_csv(FIXTURES / "synthetic_model_comparison_metrics.csv")
        funnel = st_rules.coverage_funnel(None, None, None, feats, metrics).set_index("stage")["count"]
        self.assertEqual(funnel["Events with language features"], 0)
        self.assertTrue(pd.isna(funnel["Model sample (train + holdout)"]))


class AppSmokeTests(unittest.TestCase):
    """Render the whole app headlessly with fixtures off and on."""

    def _run(self, fixtures_on):
        try:
            from streamlit.testing.v1 import AppTest
        except ImportError:  # pragma: no cover
            self.skipTest("streamlit not installed")
        app = AppTest.from_file(str(ROOT / "dashboard" / "pead_app.py"), default_timeout=60)
        app.run()
        if fixtures_on:
            app.toggle(key="use_fixtures").set_value(True).run()
        self.assertFalse(app.exception, [e.value for e in app.exception])
        return app

    def test_app_runs_without_fixtures_and_labels_synthetic_outputs(self):
        # outputs/transcript_features.csv is Abby's synthetic handoff, so the
        # banner must appear even with fixtures off.
        app = self._run(False)
        self.assertTrue(any("SYNTHETIC TEST DATA" in e.value for e in app.error))
        self.assertTrue(any("synthetic inputs" in e.value for e in app.error))
        self.assertTrue(any("PILOT DATA" in w.value for w in app.warning))

    def test_app_runs_with_fixtures_and_labels_them(self):
        app = self._run(True)
        self.assertTrue(any("SYNTHETIC TEST DATA" in e.value for e in app.error))
if __name__ == "__main__":
    unittest.main()
