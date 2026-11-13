"""I1 scenarios on the DynamoDB ledger + S3 working/canonical adapters, plus factory/route guards.

Default: in-memory doubles. With COMMON_KNOWLEDGE_ACCEPTANCE_TABLE / _BUCKET / _WORK_BUCKET (and AWS
credentials), the same scenarios run against the deployed itai table and buckets in a synthetic,
auto-expiring namespace (`acceptance#…` items, `acceptance/…` objects).
"""
import json
import os
import uuid

import pytest

import test_common_knowledge_i1 as i1
from common_knowledge_fakes import FakeDynamo, FakeS3, Faulty, client_error

from aws_adapters import DynamoDbLedger, S3Canonical, S3Work  # noqa: E402
from factory import ConfigurationError, Unavailable, build  # noqa: E402
from service import Service  # noqa: E402
from storage import Contention, digest  # noqa: E402

call, contribution, draft, claims = i1.call, i1.contribution, i1.draft, i1.claims
REAL_TABLE = os.environ.get('COMMON_KNOWLEDGE_ACCEPTANCE_TABLE')
REAL_BUCKET = os.environ.get('COMMON_KNOWLEDGE_ACCEPTANCE_BUCKET')
REAL_WORK_BUCKET = os.environ.get('COMMON_KNOWLEDGE_ACCEPTANCE_WORK_BUCKET')
BACKENDS = ['fake'] + (['aws'] if REAL_TABLE and REAL_BUCKET and REAL_WORK_BUCKET else [])


class Backend:
    def __init__(self, kind, tmp_path):
        self.kind, self.now = kind, [1800000000]
        if kind == 'aws':
            import boto3
            self.now[0] = int(__import__('time').time())
            run = uuid.uuid4().hex[:12]
            self.dynamo, self.s3 = Faulty(boto3.client('dynamodb')), Faulty(boto3.client('s3'))
            self.work_s3 = Faulty(boto3.client('s3'))
            self.namespace, self.prefix = f'acceptance#{run}#', f'acceptance/{run}/'
            self.table, self.bucket, self.work_bucket = REAL_TABLE, REAL_BUCKET, REAL_WORK_BUCKET
        else:
            self.dynamo, self.s3, self.work_s3 = Faulty(FakeDynamo()), Faulty(FakeS3()), Faulty(FakeS3())
            self.namespace, self.prefix = 'acceptance#fake#', 'acceptance/fake/'
            self.table, self.bucket, self.work_bucket = 't', 'b', 'w'
        self.policy = i1.local.synthetic_policy(self.now[0])
        self.service = self.restart()

    def restart(self):
        """New adapters on the same durable stores: nothing survives in process memory."""
        return Service(DynamoDbLedger(self.dynamo, self.table, self.namespace),
                       S3Work(self.work_s3, self.work_bucket, self.prefix),
                       S3Canonical(self.s3, self.bucket, self.prefix), self.policy,
                       enabled=True, clock=lambda: self.now[0])

    def work_versions(self, card):
        key = f'{self.prefix}drafts/{card}.md'
        listed = self.work_s3.list_object_versions(Bucket=self.work_bucket, Prefix=key)
        return len([item for item in listed.get('Versions', []) if item['Key'] == key])


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path):
    return Backend(request.param, tmp_path)


def eventually(backend, check, produce):
    """GSI pages are eventually consistent on DynamoDB; the base-table re-read is not."""
    for _attempt in range(1 if backend.kind == 'fake' else 20):
        value = produce()
        if check(value):
            return value
        __import__('time').sleep(0.5)
    return value


def saved(backend, kind='unknown_term', suffix='A'):
    return i1.saved(backend.service, backend.now[0], kind, suffix)


def approved(backend, kind='unknown_term', suffix='A'):
    return i1.approved(backend.service, backend.now[0], kind, suffix)


