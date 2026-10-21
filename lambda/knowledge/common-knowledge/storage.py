"""Shared encoding plus local synthetic durability adapters; no AWS access."""
import base64
import contextlib
import hashlib
import json
import sqlite3
import uuid


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    data = value if isinstance(value, bytes) else encode(value).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def sort_key(item):
    """Stable list position shared by every ledger adapter and the signed cursor."""
    return f'{int(item["submittedAt"]):012d}#{item["candidateId"]}'


class Contention(Exception):
    """A concurrent write won. The accepted operation stays retryable; it is not rejected."""


class SqliteUnit:
    """One BEGIN IMMEDIATE transaction exposing the ledger's domain operations."""

    def __init__(self, db):
        self.db = db

    def get(self, kind, identifier):
        row = self.db.execute('SELECT value FROM records WHERE kind=? AND id=?',
                              (kind, identifier)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, kind, identifier, value):
        self.db.execute('INSERT INTO records VALUES (?,?,?) ON CONFLICT(kind,id) '
                        'DO UPDATE SET value=excluded.value', (kind, identifier, encode(value)))

    def delete(self, kind, identifier):
        self.db.execute('DELETE FROM records WHERE kind=? AND id=?', (kind, identifier))

    @staticmethod
    def _operation(row):
        if row is None:
            return None
        return {'id': row['id'], 'actor': row['actor'], 'key': row['key'],
                'requestHash': row['request_hash'], 'target': row['target'], 'status': row['status'],
                'result': json.loads(row['result']) if row['result'] else None}

    def operation_by_key(self, actor, key):
        return self._operation(self.db.execute(
            'SELECT * FROM operations WHERE actor=? AND key=?', (actor, key)).fetchone())

    def operation(self, identifier):
        return self._operation(self.db.execute(
            'SELECT * FROM operations WHERE id=?', (identifier,)).fetchone())

    def target_pending(self, target):
        return self.db.execute("SELECT 1 FROM operations WHERE target=? AND status IN "
                               "('accepted','git_written')", (target,)).fetchone() is not None

    def accept_operation(self, identifier, actor, key, request_hash, target):
        self.db.execute('INSERT INTO operations VALUES (?,?,?,?,?,?,NULL)',
                        (identifier, actor, key, request_hash, target, 'accepted'))

    def finish_operation(self, identifier, status, result):
        self.db.execute('UPDATE operations SET status=?, result=? WHERE id=?',
                        (status, encode(result), identifier))


