"""DynamoDB ledger plus S3 working and canonical adapters (same contracts as the SQLite I1 adapters)."""
import contextlib
import json
import time
import uuid

from botocore.exceptions import ClientError

from storage import Contention, digest, encode, kb_metadata, sort_key


INDEXES = {'state': ('StateIndex', 'gsiState'), 'submitter': ('SubmitterIndex', 'gsiSubmitterState'),
           'pending': ('PendingIndex', 'gsiPendingActor')}
ACCEPTANCE_TTL_SECONDS = 7 * 24 * 3600
JSON = 'application/json; charset=utf-8'
MARKDOWN = 'text/markdown; charset=utf-8'


class DynamoUnit:
    """Optimistic unit: strongly consistent reads record versions, one TransactWriteItems commits.

    Every key read is re-validated at commit (version match / still absent), so the projection,
    event, idempotency result and lock release are applied together or not at all.
    """

    def __init__(self, ledger):
        self.ledger, self.read, self.written = ledger, {}, {}

    def _load(self, kind, identifier):
        pk = self.ledger.key(kind, identifier)
        if pk not in self.read:
            item = self.ledger.client.get_item(TableName=self.ledger.table, Key={'pk': {'S': pk}},
                                               ConsistentRead=True).get('Item')
            self.read[pk] = (int(item['v']['N']), json.loads(item['value']['S'])) if item else (None, None)
        return pk

    def get(self, kind, identifier):
        pk = self._load(kind, identifier)
        value = self.written[pk][1] if pk in self.written else self.read[pk][1]
        return None if value is None else json.loads(encode(value))

    def put(self, kind, identifier, value):
        pk = self._load(kind, identifier)  # Every write is conditioned on the version it replaces.
        self.written[pk] = (kind, json.loads(encode(value)))

    def delete(self, kind, identifier):
        pk = self._load(kind, identifier)
        self.written[pk] = (kind, None)

    def operation_by_key(self, actor, key):
        pointer = self.get('opkey', digest([actor, key]))
        return self.get('operation', pointer['operationId']) if pointer else None

    def operation(self, identifier):
        return self.get('operation', identifier)

    def target_pending(self, target):
        return self.get('lock', digest(target)) is not None

    def accept_operation(self, identifier, actor, key, request_hash, target):
        self.put('operation', identifier, {'id': identifier, 'actor': actor, 'key': key,
                 'requestHash': request_hash, 'target': target, 'status': 'accepted', 'result': None,
                 'at': int(time.time())})
        self.put('opkey', digest([actor, key]), {'operationId': identifier})
        self.put('lock', digest(target), {'operationId': identifier})

    def finish_operation(self, identifier, status, result):
        operation = self.get('operation', identifier)
        operation.update({'status': status, 'result': result})
        self.put('operation', identifier, operation)
        lock = self.get('lock', digest(operation['target']))
        if lock and lock['operationId'] == identifier:
            self.delete('lock', digest(operation['target']))

    def commit(self):
        if not self.written:
            return  # Read-only units never write; their answers are already strongly consistent.
        items = []
        for pk, (kind, value) in self.written.items():
            version = self.read.get(pk, (None, None))[0]
            condition = ({'ConditionExpression': 'attribute_not_exists(pk)'} if version is None else
                         {'ConditionExpression': '#v = :v', 'ExpressionAttributeNames': {'#v': 'v'},
                          'ExpressionAttributeValues': {':v': {'N': str(version)}}})
            if value is None:
                items.append({'Delete': {'TableName': self.ledger.table, 'Key': {'pk': {'S': pk}},
                                         **condition}})
            else:
                item = {'pk': {'S': pk}, 'v': {'N': str((version or 0) + 1)},
                        'value': {'S': encode(value)}, **self.ledger.index_attributes(kind, value)}
                items.append({'Put': {'TableName': self.ledger.table, 'Item': item, **condition}})
        for pk, (version, _value) in self.read.items():
            if pk in self.written:
                continue
            condition = ({'ConditionExpression': 'attribute_not_exists(pk)'} if version is None else
                         {'ConditionExpression': '#v = :v', 'ExpressionAttributeNames': {'#v': 'v'},
                          'ExpressionAttributeValues': {':v': {'N': str(version)}}})
            items.append({'ConditionCheck': {'TableName': self.ledger.table,
                                             'Key': {'pk': {'S': pk}}, **condition}})
        if len(items) > 100:
            raise ValueError('ledger unit too large')
        try:
            self.ledger.client.transact_write_items(TransactItems=items,
                                                    ClientRequestToken=str(uuid.uuid4()))
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') in {
                    'TransactionCanceledException', 'TransactionConflictException',
                    'ConditionalCheckFailedException'}:
                raise Contention() from None
            raise


