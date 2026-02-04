"""
トラブルシューティング エージェント Orchestrator Lambda
入力検証、Bedrock Agent呼び出し、結果統合を担当
"""
import json
import uuid
import logging
import os
import re
from typing import Dict, Any, Tuple
from datetime import datetime
import boto3

# ロギング設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWSクライアント
bedrock_client = boto3.client('bedrock-agent-runtime', 
    region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# 環境変数
AGENT_ID = os.environ.get('AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID')
SITES_TABLE_NAME = os.environ.get('SITES_TABLE_NAME', 'sites')

# バリデーションルール
VALIDATION_RULES = {
    'constructionNumber': {
        'required': True,
        'pattern': r'^[A-Za-z0-9]{8}$',
        'message': '工事番号は半角英数字8文字で指定してください'
    },
    'troubleDescription': {
        'required': True,
        'min_length': 5,
        'max_length': 2000,
        'message': '不具合情報は5文字以上2000文字以下で指定してください'
    },
    'model': {
        'required': False,
        'allowed_values': ['KE-LG', 'KM-LD', 'CF-MA', 'BD-MK'],
        'message': '指定されたモデルはサポートされていません'
    },
    'errorCode': {
        'required': False,
        'pattern': r'^[A-Z0-9]{4}$',
        'message': 'エラーコードは半角英数字4文字で指定してください'
    }
}

class ValidationError(Exception):
    """バリデーションエラー"""
    pass

def validate_input(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    リクエストボディのバリデーション

    Args:
        request_body: リクエストボディ

    Returns:
        バリデーション済みのリクエストボディ

    Raises:
        ValidationError: バリデーションエラーが発生した場合
    """
    validated_data = {}

    for key, rule in VALIDATION_RULES.items():
        value = request_body.get(key)

        if rule['required'] and not value:
            raise ValidationError(rule['message'])

        if value:
            if 'pattern' in rule and not re.match(rule['pattern'], value):
                raise ValidationError(rule['message'])
            if 'min_length' in rule and len(value) < rule['min_length']:
                raise ValidationError(rule['message'])
            if 'max_length' in rule and len(value) > rule['max_length']:
                raise ValidationError(rule['message'])
            if 'allowed_values' in rule and value not in rule['allowed_values']:
                raise ValidationError(rule['message'])

            validated_data[key] = value

    return validated_data

def get_site_info(construction_number: str) -> Dict[str, Any]:
    """
    DynamoDBから現場情報を取得

    Args:
        construction_number: 工事番号

    Returns:
        現場情報

    Raises:
        Exception: DynamoDBからの取得に失敗した場合
    """
    table = dynamodb.Table(SITES_TABLE_NAME)
    response = table.get_item(Key={'constructionNumber': construction_number})

    if 'Item' not in response:
        raise Exception(f'工事番号 {construction_number} の現場情報が見つかりませんでした')

    return response['Item']

def format_agent_input(validated_data: Dict[str, Any], site_info: Dict[str, Any]) -> str:
    """
    Bedrock Agentに渡す入力テキストを生成

    Args:
        validated_data: バリデーション済みのリクエストボディ
        site_info: DynamoDBから取得した現場情報

    Returns:
        Bedrock Agentに渡す入力テキスト
    """
    input_text = f"""
【現場情報】
工事番号: {validated_data['constructionNumber']}
不具合情報: {validated_data['troubleDescription']}

【設置機器】
"""
    if 'model' in validated_data:
        input_text += f"対象機器: {validated_data['model']}\n"
    if 'errorCode' in validated_data:
        input_text += f"エラーコード: {validated_data['errorCode']}\n"

    if site_info:
        input_text += f"""
現場名: {site_info.get('siteName', '不明')}
設置日: {site_info.get('installationDate', '不明')}
"""
    else:
        input_text += "現場情報が見つかりませんでした\n"

    input_text += """
【処理内容】
1. DynamoDBから現場情報を取得
2. Bedrock Agentに問い合わせ
3. 結果を解析し、返却
"""

    return input_text

def invoke_agent(input_text: str) -> Dict[str, Any]:
    """
    Bedrock Agentを呼び出す

    Args:
        input_text: Bedrock Agentに渡す入力テキスト

    Returns:
        Bedrock Agentからのレスポンス

    Raises:
        Exception: Bedrock Agentの呼び出しに失敗した場合
    """
    try:
        response = bedrock_client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            inputText=input_text
        )
        return response
    except Exception as e:
        logger.error(f"Error invoking Bedrock Agent: {str(e)}")
        raise

def parse_agent_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bedrock Agentからのレスポンスを解析

    Args:
        response: Bedrock Agentからのレスポンス

    Returns:
        解析済みのレスポンス

    Raises:
        Exception: レスポンスの解析に失敗した場合
    """
    try:
        return json.loads(response['outputText'])
    except Exception as e:
        logger.error(f"Error parsing Bedrock Agent response: {str(e)}")
        raise

def format_orchestration_response(status_code: int, response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bedrock Agentカスタムオーケストレーション形式のレスポンスを生成

    Args:
        status_code: HTTPステータスコード
        response: 解析済みのレスポンス

    Returns:
        Bedrock Agentカスタムオーケストレーション形式のレスポンス
    """
    return {
        'messageVersion': '1.0',
        'response': response
    }

def lambda_handler(event, context):
    """
    Orchestrator Lambdaのメインハンドラー

    Args:
        event: Lambdaイベント
        context: Lambdaコンテキスト

    Returns:
        Bedrock Agentカスタムオーケストレーション形式のレスポンス
    """
    try:
        # リクエストボディの取得
        request_body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        # 入力バリデーション
        validated_data = validate_input(request_body)

        # 現場情報の取得
        site_info = get_site_info(validated_data['constructionNumber'])

        # Bedrock Agentへの入力テキストの生成
        agent_input = format_agent_input(validated_data, site_info)

        # Bedrock Agentの呼び出し
        agent_response = invoke_agent(agent_input)

        # Bedrock Agentからのレスポンスの解析
        parsed_response = parse_agent_response(agent_response)

        # カスタムオーケストレーション形式のレスポンスの生成
        return format_orchestration_response(200, parsed_response)

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return format_orchestration_response(400, {'error': str(e)})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return format_orchestration_response(500, {'error': '分析処理中にエラーが発生しました'})