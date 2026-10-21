"""Card hashes are part of the ledger and approved manifests, so cards must stay LF on every OS."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARD_ROOT = ROOT / "knowledge" / "cards"


def test_gitattributes_pins_card_line_endings_to_lf():
    rules = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "knowledge/cards/** text eol=lf" in rules


def test_no_card_file_contains_crlf_in_the_working_tree():
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in sorted(CARD_ROOT.rglob("*.md"))
        if b"\r\n" in path.read_bytes()
    ]
    assert offenders == []
