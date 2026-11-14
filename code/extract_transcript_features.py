"""Extract local dictionary-based features from normalized earnings-call text."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

DICTIONARY_SOURCE = "https://sraf.nd.edu/loughranmcdonald-master-dictionary/"
DICTIONARY_VERSION = "Loughran-McDonald Master Dictionary 1993-2025"
REQUIRED_MANIFEST_COLUMNS = (
    "event_id",
    "transcript_id",
    "ticker",
    "company_name",
    "call_date",
    "fiscal_quarter",
    "fiscal_period_end",
    "transcript_status",
    "transcript_input_type",
    "transcript_source",
    "transcript_retrieved_at_utc",
)
REQUIRED_DICTIONARY_COLUMNS = ("Word", "Negative", "Positive", "Uncertainty")
FEATURE_COLUMNS = (
    "transcript_word_count",
    "positive_word_count",
    "positive_word_proportion",
    "negative_word_count",
    "negative_word_proportion",
    "uncertainty_word_count",
    "uncertainty_word_proportion",
    "sentiment_word_count",
    "transcript_sentiment",
    "management_prepared_word_count",
    "management_prepared_sentiment",
    "management_qa_word_count",
    "management_qa_sentiment",
    "management_word_count",
    "management_sentiment",
    "analyst_question_word_count",
    "analyst_question_sentiment",
    "analyst_question_count",
    "congratulations_mentioned",
)
TOKEN_PATTERN = re.compile(r"[A-Za-z]+")
SPEAKER_PATTERN = re.compile(
    r"(?<!\w)(?P<speaker>[A-Z][A-Za-z0-9.'-]*"
    r"(?:\s+(?:[A-Z][A-Za-z0-9.'-]*|\d+)){0,3}):\s*"
)
INCOMPLETE_MARKER = re.compile(
    r"^\[SYNTHETIC TRANSCRIPT IS INCOMPLETE:[^\]]+\]\s*", re.IGNORECASE
)


def load_dictionary(dictionary_path):
    """Load LM membership flags; negative flag years indicate removals."""
    data = pd.read_csv(dictionary_path)
    missing = set(REQUIRED_DICTIONARY_COLUMNS).difference(data.columns)
    if missing:
        raise ValueError(
            "Dictionary is missing columns: {}".format(", ".join(sorted(missing)))
        )
    words = data["Word"].fillna("").astype(str).str.strip().str.upper()
    blank_words = words.eq("")
    if blank_words.any():
        blank_flags = data.loc[blank_words, list(REQUIRED_DICTIONARY_COLUMNS[1:])]
        blank_flags = blank_flags.apply(pd.to_numeric, errors="coerce").fillna(0)
        if blank_flags.ne(0).any().any():
            raise ValueError("Blank dictionary entries cannot have category flags.")
        data = data.loc[~blank_words].reset_index(drop=True)
        words = words.loc[~blank_words].reset_index(drop=True)
    if words.duplicated().any():
        raise ValueError("Dictionary words must be unique.")

    categories = {}
    for column in ("Negative", "Positive", "Uncertainty"):
        flags = pd.to_numeric(data[column], errors="coerce")
        if (data[column].notna() & flags.isna()).any():
            raise ValueError(
                "Dictionary column {} contains nonnumeric flags.".format(column)
            )
        categories[column.lower()] = frozenset(
            word for word, flag in zip(words, flags.fillna(0)) if flag > 0
        )
    return categories


def _tokens(text):
    return TOKEN_PATTERN.findall(str(text).upper())


def _text_metrics(text, dictionary):
    words = _tokens(text)
    word_count = len(words)
    positive = sum(word in dictionary["positive"] for word in words)
    negative = sum(word in dictionary["negative"] for word in words)
    uncertainty = sum(word in dictionary["uncertainty"] for word in words)
    if word_count == 0:
        return {
            "word_count": None,
            "positive_word_count": None,
            "positive_word_proportion": None,
            "negative_word_count": None,
            "negative_word_proportion": None,
            "uncertainty_word_count": None,
            "uncertainty_word_proportion": None,
            "sentiment_word_count": None,
            "sentiment": None,
        }
    return {
        "word_count": word_count,
        "positive_word_count": positive,
        "positive_word_proportion": positive / word_count,
        "negative_word_count": negative,
        "negative_word_proportion": negative / word_count,
        "uncertainty_word_count": uncertainty,
        "uncertainty_word_proportion": uncertainty / word_count,
        "sentiment_word_count": positive + negative,
        "sentiment": (positive - negative) / word_count,
    }


def _speaker_role(label):
    normalized = " ".join(label.lower().split())
    if normalized in {"operator", "host", "moderator"}:
        return "operator"
    if re.fullmatch(r"analyst(?:\s+\d+)?", normalized):
        return "analyst"
    if normalized in {
        "ceo",
        "cfo",
        "management",
        "executive",
        "chief executive officer",
        "chief financial officer",
    }:
        return "management"
    return "unknown"


def _parse_transcript(text):
    """Split labeled turns; unknown speaker identities are never inferred."""
    clean_text = INCOMPLETE_MARKER.sub("", text.strip())
    matches = list(SPEAKER_PATTERN.finditer(clean_text))
    prefix = clean_text[: matches[0].start()].strip() if matches else clean_text
    turns = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(clean_text)
        label = match.group("speaker")
        role = _speaker_role(label)
        turns.append((role, clean_text[start:end].strip()))

    first_analyst = next(
        (index for index, (role, _) in enumerate(turns) if role == "analyst"),
        None,
    )
    prepared = []
    management_qa = []
    analysts = []
    unknown_speakers = False
    all_text = [prefix] if prefix else []
    for index, (role, turn_text) in enumerate(turns):
        if turn_text:
            all_text.append(turn_text)
        if role == "management":
            if first_analyst is None or index < first_analyst:
                prepared.append(turn_text)
            else:
                management_qa.append(turn_text)
        elif role == "analyst":
            analysts.append(turn_text)
        elif role == "unknown":
            unknown_speakers = True

    missing_sections = []
    if not any(text for text in prepared):
        missing_sections.append("missing_management_prepared_remarks")
    if not any(analysts):
        missing_sections.append("missing_analyst_questions")
    if not any(text for text in management_qa):
        missing_sections.append("missing_management_qa")
    if prefix:
        missing_sections.append("unlabeled_prefix")
    if unknown_speakers:
        missing_sections.append("unrecognized_speaker_labels")
    if not turns:
        missing_sections.append("no_speaker_labels")

    return {
        "all_text": " ".join(all_text),
        "prepared_text": " ".join(prepared),
        "management_qa_text": " ".join(management_qa),
        "management_text": " ".join(prepared + management_qa),
        "analyst_text": " ".join(analysts),
        "analyst_question_count": (
            sum(turn.count("?") for turn in analysts if turn)
            if any(analysts)
            else None
        ),
        "section_status": (
            "complete" if not missing_sections else ";".join(missing_sections)
        ),
        "congratulations_text": clean_text,
        "unrecognized_speaker_labels": unknown_speakers,
    }


def extract_transcript_features(record, metadata, dictionary, dictionary_metadata):
    """Extract one event row without retaining transcript text in the output."""
    status = metadata["transcript_status"]
    if status not in {"complete", "incomplete_transcript", "missing_transcript"}:
        raise ValueError(
            "Unknown transcript_status for {}: {}".format(
                metadata["transcript_id"], status
            )
        )

    text = record.get("transcript") if record is not None else None
    missing_text = not isinstance(text, str) or not text.strip()
    if missing_text:
        status = "missing_transcript"
        parsed = {
            "all_text": "",
            "prepared_text": "",
            "management_qa_text": "",
            "management_text": "",
            "analyst_text": "",
            "analyst_question_count": None,
            "section_status": "missing_transcript",
            "congratulations_text": "",
            "unrecognized_speaker_labels": False,
        }
    else:
        parsed = _parse_transcript(text)

    row = {column: metadata[column] for column in REQUIRED_MANIFEST_COLUMNS}
    row["transcript_status"] = status
    row["section_status"] = parsed["section_status"]
    row.update(dictionary_metadata)

    if status != "complete":
        row.update({column: None for column in FEATURE_COLUMNS})
        return row

    overall = _text_metrics(parsed["all_text"], dictionary)
    prepared = _text_metrics(parsed["prepared_text"], dictionary)
    management_qa = _text_metrics(parsed["management_qa_text"], dictionary)
    management = _text_metrics(parsed["management_text"], dictionary)
    analysts = _text_metrics(parsed["analyst_text"], dictionary)

    row.update(
        {
            "transcript_word_count": overall["word_count"],
            "positive_word_count": overall["positive_word_count"],
            "positive_word_proportion": overall["positive_word_proportion"],
            "negative_word_count": overall["negative_word_count"],
            "negative_word_proportion": overall["negative_word_proportion"],
            "uncertainty_word_count": overall["uncertainty_word_count"],
            "uncertainty_word_proportion": overall["uncertainty_word_proportion"],
            "sentiment_word_count": overall["sentiment_word_count"],
            "transcript_sentiment": overall["sentiment"],
            "management_prepared_word_count": prepared["word_count"],
            "management_prepared_sentiment": prepared["sentiment"],
            "management_qa_word_count": management_qa["word_count"],
            "management_qa_sentiment": management_qa["sentiment"],
            "management_word_count": management["word_count"],
            "management_sentiment": management["sentiment"],
            "analyst_question_word_count": analysts["word_count"],
            "analyst_question_sentiment": analysts["sentiment"],
            "analyst_question_count": parsed["analyst_question_count"],
            "congratulations_mentioned": int(
                re.search(r"\bcongratulations\b", parsed["congratulations_text"], re.I)
                is not None
            ),
        }
    )
    if parsed["unrecognized_speaker_labels"]:
        speaker_feature_columns = (
            "management_prepared_word_count",
            "management_prepared_sentiment",
            "management_qa_word_count",
            "management_qa_sentiment",
            "management_word_count",
            "management_sentiment",
            "analyst_question_word_count",
            "analyst_question_sentiment",
            "analyst_question_count",
        )
        for column in speaker_feature_columns:
            row[column] = None
    return row


def read_transcript_jsonl(input_path):
    """Read unique transcript records; source text remains in memory only."""
    records = {}
    with open(input_path, encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    "Invalid JSON on line {}: {}".format(line_number, error)
                ) from error
            transcript_id = record.get("id")
            if not transcript_id or transcript_id in records:
                raise ValueError(
                    "Transcript IDs must be present and unique (line {}).".format(
                        line_number
                    )
                )
            records[transcript_id] = record
    return records


def build_feature_dataset(
    input_path,
    manifest_path,
    dictionary_path,
    dictionary_retrieved_date="",
    dictionary_version=DICTIONARY_VERSION,
    dictionary_source=DICTIONARY_SOURCE,
):
    """Build a one-row-per-manifest-event local feature dataset."""
    manifest = pd.read_csv(manifest_path, dtype={"event_id": str, "transcript_id": str})
    missing = set(REQUIRED_MANIFEST_COLUMNS).difference(manifest.columns)
    if missing:
        raise ValueError(
            "Transcript manifest is missing columns: {}".format(
                ", ".join(sorted(missing))
            )
        )
    if manifest[list(REQUIRED_MANIFEST_COLUMNS)].isna().any().any():
        raise ValueError("Required transcript manifest values must be present.")
    string_columns = (
        "event_id",
        "transcript_id",
        "ticker",
        "company_name",
        "fiscal_quarter",
        "transcript_status",
        "transcript_input_type",
        "transcript_source",
    )
    if manifest[list(string_columns)].astype(str).apply(
        lambda column: column.str.strip().eq("").any()
    ).any():
        raise ValueError("Required transcript manifest text values cannot be blank.")
    if (
        manifest["event_id"].duplicated().any()
        or manifest["transcript_id"].duplicated().any()
    ):
        raise ValueError("Manifest event and transcript IDs must be unique.")

    transcripts = read_transcript_jsonl(input_path)
    unexpected = set(transcripts).difference(manifest["transcript_id"])
    if unexpected:
        raise ValueError(
            "Transcript IDs missing from manifest: {}".format(
                ", ".join(sorted(unexpected))
            )
        )
    dictionary = load_dictionary(dictionary_path)
    dictionary_metadata = {
        "dictionary_version": dictionary_version,
        "dictionary_source": dictionary_source,
        "dictionary_retrieved_date": dictionary_retrieved_date,
        "dictionary_sha256": _sha256(dictionary_path),
        "transcript_feature_method": (
            "Loughran-McDonald positive-minus-negative word counts / all alpha tokens"
        ),
    }
    return pd.DataFrame(
        [
            extract_transcript_features(
                transcripts.get(metadata["transcript_id"]),
                metadata,
                dictionary,
                dictionary_metadata,
            )
            for metadata in manifest.to_dict("records")
        ]
    )


def _sha256(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-jsonl", required=True, help="Speaker-labeled transcript JSONL"
    )
    parser.add_argument(
        "--manifest-csv", required=True, help="Event/transcript ID metadata CSV"
    )
    parser.add_argument(
        "--dictionary-csv", required=True, help="Local LM master dictionary CSV"
    )
    parser.add_argument(
        "--dictionary-version", default=DICTIONARY_VERSION
    )
    parser.add_argument(
        "--dictionary-source", default=DICTIONARY_SOURCE
    )
    parser.add_argument("--dictionary-retrieved-date", required=True)
    parser.add_argument("--output", required=True, help="Event-level feature CSV")
    args = parser.parse_args()
    features = build_feature_dataset(
        args.input_jsonl,
        args.manifest_csv,
        args.dictionary_csv,
        dictionary_retrieved_date=args.dictionary_retrieved_date,
        dictionary_version=args.dictionary_version,
        dictionary_source=args.dictionary_source,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    print("Wrote {} transcript feature rows to {}".format(len(features), output_path))


if __name__ == "__main__":
    main()
