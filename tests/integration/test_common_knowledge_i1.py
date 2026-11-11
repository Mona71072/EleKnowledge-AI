"""Synthetic API → durable ledger/working version → exact review → canonical → shared read → withdrawal."""
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
from storage import LocalCanonical, LocalWork, Store, digest  # noqa: E402
from service import Failure, Service  # noqa: E402


@pytest.fixture
def env(tmp_path):
    now = [1800000000]
    policy = local.synthetic_policy(now[0])
    store = Store(tmp_path / 'ledger.sqlite3')
    work = LocalWork(Store(tmp_path / 'work.sqlite3'))
    canonical = LocalCanonical(Store(tmp_path / 'canonical.sqlite3'))
    service = Service(store, work, canonical, policy, enabled=True, clock=lambda: now[0])
    return service, now


def restart(service, now):
    """Reopen every persistence adapter, rather than reading an in-memory projection."""
    return Service(Store(service.store.filename), LocalWork(Store(service.work.store.filename)),
                   LocalCanonical(Store(service.canonical.store.filename)), service.policy,
                   enabled=True, clock=lambda: now[0])


def count(store, kind):
    with store.transaction() as db:
        return len(store.items(db, kind))


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


def draft(identifier, now, revision=2, **overrides):
    return {**{'candidateId': identifier, 'candidateRevision': revision, 'kind': 'term_foundation',
            'markdown': '# 合成の用語Z\n\n架空機種Aの改訂1だけに適用する説明。\n',
            'applicability': '架空機種A・改訂1。他の機種には適用しない。',
            'sourceRefs': [{'id': 'SYN-ORIGINAL', 'version': '1', 'locator': 'p.1',
                            'sha256': 'a' * 64, 'claimType': 'source_verified', 'verified': True}],
            'domain': 'synthetic', 'audience': 'synthetic', 'expiresAt': now + 3600, 'unknowns': []},
            **overrides}


SAFETY_MARKDOWN = '# 合成の用語Z\n\n架空機種Aで感電のおそれがある作業の説明。\n'


def saved(service, now, kind='unknown_term', suffix='A', **overrides):
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
                         draft(identifier, now, **overrides), 1 if kind == 'correction' else 0, 'save-' + suffix)
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
    restarted = restart(service, now)
    rag = restarted.guarded_use(claims('reader'), card, lambda value: value)
    agent = restarted.guarded_use(claims('agent'), card, lambda value: value)
    assert rag == agent and rag['workingRevision'] == approval['revision']
    assert digest(rag['markdown'].encode()) == rag['rawSha256']
    assert approval['approvedKey'] == f'{card}/{approval["revision"]}/{rag["bundleHash"]}'
    assert restarted.canonical.read_approved(approval['approvedKey']).decode() == rag['markdown']
    attributes = restarted.canonical.published_metadata(card)['metadataAttributes']
    assert attributes['knowledgeId'] == card and attributes['bundleHash'] == rag['bundleHash']
    assert 'markdown' not in attributes and 'sourceRefs' not in attributes
    assert call(restarted, 'editor', 'GET', 'contributions/' + identifier)[1]['state'] == 'reflected'
    assert call(restarted, 'publisher', 'POST', 'cards/' + card + '/withdraw',
                {'reason': '合成停止'}, generation + 1, 'withdraw-A')[0] == 200
    assert call(restarted, 'reader', 'GET', 'published/' + card)[0] == 404
    assert call(restarted, 'agent', 'GET', 'published/' + card)[0] == 404
    assert restarted.canonical.read_published(card) is None
    assert restarted.canonical.published_metadata(card) is None


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
    """Self-approval stays denied for a version marked as a §4.3 exception (here: safety wording)."""
    service, now = env
    identifier, card, version = saved(service, now[0], markdown=SAFETY_MARKDOWN)
    assert version['secondReview']['required'] and version['secondReview']['detected'] == ['safety_legal']
    status, review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                         {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')
    assert status == 200
    service.policy['actors']['synthetic-editor']['permissions'].append('approve')
    decision = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
                'decision': 'approve', 'reason': '自己承認'}
    assert call(service, 'editor', 'POST', 'cards/' + card + '/decisions', decision, 1, 'self')[0] == 403
    service.policy['actors']['synthetic-contributor']['permissions'].append('approve')
    with pytest.raises(Failure) as own_submission:
        service.decide({'sub': 'synthetic-contributor'},
                       'own-submission', card, 1, decision)
    assert own_submission.value.code == 'SelfApprovalDenied'
    oversized = draft(identifier, now[0], 4)
    oversized['markdown'] = '合' * 90000
    with pytest.raises(Failure):
        service.validate_draft(oversized)
    edited = draft(identifier, now[0], 4, markdown=SAFETY_MARKDOWN)
    edited['sourceRefs'][0]['verified'] = False
    status, newer = call(service, 'editor', 'PUT', 'cards/' + card + '/draft', edited, 1, 'edit')
    assert status == 200, newer
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', decision, 1, 'stale')[0] == 409
    assert call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                {'bundleHash': newer['bundleHash'], 'reason': '未確認原本'}, 2, 'unverified')[0] == 409


