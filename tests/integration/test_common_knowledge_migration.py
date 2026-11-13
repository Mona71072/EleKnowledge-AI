"""ノウハウ管理の見直し WP3: Git のカードを S3 の正本へ移行する（設計 2026-11-11 §4.11）。

plan は Git の実カード（指定コミット）を読むが、AWS には触れない。apply と verify は合成の
ローカル台帳・作業用・正本（SQLite）で、Lambda の直接呼び出しと同じ handle_migration を通す。
"""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from test_common_knowledge_i1 import call, count, env, local, restart  # noqa: F401  (env is a fixture)
from storage import digest  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('migrate_cards', ROOT / 'scripts/knowledge/migrate_cards_to_s3.py')
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)
ACTOR = 'synthetic-migrator'


@pytest.fixture(scope='module')
def planned(tmp_path_factory):
    out = tmp_path_factory.mktemp('plan')
    meta = migration.plan('HEAD', out, 'synthetic', 'synthetic', now=1800000000)
    return out, meta


def prepare(service, out):
    """The operator's two manual steps: grant the migrating actor, add the evidence entry."""
    service.policy['actors'][ACTOR] = {'domains': ['synthetic'], 'audiences': ['synthetic'],
                                       'permissions': ['view', 'edit', 'approve', 'publish', 'read'],
                                       'expiresAt': 1800000000 + 4 * 365 * 24 * 3600}
    service.policy['evidence'].update(json.loads((out / 'policy-evidence-entry.json').read_text(encoding='utf-8')))
    return migration.load_plan(out)


def invoker(service):
    return lambda event: local.api.handle_migration(json.loads(json.dumps(event)), service)


def pick(rows, exception):
    return next(row for row in rows if row['secondReview'] is exception and not row['fixes'])


def test_plan_covers_every_card_in_the_version_ledger(planned):
    out, meta = planned
    ledger = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:knowledge/registry/card-versions.jsonl'],
                            capture_output=True, check=True).stdout.decode('utf-8').split('\n')
    expected = {json.loads(line)['knowledgeId']: json.loads(line) for line in ledger if line.strip()}
    _, rows, cards = migration.load_plan(out)
    assert meta['errors'] == [] and meta['counts']['cards'] == len(expected) == len(rows)
    for row in rows:
        assert row['gitSha256'] == expected[row['knowledgeId']]['sha256']
        assert row['gitCardVersion'] == expected[row['knowledgeId']]['cardVersion']
        assert row['cardVersion'] == row['gitCardVersion'] + (1 if row['fixes'] else 0)
        text = cards[row['knowledgeId']].decode('utf-8')
        assert '\nstatus: approved\n' in text and 'review_status' not in text.split('\n---\n', 1)[0]
    assert meta['expiresAt'] == 1800000000 + migration.THREE_YEARS
    assert meta['evidence']['sha256'] == digest((out / 'inventory.jsonl').read_bytes())


def test_convert_drops_old_fields_moves_misplaced_values_and_keeps_the_body():
    raw = ('---\n\nknowledge_id: KH-SYN-1\nkind: case_summary\nstatus: draft\ncard_version: 2\n'
           'title: "合成"\nmodel_scope:\n  control_methods:\n    - "LINKS"\n    - "VFGH"\n'
           '  guide_systems: ["メンテコン"]\n  scope_note: "合成の範囲"\nsource_refs:\n'
           '  - ref_type: lists_item\n    list_item_id: "1"\nreview_status: in_review\n'
           'cloud_approval: not_reviewed\n---\n# 本文\n\n変えない。\n').encode('utf-8')
    misplaced = [{'axis': 'control_methods', 'value': 'LINKS', 'move_to_axis': 'product_lines',
                  'move_to_value': 'AXIEZ-LINKs'},
                 {'axis': 'guide_systems', 'value': 'メンテコン', 'move_to_axis': None, 'move_to_value': None,
                  'note': '要確認'}]
    converted, report = migration.convert(raw, misplaced)
    text = converted.decode('utf-8')
    assert text.endswith('---\n# 本文\n\n変えない。\n')
    assert 'review_status' not in text and 'cloud_approval' not in text
    assert '\nstatus: approved\n' in text and '\ncard_version: 3\n' in text
    assert report['modelScope'] == {'control_methods': ['VFGH'], 'guide_systems': ['メンテコン'],
                                    'scope_note': '合成の範囲', 'product_lines': ['AXIEZ-LINKs']}
    assert report['unresolved'] == [{'axis': 'guide_systems', 'value': 'メンテコン', 'note': '要確認'}]
    assert report['droppedFields'] == ['review_status', 'cloud_approval']
    unchanged, plain = migration.convert(raw.replace(b'"LINKS"', b'"VFGLB"'), misplaced)
    assert plain['fixes'] == [] and b'\ncard_version: 2\n' in unchanged
    assert b'  control_methods:\n    - "VFGLB"\n' in unchanged  # untouched blocks keep their style
    with pytest.raises(migration.PlanError):
        migration.convert(raw.replace(b'\n', b'\r\n'), misplaced)
    with pytest.raises(migration.PlanError):
        migration.convert(raw.replace(b'status: draft', b'status: retired'), misplaced)
    assert migration.applicability(report['modelScope']) == (
        '合成の範囲; product_lines: AXIEZ-LINKs; control_methods: VFGH; scope_status: unverified')


