"""WP3: Git のテーマカード（約 400 枚）を共通知識の S3 正本へ移行する。

設計: docs/design-2026-11-11-knowledge-governance.md §4.11・WP3（2026-11-12 の itai 決定）。

  plan    指定コミットの Git のカードを読み、card-versions.jsonl と照合して、移行の一覧（inventory.jsonl）・
          変換後のカード（cards/*.md）・根拠台帳に足す 1 件（policy-evidence-entry.json）を作る。AWS に触れない。
  apply   変換後のカードを作業用バケット drafts/ へ書き、復旧用 Lambda を直接呼んで 1 枚ずつ
          「作業版の登録→承認→公開」を 1 つの冪等な操作で行う。中断しても同じコマンドで再実行できる。
  verify  公開版（manifest と published/）の件数と本文の hash を inventory と照合する（読み取りのみ）。

変換（frontmatter だけ。本文は変えない）:
  - 旧項目 review_status・publication_status・cloud_approval を外す。status は approved にする。
  - 語彙ファイルの「置き場違い」（移し先があるもの）を model_scope の正しい欄へ移し、card_version を 1 上げる。
    移し先が決まっていないもの（要確認）は変えず、一覧に残す。
  - knowledge_id と card_version は引き継ぐ（保存済みの回答が指す ID と版を保つため）。
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / 'lambda/knowledge/common-knowledge'
CARD_PATH = re.compile(r'^knowledge/cards/(case-summaries|practice-guides)/([^/]+)\.md$')
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')
REMOVED_FIELDS = ('review_status', 'publication_status', 'cloud_approval')
SCOPE_SUMMARY_KEYS = ('lists_model_label', 'product_lines', 'model_abbreviations', 'control_methods',
                      'machine_room', 'door_families', 'door_types', 'conditions', 'excludes')
EVIDENCE_ID = 'GIT-CARDS-MIGRATION'
DEFAULT_DOMAIN, DEFAULT_AUDIENCE = 'elevator-knowhow', 'all-users'
DEFAULT_REASON = '移行による一括登録'
THREE_YEARS = 3 * 365 * 24 * 3600


class PlanError(Exception):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, data=None):
    return subprocess.run(['git', '-C', str(ROOT), *args], input=data, capture_output=True,
                          check=True).stdout


def git_files(commit, paths):
    """Blob bytes at the commit (LF as stored), independent of the working tree's checkout."""
    request = ''.join(f'{commit}:{path}\n' for path in paths).encode('utf-8')
    output, result, offset = git('cat-file', '--batch', data=request), {}, 0
    for path in paths:
        end = output.index(b'\n', offset)
        header = output[offset:end].decode('utf-8').split()
        if header[-1] == 'missing':
            raise PlanError(f'{path} がコミットにありません')
        size = int(header[2])
        result[path] = output[end + 1:end + 1 + size]
        offset = end + 1 + size + 1
    return result


def split_frontmatter(text):
    if not text.startswith('---\n') or '\n---\n' not in text:
        raise PlanError('frontmatter がありません')
    head, body = text[4:].split('\n---\n', 1)
    return head, body


def blocks(head):
    """Top-level YAML keys with their indented continuation lines, in order."""
    result = []
    for line in head.split('\n'):
        if line and not line[0].isspace() and not line.startswith('-') and ':' in line:
            result.append([line.split(':', 1)[0], [line]])
        else:
            if not result:
                if line.strip():
                    raise PlanError('frontmatter の先頭が項目ではありません')
                result.append(['', []])  # leading blank lines are kept as they are
            result[-1][1].append(line)
    return result


def emit_scalar(value):
    if isinstance(value, (list, str, int, float, bool)) or value is None:
        return json.dumps(value, ensure_ascii=False)
    raise PlanError(f'model_scope に書き出せない値があります: {type(value).__name__}')


def move_misplaced(scope, misplaced):
    """Return (new scope, fixes, unresolved). Values only move between list axes."""
    scope = {key: (list(value) if isinstance(value, list) else value) for key, value in scope.items()}
    fixes, unresolved = [], []
    for item in misplaced:
        values = scope.get(item['axis'])
        if not isinstance(values, list) or item['value'] not in values:
            continue
        if not item.get('move_to_axis'):
            unresolved.append({'axis': item['axis'], 'value': item['value'], 'note': item.get('note', '')})
            continue
        values.remove(item['value'])
        if not values:
            del scope[item['axis']]
        target = scope.setdefault(item['move_to_axis'], [])
        if not isinstance(target, list):
            raise PlanError(f'{item["move_to_axis"]} がリストではありません')
        if item['move_to_value'] not in target:
            target.append(item['move_to_value'])
        fixes.append({'from': [item['axis'], item['value']],
                      'to': [item['move_to_axis'], item['move_to_value']]})
    return scope, fixes, unresolved