@pytest.mark.parametrize('kind', ['field_report', 'unknown_term', 'correction'])
def test_three_entries_publish_both_ai_withdraw_after_restart(backend, kind):
    service, now = backend.service, backend.now
    identifier, card, approval = approved(backend, kind)
    generation = 1 if kind == 'correction' else 0
    status, manifest = call(service, 'publisher', 'POST', 'cards/' + card + '/publish', {
        'revision': approval['revision'], 'approvalId': approval['approvalId'], 'reason': '別操作で公開'},
        generation, 'publish-A')
    assert status == 200, manifest
    restarted = backend.restart()
    rag = restarted.guarded_use(claims('reader'), card, lambda value: value)
    agent = restarted.guarded_use(claims('agent'), card, lambda value: value)
    assert rag == agent and rag['workingRevision'] == approval['revision']
    assert digest(rag['markdown'].encode()) == rag['rawSha256']
    assert call(restarted, 'editor', 'GET', 'contributions/' + identifier)[1]['state'] == 'reflected'
    attributes = restarted.canonical.published_metadata(card)['metadataAttributes']
    assert attributes['bundleHash'] == rag['bundleHash'] and attributes['domain'] == 'synthetic'
    assert restarted.canonical.read_approved(approval['approvedKey']).decode() == rag['markdown']
    assert call(restarted, 'publisher', 'POST', 'cards/' + card + '/withdraw',
                {'reason': '合成停止'}, generation + 1, 'withdraw-A')[0] == 200
    assert call(restarted, 'reader', 'GET', 'published/' + card)[0] == 404
    assert restarted.canonical.read_published(card) is None
    assert restarted.canonical.published_metadata(card) is None


@pytest.mark.parametrize('stage', ['after_work', 'before_projection_commit'])
def test_work_write_success_projection_failure_resumes_once(backend, stage):
    service = backend.service
    identifier, card, _ = saved(backend)
    body = draft(identifier, backend.now[0], 3)
    service.fault = lambda current: (_ for _ in ()).throw(OSError()) if current == stage else None
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')[0] == 503
    versions = backend.work_versions(card)
    restarted = backend.restart()
    backend.now[0] += 10
    status, result = call(restarted, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')
    assert status == 200, result
    assert backend.work_versions(card) == versions
    assert call(restarted, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'retry')[1] == result


def test_lost_commit_race_is_retryable_not_rejected(backend):
    service = backend.service
    identifier, card, _ = saved(backend)
    body = draft(identifier, backend.now[0], 3)
    failed = []

    def conflict_once(kwargs):
        if not failed and any('Put' in item and '"workingRevision":2' in item['Put']['Item']['value']['S']
                              for item in kwargs['TransactItems']):
            failed.append(True)
            return Contention()
    backend.dynamo.fail['transact_write_items'] = conflict_once
    status, result = call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'race')
    assert (status, result['code']) == (503, 'ConcurrentUpdate')
    backend.dynamo.fail.clear()
    pending = eventually(backend, lambda items: items, lambda: call(service, 'editor', 'GET', 'operations')[1]['items'])
    assert [item['status'] for item in pending] == ['accepted']
    status, result = call(service, 'editor', 'PUT', 'cards/' + card + '/draft', body, 1, 'race')
    assert status == 200 and result['workingRevision'] == 2
    assert call(service, 'editor', 'GET', 'operations')[1]['items'] == []


def test_stale_concurrent_writer_cannot_overwrite_newer_version(backend):
    """Two units read the same candidate; the second commit must fail, never last-writer-wins."""
    ledger = backend.service.store
    with ledger.unit() as unit:
        unit.put('candidate-probe', 'x', {'n': 1})
    first, second = ledger.unit(), ledger.unit()
    a, b = first.__enter__(), second.__enter__()
    a.get('candidate-probe', 'x'), b.get('candidate-probe', 'x')
    a.put('candidate-probe', 'x', {'n': 2})
    first.__exit__(None, None, None)
    b.put('candidate-probe', 'x', {'n': 3})
    with pytest.raises(Contention):
        second.__exit__(None, None, None)
    with ledger.unit() as unit:
        assert unit.get('candidate-probe', 'x') == {'n': 2}


