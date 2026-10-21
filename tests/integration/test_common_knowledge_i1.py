"""Synthetic API → durable ledger/Git → exact review → shared read → withdrawal."""
import importlib.util
import json
from pathlib import Path
import threading
from http.server import HTTPServer
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('common_local', ROOT / 'scripts/knowledge/run-common-knowledge-local.py')
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)
from storage import LocalDistribution, LocalGit, Store, digest  # noqa: E402
from service import Failure, Service  # noqa: E402


@pytest.fixture
def env(tmp_path):
    now = [1800000000]
    policy = local.synthetic_policy(now[0])
    store = Store(tmp_path / 'ledger.sqlite3')
    git = LocalGit(tmp_path / 'canonical')
    distribution = LocalDistribution(Store(tmp_path / 'distribution.sqlite3'))
    service = Service(store, git, distribution, policy, enabled=True, clock=lambda: now[0])
    return service, now


def claims(actor):
    return local.synthetic_claims('Bearer synthetic-' + actor)


def call(service, actor, method, path, body=None, revision=None, key=None, query=None):
    headers = {}
    if revision is not None:
        headers['If-Match'] = str(revision)
    if key is not None:
        headers['Idempotency-Key'] = key
    result = local.api.handle({'httpMethod': method, 'path': '/knowledge/' + path,
        'headers': headers, 'body': json.dumps(body or {}), 'queryStringParameters': query,
        'requestContext': {'authorizer': {'claims': claims(actor)}}}, service)
    return result['statusCode'], json.loads(result['body'])


def contribution(kind='unknown_term', suffix='A'):
    value = {'candidateType': kind, 'originRef': {'id': 'synthetic-' + suffix, 'revision': 1},
             'summary': '架空機種' + suffix + 'の用語Z', 'context': '合成の最小文脈。原資料ではない。',
             'domain': 'synthetic', 'audience': 'synthetic', 'permissionId': 'synthetic-sharing'}
    if kind == 'unknown_term':
        value['term'] = '用語Z'
    if kind == 'correction':
        value['targetKnowledgeId'] = 'KH-SYN-PREVIOUS'
        value['targetRevision'] = 1
    value['confirmedHash'] = digest(value)
    return value


def draft(identifier, now, revision=2):
    return {'candidateId': identifier, 'candidateRevision': revision, 'kind': 'term_foundation',
            'markdown': '# 合成の用語Z\n\n架空機種Aの改訂1だけに適用する説明。\n',
            'applicability': '架空機種A・改訂1。他の機種には適用しない。',
            'sourceRefs': [{'id': 'SYN-ORIGINAL', 'version': '1', 'locator': 'p.1',
                            'sha256': 'a' * 64, 'claimType': 'source_verified', 'verified': True}],
            'domain': 'synthetic', 'audience': 'synthetic', 'expiresAt': now + 3600, 'unknowns': []}


def saved(service, now, kind='unknown_term', suffix='A'):
    if kind == 'correction':
        _, previous_card, approval = approved(service, now, 'field_report', 'PREVIOUS')
        assert call(service, 'publisher', 'POST', 'cards/' + previous_card + '/publish',
                    {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '訂正前版の公開'},
                    0, 'baseline-publish')[0] == 200
    status, created = call(service, 'contributor', 'POST', 'contributions', contribution(kind, suffix), key='submit-' + suffix)
    assert status == 201, created
    identifier = created['candidateId']
    assert call(service, 'editor', 'PATCH', 'contributions/' + identifier,
                {'state': 'in_review', 'reason': '確認開始'}, 1, 'receive-' + suffix)[0] == 200
    card = 'KH-SYN-PREVIOUS' if kind == 'correction' else 'KH-SYN-' + suffix
    status, saved = call(service, 'editor', 'PUT', 'cards/' + card + '/draft',
                         draft(identifier, now), 1 if kind == 'correction' else 0, 'save-' + suffix)
    assert status == 200, saved
    return identifier, card, saved


def approved(service, now, kind='unknown_term', suffix='A'):
    identifier, card, version = saved(service, now, kind, suffix)
    revision = version['workingRevision']
    status, review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                         {'bundleHash': version['bundleHash'], 'reason': '原本条件を確認してください'},
                         revision, 'review-' + suffix)
    assert status == 200, review
    decision = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
                'decision': 'approve', 'reason': '合成原本・機種・版・対象外を確認'}
    status, result = call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions',
                         decision, revision, 'approve-' + suffix)
    assert status == 200, result
    return identifier, card, result


