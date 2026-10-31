"""Card hashes in ledgers and manifests must ignore checkout line-ending conversions."""
import base64
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARD_ROOT = ROOT / "knowledge" / "cards"
HASH_MODULE = ROOT / "scripts" / "knowledge" / "card-hash.mjs"


def test_gitattributes_pins_card_line_endings_to_lf():
    rules = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "knowledge/cards/** text eol=lf" in rules


def _card_hashes(content: bytes) -> list[str]:
    script = (
        f"import {{ cardDigest }} from {json.dumps(HASH_MODULE.as_uri())}; "
        "const lf = Buffer.from(process.env.CARD_CONTENT, 'base64').toString('utf8'); "
        "process.stdout.write(JSON.stringify([cardDigest(lf), "
        "cardDigest(lf.replace(/\\n/g, '\\r\\n')), cardDigest(lf.replace(/\\n/g, '\\r'))]));"
    )
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        cwd=ROOT,
        env={**os.environ, "CARD_CONTENT": base64.b64encode(content).decode("ascii")},
        text=True,
    )
    return json.loads(result.stdout)


def test_card_hash_is_independent_of_checkout_line_endings():
    source = next(CARD_ROOT.rglob("*.md"))
    content = source.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")

    assert len(set(_card_hashes(content))) == 1