class Store:
    """SQLite is the I1 ledger adapter, never a production persistence default."""

    def __init__(self, filename):
        self.filename = str(filename)
        with self.transaction() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS records (
                    kind TEXT, id TEXT, value TEXT NOT NULL,
                    PRIMARY KEY(kind, id));
                CREATE TABLE IF NOT EXISTS operations (
                    id TEXT PRIMARY KEY, actor TEXT, key TEXT, request_hash TEXT,
                    target TEXT, status TEXT, result TEXT,
                    UNIQUE(actor, key));
                CREATE UNIQUE INDEX IF NOT EXISTS pending_target
                    ON operations(target) WHERE status IN ('accepted', 'git_written');
                CREATE INDEX IF NOT EXISTS candidate_state
                    ON records(kind, json_extract(value, '$.state'), json_extract(value, '$.submittedAt'), id);
            ''')

    @contextlib.contextmanager
    def transaction(self):
        db = sqlite3.connect(self.filename, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @contextlib.contextmanager
    def unit(self):
        with self.transaction() as db:
            yield SqliteUnit(db)

    def candidates(self, state, submitter=None, after=None, limit=20):
        """Index-order page by state (and owner). Callers re-check scope and expiry."""
        sql = ("SELECT value FROM records WHERE kind='candidate' AND json_extract(value,'$.state')=?")
        params = [state]
        if submitter is not None:
            sql += " AND json_extract(value,'$.submittedBy')=?"
            params.append(submitter)
        if after is not None:
            stamp, identifier = after.split('#', 1)
            sql += (" AND (json_extract(value,'$.submittedAt')>? OR "
                    "(json_extract(value,'$.submittedAt')=? AND id>?))")
            params += [int(stamp), int(stamp), identifier]
        sql += " ORDER BY json_extract(value,'$.submittedAt'),id LIMIT ?"
        params.append(limit + 1)
        with self.transaction() as db:
            rows = [json.loads(row[0]) for row in db.execute(sql, params)]
        page = rows[:limit]
        return page, sort_key(page[-1]) if len(rows) > limit else None

    def pending_operations(self, actor, limit=50):
        with self.transaction() as db:
            return [SqliteUnit._operation(row) for row in db.execute(
                "SELECT * FROM operations WHERE actor=? AND status='accepted' LIMIT ?", (actor, limit))]

    @staticmethod
    def get(db, kind, identifier):
        return SqliteUnit(db).get(kind, identifier)

    @staticmethod
    def put(db, kind, identifier, value):
        SqliteUnit(db).put(kind, identifier, value)

    @staticmethod
    def items(db, kind):
        return [json.loads(row[0]) for row in db.execute(
            'SELECT value FROM records WHERE kind=? ORDER BY id', (kind,))]


def kb_metadata(bundle):
    """Bedrock KB sidecar for published/{id}.md. Scalars only; the guard reads the manifest instead."""
    return {'metadataAttributes': {
        'knowledgeId': bundle['knowledgeId'], 'workingRevision': bundle['workingRevision'],
        'kind': bundle['kind'], 'domain': bundle['domain'], 'audience': bundle['audience'],
        'applicability': bundle['applicability'], 'expiresAt': bundle['expiresAt'],
        'bundleHash': bundle['bundleHash'], 'rawSha256': bundle['rawSha256']}}


class LocalWork:
    """Versioned working copy (S3 drafts/ stand-in). Every put keeps a new, never-deleted version."""

    def __init__(self, store):
        self.store = store

    def put(self, identifier, raw, operation=None):
        with self.store.unit() as unit:
            head = unit.get('work-head', identifier)
            # A retried operation reuses its own version instead of stacking duplicates.
            if operation and head and head['operation'] == operation and head['sha256'] == digest(raw):
                return head['versionId']
            version = uuid.uuid4().hex
            unit.put('work-version', f'{identifier}#{version}', {'data': base64.b64encode(raw).decode()})
            unit.put('work-head', identifier, {'versionId': version, 'operation': operation,
                                               'sha256': digest(raw)})
            return version

    def read(self, identifier, version):
        with self.store.unit() as unit:
            value = unit.get('work-version', f'{identifier}#{version}')
        return None if value is None else base64.b64decode(value['data'])

    def current(self, identifier):
        with self.store.unit() as unit:
            head = unit.get('work-head', identifier)
        return (None, None) if head is None else (head['versionId'], self.read(identifier, head['versionId']))


class LocalCanonical:
    """Canonical store (S3 approved/ published/ manifests/ stand-in) in its own SQLite file."""

    available = True

    def __init__(self, store):
        self.store = store

    def _check(self):
        if not self.available:
            raise OSError('canonical store unavailable')

    def approve(self, key, raw, record):
        with self.store.unit() as unit:
            value = {'data': base64.b64encode(raw).decode(), 'record': record}
            previous = unit.get('approved', key)
            if previous is not None and previous != json.loads(encode(value)):
                raise ValueError('immutable approved conflict')
            unit.put('approved', key, value)

    def read_approved(self, key):
        self._check()
        with self.store.unit() as unit:
            value = unit.get('approved', key)
        return None if value is None else base64.b64decode(value['data'])

    def manifest(self, identifier):
        self._check()
        with self.store.unit() as unit:
            value = unit.get('manifest', identifier) or {'generation': 0, 'active': None, 'bundle': None}
        return {k: value[k] for k in ('generation', 'active', 'bundle')}

    def compare_swap(self, identifier, expected, active, operation, bundle):
        """Generations only grow; a retry is recognised only while its own manifest is current."""
        self._check()
        with self.store.unit() as unit:
            current = unit.get('manifest', identifier) or {'generation': 0, 'operation': None}
            if current['operation'] == operation:
                return {'generation': current['generation'], 'active': current['active']}
            if current['generation'] != expected:
                return None
            unit.put('manifest', identifier, {'generation': expected + 1, 'active': active,
                                              'bundle': bundle, 'operation': operation})
            return {'generation': expected + 1, 'active': active}

    def project(self, identifier):
        """Make published/ match the current manifest (SQLite: one transaction, no race)."""
        self._check()
        with self.store.unit() as unit:
            manifest = unit.get('manifest', identifier)
            if manifest is None or manifest['active'] is None:
                unit.delete('published', identifier)
                return
            approved = unit.get('approved', manifest['active'])
            unit.put('published', identifier, {'data': approved['data'],
                                               'metadata': kb_metadata(manifest['bundle'])})

    def read_published(self, identifier):
        self._check()
        with self.store.unit() as unit:
            value = unit.get('published', identifier)
        return None if value is None else base64.b64decode(value['data'])

    def published_metadata(self, identifier):
        with self.store.unit() as unit:
            value = unit.get('published', identifier)
        return None if value is None else value['metadata']
