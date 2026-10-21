"""Shared encoding plus local synthetic durability adapters; no AWS or remote Git access."""
import contextlib
import hashlib
import json
import pathlib
import sqlite3
import subprocess


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


class LocalGit:
    """Operation commits and immutable version paths permit crash recovery."""

    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        if not (self.root / '.git').exists():
            self.run('init', '--quiet')
            self.run('config', 'user.name', 'Synthetic I1')
            self.run('config', 'user.email', 'synthetic@example.invalid')
            self.run('config', 'core.autocrlf', 'false')

    def run(self, *args):
        return subprocess.check_output(
            ['git', '-c', 'core.hooksPath=/dev/null', '-C', str(self.root), *args],
            stderr=subprocess.DEVNULL).decode('utf-8').strip()

    def write(self, operation, files):
        marker = f'operations/{operation}.json'
        expected = digest({name: digest(data) for name, data in files.items()})
        # Lookup by operation marker, then verify every byte in that exact commit.
        found = self.run('log', '--all', '--format=%H', '--', marker)
        if found:
            commit = found.splitlines()[0]
            saved = json.loads(self.run('show', f'{commit}:{marker}'))
            if saved['hash'] != expected:
                raise ValueError('operation content mismatch')
            for name, data in files.items():
                actual = subprocess.check_output(['git', '-C', str(self.root),
                                                  'show', f'{commit}:{name}'])
                if actual != data:
                    raise ValueError('operation bytes mismatch')
            return commit
        for name, data in {**files, marker: encode({'hash': expected}).encode()}.items():
            path = self.root / name
            if not path.resolve().is_relative_to(self.root) or any(
                    item.is_symlink() for item in [path, *path.parents] if item != self.root.parent):
                raise ValueError('invalid Git path')
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_bytes() != data:
                raise ValueError('immutable Git path conflict')
            path.write_bytes(data)
        self.run('add', '--', *files, marker)
        self.run('commit', '--quiet', '-m', f'I1 operation {operation}')
        return self.run('rev-parse', 'HEAD')

    def read(self, commit, path):
        return subprocess.check_output(['git', '-C', str(self.root), 'show', f'{commit}:{path}'])

    def proposal_tree(self, identifier):
        return self.run('rev-parse', f'HEAD:proposals/{identifier}')


class LocalDistribution:
    """Immutable artifact + CAS manifest adapter in its own SQLite file, apart from the ledger."""

    available = True

    def __init__(self, store):
        self.store = store

    def manifest(self, identifier):
        if not self.available:
            raise OSError('manifest unavailable')
        with self.store.unit() as unit:
            return unit.get('manifest', identifier) or {'generation': 0, 'active': None}

    def artifact(self, key, value):
        with self.store.unit() as unit:
            previous = unit.get('artifact', key)
            if previous is not None and previous != value:
                raise ValueError('immutable artifact conflict')
            unit.put('artifact', key, value)

    def read_artifact(self, key):
        with self.store.unit() as unit:
            return unit.get('artifact', key)

    def compare_swap(self, identifier, expected, active, operation):
        if not self.available:
            raise OSError('manifest unavailable')
        with self.store.unit() as unit:
            current = unit.get('manifest', identifier) or {'generation': 0, 'active': None}
            receipt = unit.get('publication-operation', operation)
            if receipt:
                # A later withdrawal/publication cannot be undone by an older retry.
                return receipt if receipt == current else None
            if current['generation'] != expected:
                return None
            value = {'generation': expected + 1, 'active': active}
            unit.put('manifest', identifier, value)
            unit.put('publication-operation', operation, value)
            return value
