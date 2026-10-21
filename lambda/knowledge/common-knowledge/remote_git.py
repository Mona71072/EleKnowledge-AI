"""Company Git adapters. Lambda /tmp or a local clone is never the canonical store."""
import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from service import Failure
from storage import digest, encode


# Server-generated paths only. Anything else (including '..', absolute paths or new roots) is refused.
ALLOWED_PATH = re.compile(r'^(proposals|cards|approvals)/[A-Za-z0-9][A-Za-z0-9_-]{0,79}/[1-9][0-9]{0,8}\.(md|json)$'
                          r'|^operations/[0-9a-f-]{36}\.json$')


class UnconfiguredGit:
    """Selected while the company Git product, repository, path and credentials are undecided."""

    configured = False

    def write(self, operation, files):
        raise Failure(503, 'GitNotConfigured')

    def read(self, commit, path):
        raise Failure(503, 'GitNotConfigured')

    def proposal_tree(self, identifier):
        raise Failure(503, 'GitNotConfigured')


class GitHubCompatibleGit:
    """Candidate adapter for a GitHub-compatible REST Git Data API (blobs/trees/commits/refs).

    Exactly-once per operation: the operation marker commit is looked up on the branch and every
    byte re-verified before reuse. Ref updates are non-force, so a concurrent head is rebased onto a
    bounded number of times and an edit of the same path is refused rather than overwritten.
    """

    def __init__(self, api_base, repository, branch, root, token, transport=None, attempts=3):
        parsed = urllib.parse.urlsplit(api_base)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.query or parsed.fragment:
            raise ValueError('Git API must be an explicit HTTPS base URL')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('invalid repository')
        if not re.fullmatch(r'[A-Za-z0-9_./-]{1,100}', branch) or '..' in branch:
            raise ValueError('invalid branch')
        if root and not re.fullmatch(r'[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*', root):
            raise ValueError('invalid root')
        self.base = api_base.rstrip('/') + '/repos/' + repository
        self.host = parsed.hostname
        self.branch, self.root, self.token = branch, root, token
        self.transport, self.attempts = transport or self._urlopen, attempts

    def _urlopen(self, method, url, headers, body):
        request = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    def _call(self, method, path, body=None, ok=(200, 201)):
        url = self.base + path
        if urllib.parse.urlsplit(url).hostname != self.host:
            raise ValueError('unexpected Git host')
        headers = {'Authorization': 'Bearer ' + self.token(), 'Accept': 'application/vnd.github+json',
                   'Content-Type': 'application/json'}
        status, raw = self.transport(method, url, headers, None if body is None else encode(body).encode())
        if status not in ok:
            return status, None
        return status, json.loads(raw.decode('utf-8')) if raw else None

    def _path(self, name):
        if not ALLOWED_PATH.fullmatch(name):
            raise ValueError('Git path not allowed')
        return f'{self.root}/{name}' if self.root else name

    def _file(self, ref, name):
        quoted = urllib.parse.quote(self._path(name))
        status, value = self._call('GET', f'/contents/{quoted}?ref={urllib.parse.quote(ref)}', ok=(200,))
        if status == 404:
            return None
        if value is None or value.get('type') != 'file' or value.get('encoding') != 'base64':
            raise OSError('Git read failed')
        return base64.b64decode(value['content'])

    def _head(self):
        status, value = self._call('GET', '/git/ref/heads/' + urllib.parse.quote(self.branch), ok=(200,))
        if value is None:
            raise OSError('Git head unavailable')
        return value['object']['sha']

    def _marker_commit(self, marker):
        query = urllib.parse.urlencode({'sha': self.branch, 'path': self._path(marker), 'per_page': 1})
        status, value = self._call('GET', '/commits?' + query, ok=(200,))
        if value is None:
            raise OSError('Git history unavailable')
        return value[0]['sha'] if value else None

    def write(self, operation, files):
        marker = f'operations/{operation}.json'
        expected = digest({name: digest(data) for name, data in files.items()})
        payload = {**files, marker: encode({'hash': expected}).encode()}
        for name in payload:
            self._path(name)
        for _attempt in range(self.attempts):
            found = self._marker_commit(marker)
            if found:
                for name, data in payload.items():
                    if self._file(found, name) != data:
                        raise ValueError('operation bytes mismatch')
                return found
            head = self._head()
            for name, data in payload.items():
                current = self._file(head, name)
                if current is not None and current != data:
                    raise ValueError('immutable Git path conflict')
            _, commit = self._call('GET', '/git/commits/' + head, ok=(200,))
            tree = []
            for name, data in payload.items():
                _, blob = self._call('POST', '/git/blobs', {
                    'content': base64.b64encode(data).decode(), 'encoding': 'base64'})
                tree.append({'path': self._path(name), 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
            _, created_tree = self._call('POST', '/git/trees', {'base_tree': commit['tree']['sha'], 'tree': tree})
            _, created = self._call('POST', '/git/commits', {
                'message': f'Knowledge operation {operation}', 'tree': created_tree['sha'], 'parents': [head]})
            status, _ = self._call('PATCH', '/git/refs/heads/' + urllib.parse.quote(self.branch),
                                   {'sha': created['sha'], 'force': False}, ok=(200,))
            if status == 200:
                return created['sha']
            if status not in (409, 422):
                raise OSError('Git ref update failed')
            # Another writer moved the head: re-check the marker and immutable paths on the new head.
        raise OSError('Git head kept moving')

    def read(self, commit, path):
        data = self._file(self.branch if commit == 'HEAD' else commit, path)
        if data is None:
            raise OSError('Git object missing')
        return data

    def proposal_tree(self, identifier):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', identifier):
            raise ValueError('invalid identifier')
        _, commit = self._call('GET', '/git/commits/' + self._head(), ok=(200,))
        sha = commit['tree']['sha']
        segments = [*(self.root.split('/') if self.root else []), 'proposals', identifier]
        for segment in segments:
            _, tree = self._call('GET', '/git/trees/' + sha, ok=(200,))
            entry = next((item for item in tree['tree'] if item['path'] == segment and item['type'] == 'tree'), None)
            if entry is None:
                raise OSError('Git tree missing')
            sha = entry['sha']
        return sha
