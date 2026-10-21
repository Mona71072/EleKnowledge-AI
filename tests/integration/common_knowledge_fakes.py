"""In-memory DynamoDB/S3 doubles for the common-knowledge adapters.

They implement only what the adapters send, with the documented failure semantics: conditional
TransactWriteItems cancel as a whole, GSI pages are KEYS_ONLY and return LastEvaluatedKey whenever
Limit is reached, S3 If-None-Match/If-Match answer 412 (missing If-Match target: 404), buckets are
versioned (DeleteObject adds a delete marker; an old VersionId stays readable).
"""
import copy
import hashlib
import io
import uuid

from botocore.exceptions import ClientError


def client_error(code, status, operation):
    return ClientError({'Error': {'Code': code, 'Message': code},
                        'ResponseMetadata': {'HTTPStatusCode': status}}, operation)


INDEX_KEYS = {'StateIndex': 'gsiState', 'SubmitterIndex': 'gsiSubmitterState',
              'PendingIndex': 'gsiPendingActor'}


class FakeDynamo:
    def __init__(self):
        self.items, self.ghosts, self.transactions = {}, [], 0

    def get_item(self, TableName, Key, ConsistentRead):
        assert ConsistentRead is True
        item = self.items.get(Key['pk']['S'])
        return {'Item': copy.deepcopy(item)} if item else {}

    @staticmethod
    def _holds(item, entry):
        expression = entry.get('ConditionExpression')
        if expression == 'attribute_not_exists(pk)':
            return item is None
        if expression == '#v = :v':
            return item is not None and item['v'] == entry['ExpressionAttributeValues'][':v']
        raise AssertionError(expression)

    def transact_write_items(self, TransactItems, ClientRequestToken):
        assert 1 <= len(TransactItems) <= 100 and ClientRequestToken
        keys = []
        for entry in TransactItems:
            (action, body), = entry.items()
            pk = (body.get('Item') or body['Key'])['pk']['S']
            keys.append(pk)
            if not self._holds(self.items.get(pk), body):
                raise client_error('TransactionCanceledException', 400, 'TransactWriteItems')
        assert len(keys) == len(set(keys)), 'one action per item'
        for entry in TransactItems:
            (action, body), = entry.items()
            if action == 'Put':
                self.items[body['Item']['pk']['S']] = copy.deepcopy(body['Item'])
            elif action == 'Delete':
                self.items.pop(body['Key']['pk']['S'], None)
        self.transactions += 1

    def query(self, TableName, IndexName, Limit, KeyConditionExpression, ExpressionAttributeNames,
              ExpressionAttributeValues, ExclusiveStartKey=None):
        attribute = INDEX_KEYS[IndexName]
        assert ExpressionAttributeNames == {'#p': attribute} and KeyConditionExpression == '#p = :p'
        value = ExpressionAttributeValues[':p']['S']
        rows = [item for item in [*self.items.values(), *self.ghosts]
                if item.get(attribute, {}).get('S') == value]
        rows.sort(key=lambda item: (item['gsiSort']['S'], item['pk']['S']))
        if ExclusiveStartKey:
            start = (ExclusiveStartKey['gsiSort']['S'], ExclusiveStartKey['pk']['S'])
            rows = [item for item in rows if (item['gsiSort']['S'], item['pk']['S']) > start]
        page = [{'pk': item['pk'], attribute: item[attribute], 'gsiSort': item['gsiSort']}
                for item in rows[:Limit]]
        response = {'Items': page}
        if len(page) == Limit:
            response['LastEvaluatedKey'] = page[-1]
        return response


class FakeS3:
    def __init__(self):
        self.versions = {}  # key -> [(version id, body or None for a delete marker, etag, metadata)]

    def latest(self, key):
        versions = self.versions.get(key)
        return versions[-1] if versions and versions[-1][1] is not None else None

    def put_object(self, Bucket, Key, Body, ContentType, IfNoneMatch=None, IfMatch=None, Metadata=None):
        current = self.latest(Key)
        if IfNoneMatch == '*' and current is not None:
            raise client_error('PreconditionFailed', 412, 'PutObject')
        if IfMatch is not None:
            if current is None:
                raise client_error('NoSuchKey', 404, 'PutObject')
            if current[2] != IfMatch:
                raise client_error('PreconditionFailed', 412, 'PutObject')
        version, etag = uuid.uuid4().hex, '"' + hashlib.md5(Body).hexdigest() + '"'
        self.versions.setdefault(Key, []).append((version, Body, etag, dict(Metadata or {})))
        return {'VersionId': version, 'ETag': etag}

    def _find(self, Key, VersionId, operation):
        if VersionId is None:
            found = self.latest(Key)
            if found is None:
                raise client_error('NoSuchKey' if operation == 'GetObject' else '404', 404, operation)
            return found
        found = next((item for item in self.versions.get(Key, []) if item[0] == VersionId), None)
        if found is None or found[1] is None:
            raise client_error('NoSuchVersion', 404, operation)
        return found

    def get_object(self, Bucket, Key, VersionId=None):
        version, body, etag, metadata = self._find(Key, VersionId, 'GetObject')
        return {'Body': io.BytesIO(body), 'ETag': etag, 'VersionId': version, 'Metadata': metadata}

    def head_object(self, Bucket, Key):
        version, _body, etag, metadata = self._find(Key, None, 'HeadObject')
        return {'ETag': etag, 'VersionId': version, 'Metadata': metadata}

    def delete_object(self, Bucket, Key):
        self.versions.setdefault(Key, []).append((uuid.uuid4().hex, None, None, {}))
        return {}

    def list_object_versions(self, Bucket, Prefix):
        return {'Versions': [{'Key': key, 'VersionId': item[0]} for key, items in self.versions.items()
                             if key.startswith(Prefix) for item in items if item[1] is not None]}


class Faulty:
    """Wraps a real or fake client: `fail[name]` is a predicate(kwargs) → exception or None."""

    def __init__(self, client):
        self.client, self.fail, self.calls = client, {}, []

    def __getattr__(self, name):
        method = getattr(self.client, name)

        def call(**kwargs):
            self.calls.append((name, kwargs))
            check = self.fail.get(name)
            error = check(kwargs) if check else None
            if error is not None:
                raise error
            return method(**kwargs)
        return call