@pytest.mark.parametrize('kind', ['field_report', 'unknown_term', 'correction'])
def test_three_entries_persist_approve_publish_both_ai_withdraw(env, kind):
    service, now = env
    identifier, card, approval = approved(service, now[0], kind)
    if kind == 'correction':
        assert call(service, 'reader', 'GET', 'published/' + card)[1]['workingRevision'] == 1
    else:
        assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404
    generation = 1 if kind == 'correction' else 0
    status, manifest = call(service, 'publisher', 'POST', 'cards/' + card + '/publish',
        {'revision': approval['revision'], 'approvalId': approval['approvalId'], 'reason': '別操作で公開'}, generation, 'publish-A')
    assert status == 200, manifest
    # Reopen all persistence adapters, rather than reading an in-memory projection.
    restarted = Service(Store(service.store.filename), LocalGit(service.git.root),
                        LocalDistribution(Store(service.distribution.store.filename)),
                        service.policy, enabled=True, clock=lambda: now[0])
    rag = restarted.guarded_use(claims('reader'), card, lambda value: value)
    agent = restarted.guarded_use(claims('agent'), card, lambda value: value)
    assert rag == agent and rag['workingRevision'] == approval['revision']
    assert digest(rag['markdown'].encode()) == rag['rawSha256']
    metadata = json.loads(restarted.git.read('HEAD', f'proposals/{card}/{approval["revision"]}.json'))
    assert 'knowledge_id' in metadata and 'knowledgeId' not in metadata
    assert digest(metadata) == rag['bundleHash']
    assert call(restarted, 'editor', 'GET', 'contributions/' + identifier)[1]['state'] == 'reflected'
    assert call(restarted, 'publisher', 'POST', 'cards/' + card + '/withdraw',
                {'reason': '合成停止'}, generation + 1, 'withdraw-A')[0] == 200
    assert call(restarted, 'reader', 'GET', 'published/' + card)[0] == 404
    assert call(restarted, 'agent', 'GET', 'published/' + card)[0] == 404


def test_authorization_confirmation_origin_and_version_guards(env):
    service, now = env
    body = contribution()
    for changed in ({**body, 'userId': 'forged'}, {**body, 'role': 'approve'}, {**body, 'approved': True}):
        assert call(service, 'contributor', 'POST', 'contributions', changed, key='forged')[0] == 400
    assert call(service, 'reader', 'POST', 'contributions', body, key='other-owner')[0] == 403
    assert call(service, 'contributor', 'POST', 'contributions', {**body, 'context': 'changed'}, key='stale')[0] == 409
    assert call(service, 'reader', 'GET', 'contributions', query={'scope': 'inbox'})[0] == 403
    identifier, card, version = saved(service, now[0])
    assert call(service, 'viewer', 'PUT', 'cards/' + card + '/draft', draft(identifier, now[0], 3), 1, 'viewer')[0] == 403
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', draft(identifier, now[0], 3), 0, 'old')[0] == 409
    status, repeated = call(service, 'contributor', 'POST', 'contributions', body, key='submit-A')
    assert status == 201 and repeated['candidateId'] == identifier
    other = contribution('unknown_term', 'B')
    assert call(service, 'contributor', 'POST', 'contributions', other, key='submit-A')[0] == 409
    status, inbox = call(service, 'viewer', 'GET', 'contributions', query={'scope': 'inbox', 'state': 'in_review'})
    assert status == 200 and len(inbox['items']) == 1
    assert 'context' not in str(inbox) and 'submittedBy' not in str(inbox)
    assert 'assignee' not in call(service, 'contributor', 'GET', 'contributions/' + identifier)[1]
    service.policy['actors']['synthetic-viewer']['audiences'] = ['another']
    assert call(service, 'viewer', 'GET', 'contributions/' + identifier)[0] == 403
    assert call(service, 'contributor', 'POST', 'contributions', other, key='other')[0] == 201


def test_review_stale_evidence_and_self_approval(env):
    service, now = env
    identifier, card, version = saved(service, now[0])
    status, review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                         {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')
    assert status == 200
    service.policy['actors']['synthetic-editor']['permissions'].append('approve')
    decision = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
                'decision': 'approve', 'reason': '自己承認'}
    assert call(service, 'editor', 'POST', 'cards/' + card + '/decisions', decision, 1, 'self')[0] == 403
    service.policy['actors']['synthetic-contributor']['permissions'].append('approve')
    with pytest.raises(Failure) as own_submission:
        service.decide({'sub': 'synthetic-contributor', 'cognito:groups': ['admin']},
                       'own-submission', card, 1, decision)
    assert own_submission.value.code == 'SelfApprovalDenied'
    oversized = draft(identifier, now[0], 4)
    oversized['markdown'] = '合' * 90000
    with pytest.raises(Failure):
        service.validate_draft(oversized)
    edited = draft(identifier, now[0], 4)
    edited['sourceRefs'][0]['verified'] = False
    status, newer = call(service, 'editor', 'PUT', 'cards/' + card + '/draft', edited, 1, 'edit')
    assert status == 200, newer
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', decision, 1, 'stale')[0] == 409
    assert call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                {'bundleHash': newer['bundleHash'], 'reason': '未確認原本'}, 2, 'unverified')[0] == 409