def test_unprojected_and_lost_response_cannot_revive_withdrawn_generation(backend):
    service = backend.service
    _, card, approval = approved(backend)
    body = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    # The manifest CAS succeeds, then the process dies before published/ is projected.
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_manifest' else None
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'lost')[0] == 503
    service.fault = lambda stage: None
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 503
    # A retry while still current is recognised by operation id (no second generation) and projects.
    retried = backend.restart()
    retried.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'before_projection_commit' else None
    assert call(retried, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'lost')[0] == 503
    assert retried.canonical.manifest(card)['generation'] == 1
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 200
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/withdraw', {'reason': '停止'}, 1, 'stop')[0] == 200
    status, result = call(backend.restart(), 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'lost')
    assert (status, result['code']) == (409, 'ManifestConflict')
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404
    assert service.canonical.read_published(card) is None


def test_late_projection_converges_on_a_concurrent_withdrawal(backend):
    """A publish whose published/ write lands after a stop re-reads the manifest and removes it."""
    service = backend.service
    _, card, approval = approved(backend)
    body = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    stopped = []

    def stop_first(kwargs):
        if not stopped and kwargs['Key'] == f'{backend.prefix}published/{card}.md':
            stopped.append(call(backend.restart(), 'publisher', 'POST', 'cards/' + card + '/withdraw',
                                {'reason': '同時停止'}, 1, 'stop')[0])
    backend.s3.fail['put_object'] = stop_first
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 200
    backend.s3.fail.clear()
    assert stopped == [200]
    assert service.canonical.manifest(card) == {'generation': 2, 'active': None, 'bundle': None}
    assert service.canonical.read_published(card) is None
    assert service.canonical.published_metadata(card) is None
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404


def test_manifest_unavailable_expiry_and_stale_publish(backend):
    service = backend.service
    _, card, approval = approved(backend)
    body = {'revision': 1, 'approvalId': approval['approvalId'], 'reason': '公開'}
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 0, 'publish')[0] == 200
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/withdraw', {'reason': '停止'}, 1, 'stop')[0] == 200
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 1, 'stale')[0] == 409
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish', body, 2, 'again')[0] == 200
    backend.s3.fail['get_object'] = lambda kwargs: client_error('ServiceUnavailable', 503, 'GetObject')
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 503
    backend.s3.fail.clear()
    backend.now[0] += 4000
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 404


def test_short_pages_strong_reread_and_bound_cursor(backend):
    service = backend.service
    for suffix in ('A', 'B', 'C'):
        assert call(service, 'contributor', 'POST', 'contributions', contribution(suffix=suffix), key=suffix)[0] == 201
    eventually(backend, lambda page: len(page['items']) == 3, lambda: call(
        service, 'viewer', 'GET', 'contributions', query={'scope': 'inbox', 'state': 'unconfirmed'})[1])
    status, first = call(service, 'viewer', 'GET', 'contributions', query={
        'scope': 'inbox', 'state': 'unconfirmed', 'limit': '2'})
    assert status == 200 and len(first['items']) == 2 and first['cursor']
    moved = first['items'][0]['candidateId']
    assert call(service, 'editor', 'PATCH', 'contributions/' + moved,
                {'state': 'in_review', 'reason': '開始'}, 1, 'move')[0] == 200
    status, second = call(service, 'viewer', 'GET', 'contributions', query={
        'scope': 'inbox', 'state': 'unconfirmed', 'limit': '2', 'cursor': first['cursor']})
    assert status == 200 and len(second['items']) == 1
    mine = eventually(backend, lambda page: len(page['items']) == 2, lambda: call(
        service, 'contributor', 'GET', 'contributions', query={'scope': 'mine', 'state': 'unconfirmed'})[1])
    assert moved not in {item['candidateId'] for item in mine['items']} and len(mine['items']) == 2
    assert call(service, 'editor', 'GET', 'contributions', query={
        'scope': 'inbox', 'state': 'unconfirmed', 'cursor': first['cursor']})[0] == 400


