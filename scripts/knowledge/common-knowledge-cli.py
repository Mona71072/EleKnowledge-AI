"""Common knowledge CLI for the development agent: same Service as the API, caller = IAM principal.

Only working-bucket writes and the editor-side state changes live here (register a working version,
request review, status, pending/retry, guarded read). Approval, publication and withdrawal write
the canonical bucket, which only the Lambda roles may do, so they are API (screen) operations.
"""
import argparse
import json
from pathlib import Path
import sys

MODULES = Path(__file__).resolve().parents[2] / 'lambda/knowledge/common-knowledge'
sys.path.insert(0, str(MODULES))
from aws_adapters import DynamoDbLedger, S3Canonical, S3Work  # noqa: E402
from factory import Unavailable, policy_loader  # noqa: E402
from service import Failure, Service  # noqa: E402
from storage import Contention, digest, encode  # noqa: E402


def principal(sts):
    """`iam:` + the ARN resource part (role/session) — the account id is not recorded."""
    arn = sts.get_caller_identity()['Arn']
    return 'iam:' + arn.split(':', 5)[5]


def connect(session, stack):
    described = session.client('cloudformation').describe_stacks(StackName=stack)['Stacks'][0]
    outputs = {item['OutputKey']: item['OutputValue'] for item in described.get('Outputs', [])}
    parameters = {item['ParameterKey']: item['ParameterValue'] for item in described.get('Parameters', [])}
    dynamodb, s3 = session.client('dynamodb'), session.client('s3')
    service = Service(DynamoDbLedger(dynamodb, outputs['LedgerTableName']),
                      S3Work(s3, outputs['WorkBucketName']),
                      S3Canonical(s3, outputs['DistributionBucketName']), {},
                      enabled=parameters.get('CommonKnowledgeEnabled') == 'true',
                      policy_source=policy_loader(dynamodb, outputs['PolicyTableName']))
    service.begin_request()
    return service


def key_for(*parts):
    return 'cli-' + digest(list(parts))[:60]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stack', default='EleKnowledge-itai-common-knowledge')
    parser.add_argument('--profile', required=True)
    parser.add_argument('--region', required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    put = commands.add_parser('put-draft', help='作業用バケットの drafts/{card}.md へ本文を書く（新しい版になる）')
    put.add_argument('--card', required=True)
    put.add_argument('--file', type=Path, required=True)
    register = commands.add_parser('register', help='作業用の特定版を作業版として登録する')
    register.add_argument('--card', required=True)
    register.add_argument('--working-revision', type=int, required=True, help='現在の作業版番号（新規は0）')
    register.add_argument('--metadata', type=Path, required=True,
                          help='candidateId, candidateRevision, kind, applicability, sourceRefs, domain, '
                               'audience, expiresAt, unknowns のJSON')
    register.add_argument('--version-id', help='省略時は drafts/{card}.md の最新版')
    review = commands.add_parser('review', help='特定版の技術確認を依頼する')
    review.add_argument('--card', required=True)
    review.add_argument('--revision', type=int, required=True)
    review.add_argument('--bundle-hash', required=True)
    review.add_argument('--reason', required=True)
    status = commands.add_parser('status', help='単元の作業版・確認状態を表示する')
    status.add_argument('--card', required=True)
    read = commands.add_parser('read', help='公開manifest経由で公開版を読む')
    read.add_argument('--card', required=True)
    commands.add_parser('pending', help='自分の未完了操作')
    retry = commands.add_parser('retry', help='保存済みの要求から未完了操作を再開する')
    retry.add_argument('--operation', required=True)
    args = parser.parse_args(argv)

    import boto3
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    claims = {'sub': principal(session.client('sts'))}
    service = connect(session, args.stack)
    try:
        if args.command == 'put-draft':
            raw = args.file.read_bytes()
            if b'\r' in raw:
                raise SystemExit('LF改行のファイルにしてください')
            result = {'card': args.card, 'workVersionId': service.work.put(args.card, raw),
                      'rawSha256': digest(raw)}
        elif args.command == 'register':
            data = json.loads(args.metadata.read_text(encoding='utf-8'))
            version = args.version_id or service.work.current(args.card)[0]
            if version is None:
                raise SystemExit('drafts/ に本文がありません')
            data = {**data, 'workVersionId': version}
            result = service.register_draft(claims, key_for('register', args.card, args.working_revision, data),
                                            args.card, args.working_revision, data)
        elif args.command == 'review':
            data = {'bundleHash': args.bundle_hash, 'reason': args.reason}
            result = service.review(claims, key_for('review', args.card, args.revision, data),
                                    args.card, args.revision, data)
        elif args.command == 'status':
            result = service.card_detail(claims, args.card)
        elif args.command == 'read':
            service.store = Unavailable()  # Readers never touch the ledger.
            result = service.published(claims, args.card)
        elif args.command == 'pending':
            result = service.pending_operations(claims)
        else:
            result = service.resume(claims, args.operation)
    except Failure as error:
        print(encode({'status': error.status, 'code': error.code}))
        return 1
    except Contention:
        print(encode({'status': 503, 'code': 'ConcurrentUpdate', 'retry': 'same command'}))
        return 1
    print(json.dumps({'actor': claims['sub'], 'result': result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