@pytest.mark.parametrize('stage', ['after_git', 'before_projection_commit'])
def test_git_success_projection_failure_resumes_without_duplicate_commit(env, stage):
    service, now = env
    identifier, card, version = saved(service, now[0])
    body = draft(identifier, now[0], 3)
    def crash(current):
        if current == stage:
            raise OSError('synthetic crash')
    service.fault = crash
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')[0] == 503
    count = service.git.run('rev-list', '--count', 'HEAD')
    service.fault = lambda current: None
    now[0] += 10
    status, result = call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')
    assert status == 200, result
    assert service.git.run('rev-list', '--count', 'HEAD') == count
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')[1] == result


def test_approval_git_projection_crash_pins_actor_time_and_bundle(env):
    service, now = env
    identifier, card, version = saved(service, now[0])
    review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                  {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')[1]
    body = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
            'decision': 'approve', 'reason': '特定版を確認'}
    service.fault = lambda current: (_ for _ in ()).throw(OSError()) if current == 'after_git' else None
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', body, 1, 'approve')[0] == 503
    count = service.git.run('rev-list', '--count', 'HEAD')
    now[0] += 100
    service.fault = lambda current: None
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', body, 1, 'approve')[0] == 200
    assert service.git.run('rev-list', '--count', 'HEAD') == count


def test_manifest_races_expiry_unavailability_and_history_reuse(env):
    service, now = env
    _, card, approval = approved(service, now[0])
    body = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 200
    def withdraw_during_model(value):
        assert call(service, 'publisher', 'POST', 'cards/' + card + '/withdraw', {'reason': '停止'}, 1, 'stop')[0] == 200
        return value['markdown']
    with pytest.raises(Failure):
        service.guarded_use(claims('reader'), card, withdraw_during_model)
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 1, 'stale-publish')[0] == 409
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 2, 'new-publish')[0] == 200
    service.distribution.available = False
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 503
    service.distribution.available = True
    now[0] += 4000
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404


def test_git_failure_and_artifact_only_failure_keep_unpublished(env):
    service, now = env
    original = service.git.write
    service.git.write = lambda *_args: (_ for _ in ()).throw(OSError())
    body = contribution()
    created = call(service, 'contributor', 'POST', 'contributions', body, key='submit')[1]
    identifier = created['candidateId']
    call(service, 'editor', 'PATCH', 'contributions/' + identifier, {'state': 'in_review', 'reason': '開始'}, 1, 'receive')
    status, _ = call(service, 'editor', 'PUT', 'cards/KH-SYN-FAIL/draft', draft(identifier, now[0]), 0, 'save')
    assert status == 503
    assert call(service, 'editor', 'GET', 'cards/KH-SYN-FAIL')[0] == 404
    service.git.write = original
    assert call(service, 'editor', 'PUT', 'cards/KH-SYN-FAIL/draft', draft(identifier, now[0]), 0, 'save')[0] == 200
    _, card, approval = approved(service, now[0], suffix='B')
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_artifact' else None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish',
                {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}, 0, 'publish')[0] == 503
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404
    with service.distribution.store.transaction() as db:
        assert len(service.distribution.store.items(db, 'artifact')) == 1


def test_manifest_success_projection_crash_cannot_undo_later_withdrawal(env):
    service, now = env
    _, card, approval = approved(service, now[0])
    body = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_manifest' else None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 503
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 200
    service.fault = lambda stage: None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/withdraw', {'reason': '停止'}, 1, 'stop')[0] == 200
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 409
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404