def test_apply_publishes_marks_exceptions_and_verify_matches(env, planned, tmp_path):
    service, now = env
    meta, rows, cards = prepare(service, planned[0])
    normal, exception = pick(rows, False), pick(rows, True)
    only = {normal['knowledgeId'], exception['knowledgeId']}
    result = migration.apply(meta, rows, cards, service.work, invoker(service), ACTOR,
                             tmp_path / 'results.jsonl', only)
    assert result == {'selected': 2, 'statuses': {200: 2}}
    outcomes = {row['knowledgeId']: row for row in map(json.loads, (tmp_path / 'results.jsonl').read_text(
        encoding='utf-8').splitlines())}
    assert outcomes[normal['knowledgeId']]['result']['sampleCheck'] is None
    assert outcomes[exception['knowledgeId']]['result']['sampleCheck'] == 'pending'
    for row in (normal, exception):
        status, published = call(service, 'reader', 'GET', 'published/' + row['knowledgeId'])
        assert status == 200, published
        assert published['markdown'].encode('utf-8') == cards[row['knowledgeId']]
        assert published['generation'] == 1 and published['expiresAt'] == meta['expiresAt']
        assert published['sourceRefs'][0]['locator'] == row['path']
        approved_key = outcomes[row['knowledgeId']]['result']['approvedKey']
        with service.canonical.store.unit() as unit:
            record = unit.get('approved', approved_key)['record']
        assert record['reason'] == meta['reason'] and record['self_approved'] is True
        assert record['migration']['card_version'] == row['cardVersion']
    assert migration.verify([normal, exception], service.canonical) == {
        'expected': 2, 'matched': 2, 'mismatches': []}
    assert migration.verify([pick(rows, False) | {'knowledgeId': 'KH-NOT-MIGRATED'}], service.canonical)[
        'mismatches'] == [{'knowledgeId': 'KH-NOT-MIGRATED', 'problems': ['notPublished', 'bundleHash',
                                                                          'publishedBody']}]
    # Another person records the sample check of the exception card through the normal route.
    detail = call(service, 'reviewer', 'GET', 'cards/' + exception['knowledgeId'])[1]
    assert detail['versions']['1']['sampleCheck'] == {'status': 'pending'}
    assert detail['versions']['1']['migration']['cardVersion'] == exception['cardVersion']
    approval = outcomes[exception['knowledgeId']]['result']['approvalId']
    status, checked = call(service, 'reviewer', 'POST', 'cards/' + exception['knowledgeId'] + '/sample-checks',
                           {'approvalId': approval, 'result': 'confirmed', 'reason': '抜き取りで確認'}, 1, 'check')
    assert status == 200 and checked['status'] == 'confirmed'
    # Re-running the same command changes nothing: same results, no new working versions or generations.
    versions = count(service.work.store, 'work-version')
    again = migration.apply(meta, rows, cards, service.work, invoker(restart(service, now)), ACTOR,
                            tmp_path / 'again.jsonl', only)
    assert again == result
    assert count(service.work.store, 'work-version') == versions
    assert call(service, 'reader', 'GET', 'published/' + normal['knowledgeId'])[1]['generation'] == 1


