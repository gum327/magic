"""Registry of every dataset the dashboard reads.

This is the single integration point for teammates' outputs. When a teammate
delivers a file (or the team changes an agreed path/column), update the
matching ``DatasetSpec`` here; the dashboard tabs read only through
``load_dataset``. The specs mirror the *proposed* contract in
``docs/DATA_CONTRACT_PROPOSAL.md``, which the team has not yet approved.

The dashboard is presentation-only: nothing here estimates returns or models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"

# Data-status labels, from least to most final. A view shows the least-final
# label among the datasets it draws on.
SYNTHETIC = "synthetic"
PILOT = "pilot"
METADATA = "metadata"
REFERENCE = "reference"
COHORT = "cohort"
STATUS_RANK = {SYNTHETIC: 0, PILOT: 1, METADATA: 2, REFERENCE: 3, COHORT: 4}
STATUS_LABELS = {
    SYNTHETIC: "Synthetic test data",
    PILOT: "Pilot (convenience sample)",
    METADATA: "Metadata only",
    REFERENCE: "Reference input",
    COHORT: "Target-cohort output",
}

# Event join keys proposed in the data contract.
JOIN_KEYS = ("ticker", "fiscal_period_end")
LANGUAGE_FEATURE_PREFIX = "lang_"


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    label: str
    owner: str
    path: Optional[str]  # relative to repo root; None = fixture-only
    required_columns: tuple
    default_status: str
    description: str
    fixture: Optional[str] = None  # file name in tests/fixtures (synthetic only)
    parse_dates: tuple = field(default_factory=tuple)


DATASETS = {
    spec.key: spec
    for spec in [
        DatasetSpec(
            key="roster",
            label="S&P 500 roster (June 30, 2026)",
            owner="Shared input",
            path="inputs/sp500_constituents_20260630.csv",
            required_columns=("Symbol", "Security", "GICS Sector", "roster_date"),
            default_status=REFERENCE,
            description="Archived Wikipedia revision 1361794875; dated research "
            "roster, not an official S&P file.",
        ),
        DatasetSpec(
            key="pilot",
            label="Four-company pilot output",
            owner="Gus (pipeline)",
            path="outputs/pead_sample.csv",
            required_columns=(
                "ticker",
                "earnings_timestamp",
                "earnings_date",
                "eps_surprise_pct",
                "abnormal_20d_return_pct",
            ),
            default_status=PILOT,
            description="Yahoo Finance convenience sample (AAPL, MSFT, NVDA, "
            "TSLA). Validates plumbing only; not evidence for the question.",
        ),
        DatasetSpec(
            key="cohort",
            label="Q2 2026 cohort output",
            owner="Gus (pipeline)",
            path="outputs/q2_2026_cohort.csv",
            required_columns=(
                "ticker",
                "fiscal_period_end",
                "earnings_timestamp",
                "eps_surprise_pct",
                "factor_proxy_announcement_abnormal_return_pct",
                "factor_proxy_abnormal_20d_return_pct",
            ),
            default_status=COHORT,
            description="Pipeline output built from the verified event manifest.",
        ),
        DatasetSpec(
            key="exclusions",
            label="Cohort exclusion log",
            owner="Gus (pipeline)",
            path="outputs/q2_2026_exclusions.csv",
            required_columns=("ticker", "reason"),
            default_status=COHORT,
            description="Proposed: one row per roster firm not in the cohort, "
            "with the reason (e.g. non-Q2 fiscal end, missing EPS).",
        ),
        DatasetSpec(
            key="transcript_screen",
            label="Transcript candidate screen",
            owner="Transcript features & coordination",
            path="inputs/transcript_candidate_screen_q2_2026.csv",
            required_columns=("ticker", "company", "transcript_listing_sources"),
            default_status=METADATA,
            description="Listing leads from a Nov 7, 2026 metadata screen. Not "
            "verified transcripts and not rights-cleared.",
        ),
        DatasetSpec(
            key="transcript_audit",
            label="Transcript access & rights log",
            owner="Transcript features & coordination",
            path="inputs/transcript_access_audit_template.csv",
            required_columns=(
                "ticker",
                "transcript_available",
                "retention_permission",
                "external_model_permission",
            ),
            default_status=METADATA,
            description="Metadata-only coverage and rights log. No transcript text.",
        ),
        DatasetSpec(
            key="features",
            label="Transcript language features",
            owner="Transcript features & coordination",
            path="outputs/transcript_features.csv",
            required_columns=("ticker", "fiscal_period_end", "data_status"),
            default_status=SYNTHETIC,
            description="Proposed: one row per event with lang_* score columns.",
            fixture="synthetic_transcript_features.csv",
        ),
        DatasetSpec(
            key="metrics",
            label="Model comparison metrics",
            owner="Cammy (statistics)",
            path="outputs/model_comparison_metrics.csv",
            required_columns=(
                "model",
                "mae",
                "rmse",
                "out_of_sample_r2",
                "train_n",
                "test_n",
                "data_status",
            ),
            default_status=SYNTHETIC,
            description="Proposed: saved output of compare_chronological_predictions.",
            fixture="synthetic_model_comparison_metrics.csv",
        ),
        DatasetSpec(
            key="holdout",
            label="Holdout predictions",
            owner="Cammy (statistics)",
            path="outputs/holdout_predictions.csv",
            required_columns=(
                "ticker",
                "earnings_timestamp",
                "actual",
                "baseline_prediction",
                "language_model_prediction",
                "data_status",
            ),
            default_status=SYNTHETIC,
            description="Proposed: holdout_predictions frame from the helper.",
            fixture="synthetic_holdout_predictions.csv",
        ),
        DatasetSpec(
            key="synthetic_events",
            label="Synthetic events (fixture only)",
            owner="Dashboard test fixture",
            path=None,
            required_columns=(
                "ticker",
                "fiscal_period_end",
                "factor_proxy_abnormal_20d_return_pct",
                "data_status",
            ),
            default_status=SYNTHETIC,
            description="Random synthetic events used only to preview the "
            "Findings tab. Never a research input.",
            fixture="synthetic_events.csv",
        ),
    ]
}


@dataclass
class LoadedDataset:
    spec: DatasetSpec
    frame: Optional[pd.DataFrame]
    source: str  # "real", "fixture", or "absent"
    path: Optional[Path]
    missing_columns: tuple = ()
    error: Optional[str] = None

    @property
    def available(self) -> bool:
        return self.frame is not None and not self.missing_columns and self.error is None

    @property
    def status(self) -> str:
        """Least-final data status in this dataset.

        A ``data_status`` column overrides the default; fixtures are always
        synthetic regardless of their contents.
        """
        if self.source == "fixture":
            return SYNTHETIC
        if self.frame is not None and "data_status" in self.frame.columns:
            values = self.frame["data_status"].dropna().astype(str).str.lower()
            known = [v for v in values.unique() if v in STATUS_RANK]
            if known:
                return min(known, key=STATUS_RANK.get)
        return self.spec.default_status

    @property
    def n_rows(self) -> Optional[int]:
        return None if self.frame is None else len(self.frame)


def load_dataset(key: str, allow_fixture: bool = False, root: Path = REPO_ROOT) -> LoadedDataset:
    """Load one registered dataset without ever raising.

    Real files always win. Fixtures load only when ``allow_fixture`` is true
    and the real file is absent, and the result is labelled synthetic.
    """
    spec = DATASETS[key]
    real_path = root / spec.path if spec.path else None
    fixture_path = root / "tests" / "fixtures" / spec.fixture if spec.fixture else None
    if real_path is not None and real_path.exists():
        path, source = real_path, "real"
    elif allow_fixture and fixture_path is not None and fixture_path.exists():
        path, source = fixture_path, "fixture"
    else:
        return LoadedDataset(spec, None, "absent", None)

    try:
        frame = pd.read_csv(path)
    except Exception as exc:  # malformed delivery: report, don't crash
        return LoadedDataset(spec, None, source, path, error=str(exc))

    missing = tuple(c for c in spec.required_columns if c not in frame.columns)
    if "ticker" in frame.columns:
        frame["ticker"] = frame["ticker"].astype(str).str.strip().str.upper()
    return LoadedDataset(spec, frame, source, path, missing_columns=missing)


def language_feature_columns(frame: Optional[pd.DataFrame]) -> list:
    if frame is None:
        return []
    return [c for c in frame.columns if c.startswith(LANGUAGE_FEATURE_PREFIX)]


def least_final_status(datasets) -> Optional[str]:
    statuses = [d.status for d in datasets if d.frame is not None]
    return min(statuses, key=STATUS_RANK.get) if statuses else None
