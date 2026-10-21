"""DynamoDB ledger and private S3 distribution adapters (same contracts as the SQLite I1 adapters)."""
import contextlib
import json
import time
import uuid

from botocore.exceptions import ClientError

from storage import Contention, digest, encode, sort_key


INDEXES = {'state': ('StateIndex', 'gsiState'), 'submitter': ('SubmitterIndex', 'gsiSubmitterState'),
           'pending': ('PendingIndex', 'gsiPendingActor')}
ACCEPTANCE_TTL_SECONDS = 7 * 24 * 3600


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


class S3Distribution:
    """Private immutable artifacts + ETag-CAS manifest that records the operation that wrote it.

    Generations only grow, so a retried publish whose manifest was later replaced (e.g. by a
    withdrawal) fails the generation check and can never revive; a retry whose manifest is still
    current is recognised by its operation id and returns the same result.
    """

    def __init__(self, client, bucket, prefix=''):
        self.client, self.bucket, self.prefix = client, bucket, prefix

    def _get(self, key):
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=self.prefix + key)
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') in {'NoSuchKey', '404'}:
                return None, None
            raise
        return json.loads(response['Body'].read().decode('utf-8')), response['ETag']

    def _put(self, key, value, **condition):
        try:
            self.client.put_object(Bucket=self.bucket, Key=self.prefix + key,
                                   Body=encode(value).encode('utf-8'),
                                   ContentType='application/json; charset=utf-8', **condition)
            return True
        except ClientError as error:
            code = error.response.get('Error', {}).get('Code')
            status = error.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if code in {'PreconditionFailed', 'ConditionalRequestConflict', 'NoSuchKey'} or status in {
                    409, 412, 404}:
                return False
            raise

    @staticmethod
    def public(manifest):
        return {'generation': manifest['generation'], 'active': manifest['active']}

    def manifest(self, identifier):
        value, _ = self._get(f'manifests/{identifier}.json')
        return self.public(value) if value else {'generation': 0, 'active': None}

    def artifact(self, key, value):
        if self._put(f'artifacts/{key}.json', value, IfNoneMatch='*'):
            return
        previous, _ = self._get(f'artifacts/{key}.json')
        if previous != json.loads(encode(value)):
            raise ValueError('immutable artifact conflict')

    def read_artifact(self, key):
        return self._get(f'artifacts/{key}.json')[0]

    def compare_swap(self, identifier, expected, active, operation):
        key = f'manifests/{identifier}.json'
        for _attempt in range(3):
            current, etag = self._get(key)
            current = current or {'generation': 0, 'active': None, 'operation': None}
            if current.get('operation') == operation:
                return self.public(current)
            if current['generation'] != expected:
                return None
            value = {'generation': expected + 1, 'active': active, 'operation': operation}
            if self._put(key, value, **({'IfMatch': etag} if etag else {'IfNoneMatch': '*'})):
                return self.public(value)
            # 412/409: another writer won between read and write. Re-read and decide again.
        raise Contention()
