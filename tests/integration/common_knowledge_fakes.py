"""In-memory DynamoDB/S3/GitHub-compatible doubles for the common-knowledge adapters.

They implement only what the adapters send, with the documented failure semantics: conditional
TransactWriteItems cancel as a whole, GSI pages are KEYS_ONLY and return LastEvaluatedKey whenever
Limit is reached, S3 If-None-Match/If-Match answer 412 (missing If-Match target: 404).
"""
import base64
import copy
import hashlib
import io
import json

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
        self.objects = {}

    def put_object(self, Bucket, Key, Body, ContentType, IfNoneMatch=None, IfMatch=None):
        current = self.objects.get(Key)
        if IfNoneMatch == '*' and current is not None:
            raise client_error('PreconditionFailed', 412, 'PutObject')
        if IfMatch is not None:
            if current is None:
                raise client_error('NoSuchKey', 404, 'PutObject')
            if current[1] != IfMatch:
                raise client_error('PreconditionFailed', 412, 'PutObject')
        self.objects[Key] = (Body, '"' + hashlib.md5(Body).hexdigest() + '"')

    def get_object(self, Bucket, Key):
        if Key not in self.objects:
            raise client_error('NoSuchKey', 404, 'GetObject')
        body, etag = self.objects[Key]
        return {'Body': io.BytesIO(body), 'ETag': etag}


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


class FakeGitHub:
    """Minimal GitHub-compatible Git Data API: blobs, trees, commits, refs, contents, commits?path."""

    def __init__(self, branch='main'):
        self.objects, self.branch, self.calls, self.before_patch = {}, branch, [], None
        empty = self._store({'kind': 'tree', 'entries': {}})
        self.head = self._store({'kind': 'commit', 'tree': empty, 'parents': [], 'message': 'init'})

    def _store(self, value):
        sha = hashlib.sha1(json.dumps(value, sort_keys=True).encode()).hexdigest()
        self.objects[sha] = value
        return sha

    def _tree_put(self, tree_sha, parts, blob):
        entries = dict(self.objects[tree_sha]['entries']) if tree_sha else {}
        if len(parts) == 1:
            entries[parts[0]] = ('blob', blob)
        else:
            child = entries.get(parts[0], ('tree', None))[1]
            entries[parts[0]] = ('tree', self._tree_put(child, parts[1:], blob))
        return self._store({'kind': 'tree', 'entries': entries})

    def _lookup(self, commit, path):
        sha = self.objects[commit]['tree']
        for part in path.split('/'):
            entry = self.objects[sha]['entries'].get(part)
            if entry is None:
                return None
            sha = entry[1]
        return sha

    def _history(self, path):
        commit, found = self.head, []
        while commit:
            value = self.objects[commit]
            parent = value['parents'][0] if value['parents'] else None
            if self._lookup(commit, path) != (self._lookup(parent, path) if parent else None):
                found.append(commit)
            commit = parent
        return found

    def commit_external(self, path, data):
        """Simulate another client committing directly to the branch."""
        blob = self._store({'kind': 'blob', 'data': base64.b64encode(data).decode()})
        tree = self._tree_put(self.objects[self.head]['tree'], path.split('/'), blob)
        self.head = self._store({'kind': 'commit', 'tree': tree, 'parents': [self.head], 'message': 'external'})

    def __call__(self, method, url, headers, body):
        assert headers['Authorization'] == 'Bearer synthetic-token'
        self.calls.append((method, url))
        path, _, query = url.split('/repos/synthetic/knowledge', 1)[1].partition('?')
        params = dict(item.split('=', 1) for item in query.split('&')) if query else {}
        data = json.loads(body) if body else None
        from urllib.parse import unquote
        if method == 'GET' and path == f'/git/ref/heads/{self.branch}':
            return 200, json.dumps({'object': {'sha': self.head}}).encode()
        if method == 'GET' and path == '/commits':
            found = self._history(unquote(params['path']))
            return 200, json.dumps([{'sha': sha} for sha in found[-1:]]).encode()
        if method == 'GET' and path.startswith('/contents/'):
            ref = unquote(params['ref'])
            commit = self.head if ref == self.branch else ref
            sha = self._lookup(commit, unquote(path[len('/contents/'):]))
            if sha is None or self.objects[sha]['kind'] != 'blob':
                return 404, b'{}'
            return 200, json.dumps({'type': 'file', 'encoding': 'base64',
                                    'content': self.objects[sha]['data']}).encode()
        if method == 'GET' and path.startswith('/git/commits/'):
            value = self.objects[path.rsplit('/', 1)[1]]
            return 200, json.dumps({'tree': {'sha': value['tree']}}).encode()
        if method == 'GET' and path.startswith('/git/trees/'):
            entries = self.objects[path.rsplit('/', 1)[1]]['entries']
            return 200, json.dumps({'tree': [{'path': name, 'type': kind, 'sha': sha}
                                             for name, (kind, sha) in entries.items()]}).encode()
        if method == 'POST' and path == '/git/blobs':
            return 201, json.dumps({'sha': self._store({'kind': 'blob', 'data': data['content']})}).encode()
        if method == 'POST' and path == '/git/trees':
            tree = data['base_tree']
            for entry in data['tree']:
                tree = self._tree_put(tree, entry['path'].split('/'), entry['sha'])
            return 201, json.dumps({'sha': tree}).encode()
        if method == 'POST' and path == '/git/commits':
            sha = self._store({'kind': 'commit', 'tree': data['tree'], 'parents': data['parents'],
                               'message': data['message']})
            return 201, json.dumps({'sha': sha}).encode()
        if method == 'PATCH' and path == f'/git/refs/heads/{self.branch}':
            if self.before_patch:
                hook, self.before_patch = self.before_patch, None
                hook()
            assert data['force'] is False
            if self.objects[data['sha']]['parents'] != [self.head]:
                return 422, b'{"message":"Update is not a fast forward"}'
            self.head = data['sha']
            return 200, b'{}'
        raise AssertionError((method, path))
