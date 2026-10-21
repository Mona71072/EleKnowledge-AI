"""共通知識 itai 専用スタック: 分離・既定オフ・Git未設定・責任別の最小権限の契約テスト。"""
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


def test_flags_default_off_and_git_cannot_be_selected(template):
    params = template['Parameters']
    assert params['CommonKnowledgeEnabled']['Default'] == 'false'
    assert params['GitMode']['AllowedValues'] == ['unconfigured']
    assert 'Default' not in params['AllowedIPList'] and 'Default' not in params['WebAclArn']
    assert '*' not in params['CorsAllowedOrigin']['AllowedPattern']
    env = template['Globals']['Function']['Environment']['Variables']
    assert env['COMMON_KNOWLEDGE_ENABLED'] == 'CommonKnowledgeEnabled'
    assert env['COMMON_KNOWLEDGE_GIT_MODE'] == 'GitMode'
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
    for name in ('LedgerTable', 'PolicyTable', 'DistributionBucket', 'DistributionBucketPolicy'):
        assert resources[name]['DeletionPolicy'] == 'Retain' == resources[name]['UpdateReplacePolicy']
    for name in ('LedgerTable', 'PolicyTable'):
        properties = resources[name]['Properties']
        assert properties['SSESpecification'] == {'SSEEnabled': True}
        assert properties['PointInTimeRecoverySpecification'] == {'PointInTimeRecoveryEnabled': True}
        assert properties['BillingMode'] == 'PAY_PER_REQUEST'
    ledger = resources['LedgerTable']['Properties']
    assert {index['Projection']['ProjectionType'] for index in ledger['GlobalSecondaryIndexes']} == {'KEYS_ONLY'}
    assert ledger['TimeToLiveSpecification']['AttributeName'] == 'acceptancePurgeAt'
    bucket = resources['DistributionBucket']['Properties']
    assert bucket['VersioningConfiguration'] == {'Status': 'Enabled'}
    assert 'PublicAccessBlockConfiguration' not in bucket  # SCP denies the call; verify after create
    rules = bucket['LifecycleConfiguration']['Rules']
    assert [rule['Prefix'] for rule in rules if 'ExpirationInDays' in rule] == ['acceptance/']
    deny = resources['DistributionBucketPolicy']['Properties']['PolicyDocument']['Statement'][0]
    assert deny['Effect'] == 'Deny' and deny['Condition'] == {'Bool': {'aws:SecureTransport': 'false'}}


def test_roles_are_split_by_responsibility(template):
    assert actions(template, 'ReaderRole') == {'dynamodb:GetItem', 's3:GetObject', 's3:ListBucket'}
    reader_get = next(s for s in statements(template, 'ReaderRole') if s['Action'] == 'dynamodb:GetItem')
    assert reader_get['Resource'] == 'PolicyTable.Arn'  # never the ledger
    assert 's3:PutObject' not in actions(template, 'IntakeRole') | actions(template, 'EditorialRole')
    assert 'secretsmanager:GetSecretValue' in actions(template, 'IntakeRole')
    for role in ('EditorialRole', 'PublicationRole', 'ReaderRole', 'RecoveryRole'):
        assert not any(a.startswith('secretsmanager') for a in actions(template, role)), role
    assert actions(template, 'RecoveryRole') == actions(template, 'PublicationRole')
    for role in ROLES.values():
        found = actions(template, role)
        assert not {'dynamodb:Scan', 'dynamodb:UpdateItem', 's3:DeleteObject', 's3:*', 'dynamodb:*'} & found, role
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
    assert api['Auth']['ResourcePolicy'] == {'IpRangeWhitelist': 'AllowedIPList'}
    assert api['Cors']['AllowOrigin'] == "'${CorsAllowedOrigin}'" and api['MethodSettings'][0]['ThrottlingRateLimit']
    assert 'authorization' not in api['AccessLogSetting']['Format'].lower()
