"""WP4: 共通知識の公開版（manifest → published/）を、先輩の索引を作るためにローカルへ書き出す。

設計: docs/design-2026-11-11-knowledge-governance.md §4.11 手順 4・§4.12。読み取りのみ（AWS へ書かない）。

  python scripts/knowledge/snapshot_published_cards.py --profile P --region R --out DIR
  node scripts/knowledge/build-senpai-index.mjs build-published . DIR   # → .private-knowhow/index-published.json

公開中（manifest の active あり）で、読者が --audience に含まれ、束の期限内のカードだけを書き出す。
本文は manifest の rawSha256 と照合し、一致しなければ失敗する（索引を作らない）。
--inventory を渡すと、WP3 の移行一覧と件数・本文の hash を照合する（§4.11 手順 4）。
"""
import argparse
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'lambda/knowledge/common-knowledge'))
from storage import digest  # noqa: E402

ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')


class SnapshotError(Exception):
    pass


def snapshot(identifiers, canonical, out, audiences, now=None):
    """Write out/published.json and out/cards/{id}.md. Returns the listing."""
    now = int(time.time() if now is None else now)
    out = Path(out)
    (out / 'cards').mkdir(parents=True, exist_ok=True)
    entries, skipped = [], {}
    for identifier in sorted(set(identifiers)):
        if not ID.fullmatch(identifier):
            raise SnapshotError(f'{identifier!r} は ID の形式ではありません')
        manifest = canonical.manifest(identifier)
        bundle = manifest.get('bundle') or {}
        reason = ('notPublished' if not manifest.get('active')
                  else 'audience' if bundle.get('audience') not in audiences
                  else 'expired' if not isinstance(bundle.get('expiresAt'), int) or bundle['expiresAt'] <= now
                  else None)
        if reason:
            skipped[reason] = skipped.get(reason, 0) + 1
            continue
        raw = canonical.read_published(identifier)
        if raw is None or digest(raw) != bundle.get('rawSha256') or bundle.get('knowledgeId') != identifier:
            raise SnapshotError(f'{identifier} の公開本文が manifest と一致しません（投影待ちの可能性）')
        if canonical.manifest(identifier) != manifest:
            raise SnapshotError(f'{identifier} の公開が読み取り中に変わりました。やり直してください')
        (out / 'cards' / f'{identifier}.md').write_bytes(raw)
        entries.append({'knowledgeId': identifier, 'generation': manifest['generation'],
                        'rawSha256': bundle['rawSha256'], 'bundleHash': bundle['bundleHash'],
                        'audience': bundle['audience'], 'expiresAt': bundle['expiresAt']})
    listing = {'schemaVersion': 1, 'purpose': 'common-knowledge-published', 'audiences': sorted(audiences),
               'snapshotAt': now, 'entries': entries}
    (out / 'published.json').write_text(json.dumps(listing, ensure_ascii=False, indent=2) + '\n',
                                        encoding='utf-8', newline='\n')
    return listing, skipped


def compare_inventory(listing, inventory_path):
    """§4.11 step 4: every migrated card is published with exactly the migrated body."""
    rows = [json.loads(line) for line in Path(inventory_path).read_text(encoding='utf-8').splitlines() if line.strip()]
    published = {entry['knowledgeId']: entry['rawSha256'] for entry in listing['entries']}
    missing = sorted(row['knowledgeId'] for row in rows if row['knowledgeId'] not in published)
    changed = sorted(row['knowledgeId'] for row in rows
                     if row['knowledgeId'] in published and published[row['knowledgeId']] != row['rawSha256'])
    return {'inventory': len(rows), 'published': len(published), 'missing': missing, 'changed': changed,
            'extra': sorted(set(published) - {row['knowledgeId'] for row in rows})}


def list_manifest_ids(client, bucket):
    identifiers, token = [], None
    while True:
        response = client.list_objects_v2(Bucket=bucket, Prefix='manifests/',
                                          **({'ContinuationToken': token} if token else {}))
        for item in response.get('Contents', []):
            name = item['Key'][len('manifests/'):]
            if name.endswith('.json') and '/' not in name:
                identifiers.append(name[:-len('.json')])
        if not response.get('IsTruncated'):
            return identifiers
        token = response['NextContinuationToken']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stack', default='EleKnowledge-itai-common-knowledge')
    parser.add_argument('--profile', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--audience', action='append', default=None, help='既定: all-users')
    parser.add_argument('--inventory', type=Path, help='WP3 の inventory.jsonl（照合する場合）')
    args = parser.parse_args(argv)
    import boto3
    from aws_adapters import S3Canonical
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    stack = session.client('cloudformation').describe_stacks(StackName=args.stack)['Stacks'][0]
    bucket = {o['OutputKey']: o['OutputValue'] for o in stack.get('Outputs', [])}['DistributionBucketName']
    s3 = session.client('s3')
    try:
        listing, skipped = snapshot(list_manifest_ids(s3, bucket), S3Canonical(s3, bucket), args.out,
                                    set(args.audience or ['all-users']))
    except SnapshotError as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False))
        return 1
    result = {'published': len(listing['entries']), 'skipped': skipped}
    if args.inventory:
        result['inventory'] = compare_inventory(listing, args.inventory)
        if any(result['inventory'][key] for key in ('missing', 'changed')):
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
