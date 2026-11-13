"""Merge event-level financial, event-study, and transcript feature files."""

import argparse
from pathlib import Path

import pandas as pd

EVENT_ID = "event_id"
IDENTITY_COLUMNS = ("ticker", "fiscal_period_end")
COMPONENTS = ("financial", "event_study", "transcript")


def _validate_component(data, name):
    required = {EVENT_ID, *IDENTITY_COLUMNS}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            "{} dataset is missing columns: {}".format(name, ", ".join(sorted(missing)))
        )
    if data[EVENT_ID].isna().any() or data[list(IDENTITY_COLUMNS)].isna().any().any():
        raise ValueError("{} dataset contains missing event identifiers.".format(name))
    if data[EVENT_ID].duplicated().any():
        raise ValueError("{} dataset contains duplicate event IDs.".format(name))
    if data.duplicated(list(IDENTITY_COLUMNS)).any():
        raise ValueError("{} dataset contains duplicate ticker/period rows.".format(name))


def merge_event_datasets(financial, event_study, transcript):
    """Outer-join components and preserve events absent from any component."""
    data = {
        "financial": financial.copy(),
        "event_study": event_study.copy(),
        "transcript": transcript.copy(),
    }
    used_columns = set()
    prepared = []
    for name in COMPONENTS:
        frame = data[name]
        _validate_component(frame, name)
        non_identity = set(frame.columns).difference(
            {EVENT_ID, *IDENTITY_COLUMNS}
        )
        overlaps = used_columns.intersection(non_identity)
        if overlaps:
            raise ValueError(
                "Component columns overlap: {}".format(", ".join(sorted(overlaps)))
            )
        used_columns.update(non_identity)
        frame = frame.rename(
            columns={
                column: "{}__{}".format(column, name)
                for column in IDENTITY_COLUMNS
            }
        )
        frame["{}_record_present".format(name)] = True
        prepared.append(frame)

    merged = prepared[0]
    for frame in prepared[1:]:
        merged = merged.merge(
            frame,
            on=EVENT_ID,
            how="outer",
            validate="one_to_one",
        )

    for column in IDENTITY_COLUMNS:
        source_columns = [
            "{}__{}".format(column, name) for name in COMPONENTS
        ]
        values = merged[source_columns]
        mismatches = values.nunique(axis=1, dropna=True).gt(1)
        if mismatches.any():
            invalid_ids = merged.loc[mismatches, EVENT_ID].astype(str).tolist()
            raise ValueError(
                "Conflicting {} values for event IDs: {}".format(
                    column, ", ".join(invalid_ids)
                )
            )
        merged[column] = values.bfill(axis=1).iloc[:, 0]
        merged = merged.drop(columns=source_columns)

    for name in COMPONENTS:
        presence_column = "{}_record_present".format(name)
        merged[presence_column] = merged[presence_column].fillna(False).astype(bool)
    if merged.duplicated(list(IDENTITY_COLUMNS)).any():
        raise ValueError(
            "Components assign multiple event IDs to the same ticker/period."
        )
    return merged.sort_values(EVENT_ID).reset_index(drop=True)


def merge_event_files(financial_path, event_study_path, transcript_path, output_path):
    merged = merge_event_datasets(
        pd.read_csv(financial_path),
        pd.read_csv(event_study_path),
        pd.read_csv(transcript_path),
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--financial", required=True, help="Event-level Yahoo variables CSV")
    parser.add_argument("--event-study", required=True, help="Event-study results CSV")
    parser.add_argument("--transcript", required=True, help="Transcript features CSV")
    parser.add_argument("--output", required=True, help="Merged event-level output CSV")
    args = parser.parse_args()
    merged = merge_event_files(
        args.financial, args.event_study, args.transcript, args.output
    )
    print("Wrote {} merged event rows to {}".format(len(merged), args.output))


if __name__ == "__main__":
    main()
