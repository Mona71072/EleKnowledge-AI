"""Explicit loopback-only synthetic I1 server. Never contacts AWS or remote Git."""
import argparse
import importlib.util
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
import tempfile
import time
from urllib.parse import parse_qs, urlsplit


MODULES = Path(__file__).resolve().parents[2] / 'lambda/knowledge/common-knowledge'
sys.path.insert(0, str(MODULES))
from storage import LocalDistribution, LocalGit, Store  # noqa: E402
from service import Service  # noqa: E402

spec = importlib.util.spec_from_file_location('common_knowledge_app', MODULES / 'app.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


def synthetic_policy(now=None):
    expires = int(now or time.time()) + 180 * 24 * 3600
    actors = {}
    for actor, permissions in {
        'viewer': ['view', 'read'], 'editor': ['view', 'edit', 'read'],
        'reviewer': ['view', 'approve', 'read'], 'publisher': ['view', 'publish', 'read'],
        'reader': ['read'], 'agent': ['read'], 'contributor': ['read'],
    }.items():
        actors['synthetic-' + actor] = {'domains': ['synthetic'], 'audiences': ['synthetic'],
            'permissions': permissions, 'expiresAt': expires}
    return {'actors': actors, 'cursorSecret': 'synthetic-local-cursor-only-20261022',
            'evidence': {'SYN-ORIGINAL': {'version': '1', 'sha256': 'a' * 64,
                'domain': 'synthetic', 'audience': 'synthetic', 'expiresAt': expires,
                'independent': True, 'sourceVerified': True}},
            'contributions': {'synthetic-sharing': {'actor': 'synthetic-contributor',
                'domain': 'synthetic', 'audience': 'synthetic', 'allowDerived': True,
                'expiresAt': expires, 'retentionPolicyId': 'synthetic-180d'}}}


def synthetic_claims(token):
    actor = token.removeprefix('Bearer ')
    if actor not in {'synthetic-' + name for name in (
            'viewer', 'editor', 'reviewer', 'publisher', 'reader', 'agent', 'contributor')}:
        return {}
    return {'sub': actor, 'cognito:groups': [] if actor in {
        'synthetic-reader', 'synthetic-agent', 'synthetic-contributor'} else ['admin']}


def make_handler(service, origin):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # No tokens, paths, candidate text or personal identifiers in access logs.

        def respond(self, status, value):
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Headers', 'Authorization,Content-Type,If-Match,Idempotency-Key')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,OPTIONS')
            self.end_headers()
            self.wfile.write(value.encode('utf-8'))

        def dispatch(self):
            if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}' or (
                    self.headers.get('Origin') not in (None, origin)):
                return self.respond(403, '{"code":"LocalOriginRequired"}')
            if self.command == 'OPTIONS':
                return self.respond(200, '{}')
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 <= length <= 300 * 1024:
                    return self.respond(400, '{"code":"InputTooLarge"}')
                parsed = urlsplit(self.path)
                body = self.rfile.read(length).decode('utf-8')
                event = {'httpMethod': self.command, 'path': parsed.path, 'body': body,
                    'headers': dict(self.headers), 'queryStringParameters': {
                        k: v[0] for k, v in parse_qs(parsed.query).items()},
                    'requestContext': {'authorizer': {'claims': synthetic_claims(
                        self.headers.get('Authorization', ''))}}}
                result = api.handle(event, service)
                self.respond(result['statusCode'], result['body'])
            except (ValueError, UnicodeError):
                self.respond(400, '{"code":"ValidationError"}')

        do_GET = do_POST = do_PUT = do_PATCH = do_OPTIONS = dispatch
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable-synthetic', action='store_true')
    parser.add_argument('--data-dir', type=Path, default=Path(tempfile.gettempdir()) / 'eleknowledge-common-i1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--origin', default='http://localhost:3000')
    args = parser.parse_args()
    if not args.enable_synthetic:
        parser.error('合成I1のみ: --enable-synthetic を明示してください')
    if args.origin not in {'http://localhost:3000', 'http://127.0.0.1:3000'}:
        parser.error('origin must be a loopback Next development origin')
    directory = args.data_dir.resolve()
    repo = Path(__file__).resolve().parents[2]
    if directory.is_relative_to(repo) or repo.is_relative_to(directory):
        parser.error('保存先はアプリrepo外の合成専用領域にしてください')
    directory.mkdir(parents=True, exist_ok=True)
    service = Service(Store(directory / 'ledger.sqlite3'), LocalGit(directory / 'canonical-git'),
                      LocalDistribution(Store(directory / 'distribution.sqlite3')), synthetic_policy(), enabled=True)
    server = HTTPServer(('127.0.0.1', args.port), make_handler(service, args.origin))
    print(f'Synthetic I1 only: http://127.0.0.1:{args.port}; persistent local ledger ready.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