@pytest.mark.parametrize('stage', ['after_approved', 'after_manifest', 'before_projection_commit'])
def test_a_crash_resumes_with_the_same_command(env, planned, tmp_path, stage):
    service, now = env
    meta, rows, cards = prepare(service, planned[0])
    row = pick(rows, False)
    service.fault = lambda current: (_ for _ in ()).throw(OSError()) if current == stage else None
    first = migration.apply(meta, rows, cards, service.work, invoker(service), ACTOR,
                            tmp_path / 'r.jsonl', {row['knowledgeId']})
    assert first['statuses'] == {503: 1}
    with service.store.unit() as unit:
        assert unit.get('card', row['knowledgeId']) is None  # the ledger commits last
    service.fault = lambda current: None
    now[0] += 100
    second = migration.apply(meta, rows, cards, service.work, invoker(service), ACTOR,
                             tmp_path / 'r.jsonl', {row['knowledgeId']})
    assert second['statuses'] == {200: 1}
    assert count(service.canonical.store, 'approved') == 1
    assert migration.verify([row], service.canonical)['matched'] == 1
    assert call(service, 'reader', 'GET', 'published/' + row['knowledgeId'])[1]['generation'] == 1


def migrate_event(meta, row, version, **overrides):
    data = {'workVersionId': version, 'rawSha256': row['rawSha256'], 'kind': row['kind'],
            'applicability': row['applicability'], 'domain': meta['domain'], 'audience': meta['audience'],
            'expiresAt': meta['expiresAt'], 'cardVersion': row['cardVersion'], 'reason': meta['reason'],
            'evidence': {**{k: meta['evidence'][k] for k in ('id', 'version', 'sha256')}, 'locator': row['path']}}
    data.update(overrides.pop('data', {}))
    body = {'actor': ACTOR, 'idempotencyKey': 'migrate-test', 'knowledgeId': row['knowledgeId'], 'data': data}
    body.update(overrides)
    return {'commonKnowledgeMigration': body}


def test_migration_guards(env, planned):
    service, _now = env
    meta, rows, cards = prepare(service, planned[0])
    row, other = rows[0], rows[1]
    version = service.work.put(row['knowledgeId'], cards[row['knowledgeId']])
    handle = local.api.handle_migration

    def outcome(event, key='migrate-test'):
        event['commonKnowledgeMigration']['idempotencyKey'] = key
        result = handle(event, service)
        return result['status'], result.get('code')

    assert outcome(migrate_event(meta, row, version, data={'rawSha256': 'f' * 64}), 'k1') == (409, 'WorkVersionConflict')
    assert outcome(migrate_event(meta, other, version), 'k2') == (409, 'WorkVersionConflict')
    assert outcome(migrate_event(meta, row, version, data={'evidence': {
        **migrate_event(meta, row, version)['commonKnowledgeMigration']['data']['evidence'], 'sha256': 'e' * 64}}),
        'k3') == (403, 'EvidenceNotPermitted')
    assert outcome(migrate_event(meta, row, version, actor='synthetic-editor'), 'k4') == (403, 'Forbidden')
    assert outcome(migrate_event(meta, row, version, data={'extra': 1}), 'k5') == (400, 'ValidationError')
    assert handle({**migrate_event(meta, row, version), 'other': 1}, service)['status'] == 400
    assert handle(migrate_event(meta, row, version), None) == {'status': 503, 'code': 'StorageNotConfigured'}
    assert outcome(migrate_event(meta, row, version), 'k6')[0] == 200
    # The same card again under another request (e.g. a re-plan) never overwrites the first migration.
    assert outcome(migrate_event(meta, row, version, data={'expiresAt': meta['expiresAt'] - 1}),
                   'k7') == (409, 'AlreadyExists')


def test_only_a_direct_invoke_on_the_recovery_function_reaches_the_migration(monkeypatch):
    api = local.api
    event = {'commonKnowledgeMigration': {}}
    assert api.is_migration(event)
    assert not api.is_migration({**event, 'httpMethod': 'POST'})
    assert not api.is_migration({**event, 'requestContext': {}})
    monkeypatch.setattr(api, 'deployed', lambda: (None, 'editorial', None))
    assert api.lambda_handler(event, None) == {'status': 404, 'code': 'NotFound'}
    monkeypatch.setattr(api, 'deployed', lambda: (None, 'recovery', None))
    assert api.lambda_handler(event, None) == {'status': 503, 'code': 'StorageNotConfigured'}
