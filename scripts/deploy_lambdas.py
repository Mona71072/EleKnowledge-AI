"""Phase 3 Lambda デプロイスクリプト（SAM 不要版）"""
import zipfile
import os
import shutil
import subprocess
import json
import sys

BASE = os.path.join(os.path.dirname(__file__), '..', 'lambda', 'troubleshooting')
ROLE_NAME = 'troubleshooting-lambda-poc-role'
KB_IDS = {
    'kb-search1': 'GKCWPMZUD0',
    'kb-search2': 'OCLVRJDMAH',
    'kb-search3': 'LCCRXQFJB9',
}

ENV_VARS = {
    'SitesTableName': 'sites',
    'BEDROCK_REGION': 'us-east-1',
    'AGENT_ID': 'D6FAGLJPPO',
    'AGENT_ALIAS_ID': 'TSTALIASID',
    'ENVIRONMENT': 'development',
    'DOCUMENTS_BUCKET': 'eleknowledge-ai-troubleshooting-docs',
    'DEFAULT_CONTROL_SYSTEM': 'VFGLF',
}

AUTHORIZER_ENV_VARS = {
    'COGNITO_REGION': 'us-east-1',
    'USER_POOL_ID': 'us-east-1_fCbgU2FR9',
    'APP_CLIENT_ID': '5e3penrp89bbscs1001b246tqj',
}

FUNCTIONS = [
    ('troubleshooting-orchestrator', 'orchestrator'),
    ('troubleshooting-db-search',    'db-search'),
    ('troubleshooting-kb-search1',   'kb-search1'),
    ('troubleshooting-kb-search2',   'kb-search2'),
    ('troubleshooting-kb-search3',   'kb-search3'),
]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def get_role_arn():
    """Lambda 実行ロールの ARN を組み立てる。
    アカウント ID は環境変数 AWS_ACCOUNT_ID、未設定なら現在の認証情報（sts）から取得する。
    """
    account_id = os.environ.get('AWS_ACCOUNT_ID', '').strip()
    if not account_id:
        r = run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'])
        account_id = r.stdout.strip()
    if not account_id:
        print('ERROR: AWS アカウント ID を取得できません（AWS_ACCOUNT_ID を設定してください）', file=sys.stderr)
        sys.exit(1)
    return f'arn:aws:iam::{account_id}:role/{ROLE_NAME}'


def deploy(func_name, dir_name):
    tmp = os.environ.get('TEMP', '/tmp')
    zip_path = os.path.join(tmp, f'{func_name}.zip')
    env_path = os.path.join(tmp, f'{func_name}-env.json')
    app_path = os.path.normpath(os.path.join(BASE, dir_name, 'app.py'))

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(app_path, 'app.py')
    print(f'  Zipped: {zip_path}')

    env_vars = dict(ENV_VARS)
    if dir_name in KB_IDS:
        env_vars['KnowledgeBaseId'] = KB_IDS[dir_name]

    with open(env_path, 'w') as f:
        json.dump({'Variables': env_vars}, f)

    exists = run(['aws', 'lambda', 'get-function', '--function-name', func_name])

    if exists.returncode == 0:
        r = run(['aws', 'lambda', 'update-function-code',
                 '--function-name', func_name,
                 '--zip-file', f'fileb://{zip_path}',
                 '--query', 'FunctionName', '--output', 'text'])
        if r.returncode == 0:
            run(['aws', 'lambda', 'update-function-configuration',
                 '--function-name', func_name,
                 '--environment', f'file://{env_path}'])
        status = 'Updated'
    else:
        r = run(['aws', 'lambda', 'create-function',
                 '--function-name', func_name,
                 '--runtime', 'python3.11',
                 '--role', get_role_arn(),
                 '--handler', 'app.lambda_handler',
                 '--timeout', '60',
                 '--memory-size', '512',
                 '--zip-file', f'fileb://{zip_path}',
                 '--environment', f'file://{env_path}',
                 '--query', 'FunctionName', '--output', 'text'])
        status = 'Created'

    if r.returncode == 0:
        print(f'  {status}: {r.stdout.strip()}')
    else:
        print(f'  ERROR: {r.stderr.strip()}', file=sys.stderr)
        sys.exit(1)


def deploy_authorizer():
    """PyJWT 依存関係を含めて Authorizer Lambda をデプロイする"""
    func_name = 'troubleshooting-authorizer'
    tmp = os.environ.get('TEMP', '/tmp')
    build_dir = os.path.join(tmp, f'{func_name}-build')
    zip_path = os.path.join(tmp, f'{func_name}.zip')
    env_path = os.path.join(tmp, f'{func_name}-env.json')
    src_dir = os.path.normpath(os.path.join(BASE, 'authorizer'))
    req_path = os.path.join(src_dir, 'requirements.txt')

    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir)

    # Lambda は Amazon Linux (x86_64) のため、Linux 用ホイールを明示指定して取得する
    r = subprocess.run(
        ['pip', 'install', '-r', req_path, '-t', build_dir, '--quiet',
         '--platform', 'manylinux2014_x86_64',
         '--implementation', 'cp',
         '--python-version', '311',
         '--only-binary', ':all:'],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f'  pip install failed: {r.stderr}', file=sys.stderr)
        sys.exit(1)

    shutil.copy(os.path.join(src_dir, 'app.py'), build_dir)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(build_dir):
            for fname in files:
                full = os.path.join(root, fname)
                zf.write(full, os.path.relpath(full, build_dir))
    print(f'  Zipped with deps: {zip_path}')

    with open(env_path, 'w') as f:
        json.dump({'Variables': AUTHORIZER_ENV_VARS}, f)

    exists = run(['aws', 'lambda', 'get-function', '--function-name', func_name])

    if exists.returncode == 0:
        r = run(['aws', 'lambda', 'update-function-code',
                 '--function-name', func_name,
                 '--zip-file', f'fileb://{zip_path}',
                 '--query', 'FunctionName', '--output', 'text'])
        if r.returncode == 0:
            run(['aws', 'lambda', 'update-function-configuration',
                 '--function-name', func_name,
                 '--environment', f'file://{env_path}'])
        status = 'Updated'
    else:
        r = run(['aws', 'lambda', 'create-function',
                 '--function-name', func_name,
                 '--runtime', 'python3.11',
                 '--role', get_role_arn(),
                 '--handler', 'app.lambda_handler',
                 '--timeout', '10',
                 '--memory-size', '256',
                 '--zip-file', f'fileb://{zip_path}',
                 '--environment', f'file://{env_path}',
                 '--query', 'FunctionName', '--output', 'text'])
        status = 'Created'

    if r.returncode == 0:
        print(f'  {status}: {r.stdout.strip()}')
    else:
        print(f'  ERROR: {r.stderr.strip()}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    print('=== Phase 3 Lambda デプロイ ===')
    for func_name, dir_name in FUNCTIONS:
        print(f'\n[{func_name}]')
        deploy(func_name, dir_name)
    print(f'\n[troubleshooting-authorizer]')
    deploy_authorizer()
    print('\n=== 完了 ===')
