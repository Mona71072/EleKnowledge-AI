"""Deployed adapter factory. Every setting is explicit; a gap raises and the API answers 503."""
import json
import re

from service import Service


RESPONSIBILITIES = {'intake', 'editorial', 'publication', 'reader', 'recovery'}
NEEDS_LEDGER = {'intake', 'editorial', 'publication', 'recovery'}
NEEDS_WORK = {'editorial', 'recovery'}
NEEDS_CANONICAL = {'editorial', 'publication', 'reader', 'recovery'}
NAME = re.compile(r'^[A-Za-z0-9_.-]{3,255}$')
POLICY_SECTIONS = ('actors', 'contributions', 'evidence')


class ConfigurationError(Exception):
    pass


class Unavailable:
    """Stands in for a store this responsibility must never touch (no IAM grant either)."""

    def __getattr__(self, name):
        raise OSError('store not available to this function')


def setting(environ, name, pattern=NAME):
    value = environ.get(name, '')
    if not pattern.fullmatch(value):
        raise ConfigurationError(name)
    return value


def policy_loader(client, table):
    """Grants come only from the protected policy table (GetItem). Missing → no grants at all."""
    def load():
        item = client.get_item(TableName=table, Key={'pk': {'S': 'current'}},
                               ConsistentRead=True).get('Item')
        if not item:
            return {}
        value = json.loads(item['value']['S'])
        if not isinstance(value, dict) or not set(value) <= set(POLICY_SECTIONS) or not all(
                isinstance(value.get(section, {}), dict) for section in POLICY_SECTIONS):
            raise ConfigurationError('policy shape')
        return value
    return load


def build(environ, boto3_module=None):
    responsibility = environ.get('COMMON_KNOWLEDGE_RESPONSIBILITY')
    if responsibility not in RESPONSIBILITIES:
        raise ConfigurationError('COMMON_KNOWLEDGE_RESPONSIBILITY')
    enabled = environ.get('COMMON_KNOWLEDGE_ENABLED')
    if enabled not in {'true', 'false'}:
        raise ConfigurationError('COMMON_KNOWLEDGE_ENABLED')
    origin = environ.get('COMMON_KNOWLEDGE_ALLOWED_ORIGIN', '')
    if not re.fullmatch(r'https://[A-Za-z0-9.-]+(:[0-9]{1,5})?', origin):
        raise ConfigurationError('COMMON_KNOWLEDGE_ALLOWED_ORIGIN')
    policy_table = setting(environ, 'COMMON_KNOWLEDGE_POLICY_TABLE')
    if boto3_module is None:
        import boto3 as boto3_module
    from aws_adapters import DynamoDbLedger, S3Canonical, S3Work
    dynamodb = boto3_module.client('dynamodb')
    ledger = Unavailable()
    if responsibility in NEEDS_LEDGER:
        ledger = DynamoDbLedger(dynamodb, setting(environ, 'COMMON_KNOWLEDGE_LEDGER_TABLE'))
    work = Unavailable()
    if responsibility in NEEDS_WORK:
        work = S3Work(boto3_module.client('s3'), setting(environ, 'COMMON_KNOWLEDGE_WORK_BUCKET'))
    canonical = Unavailable()
    if responsibility in NEEDS_CANONICAL:
        canonical = S3Canonical(boto3_module.client('s3'), setting(environ, 'COMMON_KNOWLEDGE_CANONICAL_BUCKET'))
    load_policy = policy_loader(dynamodb, policy_table)
    if responsibility == 'intake':
        secret_arn = setting(environ, 'COMMON_KNOWLEDGE_CURSOR_SECRET_ARN',
                             re.compile(r'^arn:aws:secretsmanager:[a-z0-9-]+:[0-9]{12}:secret:[A-Za-z0-9/_+=.@-]+$'))
        secrets = boto3_module.client('secretsmanager')
        cached = {}

        def source():
            if 'secret' not in cached:
                cached['secret'] = secrets.get_secret_value(SecretId=secret_arn)['SecretString']
            return {**load_policy(), 'cursorSecret': cached['secret']}
    else:
        source = load_policy
    service = Service(ledger, work, canonical, {}, enabled=enabled == 'true',
                      policy_source=source)
    return service, responsibility, origin