def test_stale_index_entry_is_not_authority():
    backend = Backend('fake', __import__('pathlib').Path(__import__('tempfile').mkdtemp()))
    service = backend.service
    created = call(service, 'contributor', 'POST', 'contributions', contribution(), key='A')[1]
    call(service, 'editor', 'PATCH', 'contributions/' + created['candidateId'],
         {'state': 'held', 'reason': '保留', 'resumeCondition': '原本確認後'}, 1, 'hold')
    stale = dict(backend.dynamo.client.items[service.store.key('candidate', created['candidateId'])])
    stale['gsiState'] = {'S': service.store.namespace + 'unconfirmed'}
    backend.dynamo.client.ghosts.append(stale)
    status, page = call(service, 'viewer', 'GET', 'contributions', query={'scope': 'inbox', 'state': 'unconfirmed'})
    assert status == 200 and page['items'] == []
    assert all(set(item) <= {'pk', 'v', 'value', 'gsiState', 'gsiSubmitterState', 'gsiSort',
                             'gsiPendingActor', 'acceptancePurgeAt'}
               for item in backend.dynamo.client.items.values())


def test_pending_operation_recovers_after_restart(backend):
    service = backend.service
    identifier, card, _ = saved(backend)
    service.fault = lambda stage: (_ for _ in ()).throw(OSError()) if stage == 'after_work' else None
    assert call(service, 'editor', 'PUT', 'cards/' + card + '/draft', draft(identifier, backend.now[0], 3),
                1, 'lost')[0] == 503
    operation = eventually(backend, lambda items: items, lambda: call(
        service, 'editor', 'GET', 'operations')[1]['items'])[0]['operationId']
    assert call(service, 'viewer', 'POST', f'operations/{operation}/retry', {}, key='resume')[0] == 404
    restarted = backend.restart()
    assert call(restarted, 'editor', 'POST', f'operations/{operation}/retry', {}, key='resume')[0] == 200
    assert call(restarted, 'editor', 'GET', 'operations')[1]['items'] == []
    assert call(restarted, 'editor', 'GET', 'cards/' + card)[1]['workingRevision'] == 2


def test_pinned_version_survives_later_working_edits(backend):
    service = backend.service
    _, card, version = saved(backend)
    later = service.work.put(card, '# 別の編集\n'.encode('utf-8'))
    assert later != version['workVersionId']
    assert digest(service.work.read(card, version['workVersionId'])) == version['rawSha256']
    assert service.work.read(card, '0' * 32) is None
    status, review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                          {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, 1, 'review')
    assert status == 200 and review['workVersionId'] == version['workVersionId']


ENV = {'COMMON_KNOWLEDGE_RESPONSIBILITY': 'intake', 'COMMON_KNOWLEDGE_ENABLED': 'false',
       'COMMON_KNOWLEDGE_ALLOWED_ORIGIN': 'https://itai.example.invalid',
       'COMMON_KNOWLEDGE_POLICY_TABLE': 'policy-table', 'COMMON_KNOWLEDGE_LEDGER_TABLE': 'ledger-table',
       'COMMON_KNOWLEDGE_CANONICAL_BUCKET': 'canonical-bucket', 'COMMON_KNOWLEDGE_WORK_BUCKET': 'work-bucket',
       'COMMON_KNOWLEDGE_CURSOR_SECRET_ARN': 'arn:aws:secretsmanager:ap-northeast-1:000000000000:secret:cursor-AbCdEf'}


class FakeBoto:
    def __init__(self, dynamo=None, secret='s' * 48):
        self.dynamo, self.secret, self.made = dynamo or FakeDynamo(), secret, []

    def client(self, name):
        self.made.append(name)
        if name == 'dynamodb':
            return self.dynamo
        if name == 's3':
            return FakeS3()
        secret = self.secret

        class Secrets:
            def get_secret_value(self, SecretId):
                return {'SecretString': secret}
        return Secrets()


@pytest.mark.parametrize('change', [
    {'COMMON_KNOWLEDGE_RESPONSIBILITY': 'all'}, {'COMMON_KNOWLEDGE_ENABLED': 'yes'},
    {'COMMON_KNOWLEDGE_RESPONSIBILITY': 'editorial', 'COMMON_KNOWLEDGE_WORK_BUCKET': ''},
    {'COMMON_KNOWLEDGE_RESPONSIBILITY': 'editorial', 'COMMON_KNOWLEDGE_CANONICAL_BUCKET': ''},
    {'COMMON_KNOWLEDGE_RESPONSIBILITY': 'reader', 'COMMON_KNOWLEDGE_CANONICAL_BUCKET': 'a/b'},
    {'COMMON_KNOWLEDGE_ALLOWED_ORIGIN': 'http://itai.example.invalid'}, {'COMMON_KNOWLEDGE_ALLOWED_ORIGIN': '*'},
    {'COMMON_KNOWLEDGE_LEDGER_TABLE': ''}, {'COMMON_KNOWLEDGE_CURSOR_SECRET_ARN': 'cursor'},
    {'COMMON_KNOWLEDGE_POLICY_TABLE': ''}])