def convert(raw, misplaced):
    """Git card bytes → (converted bytes, report). Verified by re-parsing, not by trusting the edit."""
    text = raw.decode('utf-8')
    if '\r' in text:
        raise PlanError('CRLF のカードは移行できません')
    head, body = split_frontmatter(text)
    original = yaml.safe_load(head)
    if not isinstance(original, dict):
        raise PlanError('frontmatter が辞書ではありません')
    if original.get('status') not in {'draft', 'approved'}:
        raise PlanError(f'status {original.get("status")!r} は移行の対象外です')
    if type(original.get('card_version')) is not int or original['card_version'] < 1:
        raise PlanError('card_version が不正です')
    scope, fixes, unresolved = move_misplaced(original.get('model_scope') or {}, misplaced)
    version = original['card_version'] + (1 if fixes else 0)
    lines = []
    for key, chunk in blocks(head):
        if key in REMOVED_FIELDS:
            continue
        if key == 'status':
            chunk = ['status: approved']
        elif key == 'card_version':
            chunk = [f'card_version: {version}']
        elif key == 'model_scope' and fixes:
            chunk = ['model_scope:'] + [f'  {name}: {emit_scalar(value)}' for name, value in scope.items()]
        lines += chunk
    converted = '---\n' + '\n'.join(lines) + '\n---\n' + body
    expected = {key: value for key, value in original.items() if key not in REMOVED_FIELDS}
    expected.update({'status': 'approved', 'card_version': version})
    if 'model_scope' in original:
        expected['model_scope'] = scope
    new_head, new_body = split_frontmatter(converted)
    if yaml.safe_load(new_head) != expected or new_body != body:
        raise PlanError('変換後の frontmatter が期待と一致しません')
    return converted.encode('utf-8'), {
        'knowledgeId': original.get('knowledge_id'), 'kind': original.get('kind'),
        'gitCardVersion': original['card_version'], 'cardVersion': version,
        'modelScope': expected.get('model_scope') or {}, 'fixes': fixes, 'unresolved': unresolved,
        'droppedFields': [key for key in REMOVED_FIELDS if key in original]}


def applicability(scope):
    """Short text for the I1 bundle. The structured model_scope stays in the card's frontmatter."""
    parts = []
    note = scope.get('scope_note')
    if isinstance(note, str) and note.strip():
        parts.append(note.strip())
    for key in SCOPE_SUMMARY_KEYS:
        values = scope.get(key)
        if isinstance(values, list) and values:
            parts.append(f'{key}: ' + ', '.join(str(value) for value in values))
    parts.append('scope_status: ' + str(scope.get('scope_status') or 'unverified'))
    value = '; '.join(parts)
    if len(value) > 2000 or any(ord(char) < 32 for char in value):
        raise PlanError('適用範囲の要約が 2000 文字を超えるか、制御文字を含みます')
    return value