@pytest.mark.parametrize('stage', ['after_work', 'before_projection_commit'])
def test_work_write_success_projection_failure_resumes_without_duplicate_version(env, stage):
    service, now = env
    identifier, card, version = saved(service, now[0])
    body = draft(identifier, now[0], 3)
    def crash(current):
        if current == stage:
            raise OSError('synthetic crash')
    service.fault = crash
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')[0] == 503
    versions = count(service.work.store, 'work-version')
    service.fault = lambda current: None
    now[0] += 10
    status, result = call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')
    assert status == 200, result
    assert count(service.work.store, 'work-version') == versions
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')[1] == result


def test_approval_copy_projection_crash_pins_actor_time_and_bundle(env):
    service, now = env
    identifier, card, version = saved(service, now[0])
    review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                  {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')[1]
    body = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
            'decision': 'approve', 'reason': '特定版を確認'}
    service.fault = lambda current: (_ for _ in ()).throw(OSError()) if current == 'after_approved' else None
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', body, 1, 'approve')[0] == 503
    assert count(service.canonical.store, 'approved') == 1
    now[0] += 100
    service.fault = lambda current: None
    # The approval record is immutable: a retry with a later clock must rewrite identical bytes.
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', body, 1, 'approve')[0] == 200
    assert count(service.canonical.store, 'approved') == 1


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
    service.canonical.available = False
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 503
    service.canonical.available = True
    now[0] += 4000
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404


def test_work_failure_and_unprojected_manifest_keep_unpublished(env):
    service, now = env
    original = service.work.put
    service.work.put = lambda *_args: (_ for _ in ()).throw(OSError())
    body = contribution()
    created = call(service, 'contributor', 'POST', 'contributions', body, key='submit')[1]
    identifier = created['candidateId']
    call(service, 'editor', 'PATCH', 'contributions/' + identifier, {'state': 'in_review', 'reason': '開始'}, 1, 'receive')
    status, _ = call(service, 'editor', 'PUT', 'cards/KH-SYN-FAIL/draft', draft(identifier, now[0]), 0, 'save')
    assert status == 503
    assert call(service, 'editor', 'GET', 'cards/KH-SYN-FAIL')[0] == 404
    service.work.put = original
    assert call(service, 'editor', 'PUT', 'cards/KH-SYN-FAIL/draft', draft(identifier, now[0]), 0, 'save')[0] == 200
    _, card, approval = approved(service, now[0], suffix='B')
    publish = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_manifest' else None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', publish, 0, 'publish')[0] == 503
    # The manifest moved but published/ is not projected: readers refuse rather than guess.
    status, result = call(service, 'reader', 'GET', 'published/' + card)
    assert (status, result['code']) == (503, 'ProjectionPending')
    assert service.canonical.read_published(card) is None
    service.fault = lambda stage: None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', publish, 0, 'publish')[0] == 200
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 200


def test_manifest_success_projection_crash_cannot_undo_later_withdrawal(env):
    service, now = env
    _, card, approval = approved(service, now[0])
    body = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_manifest' else None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 503
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 503
    service.fault = lambda stage: None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/withdraw', {'reason': '停止'}, 1, 'stop')[0] == 200
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 409
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404
    assert service.canonical.read_published(card) is None


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
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_work' else None
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'lost-response')[0] == 503
    pending = call(service, 'editor', 'GET', 'operations')[1]['items']
    assert len(pending) == 1
    operation = pending[0]['operationId']
    assert call(service, 'viewer', 'POST', f'operations/{operation}/retry', {}, key='resume')[0] == 404
    restarted = restart(service, now)
    now[0] += 10
    assert call(restarted, 'editor', 'POST', f'operations/{operation}/retry', {}, key='resume')[0] == 200
    assert call(restarted, 'editor', 'GET', 'operations')[1]['items'] == []
    assert call(restarted, 'editor', 'GET', 'cards/' + card)[1]['workingRevision'] == 2