class DynamoDbLedger:
    def __init__(self, client, table, namespace=''):
        self.client, self.table, self.namespace = client, table, namespace

    def key(self, kind, identifier):
        return f'{self.namespace}{kind}#{identifier}'

    def index_attributes(self, kind, value):
        """KEYS_ONLY index attributes. No body, context or names are ever projected."""
        attributes = {}
        if kind == 'candidate':
            attributes = {'gsiState': self.namespace + value['state'],
                          'gsiSubmitterState': f'{self.namespace}{value["submittedBy"]}#{value["state"]}',
                          'gsiSort': sort_key(value)}
        elif kind == 'operation' and value['status'] == 'accepted':
            attributes = {'gsiPendingActor': self.namespace + value['actor'],
                          'gsiSort': f'{int(value["at"]):012d}#{value["id"]}'}
        attributes = {name: {'S': text} for name, text in attributes.items()}
        if self.namespace.startswith('acceptance#'):
            # Only synthetic acceptance data expires automatically; business retention is undecided.
            attributes['acceptancePurgeAt'] = {'N': str(int(time.time()) + ACCEPTANCE_TTL_SECONDS)}
        return attributes

    @contextlib.contextmanager
    def unit(self):
        unit = DynamoUnit(self)
        yield unit
        unit.commit()

    def _page(self, index, partition, after, limit):
        name, attribute = INDEXES[index]
        request = {'TableName': self.table, 'IndexName': name, 'Limit': limit,
                   'KeyConditionExpression': '#p = :p', 'ExpressionAttributeNames': {'#p': attribute},
                   'ExpressionAttributeValues': {':p': {'S': partition}}}
        if after is not None:
            request['ExclusiveStartKey'] = after
        response = self.client.query(**request)
        return [item['pk']['S'] for item in response.get('Items', [])], response.get('LastEvaluatedKey')

    def _reread(self, keys):
        values = []
        for pk in keys:
            item = self.client.get_item(TableName=self.table, Key={'pk': {'S': pk}},
                                        ConsistentRead=True).get('Item')
            if item:
                values.append(json.loads(item['value']['S']))
        return values

    def candidates(self, state, submitter=None, after=None, limit=20):
        if submitter is None:
            index, partition = 'state', self.namespace + state
        else:
            index, partition = 'submitter', f'{self.namespace}{submitter}#{state}'
        start = None
        if after is not None:
            identifier = after.split('#', 1)[1]
            start = {'pk': {'S': self.key('candidate', identifier)},
                     INDEXES[index][1]: {'S': partition}, 'gsiSort': {'S': after}}
        keys, last = self._page(index, partition, start, limit)
        page = self._reread(keys)
        return page, last['gsiSort']['S'] if last else None

    def pending_operations(self, actor, limit=50):
        keys, _ = self._page('pending', self.namespace + actor, None, limit)
        return self._reread(keys)



def _missing(error):
    return (error.response.get('Error', {}).get('Code') in {'NoSuchKey', 'NoSuchVersion', '404'}
            or error.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 404)


class S3Work:
    """Versioned working bucket. drafts/{id}.md is edited freely; the ledger pins VersionId+sha256."""

    def __init__(self, client, bucket, prefix=''):
        self.client, self.bucket, self.prefix = client, bucket, prefix

    def key(self, identifier):
        return f'{self.prefix}drafts/{identifier}.md'

    def put(self, identifier, raw, operation=None):
        if operation:
            # A retried operation reuses its own version instead of stacking duplicates.
            try:
                head = self.client.head_object(Bucket=self.bucket, Key=self.key(identifier))
                metadata = head.get('Metadata', {})
                if metadata.get('operation') == operation and metadata.get('sha256') == digest(raw):
                    return head['VersionId']
            except ClientError as error:
                if not _missing(error):
                    raise
        response = self.client.put_object(
            Bucket=self.bucket, Key=self.key(identifier), Body=raw, ContentType=MARKDOWN,
            Metadata={'sha256': digest(raw), **({'operation': operation} if operation else {})})
        return response['VersionId']

    def read(self, identifier, version):
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self.key(identifier),
                                              VersionId=version)
        except ClientError as error:
            if _missing(error) or error.response.get('Error', {}).get('Code') == 'InvalidArgument':
                return None
            raise
        return response['Body'].read()

    def current(self, identifier):
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self.key(identifier))
        except ClientError as error:
            if _missing(error):
                return None, None
            raise
        return response['VersionId'], response['Body'].read()