def plan(commit, out, domain=DEFAULT_DOMAIN, audience=DEFAULT_AUDIENCE, reason=DEFAULT_REASON, now=None):
    sys.path.insert(0, str(MODULES))
    import second_review

    commit = git('rev-parse', '--verify', commit + '^{commit}').decode().strip()
    names = git('ls-tree', '-r', '--name-only', commit, 'knowledge/cards/').decode('utf-8').split('\n')
    paths = sorted(name for name in names if CARD_PATH.match(name))
    ledger_path, vocab_path = 'knowledge/registry/card-versions.jsonl', 'knowledge/registry/applicability-vocabulary.json'
    files = git_files(commit, [*paths, ledger_path, vocab_path])
    ledger = {}
    for line in files[ledger_path].decode('utf-8').splitlines():
        if line.strip():
            row = json.loads(line)
            ledger[row['knowledgeId']] = row
    misplaced = json.loads(files[vocab_path])['misplaced']
    planned_at = int(now if now is not None else time.time())
    expires_at = planned_at + THREE_YEARS
    out = Path(out)
    (out / 'cards').mkdir(parents=True, exist_ok=True)
    rows, errors, seen = [], [], set()
    for path in paths:
        raw = files[path]
        stem = CARD_PATH.match(path).group(2)
        try:
            converted, report = convert(raw, misplaced)
            identifier = report['knowledgeId']
            if identifier != stem or not isinstance(identifier, str) or not ID.fullmatch(identifier):
                raise PlanError('knowledge_id がファイル名と一致しないか、ID の形式ではありません')
            if identifier in seen:
                raise PlanError('knowledge_id が重複しています')
            seen.add(identifier)
            entry = ledger.get(identifier)
            if entry is None or entry['sha256'] != sha256(raw) or entry['cardVersion'] != report['gitCardVersion']:
                raise PlanError('card-versions.jsonl と版または hash が一致しません')
            if report['kind'] not in {'case_summary', 'practice_guide'}:
                raise PlanError('kind が case_summary / practice_guide ではありません')
            if len(converted) > 256 * 1024:
                raise PlanError('256 KiB を超えます')
            summary = applicability(report['modelScope'])
            marks = second_review.assess(converted.decode('utf-8'), {'applicability': summary}, [], None)
        except PlanError as error:
            errors.append({'path': path, 'error': str(error)})
            continue
        (out / 'cards' / f'{identifier}.md').write_bytes(converted)
        rows.append({'knowledgeId': identifier, 'path': path, 'kind': report['kind'],
                     'gitCardVersion': report['gitCardVersion'], 'gitSha256': sha256(raw),
                     'cardVersion': report['cardVersion'], 'rawSha256': sha256(converted),
                     'applicability': summary, 'secondReview': marks['required'],
                     'secondReviewDetected': marks['detected'], 'fixes': report['fixes'],
                     'unresolved': report['unresolved'], 'droppedFields': report['droppedFields']})
    missing = sorted(set(ledger) - seen - {Path(e['path']).stem for e in errors})
    for identifier in missing:
        errors.append({'path': identifier, 'error': 'card-versions.jsonl にあるが、カードがありません'})
    inventory = ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows).encode('utf-8')
    (out / 'inventory.jsonl').write_bytes(inventory)
    evidence = {'id': EVIDENCE_ID, 'version': commit, 'sha256': sha256(inventory)}
    (out / 'plan.json').write_text(json.dumps({
        'commit': commit, 'plannedAt': planned_at, 'expiresAt': expires_at, 'domain': domain,
        'audience': audience, 'reason': f'{reason}（Git {commit[:12]}）', 'evidence': evidence,
        'counts': {'cards': len(rows), 'errors': len(errors),
                   'secondReview': sum(row['secondReview'] for row in rows),
                   'fixed': sum(bool(row['fixes']) for row in rows),
                   'unresolved': sum(bool(row['unresolved']) for row in rows),
                   'droppedFields': sum(bool(row['droppedFields']) for row in rows)},
        'errors': errors}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    # The protected policy table entry the operator adds before apply (this script never writes policy).
    (out / 'policy-evidence-entry.json').write_text(json.dumps({EVIDENCE_ID: {
        'version': commit, 'sha256': evidence['sha256'], 'domain': domain, 'audience': audience,
        'expiresAt': expires_at, 'independent': True, 'sourceVerified': False}}, indent=2) + '\n',
        encoding='utf-8', newline='\n')
    return json.loads((out / 'plan.json').read_text(encoding='utf-8'))


def load_plan(plan_dir):
    """Re-check the plan directory before any write: the evidence hash covers the inventory."""
    plan_dir = Path(plan_dir)
    meta = json.loads((plan_dir / 'plan.json').read_text(encoding='utf-8'))
    inventory = (plan_dir / 'inventory.jsonl').read_bytes()
    if meta['errors']:
        raise PlanError('plan にエラーがあります。直してから plan を作り直してください')
    if sha256(inventory) != meta['evidence']['sha256']:
        raise PlanError('inventory.jsonl が plan.json の hash と一致しません')
    rows = [json.loads(line) for line in inventory.decode('utf-8').splitlines() if line.strip()]
    cards = {}
    for row in rows:
        raw = (plan_dir / 'cards' / f'{row["knowledgeId"]}.md').read_bytes()
        if sha256(raw) != row['rawSha256']:
            raise PlanError(f'{row["knowledgeId"]} の変換後のカードが inventory と一致しません')
        cards[row['knowledgeId']] = raw
    return meta, rows, cards


def idempotency_key(meta, row):
    return 'migrate-' + sha256(json.dumps([row['knowledgeId'], row['rawSha256'], meta['expiresAt'],
                                           meta['domain'], meta['audience']]).encode())[:60]


def migrate_one(meta, row, raw, work, invoke, actor):
    """Write drafts/ (reusing an identical current version), then one migration operation."""
    sys.path.insert(0, str(MODULES))
    from storage import digest
    identifier = row['knowledgeId']
    version, current = work.current(identifier)
    if version is None or current is None or digest(current) != row['rawSha256']:
        version = work.put(identifier, raw)
    data = {'workVersionId': version, 'rawSha256': row['rawSha256'], 'kind': row['kind'],
            'applicability': row['applicability'], 'domain': meta['domain'], 'audience': meta['audience'],
            'expiresAt': meta['expiresAt'], 'cardVersion': row['cardVersion'], 'reason': meta['reason'],
            'evidence': {**{k: meta['evidence'][k] for k in ('id', 'version', 'sha256')},
                         'locator': row['path']}}
    return invoke({'commonKnowledgeMigration': {'actor': actor, 'idempotencyKey': idempotency_key(meta, row),
                                                'knowledgeId': identifier, 'data': data}})


def apply(meta, rows, cards, work, invoke, actor, results_path, only=None, limit=None):
    selected = [row for row in rows if only is None or row['knowledgeId'] in only][:limit]
    counts = {}
    with open(results_path, 'a', encoding='utf-8', newline='\n') as results:
        for row in selected:
            outcome = migrate_one(meta, row, cards[row['knowledgeId']], work, invoke, actor)
            counts[outcome['status']] = counts.get(outcome['status'], 0) + 1
            results.write(json.dumps({'knowledgeId': row['knowledgeId'], **outcome}, ensure_ascii=False,
                                     sort_keys=True) + '\n')
    return {'selected': len(selected), 'statuses': counts}


def verify(rows, canonical):
    """Count and hash of the published versions against the inventory (manifest → published/)."""
    sys.path.insert(0, str(MODULES))
    from storage import digest
    mismatches = []
    for row in rows:
        manifest = canonical.manifest(row['knowledgeId'])
        bundle = manifest.get('bundle') or {}
        raw = canonical.read_published(row['knowledgeId']) if manifest.get('active') else None
        problems = [name for name, ok in (
            ('notPublished', manifest.get('active') is not None),
            ('bundleHash', bundle.get('rawSha256') == row['rawSha256']
             and bundle.get('knowledgeId') == row['knowledgeId']),
            ('publishedBody', raw is not None and digest(raw) == row['rawSha256'])) if not ok]
        if problems:
            mismatches.append({'knowledgeId': row['knowledgeId'], 'problems': problems})
    return {'expected': len(rows), 'matched': len(rows) - len(mismatches), 'mismatches': mismatches}


def aws(args):
    import boto3
    sys.path.insert(0, str(MODULES))
    from aws_adapters import S3Canonical, S3Work
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    cloudformation = session.client('cloudformation')
    stack = cloudformation.describe_stacks(StackName=args.stack)['Stacks'][0]
    outputs = {item['OutputKey']: item['OutputValue'] for item in stack.get('Outputs', [])}
    s3 = session.client('s3')
    return session, cloudformation, outputs, S3Work(s3, outputs['WorkBucketName']), \
        S3Canonical(s3, outputs['DistributionBucketName'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('plan', help='Git のカードから移行の一覧と変換後のカードを作る（AWS に触れない）')
    p.add_argument('--commit', default='HEAD')
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--domain', default=DEFAULT_DOMAIN)
    p.add_argument('--audience', default=DEFAULT_AUDIENCE)
    for name in ('apply', 'verify'):
        sub = commands.add_parser(name)
        sub.add_argument('--plan', type=Path, required=True)
        sub.add_argument('--stack', default='EleKnowledge-itai-common-knowledge')
        sub.add_argument('--profile', required=True)
        sub.add_argument('--region', required=True)
        if name == 'apply':
            sub.add_argument('--actor-sub', required=True, help='承認者（itai または mona）の Cognito sub。認可表で判定する')
            sub.add_argument('--only', nargs='*', help='この knowledge_id だけ（試行用）')
            sub.add_argument('--limit', type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == 'plan':
            result = plan(args.commit, args.out, args.domain, args.audience)
            print(json.dumps({k: result[k] for k in ('commit', 'expiresAt', 'counts', 'errors')},
                             ensure_ascii=False, indent=2))
            return 1 if result['errors'] else 0
        meta, rows, cards = load_plan(args.plan)
        session, cloudformation, _outputs, work, canonical = aws(args)
        if args.command == 'verify':
            result = verify(rows, canonical)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if not result['mismatches'] else 1
        function = cloudformation.describe_stack_resource(
            StackName=args.stack, LogicalResourceId='RecoveryFunction')['StackResourceDetail']['PhysicalResourceId']
        client = session.client('lambda')

        def invoke(event):
            response = client.invoke(FunctionName=function, Payload=json.dumps(event).encode('utf-8'))
            if response.get('FunctionError'):
                return {'status': 503, 'code': 'FunctionError'}
            return json.loads(response['Payload'].read())
        result = apply(meta, rows, cards, work, invoke, args.actor_sub, args.plan / 'results.jsonl',
                       set(args.only) if args.only else None, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if set(result['statuses']) <= {200} else 1
    except PlanError as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
