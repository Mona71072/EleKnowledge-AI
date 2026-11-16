"""Tests for the scope review queue generator (synthetic cards only, no network)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "knowledge" / "build_scope_review_queue.py"


def _module():
    spec = importlib.util.spec_from_file_location("build_scope_review_queue_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def _write_card(root: Path, knowledge_id: str, scope_yaml: str, *, title: str = "合成カード") -> None:
    directory = root / "cards" / "practice-guides"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{knowledge_id}.md").write_text(
        f"---\nknowledge_id: {knowledge_id}\ncard_version: 1\nkind: practice_guide\nstatus: draft\n"
        f"title: \"{title}\"\nmodel_scope:\n{scope_yaml}\n---\n\n# body\n",
        encoding="utf-8",
    )


@pytest.fixture
def cards_root(tmp_path):
    root = tmp_path / "knowledge"
    _write_card(root, "KH-P1", '  product_lines: ["AXIEZ"]\n  scope_note: "全エレ機種で共通"')
    _write_card(root, "KH-P1B", '  product_lines: ["Nexcube"]\n  lists_model_label: ["全エレ機種"]')
    _write_card(root, "KH-P2", '  product_lines: ["AXIEZ-LINKs"]')
    _write_card(root, "KH-P3", '  control_methods: ["VFGH"]\n  model_abbreviations: ["VFGH"]')
    _write_card(root, "KH-P4", '  lists_model_label: ["全エレ機種"]')
    _write_card(root, "KH-P4E", "  product_lines: []")
    _write_card(
        root, "KH-DONE",
        '  product_lines: ["AXIEZ"]\n  scope_status: verified\n'
        '  scope_verified_by: reviewer\n  scope_verified_at: "2026-10-20"',
    )
    return root


def _priorities(module, root):
    return {row.knowledge_id: row.priority for row in module.collect_rows(root)}


def test_cards_are_assigned_to_priorities(cards_root):
    assert _priorities(_module(), cards_root) == {
        "KH-P1": "P1", "KH-P1B": "P1", "KH-P2": "P2", "KH-P3": "P3", "KH-P4": "P4", "KH-P4E": "P4",
    }


def test_verified_cards_are_not_queued_but_counted(cards_root):
    module = _module()
    assert "KH-DONE" not in _priorities(module, cards_root)
    assert module.render_queue(cards_root).count("検証済み") >= 1


def test_render_is_deterministic_and_groups_by_priority(cards_root):
    module = _module()
    first = module.render_queue(cards_root)
    assert first == module.render_queue(cards_root)
    assert first.index("## P1") < first.index("## P2") < first.index("## P3") < first.index("## P4")
    assert "scope_status: verified" in first
    assert "build_scope_review_queue.py" in first
    assert "機種フィルタ対象外" in first
    assert "[KH-P1](../../cards/practice-guides/KH-P1.md)" in first


def test_p4_lists_no_per_card_table_rows_for_generic_cards(cards_root):
    section = _module().render_queue(cards_root).split("## P4", 1)[1]
    assert "KH-P4E" in section and "KH-P4](" not in section


def test_main_writes_queue_file(cards_root, tmp_path):
    module = _module()
    out = tmp_path / "queues" / "scope-review" / "QUEUE.md"

    assert module.main(["--knowledge-root", str(cards_root), "--output", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == module.render_queue(cards_root)


def test_unparseable_card_is_reported_not_fatal(cards_root):
    (cards_root / "cards" / "practice-guides" / "KH-BAD.md").write_text("---\n: [\n---\n", encoding="utf-8")

    assert "KH-BAD" in _module().render_queue(cards_root)


# --- field reports (「結果を残す」) -------------------------------------------

import json  # noqa: E402

AXIEZ_CARD = '  product_lines: ["AXIEZ"]\n  scope_status: verified\n  scope_verified_by: r\n  scope_verified_at: "2026-10-20"'


def _report(card_id, reaction, *, model="NEXCUBE", turn_model=None, state="unconfirmed", version=1,
            created="2026-10-20T01:00:00Z", finding="現場の本文ZZZ-FINDING", user="user-ZZZ"):
    report = {
        "reportId": f"field-report-{card_id}-{reaction}-{created}", "userId": user,
        "senpaiConversationId": "conv-ZZZ", "senpaiTurnId": "turn-ZZZ", "createdAt": created,
        "finding": finding, "condition": "条件ZZZ-CONDITION", "reviewState": state,
        "cardReactions": [{"knowledgeId": card_id, "cardVersion": version, "reaction": reaction,
                           "cardScopeStatus": "verified", "cardProductScope": ["AXIEZ"]}],
    }
    if model:
        report["modelType"] = model
    if turn_model:
        report["turnModelType"] = turn_model
    return report


@pytest.fixture
def reports_root(cards_root):
    _write_card(cards_root, "KH-AX", AXIEZ_CARD, title="AXIEZ 検証済みカード")
    return cards_root


def _export(tmp_path, reports, wrap=False):
    path = tmp_path / "export.json"
    path.write_text(json.dumps({"items": reports} if wrap else reports, ensure_ascii=False), encoding="utf-8")
    return path


def test_aggregate_counts_reactions_by_model_and_drops_text_and_people(reports_root, tmp_path):
    module = _module()
    export = _export(tmp_path, [
        _report("KH-AX", "not_matched"),
        _report("KH-AX", "not_matched", model=None, turn_model="AXIEZ", created="2026-10-21T00:00:00Z"),
        _report("KH-AX", "matched", model=None),
        _report("KH-P2", "unsure"),
        _report("KH-P2", "not_matched", state="reflected"),
        _report("KH-P2", "not_matched", state="held_or_rejected"),
        {"broken": True},
    ], wrap=True)
    aggregate = module.aggregate_field_reports(module.load_field_report_export(export))
    assert aggregate["cards"]["KH-AX"]["byVersion"] == {
        "1": {
            "reactions": {
                "": {"matched": 1, "not_matched": 0, "unsure": 0},
                "AXIEZ": {"matched": 0, "not_matched": 1, "unsure": 0},
                "NEXCUBE": {"matched": 0, "not_matched": 1, "unsure": 0},
            },
            "latestReportDate": "2026-10-21",
        }
    }
    assert aggregate["cards"]["KH-P2"]["byVersion"]["1"]["reactions"] == {
        "NEXCUBE": {"matched": 0, "not_matched": 0, "unsure": 1}
    }
    assert aggregate["counted"] == 4 and aggregate["skipped"] == 3
    text = json.dumps(aggregate, ensure_ascii=False)
    for secret in ("ZZZ-FINDING", "ZZZ-CONDITION", "user-ZZZ", "conv-ZZZ", "turn-ZZZ"):
        assert secret not in text


def test_export_must_be_a_list_or_items_object(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"reports": []}', encoding="utf-8")
    with pytest.raises(ValueError):
        _module().load_field_report_export(path)


def test_p0_lists_not_matched_and_other_model_reports_first_including_verified(reports_root, tmp_path):
    module = _module()
    export = _export(tmp_path, [
        _report("KH-AX", "matched", model="NEXCUBE"),      # other model than the card's AXIEZ
        _report("KH-P2", "not_matched", model="AXIEZ-LINKs"),
        _report("KH-P2", "not_matched", model="AXIEZ-LINKs"),
        _report("KH-P3", "matched", model="AXIEZ"),         # control-code only: no mismatch, only matched
        _report("KH-GONE", "not_matched"),
    ])
    module.write_field_report_aggregate(module.load_field_report_export(export), reports_root)
    queue = module.render_queue(reports_root)
    p0 = queue.split("## P0", 1)[1].split("\n## P1", 1)[0]
    assert queue.index("## P0") < queue.index("## P1")
    assert p0.index("[KH-P2]") < p0.index("[KH-AX]")
    assert "検証済み" in p0.split("[KH-AX]", 1)[1].split("\n", 1)[0]
    assert "[KH-P3]" not in p0 and "KH-P3" in p0  # listed only in the reference line
    assert "KH-GONE" in p0  # unknown card is surfaced, not dropped
    assert "ZZZ" not in queue


def test_p0_keeps_reactions_separate_by_version_and_prioritizes_current_version(reports_root, tmp_path):
    module = _module()
    card_path = reports_root / "cards" / "practice-guides" / "KH-AX.md"
    card_path.write_text(card_path.read_text(encoding="utf-8").replace("card_version: 1", "card_version: 2"), encoding="utf-8")
    export = _export(tmp_path, [
        _report("KH-AX", "not_matched", model="AXIEZ", version=1),
        _report("KH-AX", "matched", model="NEXCUBE", version=2, created="2026-10-21T01:00:00Z"),
        _report("KH-AX", "not_matched", model="AXIEZ", version=99, created="2026-10-22T01:00:00Z"),
    ])
    module.write_field_report_aggregate(module.load_field_report_export(export), reports_root)

    aggregate = module._read_aggregate(reports_root)
    queue = module.render_queue(reports_root)
    p0 = queue.split("## P0", 1)[1].split("\n## P1", 1)[0]

    assert aggregate["cards"]["KH-AX"]["byVersion"]["1"]["reactions"]["AXIEZ"]["not_matched"] == 1
    assert aggregate["cards"]["KH-AX"]["byVersion"]["2"]["reactions"]["NEXCUBE"]["matched"] == 1
    assert "v2（現行）" in p0
    assert "v1（旧版）" in p0 and "v99（現行より新しい版）" in p0
    assert p0.index("v2（現行）") < p0.index("v1（旧版）")
    old_line = next(line for line in p0.splitlines() if "v1（旧版）" in line)
    assert "| 1 | — |" in old_line
    assert "報告に記録されたカード版を先に確認" in old_line


def test_legacy_aggregate_and_unknown_versions_remain_visible(reports_root):
    module = _module()
    aggregate_path = reports_root / "queues" / "scope-review" / "field-reports.json"
    aggregate_path.parent.mkdir(parents=True)
    aggregate_path.write_text(json.dumps({"counted": 2, "cards": {
        "KH-AX": {"versions": [1, 2], "reactions": {
            "NEXCUBE": {"matched": 1, "not_matched": 1, "unsure": 0}
        }, "latestReportDate": "2026-10-20"},
        "KH-GONE": {"versions": [4], "reactions": {
            "NEXCUBE": {"matched": 1, "not_matched": 0, "unsure": 0}
        }, "latestReportDate": ""},
    }}), encoding="utf-8")

    p0 = module.render_queue(reports_root).split("## P0", 1)[1].split("\n## P1", 1)[0]
    assert "版不明（旧集計・版を特定できない）" in p0
    assert "記録版: v1, v2" in p0
    assert "KH-GONE" in p0
    assert "版不明（旧集計" in p0
    missing_line = next(line for line in p0.splitlines() if "KH-GONE" in line)
    assert "| — |" in missing_line
    assert "報告に記録されたカード版を先に確認" in missing_line


def test_untrusted_report_model_is_not_written_to_aggregate(tmp_path):
    module = _module()
    aggregate = module.aggregate_field_reports([_report("KH-AX", "matched", model="PERSONAL-NAME-123")])
    serialized = json.dumps(aggregate, ensure_ascii=False)

    assert "PERSONAL-NAME-123" not in serialized
    assert "NEXCUBE" not in serialized


def test_report_card_version_must_be_positive_and_bounded():
    module = _module()
    aggregate = module.aggregate_field_reports([
        _report("KH-ZERO", "not_matched", version=0),
        _report("KH-NEGATIVE", "not_matched", version=-1),
        _report("KH-TOO-LARGE", "not_matched", version=1_000_001),
    ])

    assert aggregate["cards"] == {}


def test_queue_without_aggregate_has_empty_p0_and_is_deterministic(cards_root):
    module = _module()
    queue = module.render_queue(cards_root)
    assert "## P0" in queue and "現場の報告はまだ集計されていません" in queue
    assert queue == module.render_queue(cards_root)


def test_main_with_field_reports_writes_aggregate_and_queue(reports_root, tmp_path):
    module = _module()
    export = _export(tmp_path, [_report("KH-AX", "not_matched")])
    out = tmp_path / "QUEUE.md"
    assert module.main(["--knowledge-root", str(reports_root), "--output", str(out),
                        "--field-reports", str(export)]) == 0
    aggregate_path = reports_root / "queues" / "scope-review" / "field-reports.json"
    assert json.loads(aggregate_path.read_text(encoding="utf-8"))["cards"]["KH-AX"]
    assert out.read_text(encoding="utf-8") == module.render_queue(reports_root)
    assert "[KH-AX]" in out.read_text(encoding="utf-8").split("## P1", 1)[0]


def _write_ref_card(root: Path, knowledge_id: str, refs_yaml: str, *, title: str = "重複カード",
                    scope_yaml: str = '  product_lines: ["AXIEZ"]') -> None:
    directory = root / "cards" / "practice-guides"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{knowledge_id}.md").write_text(
        f"---\nknowledge_id: {knowledge_id}\nkind: practice_guide\nstatus: draft\n"
        f"title: \"{title}\"\nmodel_scope:\n{scope_yaml}\nsource_refs:\n{refs_yaml}\n---\n\n# body\n",
        encoding="utf-8",
    )


def _lists_ref(item: str, onenote: str | None = None) -> str:
    text = f"  - ref_type: lists_item\n    list_item_id: \"{item}\"\n"
    if onenote:
        text += f"  - ref_type: onenote_page\n    onenote_id: \"{onenote}\"\n"
    return text.rstrip("\n")


def test_duplicate_groups_share_a_lists_item_number(tmp_path):
    module = _module()
    root = tmp_path / "knowledge"
    _write_ref_card(root, "KH-D2", _lists_ref("153"), title="B")
    _write_ref_card(root, "KH-D1", _lists_ref("153"), title="A")
    _write_ref_card(root, "KH-D3", _lists_ref("153"), title="C")
    _write_ref_card(root, "KH-X1", _lists_ref("7"))
    _write_ref_card(root, "KH-X2", _lists_ref("8"))
    _write_card(root, "KH-NOREF", "  product_lines: [\"AXIEZ\"]")

    groups = module.duplicate_groups(root)

    assert [(g.list_item_id, g.knowledge_ids) for g in groups] == [("153", ("KH-D1", "KH-D2", "KH-D3"))]


def test_duplicate_groups_sorted_numerically_and_include_verified_cards(tmp_path):
    module = _module()
    root = tmp_path / "knowledge"
    for kid, item in (("KH-A", "19"), ("KH-B", "19"), ("KH-C", "123"), ("KH-D", "123")):
        _write_ref_card(root, kid, _lists_ref(item))
    _write_ref_card(
        root, "KH-V", _lists_ref("19"),
        scope_yaml='  product_lines: ["AXIEZ"]\n  scope_status: verified\n'
                   '  scope_verified_by: r\n  scope_verified_at: "2026-10-20"',
    )

    groups = module.duplicate_groups(root)

    assert [g.list_item_id for g in groups] == ["19", "123"]
    assert groups[0].knowledge_ids == ("KH-A", "KH-B", "KH-V")


def test_duplicate_group_notes_shared_onenote_id(tmp_path):
    module = _module()
    root = tmp_path / "knowledge"
    _write_ref_card(root, "KH-A", _lists_ref("5", "{u}:1"))
    _write_ref_card(root, "KH-B", _lists_ref("5", "{u}:1"))
    _write_ref_card(root, "KH-C", _lists_ref("6", "{u}:1"))
    _write_ref_card(root, "KH-D", _lists_ref("6", "{u}:2"))

    five, six = module.duplicate_groups(root)

    assert five.shared_onenote_ids == ("{u}:1",)
    assert six.shared_onenote_ids == ()
    assert six.knowledge_ids == ("KH-C", "KH-D")


def test_queue_has_duplicate_section_with_links_titles_and_actions(tmp_path):
    module = _module()
    root = tmp_path / "knowledge"
    _write_ref_card(root, "KH-A", _lists_ref("153"), title="床A")
    _write_ref_card(root, "KH-B", _lists_ref("153"), title="床B")
    _write_ref_card(root, "KH-C", _lists_ref("9"))

    text = module.render_queue(root)

    assert text == module.render_queue(root)
    section = text.split("## 重複の疑い（同じ Lists 番号）", 1)[1]
    assert "[KH-A](../../cards/practice-guides/KH-A.md)" in section
    assert "[KH-B](../../cards/practice-guides/KH-B.md)" in section
    assert "床A" in section and "床B" in section
    assert "統合する" in section and "関連を明記" in section
    assert "KH-C" not in section
    assert "| 重複の疑い（同じ Lists 番号） | 1 |" in text
    assert text.index("## P4") < text.index("## 重複の疑い")


def test_queue_duplicate_section_says_none_when_no_duplicates(cards_root):
    text = _module().render_queue(cards_root)
    section = text.split("## 重複の疑い（同じ Lists 番号）", 1)[1]
    assert "（なし）" in section
    assert "| 重複の疑い（同じ Lists 番号） | 0 |" in text