def test_later_working_edit_cannot_change_the_pinned_version_under_review(env):
    service, now = env
    _, card, version = saved(service, now[0])
    review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                  {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')[1]
    assert review['workVersionId'] == version['workVersionId']
    # The development agent keeps editing drafts/: a new version, never an overwrite.
    edited = '# 別クライアントからの同時編集\n'.encode('utf-8')
    later = service.work.put(card, edited)
    body = {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
            'decision': 'approve', 'reason': '確認した特定版を承認'}
    status, result = call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions', body, 1, 'approve')
    assert status == 200, result
    approved_raw = service.canonical.read_approved(result['approvedKey'])
    assert digest(approved_raw) == version['rawSha256'] and approved_raw != edited
    assert service.work.current(card) == (later, edited)


def test_missing_pinned_working_version_is_refused(env):
    service, now = env
    _, card, version = saved(service, now[0])
    with service.work.store.unit() as unit:
        unit.delete('work-version', f'{card}#{version["workVersionId"]}')
    status, result = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                          {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')
    assert (status, result['code']) == (409, 'WorkVersionConflict')
    assert call(service, 'editor', 'GET', 'cards/' + card)[0] == 409


def test_cli_registers_an_agent_written_version_with_the_iam_editor(env):
    service, now = env
    agent = 'iam:assumed-role/Synthetic/agent-session'
    service.policy['actors'][agent] = {**service.policy['actors']['synthetic-editor']}
    created = call(service, 'contributor', 'POST', 'contributions', contribution(), key='submit')[1]
    identifier = created['candidateId']
    call(service, 'editor', 'PATCH', 'contributions/' + identifier, {'state': 'in_review', 'reason': '開始'}, 1, 'receive')
    raw = '# エージェントが書いた合成の用語Z\n\n架空機種Aだけに適用する。\n'.encode('utf-8')
    written = service.work.put('KH-SYN-CLI', raw)
    fields = {k: v for k, v in draft(identifier, now[0]).items() if k != 'markdown'}
    with pytest.raises(Failure) as missing:
        service.register_draft({'sub': agent}, 'register', 'KH-SYN-CLI', 0, {**fields, 'workVersionId': 'absent'})
    assert missing.value.code == 'WorkVersionMissing'
    service.work.put('KH-SYN-CRLF', b'# CR\r\n')
    with pytest.raises(Failure):
        service.register_draft({'sub': agent}, 'crlf', 'KH-SYN-CRLF', 0,
                               {**fields, 'workVersionId': service.work.current('KH-SYN-CRLF')[0]})
    saved_version = service.register_draft({'sub': agent}, 'register', 'KH-SYN-CLI', 0,
                                           {**fields, 'workVersionId': written})
    assert saved_version['workVersionId'] == written and saved_version['rawSha256'] == digest(raw)
    assert call(service, 'editor', 'GET', 'cards/KH-SYN-CLI')[1]['versions']['1']['editor'] == agent
    review = service.review({'sub': agent}, 'review', 'KH-SYN-CLI', 1,
                            {'bundleHash': saved_version['bundleHash'], 'reason': 'CLIから確認依頼'})
    status, result = call(service, 'reviewer', 'POST', 'cards/KH-SYN-CLI/decisions', {
        'reviewRequestId': review['reviewRequestId'], 'bundleHash': saved_version['bundleHash'],
        'decision': 'approve', 'reason': '特定版を確認'}, 1, 'approve')
    assert status == 200, result
    assert service.canonical.read_approved(result['approvedKey']) == raw


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
    for forged in ({'sub': 'unknown-admin', 'cognito:groups': ['admin']},
                   {'sub': 'synthetic-contributor', 'cognito:groups': 'admin'}):
        with pytest.raises(Failure):
            service.list_candidates(forged, 'inbox', 'unconfirmed')


def test_grants_not_cognito_groups_decide_and_me_shows_live_grants(env):
    service, now = env
    # Admin membership alone grants nothing; a non-admin with the grant can approve.
    service.policy['actors']['admin-only'] = {'domains': [], 'audiences': [], 'permissions': [], 'expiresAt': 0}
    for operation in (lambda c: service.list_candidates(c, 'inbox', 'unconfirmed'),
                      lambda c: service.authorize(c, 'approve', 'synthetic', 'synthetic')):
        with pytest.raises(Failure):
            operation({'sub': 'admin-only', 'cognito:groups': ['admin']})
    assert service.authorize({'sub': 'synthetic-reviewer'}, 'approve', 'synthetic', 'synthetic') == 'synthetic-reviewer'
    status, mine = call(service, 'editor', 'GET', 'me')
    assert status == 200 and mine['actor'] == 'synthetic-editor'
    assert 'edit' in mine['assignment']['permissions'] and [e['id'] for e in mine['evidence']] == ['SYN-ORIGINAL']
    assert call(service, 'contributor', 'GET', 'me')[1]['contributions'][0]['permissionId'] == 'synthetic-sharing'
    assert call(service, 'reader', 'GET', 'me')[1]['evidence'] == []
    now[0] += 365 * 24 * 3600
    assert call(service, 'editor', 'GET', 'me')[1]['assignment'] is None


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
