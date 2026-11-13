"""WP4: 先輩の索引のカードを、共通知識の公開 manifest で使う直前に照合する（設計 2026-11-11 §4.12）。"""
import importlib.util
import io
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('knowhow_guard_under_test', ROOT / 'lambda/rag/rag-function/knowhow_retrieval.py')
k = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k)

NOW = 1_800_000_000


class Missing(Exception):
    response = {'Error': {'Code': 'NoSuchKey'}}


class Denied(Exception):
    response = {'Error': {'Code': 'AccessDenied'}}


class FakeS3:
    def __init__(self, manifests, fail=None):
        self.manifests, self.fail, self.calls = manifests, fail, 0

    def get_object(self, Bucket, Key):
        self.calls += 1
        assert Bucket == 'canonical' and Key.startswith('manifests/') and Key.endswith('.json')
        if self.fail:
            raise self.fail()
        identifier = Key[len('manifests/'):-len('.json')]
        if identifier not in self.manifests:
            raise Missing()
        return {'Body': io.BytesIO(json.dumps(self.manifests[identifier]).encode())}


def manifest(identifier, sha, audience='all-users', active=True, expires=NOW + 100):
    return {'generation': 1, 'active': 'k' if active else None, 'operation': 'o',
            'bundle': {'knowledgeId': identifier, 'rawSha256': sha, 'audience': audience, 'expiresAt': expires}}


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    k.clear_cache()
    monkeypatch.setenv('KNOWHOW_CANONICAL_BUCKET', 'canonical')
    monkeypatch.setenv('KNOWHOW_AUDIENCES', 'all-users')
    yield
    k.clear_cache()


def card(identifier, sha='a' * 64):
    return {'knowledgeId': identifier, 'sha256': sha}


def test_only_the_active_published_body_for_an_allowed_audience_is_kept():
    s3 = FakeS3({'KH-OK': manifest('KH-OK', 'a' * 64), 'KH-NEWER': manifest('KH-NEWER', 'b' * 64),
                 'KH-STOPPED': manifest('KH-STOPPED', 'a' * 64, active=False),
                 'KH-OTHER': manifest('KH-OTHER', 'a' * 64, audience='itai-validation'),
                 'KH-OLD': manifest('KH-OLD', 'a' * 64, expires=NOW - 1),
                 'KH-WRONG': manifest('KH-SOMETHING-ELSE', 'a' * 64)})
    cards = [card(name) for name in ('KH-OK', 'KH-NEWER', 'KH-STOPPED', 'KH-OTHER', 'KH-OLD', 'KH-WRONG',
                                     'KH-NEVER', '../escape')]
    assert k.confirm_published(cards, s3_client=s3, now=NOW, monotonic=0) == [card('KH-OK')]


def test_manifests_are_cached_for_the_index_ttl_only():
    s3 = FakeS3({'KH-OK': manifest('KH-OK', 'a' * 64)})
    k.confirm_published([card('KH-OK')], s3_client=s3, now=NOW, monotonic=0)
    k.confirm_published([card('KH-OK')], s3_client=s3, now=NOW, monotonic=k.CACHE_TTL_SECONDS - 1)
    assert s3.calls == 1
    s3.manifests['KH-OK'] = manifest('KH-OK', 'a' * 64, active=False)  # withdrawn
    assert k.confirm_published([card('KH-OK')], s3_client=s3, now=NOW, monotonic=k.CACHE_TTL_SECONDS + 1) == []
    assert s3.calls == 2


def test_unreadable_manifest_store_fails_closed():
    with pytest.raises(k.KnowhowIndexError):
        k.confirm_published([card('KH-OK')], s3_client=FakeS3({}, fail=Denied), now=NOW, monotonic=0)


def test_without_a_canonical_bucket_the_git_index_is_used_unchanged(monkeypatch):
    monkeypatch.delenv('KNOWHOW_CANONICAL_BUCKET')
    cards = [card('KH-ANY')]
    assert k.confirm_published(cards, s3_client=None) is cards
    monkeypatch.setenv('KNOWHOW_CANONICAL_BUCKET', 'canonical')
    monkeypatch.setenv('KNOWHOW_AUDIENCES', ' ')
    with pytest.raises(k.KnowhowIndexError):
        k.confirm_published(cards, s3_client=FakeS3({}))
