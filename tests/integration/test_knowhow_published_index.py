"""WP4: 移行した公開版 → 書き出し → 公開版からの索引 → Lambda の索引検査と manifest 照合（ローカル合成）。"""
import importlib.util
import io
import json
from pathlib import Path
import subprocess

from test_common_knowledge_i1 import env  # noqa: F401  (fixture)
from test_common_knowledge_migration import ACTOR, invoker, migration, pick, planned, prepare  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]
BUILDER = str(ROOT / 'scripts/knowledge/build-senpai-index.mjs')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


snap = load('snapshot_published_under_test', 'scripts/knowledge/snapshot_published_cards.py')
retrieval = load('knowhow_retrieval_published_test', 'lambda/rag/rag-function/knowhow_retrieval.py')


class CanonicalS3:
    """The RAG Lambda reads manifests/ through S3 get_object; serve them from the local canonical store."""

    def __init__(self, canonical):
        self.canonical = canonical

    def get_object(self, Bucket, Key):
        identifier = Key[len('manifests/'):-len('.json')]
        with self.canonical.store.unit() as unit:
            value = unit.get('manifest', identifier)
        return {'Body': io.BytesIO(json.dumps(value).encode())}


def test_index_from_published_versions_passes_the_lambda_checks(env, planned, tmp_path, monkeypatch):
    service, now = env
    meta, rows, cards = prepare(service, planned[0])
    chosen = [pick(rows, False), pick(rows, True), next(row for row in rows if row['fixes'])]
    migration.apply(meta, rows, cards, service.work, invoker(service), ACTOR, tmp_path / 'r.jsonl',
                    {row['knowledgeId'] for row in chosen})
    out = tmp_path / 'snapshot'
    listing, skipped = snap.snapshot([row['knowledgeId'] for row in chosen] + ['KH-NOT-MIGRATED'],
                                     service.canonical, out, {'synthetic'}, now=now[0])
    assert len(listing['entries']) == 3 and skipped == {'notPublished': 1}
    compared = snap.compare_inventory(listing, planned[0] / 'inventory.jsonl')
    assert compared['published'] == 3 and compared['changed'] == [] and compared['extra'] == []
    assert snap.snapshot([chosen[0]['knowledgeId']], service.canonical, tmp_path / 'other', {'all-users'},
                         now=now[0])[1] == {'audience': 1}

    root = tmp_path / 'root'
    root.mkdir()
    subprocess.run(['node', BUILDER, 'build-published', str(root), str(out)], check=True, capture_output=True)
    index = retrieval.parse_index((root / '.private-knowhow/index-published.json').read_bytes())
    assert {card['knowledgeId'] for card in index['cards']} == {row['knowledgeId'] for row in chosen}
    assert {card['sha256'] for card in index['cards']} == {row['rawSha256'] for row in chosen}
    fixed = next(card for card in index['cards'] if card['knowledgeId'] == chosen[2]['knowledgeId'])
    assert fixed['cardVersion'] == chosen[2]['cardVersion'] and fixed['status'] == 'approved'

    monkeypatch.setenv('KNOWHOW_CANONICAL_BUCKET', 'canonical')
    monkeypatch.setenv('KNOWHOW_AUDIENCES', 'synthetic')
    retrieval.clear_cache()
    kept = retrieval.confirm_published(index['cards'], s3_client=CanonicalS3(service.canonical),
                                       now=now[0], monotonic=0)
    assert len(kept) == 3
    # A body that differs from its manifest hash (e.g. edited after the snapshot) is refused by the builder.
    (out / 'cards' / f'{chosen[0]["knowledgeId"]}.md').write_text('---\nknowledge_id: X\n---\n', encoding='utf-8')
    failed = subprocess.run(['node', BUILDER, 'build-published', str(root), str(out)], capture_output=True)
    assert failed.returncode != 0
