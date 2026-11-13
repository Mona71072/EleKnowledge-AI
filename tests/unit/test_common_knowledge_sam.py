"""共通知識 itai 専用スタック: 分離・既定オフ・S3正本（作業用／正本）・責任別の最小権限の契約テスト。"""
import json
import re

import pytest

SHARED_PHASE2 = ("phase1-template.yaml", "phase2-template.yaml")
ROLES = {'IntakeFunction': 'IntakeRole', 'EditorialFunction': 'EditorialRole',
         'PublicationFunction': 'PublicationRole', 'ReaderFunction': 'ReaderRole',
         'RecoveryFunction': 'RecoveryRole'}


@pytest.fixture(scope="module")
def template():
    from test_iam_function_permissions import _template
    return _template("common-knowledge-itai-template.yaml")


def statements(template, role):
    return [statement for policy in template['Resources'][role]['Properties']['Policies']
            for statement in policy['PolicyDocument']['Statement']]


def actions(template, role):
    found = set()
    for statement in statements(template, role):
        assert statement['Effect'] == 'Allow'
        found |= set([statement['Action']] if isinstance(statement['Action'], str) else statement['Action'])
    return found


def test_flag_defaults_off_and_no_git_path_remains(template):
    params = template['Parameters']
    assert params['CommonKnowledgeEnabled']['Default'] == 'false'
    assert 'GitMode' not in params
    assert 'Default' not in params['AllowedIPList'] and 'Default' not in params['WebAclArn']
    assert '*' not in params['CorsAllowedOrigin']['AllowedPattern']
    env = template['Globals']['Function']['Environment']['Variables']
    assert env['COMMON_KNOWLEDGE_ENABLED'] == 'CommonKnowledgeEnabled'
    assert not any('GIT' in name for name in env)
    assert env['COMMON_KNOWLEDGE_WORK_BUCKET'] == 'WorkBucket'
    assert env['COMMON_KNOWLEDGE_CANONICAL_BUCKET'] == 'DistributionBucket'
    text = json.dumps(template)
    assert not re.search(r'SKIP_AUTH|synthetic-|ENABLE_SYNTHETIC|DEV_ADMIN', text)


def test_no_physical_names_or_exports_and_shared_resources_only_referenced(template):
    from test_iam_function_permissions import _template
    resources = template['Resources']
    for name, resource in resources.items():
        properties = resource.get('Properties', {})
        assert not {'TableName', 'BucketName', 'RoleName', 'FunctionName'} & properties.keys(), name
    assert all('Export' not in output for output in template['Outputs'].values())
    shared = set()
    for filename in SHARED_PHASE2:
        shared |= set(_template(filename)['Resources'])
    assert not shared & set(resources), 'logical IDs must not shadow shared templates'
    text = json.dumps(template)
    assert re.findall(r'"Fn::ImportValue"', text) and 'CognitoUserPoolArn' in text
    assert not any(resource['Type'].startswith(('AWS::Cognito', 'AWS::WAFv2::WebACL"'))
                   for resource in resources.values())
    assert {resource['Type'] for resource in resources.values() if 'WAFv2' in resource['Type']} == {
        'AWS::WAFv2::WebACLAssociation'}


def test_durable_stores_are_retained_encrypted_and_keys_only(template):
    resources = template['Resources']
    for name in ('LedgerTable', 'PolicyTable', 'DistributionBucket', 'DistributionBucketPolicy',
                 'WorkBucket', 'WorkBucketPolicy'):
        assert resources[name]['DeletionPolicy'] == 'Retain' == resources[name]['UpdateReplacePolicy']
    for name in ('LedgerTable', 'PolicyTable'):
        properties = resources[name]['Properties']
        assert properties['SSESpecification'] == {'SSEEnabled': True}
        assert properties['PointInTimeRecoverySpecification'] == {'PointInTimeRecoveryEnabled': True}
        assert properties['BillingMode'] == 'PAY_PER_REQUEST'
    ledger = resources['LedgerTable']['Properties']
    assert {index['Projection']['ProjectionType'] for index in ledger['GlobalSecondaryIndexes']} == {'KEYS_ONLY'}
    assert ledger['TimeToLiveSpecification']['AttributeName'] == 'acceptancePurgeAt'
    for name in ('DistributionBucket', 'WorkBucket'):
        bucket = resources[name]['Properties']
        assert bucket['VersioningConfiguration'] == {'Status': 'Enabled'}
        assert 'PublicAccessBlockConfiguration' not in bucket  # SCP denies the call; verify after create
        rules = bucket['LifecycleConfiguration']['Rules']
        assert [rule['Prefix'] for rule in rules if 'ExpirationInDays' in rule] == ['acceptance/']
        statements = resources[name + 'Policy']['Properties']['PolicyDocument']['Statement']
        assert statements[0]['Effect'] == 'Deny'
        assert statements[0]['Condition'] == {'Bool': {'aws:SecureTransport': 'false'}}
        version = next(item for item in statements if item['Action'] == 's3:DeleteObjectVersion')
        assert version['Effect'] == 'Deny' and 'Condition' not in version


def test_canonical_writes_are_denied_to_everyone_but_the_lambda_roles(template):
    statements = template['Resources']['DistributionBucketPolicy']['Properties']['PolicyDocument']['Statement']
    writes = {item['Sid']: item for item in statements if item['Action'] == ['s3:PutObject', 's3:DeleteObject']}
    approved = writes['DenyApprovedWritesExceptApproval']
    assert approved['Effect'] == 'Deny' and approved['Principal'] == '*'
    assert approved['Resource'] == '${DistributionBucket.Arn}/approved/*'
    assert approved['Condition'] == {'ArnNotEquals': {'aws:PrincipalArn': ['EditorialRole.Arn', 'RecoveryRole.Arn']}}
    published = writes['DenyPublicationWritesExceptPublication']
    assert published['Resource'] == ['${DistributionBucket.Arn}/manifests/*', '${DistributionBucket.Arn}/published/*']
    assert published['Condition'] == {
        'ArnNotEquals': {'aws:PrincipalArn': ['PublicationRole.Arn', 'RecoveryRole.Arn']}}


