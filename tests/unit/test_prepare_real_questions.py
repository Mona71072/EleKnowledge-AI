import importlib.util
import csv
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/eval/prepare_real_questions.py"
SPEC = importlib.util.spec_from_file_location("prepare_real_questions", SCRIPT)
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


def test_anonymize_replaces_identifiers_and_keeps_technical_terms():
    value, labels = prepare.anonymize(
        "株式会社東西電機の新宿第一ビル現場、工事番号ABC-1234でAXIEZのかごに異音。"
        "連絡は user@example.com、03-1234-5678。"
    )

    assert "株式会社東西電機" not in value
    assert "新宿第一ビル" not in value
    assert "ABC-1234" not in value
    assert "user@example.com" not in value
    assert "03-1234-5678" not in value
    assert "AXIEZ" in value and "かご" in value and "異音" in value
    assert {"company", "site", "work_order", "email", "phone"} <= set(labels)


def test_anonymize_replaces_international_phone_and_postfix_company():
    value, labels = prepare.anonymize("三菱電機株式会社へ +81-90-1234-5678 で連絡する。")

    assert "三菱電機株式会社" not in value
    assert "+81-90-1234-5678" not in value
    assert "○○会社" in value and "○○電話番号" in value
    assert {"company", "phone"} <= set(labels)


def test_anonymize_does_not_guess_unlabelled_person_names():
    value, labels = prepare.anonymize("山田太郎がAXIEZの異音を確認した。")

    assert "山田太郎" in value
    assert "person" not in labels and "person_honorific" not in labels


def test_stratified_sample_respects_primary_stratum_quotas_and_seed():
    rows = []
    for stratum in prepare.DEFAULT_QUOTAS:
        rows.extend({"question": f"{stratum} question {i}", "response_type": {
            "not_found": "not_found", "ordinary_answered": "pages",
        }.get(stratum, ""), "feedback": "bad" if stratum == "thumbs_down" else "",
            "preceded_by_clarify": "true" if stratum == "clarify_followup" else "",
            "model_type": "MODEL" if stratum == "model_specified" else ""}
            for i in range(8))

    first = prepare.stratified_sample(rows, target=20, seed=42)
    second = prepare.stratified_sample(rows, target=20, seed=42)
    counts = {key: sum(stratum == key for _, stratum in first)
              for key in prepare.DEFAULT_QUOTAS}

    assert len(first) == 20
    assert counts == prepare.DEFAULT_QUOTAS
    assert [row["question"] for row, _ in first] == [row["question"] for row, _ in second]


def test_variable_target_scales_quotas_proportionally():
    assert prepare._proportional_quotas(10) == {
        "thumbs_down": 2,
        "not_found": 2,
        "ordinary_answered": 3,
        "clarify_followup": 1,
        "model_specified": 1,
        "model_unspecified": 1,
    }
    assert prepare._proportional_quotas(21) == {
        "thumbs_down": 4,
        "not_found": 4,
        "ordinary_answered": 6,
        "clarify_followup": 3,
        "model_specified": 2,
        "model_unspecified": 2,
    }


def test_extract_sql_scans_previous_partition_but_filters_candidates_at_start_date():
    sql_path = SCRIPT.parents[1] / "eval" / "extract_user_questions.sql"
    sql = sql_path.read_text(encoding="utf-8")
    latest_events = sql.split("latest_events AS (", 1)[1].split("removed_messages AS (", 1)[0]
    eligible_questions = sql.split("eligible_questions AS (", 1)[1].split("limited_questions AS (", 1)[0]

    assert "dt >= extraction_window.remove_start_dt" in latest_events
    assert "substr(message_timestamp, 1, 10) >= extraction_window.start_dt" in eligible_questions


def test_write_outputs_carries_model_type_to_review_csv_and_filters(tmp_path):
    review_path = tmp_path / "review.csv"
    jsonl_path = tmp_path / "draft.jsonl"
    rows = [
        {"question": "機種指定あり", "model_type": "AXIEZ"},
        {"question": "機種指定なし", "model_type": "  "},
    ]

    assert prepare.write_outputs(rows, review_path, jsonl_path, target=2, seed=1) == 2

    with review_path.open(encoding="utf-8-sig", newline="") as csv_file:
        review_rows = list(csv.DictReader(csv_file))
    drafts = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
    reviewed_by_question = {row["question_anonymized"]: row for row in review_rows}
    drafts_by_question = {row["query"]: row for row in drafts}

    assert reviewed_by_question["機種指定あり"]["model_type"] == "AXIEZ"
    assert drafts_by_question["機種指定あり"]["filters"] == {"modelType": "AXIEZ"}
    assert reviewed_by_question["機種指定なし"]["model_type"] == ""
    assert drafts_by_question["機種指定なし"]["filters"] == {}


def test_write_outputs_rejects_repository_local_paths_outside_ignored_directory(tmp_path):
    repo_output = SCRIPT.parents[2] / "docs" / "must-not-be-written.jsonl"

    with pytest.raises(ValueError, match="under .eval-real-questions"):
        prepare.write_outputs(
            [{"question": "candidate"}], tmp_path / "review.csv", repo_output, target=1
        )

    assert not repo_output.exists()