class S3Canonical:
    """approved/ (immutable), manifests/ (ETag CAS) and published/ (projection of the manifest).

    Generations only grow and the manifest records the operation that wrote it, so a retried
    publish whose manifest was later replaced (e.g. by a withdrawal) can never revive. published/
    is always rebuilt from the latest manifest, so a lost or late projection cannot undo a stop.
    """

    def __init__(self, client, bucket, prefix=''):
        self.client, self.bucket, self.prefix = client, bucket, prefix

    def _get(self, key):
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self.prefix + key)
        except ClientError as error:
            if _missing(error):
                return None, None
            raise
        return response['Body'].read(), response['ETag']

    def _put(self, key, body, content_type, **condition):
        try:
            self.client.put_object(Bucket=self.bucket, Key=self.prefix + key, Body=body,
                                   ContentType=content_type, **condition)
            return True
        except ClientError as error:
            code = error.response.get('Error', {}).get('Code')
            status = error.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if condition and (code in {'PreconditionFailed', 'ConditionalRequestConflict', 'NoSuchKey'}
                              or status in {409, 412, 404}):
                return False
            raise

    def _immutable(self, key, body, content_type):
        if self._put(key, body, content_type, IfNoneMatch='*'):
            return
        if self._get(key)[0] != body:
            raise ValueError('immutable approved conflict')

    def approve(self, key, raw, record):
        self._immutable(f'approved/{key}.md', raw, MARKDOWN)
        self._immutable(f'approved/{key}.json', encode(record).encode('utf-8'), JSON)

    def read_approved(self, key):
        return self._get(f'approved/{key}.md')[0]

    def _manifest(self, identifier):
        body, etag = self._get(f'manifests/{identifier}.json')
        if body is None:
            return {'generation': 0, 'active': None, 'bundle': None, 'operation': None}, None
        return json.loads(body), etag

    def manifest(self, identifier):
        value = self._manifest(identifier)[0]
        return {k: value[k] for k in ('generation', 'active', 'bundle')}

    def compare_swap(self, identifier, expected, active, operation, bundle):
        key = f'manifests/{identifier}.json'
        for _attempt in range(3):
            current, etag = self._manifest(identifier)
            if current['operation'] == operation:
                return {'generation': current['generation'], 'active': current['active']}
            if current['generation'] != expected:
                return None
            value = {'generation': expected + 1, 'active': active, 'bundle': bundle, 'operation': operation}
            if self._put(key, encode(value).encode('utf-8'), JSON,
                         **({'IfMatch': etag} if etag else {'IfNoneMatch': '*'})):
                return {'generation': value['generation'], 'active': active}
            # 412/409: another writer won between read and write. Re-read and decide again.
        raise Contention()

    def project(self, identifier):
        body_key = f'published/{identifier}.md'
        meta_key = body_key + '.metadata.json'
        for _attempt in range(3):
            manifest, etag = self._manifest(identifier)
            current = self._get(body_key)[0]
            if manifest['active'] is None:
                if current is not None:
                    self.client.delete_object(Bucket=self.bucket, Key=self.prefix + body_key)
                if self._get(meta_key)[0] is not None:
                    self.client.delete_object(Bucket=self.bucket, Key=self.prefix + meta_key)
            else:
                raw = self.read_approved(manifest['active'])
                if raw is None:
                    raise OSError('approved object missing')
                if current != raw:
                    self._put(body_key, raw, MARKDOWN)
                metadata = encode(kb_metadata(manifest['bundle'])).encode('utf-8')
                if self._get(meta_key)[0] != metadata:
                    self._put(meta_key, metadata, JSON)
            # Another publish/stop may have swapped the manifest meanwhile: converge on the latest.
            if self._manifest(identifier)[1] == etag:
                return
        raise Contention()

    def read_published(self, identifier):
        return self._get(f'published/{identifier}.md')[0]

    def published_metadata(self, identifier):
        body = self._get(f'published/{identifier}.md.metadata.json')[0]
        return None if body is None else json.loads(body)