def test_factory_rejects_incomplete_or_widened_configuration(change):
    with pytest.raises(ConfigurationError):
        build({**ENV, **change}, FakeBoto())


def test_factory_scopes_stores_and_routes_by_responsibility():
    app = i1.local.api  # path-loaded: a bare `import app` collides with other Lambdas in a full run
    boto = FakeBoto()
    service, responsibility, origin = build({**ENV, 'COMMON_KNOWLEDGE_RESPONSIBILITY': 'reader'}, boto)
    assert isinstance(service.store, Unavailable) and 'secretsmanager' not in boto.made
    assert isinstance(service.work, Unavailable) and service.enabled is False
    event = {'httpMethod': 'GET', 'path': '/knowledge/published/KH-SYN-A',
             'requestContext': {'authorizer': {'claims': {'sub': 'someone'}}}}
    result = app.handle(event, service, responsibility, origin)
    assert result['statusCode'] == 403 and json.loads(result['body'])['code'] == 'FeatureUnavailable'
    assert result['headers']['Access-Control-Allow-Origin'] == 'https://itai.example.invalid'
    service.enabled = True
    assert app.handle(event, service, responsibility, origin)['statusCode'] == 404  # nothing published
    publish = {**event, 'httpMethod': 'POST', 'path': '/knowledge/cards/KH-SYN-A/publish'}
    assert app.handle(publish, service, responsibility, origin)['statusCode'] == 404
    intake, _, _ = build({**ENV, 'COMMON_KNOWLEDGE_ENABLED': 'true'}, FakeBoto(boto.dynamo))
    assert isinstance(intake.canonical, Unavailable) and isinstance(intake.work, Unavailable)
    editorial, _, _ = build({**ENV, 'COMMON_KNOWLEDGE_RESPONSIBILITY': 'editorial'}, FakeBoto())
    assert isinstance(editorial.work, S3Work) and isinstance(editorial.canonical, S3Canonical)
    body = contribution()
    created = app.handle({'httpMethod': 'POST', 'path': '/knowledge/contributions',
                          'headers': {'Idempotency-Key': 'k'}, 'body': json.dumps(body),
                          'requestContext': {'authorizer': {'claims': {'sub': 'synthetic-contributor'}}}},
                         intake, 'intake', origin)
    assert created['statusCode'] == 403 and json.loads(created['body'])['code'] == 'SharingNotPermitted'


def test_factory_policy_table_is_read_per_request_and_shape_checked():
    boto = FakeBoto()
    service, _, _ = build({**ENV, 'COMMON_KNOWLEDGE_ENABLED': 'true'}, boto)
    service.begin_request()
    assert service.policy == {'cursorSecret': 's' * 48}
    boto.dynamo.items['current'] = {'pk': {'S': 'current'}, 'value': {'S': json.dumps({'cursorSecret': 'x'})}}
    with pytest.raises(ConfigurationError):
        service.begin_request()
    boto.dynamo.items['current']['value']['S'] = json.dumps({'actors': {}})
    service.begin_request()
    assert service.policy == {'actors': {}, 'cursorSecret': 's' * 48}


def test_lambda_handler_without_configuration_is_unavailable(monkeypatch):
    app = i1.local.api  # path-loaded: a bare `import app` collides with other Lambdas in a full run
    monkeypatch.setattr(app, '_DEPLOYED', None)
    for name in ENV:
        monkeypatch.delenv(name, raising=False)
    result = app.lambda_handler({'httpMethod': 'GET', 'path': '/knowledge/contributions'}, None)
    assert result['statusCode'] == 503 and json.loads(result['body'])['code'] == 'StorageNotConfigured'
