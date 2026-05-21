"""Phase 3 Lambda デプロイスクリプト（SAM 不要版）"""
import zipfile
import os
import subprocess
import json
import sys
import time

BASE = os.path.join(os.path.dirname(__file__), '..', 'lambda', 'troubleshooting')
ROLE_ARN = 'arn:aws:iam::423623870147:role/troubleshooting-lambda-poc-role'
KB_ID = 'OCLVRJDMAH'

ENV_VARS = {
    'KnowledgeBaseId': KB_ID,
    'SitesTableName': 'sites',
    'BEDROCK_REGION': 'us-east-1',
    'AGENT_ID': 'D6FAGLJPPO',
    'AGENT_ALIAS_ID': 'TSTALIASID',
    'ENVIRONMENT': 'development',
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


def deploy(func_name, dir_name):
    tmp = os.environ.get('TEMP', '/tmp')
    zip_path = os.path.join(tmp, f'{func_name}.zip')
    env_path = os.path.join(tmp, f'{func_name}-env.json')
    app_path = os.path.normpath(os.path.join(BASE, dir_name, 'app.py'))

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(app_path, 'app.py')
    print(f'  Zipped: {zip_path}')

    with open(env_path, 'w') as f:
        json.dump({'Variables': ENV_VARS}, f)

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
                 '--role', ROLE_ARN,
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


if __name__ == '__main__':
    print('=== Phase 3 Lambda デプロイ ===')
    for func_name, dir_name in FUNCTIONS:
        print(f'\n[{func_name}]')
        deploy(func_name, dir_name)
    print('\n=== 完了 ===')