def test_forged_evidence_and_revoked_source_permission_are_denied(env):
    service, now = env
    identifier, card, saved_version = saved(service, now[0])
    service.policy['evidence']['SYN-ORIGINAL']['independent'] = False
    assert call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                {'bundleHash': saved_version['bundleHash'], 'reason': '派生の再取得'}, 1, 'cycle')[0] == 403
    service.policy['evidence']['SYN-ORIGINAL']['independent'] = True
    _, published_card, approval = approved(service, now[0], suffix='B')
    assert call(service, 'publisher', 'POST', 'cards/' + published_card + '/publish',
                {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}, 0, 'publish')[0] == 200
    service.policy['evidence']['SYN-ORIGINAL']['expiresAt'] = now[0] - 1
    assert call(service, 'reader', 'GET', 'published/' + published_card)[0] == 403


def test_pending_operation_recovers_original_request_after_restart(env):
    service, now = env
    identifier, card, version = saved(service, now[0])
    body = draft(identifier, now[0], 3)
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_git' else None
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'lost-response')[0] == 503
    pending = call(service, 'editor', 'GET', 'operations')[1]['items']
    assert len(pending) == 1
    operation = pending[0]['operationId']
    assert call(service, 'viewer', 'POST', f'operations/{operation}/retry', {}, key='resume')[0] == 404
    restarted = Service(Store(service.store.filename), LocalGit(service.git.root),
                        LocalDistribution(Store(service.distribution.store.filename)), service.policy,
                        enabled=True, clock=lambda: now[0])
    now[0] += 10
    assert call(restarted, 'editor', 'POST', f'operations/{operation}/retry', {}, key='resume')[0] == 200
    assert call(restarted, 'editor', 'GET', 'operations')[1]['items'] == []
    assert call(restarted, 'editor', 'GET', 'cards/' + card)[1]['workingRevision'] == 2


def test_external_git_edit_invalidates_exact_review_without_overwriting(env):
    service, now = env
    _, card, version = saved(service, now[0])
    review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                  {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')[1]
    changed = service.git.root / f'proposals/{card}/1.md'
    changed.write_text('# 別クライアントからの同時編集\n', encoding='utf-8')
    service.git.run('add', '--', f'proposals/{card}/1.md')
    service.git.run('commit', '--quiet', '-m', 'synthetic concurrent editor')
    body = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
            'decision': 'approve', 'reason': '古い版の承認を試行'}
    status, result = call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', body, 1, 'approve')
    assert status == 409 and result['code'] == 'GitVersionConflict'
    assert changed.read_text(encoding='utf-8') == '# 別クライアントからの同時編集\n'


def test_pagination_is_actor_and_state_bound_and_requires_verified_claims(env):
    service, now = env
    for suffix in ('A', 'B', 'C'):
        assert call(service, 'contributor', 'POST', 'contributions', contribution(suffix=suffix), key=suffix)[0] == 201
    status, first = call(service, 'viewer', 'GET', 'contributions', query={
        'scope': 'inbox', 'state': 'unconfirmed', 'limit': '2'})
    assert status == 200 and len(first['items']) == 2 and first['cursor']
    status, second = call(service, 'viewer', 'GET', 'contributions', query={
        'scope': 'inbox', 'state': 'unconfirmed', 'limit': '2', 'cursor': first['cursor']})
    assert status == 200 and len(second['items']) == 1 and second['cursor'] is None
    assert {v['candidateId'] for v in first['items']}.isdisjoint(v['candidateId'] for v in second['items'])
    assert call(service, 'editor', 'GET', 'contributions', query={
        'scope': 'inbox', 'cursor': first['cursor']})[0] == 400
    assert call(service, 'viewer', 'GET', 'contributions', query={
        'scope': 'inbox', 'state': 'held', 'cursor': first['cursor']})[0] == 400
    assert local.api.handle({'path': '/knowledge/contributions', 'headers': {
        'Authorization': 'Bearer forged-sub-admin'}}, service)['statusCode'] == 401
    with pytest.raises(Failure):
        service.list_candidates({'sub': 'synthetic-viewer', 'cognito:groups': 'superadmin'},
                                'inbox', 'unconfirmed')


def test_disabled_unconfigured_and_loopback_http(env):
    service, now = env
    assert local.api.lambda_handler({}, None)['statusCode'] == 503
    service.enabled = False
    assert call(service, 'viewer', 'GET', 'contributions')[0] == 403
    service.enabled = True
    server = HTTPServer(('127.0.0.1', 0), local.make_handler(service, 'http://localhost:3000'))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        request = Request(f'http://127.0.0.1:{server.server_port}/knowledge/contributions?scope=inbox',
                          headers={'Authorization': 'Bearer synthetic-viewer'})
        with urlopen(request, timeout=5) as response:
            assert response.status == 200
            assert response.headers['Cache-Control'] == 'no-store'
            assert json.load(response)['items'] == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(5)