def resources_of(template, role, action):
    found = set()
    for statement in statements(template, role):
        names = [statement['Action']] if isinstance(statement['Action'], str) else statement['Action']
        if action in names:
            found |= set([statement['Resource']] if isinstance(statement['Resource'], str) else statement['Resource'])
    return found


def test_roles_are_split_by_responsibility(template):
    assert actions(template, 'ReaderRole') == {'dynamodb:GetItem', 's3:GetObject', 's3:ListBucket'}
    reader_get = next(s for s in statements(template, 'ReaderRole') if s['Action'] == 'dynamodb:GetItem')
    assert reader_get['Resource'] == 'PolicyTable.Arn'  # never the ledger
    assert not any(a.startswith('s3:') for a in actions(template, 'IntakeRole'))
    # Readers never reach drafts/ or approved/; only editorial/recovery touch the working bucket.
    assert resources_of(template, 'ReaderRole', 's3:GetObject') == {
        '${DistributionBucket.Arn}/manifests/*', '${DistributionBucket.Arn}/published/*'}
    for role in ('IntakeRole', 'PublicationRole', 'ReaderRole'):
        assert 'WorkBucket' not in json.dumps(statements(template, role)), role
    assert resources_of(template, 'EditorialRole', 's3:PutObject') == {
        '${WorkBucket.Arn}/drafts/*', '${DistributionBucket.Arn}/approved/*'}
    assert resources_of(template, 'PublicationRole', 's3:PutObject') == {
        '${DistributionBucket.Arn}/manifests/*', '${DistributionBucket.Arn}/published/*'}
    for role in ROLES.values():
        assert resources_of(template, role, 's3:DeleteObject') <= {'${DistributionBucket.Arn}/published/*'}, role
    assert 'secretsmanager:GetSecretValue' in actions(template, 'IntakeRole')
    for role in ('EditorialRole', 'PublicationRole', 'ReaderRole', 'RecoveryRole'):
        assert not any(a.startswith('secretsmanager') for a in actions(template, role)), role
    assert actions(template, 'RecoveryRole') == actions(template, 'PublicationRole') | actions(template, 'EditorialRole')
    for action in ('s3:GetObject', 's3:PutObject', 's3:DeleteObject', 's3:GetObjectVersion'):
        assert resources_of(template, 'RecoveryRole', action) == (
            resources_of(template, 'PublicationRole', action) | resources_of(template, 'EditorialRole', action)), action
    for role in ROLES.values():
        found = actions(template, role)
        assert not {'dynamodb:Scan', 'dynamodb:UpdateItem', 's3:DeleteObjectVersion', 's3:*', 'dynamodb:*'} & found, role
        assert all(':*' not in a and a != '*' for a in found), role
        for statement in statements(template, role):
            resources = statement['Resource'] if isinstance(statement['Resource'], list) else [statement['Resource']]
            assert '*' not in resources, role
            if {'dynamodb:PutItem', 'dynamodb:DeleteItem'} & set(statement['Action'] if isinstance(
                    statement['Action'], list) else [statement['Action']]):
                assert statement['Condition'] == {'ForAnyValue:StringEquals': {
                    'dynamodb:EnclosingOperation': 'TransactWriteItems'}}, role
    queries = [s for role in ROLES.values() for s in statements(template, role) if s['Action'] == 'dynamodb:Query']
    assert len(queries) == 1 and all('/index/' in json.dumps(r) for r in queries[0]['Resource'])


def test_routes_map_to_their_responsibility_and_cursor_secret_only_on_intake(template):
    import importlib.util
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('ck_app', root / 'lambda/knowledge/common-knowledge/app.py')
    import sys
    sys.path.insert(0, str(root / 'lambda/knowledge/common-knowledge'))
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    for function, role in ROLES.items():
        properties = template['Resources'][function]['Properties']
        assert properties['Role'] == role + '.Arn'
        responsibility = properties['Environment']['Variables']['COMMON_KNOWLEDGE_RESPONSIBILITY']
        assert ('COMMON_KNOWLEDGE_CURSOR_SECRET_ARN' in properties['Environment']['Variables']) == (
            responsibility == 'intake')
        for event in properties['Events'].values():
            path = re.sub(r'\{id\}', 'KH-SYN-A', event['Properties']['Path'])
            name, _ = app.route(event['Properties']['Method'].upper(), path)
            assert name in app.RESPONSIBILITIES[responsibility], (function, path)
    api = template['Resources']['CommonKnowledgeApi']['Properties']
    assert api['Auth']['DefaultAuthorizer'] == 'CognitoAuthorizer'
    # Whole-API IP restriction in two statements (per-route pairs exceeded the 8192-byte policy limit).
    assert api['Auth']['ResourcePolicy'] == {'CustomStatements': [
        {'Effect': 'Allow', 'Principal': '*', 'Action': 'execute-api:Invoke', 'Resource': 'execute-api:/*'},
        {'Effect': 'Deny', 'Principal': '*', 'Action': 'execute-api:Invoke', 'Resource': 'execute-api:/*',
         'Condition': {'NotIpAddress': {'aws:SourceIp': 'AllowedIPList'}}}]}
    assert api['Cors']['AllowOrigin'] == "'${CorsAllowedOrigin}'" and api['MethodSettings'][0]['ThrottlingRateLimit']
    assert 'authorization' not in api['AccessLogSetting']['Format'].lower()
