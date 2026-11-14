import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from extract_transcript_features import (
    FEATURE_COLUMNS,
    build_feature_dataset,
    extract_transcript_features,
    load_dictionary,
    read_transcript_jsonl,
)
from merge_event_datasets import merge_event_datasets


class TranscriptFeatureTests(unittest.TestCase):
    def setUp(self):
        self.dictionary = {
            "positive": frozenset({"PROFIT", "GROWTH", "STRONG", "IMPROVES"}),
            "negative": frozenset({"LOSSES", "DECLINE"}),
            "uncertainty": frozenset({"RISK", "MAY", "UNCERTAINTY"}),
        }
        self.metadata = {
            "event_id": "SYN-TEST",
            "transcript_id": "SYN-TEST",
            "ticker": "SYNTEST",
            "company_name": "Synthetic Test Company",
            "call_date": "2026-07-20",
            "fiscal_quarter": "2026Q2",
            "fiscal_period_end": "2026-06-30",
            "transcript_status": "complete",
            "transcript_input_type": "synthetic",
            "transcript_source": "Unit-test text",
            "transcript_retrieved_at_utc": "not_applicable_synthetic",
        }
        self.provenance = {
            "dictionary_version": "test",
            "dictionary_source": "unit test",
            "dictionary_retrieved_date": "",
            "dictionary_sha256": "test",
            "transcript_feature_method": "test",
        }

    def test_dictionary_uses_positive_flags_not_negative_removal_years(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dictionary.csv"
            pd.DataFrame(
                {
                    "Word": ["GOOD", "BAD", "REMOVED", "UNCERTAIN", None],
                    "Negative": [0, 2024, -2025, 0, 0],
                    "Positive": [2024, 0, 0, 0, 0],
                    "Uncertainty": [0, 0, 0, 2023, 0],
                }
            ).to_csv(path, index=False)
            dictionary = load_dictionary(path)
        self.assertEqual(dictionary["positive"], {"GOOD"})
        self.assertEqual(dictionary["negative"], {"BAD"})
        self.assertEqual(dictionary["uncertainty"], {"UNCERTAIN"})

    def test_extracts_overall_and_speaker_section_features(self):
        record = {
            "transcript": (
                "CEO: Profit growth is strong. "
                "Analyst: Risk may increase? "
                "CFO: We face losses and uncertainty. "
                "Operator: Congratulations."
            )
        }
        row = extract_transcript_features(
            record, self.metadata, self.dictionary, self.provenance
        )
        self.assertEqual(row["section_status"], "complete")
        self.assertEqual(row["transcript_word_count"], 13)
        self.assertEqual(row["positive_word_count"], 3)
        self.assertEqual(row["negative_word_count"], 1)
        self.assertEqual(row["uncertainty_word_count"], 3)
        self.assertAlmostEqual(row["transcript_sentiment"], 2 / 13)
        self.assertEqual(row["management_prepared_word_count"], 4)
        self.assertAlmostEqual(row["management_prepared_sentiment"], 3 / 4)
        self.assertEqual(row["management_qa_word_count"], 5)
        self.assertAlmostEqual(row["management_qa_sentiment"], -1 / 5)
        self.assertAlmostEqual(row["management_sentiment"], 2 / 9)
        self.assertEqual(row["analyst_question_word_count"], 3)
        self.assertEqual(row["analyst_question_sentiment"], 0)
        self.assertEqual(row["congratulations_mentioned"], 1)
        self.assertFalse(
            any("transcript" in key.lower() and "text" in key.lower() for key in row)
        )

    def test_missing_sections_and_incomplete_transcripts_are_not_zero_filled(self):
        record = {"transcript": "CEO: Growth improves."}
        row = extract_transcript_features(
            record, self.metadata, self.dictionary, self.provenance
        )
        self.assertEqual(
            row["section_status"],
            "missing_analyst_questions;missing_management_qa",
        )
        self.assertIsNone(row["analyst_question_sentiment"])
        self.assertIsNone(row["management_qa_sentiment"])

        incomplete_metadata = dict(self.metadata, transcript_status="incomplete_transcript")
        incomplete = extract_transcript_features(
            record, incomplete_metadata, self.dictionary, self.provenance
        )
        self.assertTrue(all(incomplete[column] is None for column in FEATURE_COLUMNS))

    def test_synthetic_corpus_produces_one_event_keyed_row_per_manifest_record(self):
        with tempfile.TemporaryDirectory() as directory:
            dictionary_path = Path(directory) / "dictionary.csv"
            pd.DataFrame(
                {
                    "Word": ["GROWTH", "STRONG", "IMPROVED", "DECLINE", "RISK"],
                    "Negative": [0, 0, 0, 2024, 0],
                    "Positive": [2024, 2024, 2024, 0, 0],
                    "Uncertainty": [0, 0, 0, 0, 2024],
                }
            ).to_csv(dictionary_path, index=False)
            features = build_feature_dataset(
                ROOT / "inputs" / "synthetic_transcript_checkpoint.jsonl",
                ROOT / "inputs" / "synthetic_transcript_manifest.csv",
                dictionary_path,
            )

        manifest = pd.read_csv(ROOT / "inputs" / "synthetic_transcript_manifest.csv")
        self.assertEqual(len(features), 20)
        self.assertEqual(features["event_id"].tolist(), manifest["event_id"].tolist())
        self.assertEqual(features["transcript_id"].nunique(), 20)
        self.assertEqual(
            features["transcript_status"].value_counts().to_dict(),
            {"complete": 18, "incomplete_transcript": 2},
        )
        financial = pd.read_csv(ROOT / "outputs" / "synthetic_yahoo_finance_variables.csv")
        aligned = features.merge(
            financial[["event_id", "ticker", "fiscal_period_end"]],
            on="event_id",
            suffixes=("_transcript", "_financial"),
            validate="one_to_one",
        )
        self.assertEqual(len(aligned), 20)
        self.assertTrue(
            aligned["ticker_transcript"].equals(aligned["ticker_financial"])
        )
        self.assertTrue(
            aligned["fiscal_period_end_transcript"].equals(
                aligned["fiscal_period_end_financial"]
            )
        )
        event_study = pd.read_csv(
            ROOT / "outputs" / "synthetic_event_study_results.csv"
        )
        merged = merge_event_datasets(financial, event_study, features)
        self.assertEqual(len(merged), 20)
        self.assertEqual(merged["transcript_record_present"].sum(), 20)
        conflicting_names = features.copy()
        conflicting_names.loc[0, "company_name"] = "Wrong Synthetic Name"
        with self.assertRaisesRegex(ValueError, "Conflicting company_name"):
            merge_event_datasets(financial, event_study, conflicting_names)
        complete = features["transcript_status"].eq("complete")
        incomplete = features["transcript_status"].eq("incomplete_transcript")
        self.assertTrue(features.loc[complete, "transcript_sentiment"].notna().all())
        self.assertTrue(features.loc[complete, "section_status"].eq("complete").all())
        self.assertTrue(
            features.loc[incomplete, list(FEATURE_COLUMNS)].isna().all().all()
        )
        self.assertFalse(
            any(
                "transcript" in column.lower() and "text" in column.lower()
                for column in features.columns
            )
        )

    def test_missing_input_transcript_keeps_manifest_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dictionary_path = root / "dictionary.csv"
            pd.DataFrame(
                {
                    "Word": ["GOOD"],
                    "Negative": [0],
                    "Positive": [2024],
                    "Uncertainty": [0],
                }
            ).to_csv(dictionary_path, index=False)
            manifest_path = root / "manifest.csv"
            pd.DataFrame([self.metadata]).to_csv(manifest_path, index=False)
            input_path = root / "empty.jsonl"
            input_path.write_text("", encoding="utf-8")
            features = build_feature_dataset(
                input_path, manifest_path, dictionary_path
            )
        self.assertEqual(len(features), 1)
        self.assertEqual(features.loc[0, "transcript_status"], "missing_transcript")
        self.assertTrue(features.loc[0, list(FEATURE_COLUMNS)].isna().all())

    def test_batch_processes_500_records_without_manual_steps(self):
        source_records = read_transcript_jsonl(
            ROOT / "inputs" / "synthetic_transcript_checkpoint.jsonl"
        )
        source_manifest = pd.read_csv(
            ROOT / "inputs" / "synthetic_transcript_manifest.csv"
        ).set_index("transcript_id")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dictionary_path = root / "dictionary.csv"
            pd.DataFrame(
                {
                    "Word": ["GROWTH", "STRONG", "IMPROVED", "DECLINE", "RISK"],
                    "Negative": [0, 0, 0, 2024, 0],
                    "Positive": [2024, 2024, 2024, 0, 0],
                    "Uncertainty": [0, 0, 0, 0, 2024],
                }
            ).to_csv(dictionary_path, index=False)
            manifest_rows = []
            with open(root / "transcripts.jsonl", "w", encoding="utf-8") as output:
                for index in range(500):
                    source_id = "SYN-{:03d}".format(index % 20 + 1)
                    transcript_id = "BATCH-{:04d}".format(index + 1)
                    source = source_records[source_id]
                    metadata = source_manifest.loc[source_id].to_dict()
                    metadata.update(
                        {
                            "event_id": transcript_id,
                            "transcript_id": transcript_id,
                            "ticker": "BATCH{:04d}".format(index + 1),
                        }
                    )
                    manifest_rows.append(metadata)
                    output.write(
                        json.dumps(
                            {
                                "id": transcript_id,
                                "transcript": source["transcript"],
                            }
                        )
                        + "\n"
                    )
            manifest_path = root / "manifest.csv"
            pd.DataFrame(manifest_rows).to_csv(manifest_path, index=False)
            features = build_feature_dataset(
                root / "transcripts.jsonl", manifest_path, dictionary_path
            )
        self.assertEqual(len(features), 500)
        self.assertEqual(features["event_id"].nunique(), 500)


if __name__ == "__main__":
    unittest.main()
