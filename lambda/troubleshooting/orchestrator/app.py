"""
トラブルシューティング エージェント Orchestrator Lambda
入力検証、Bedrock Agent呼び出し、結果統合を担当
"""
import json
import logging
import os
import re
import uuid
from typing import Dict, Any
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AGENT_ID = os.environ.get('AGENT_ID', '')
AGENT_ALIAS_ID = os.environ.get('AGENT_ALIAS_ID', 'TSTALIASID')

ALLOWED_MODELS = ['KE-LG', 'KM-LD', 'CM-MA', 'ME-CH']


class ValidationError(Exception):
    """入力バリデーションエラー"""
    pass


def validate_input(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """入力バリデーション"""
    construction_number = request_body.get('constructionNumber', '').strip()
    model = request_body.get('model', '').strip()

    # constructionNumber か model のどちらかは必須
    if not construction_number and not model:
        raise ValidationError("constructionNumber か model のどちらかは必須です")

    if construction_number and not re.match(r'^[A-Za-z0-9]{8}$', construction_number):
        raise ValidationError("工事番号は半角英数8文字で指定してください")

    trouble_description = request_body.get('troubleDescription', '').strip()
    if not trouble_description:
        raise ValidationError("troubleDescription は必須です")
    if len(trouble_description) < 5 or len(trouble_description) > 2000:
        raise ValidationError("不具合情報は5～2000文字で入力してください")

    if model and model not in ALLOWED_MODELS:
        raise ValidationError(f"model は {ALLOWED_MODELS} から選択してください")

    error_code = request_body.get('errorCode', '').strip()
    if error_code and not re.match(r'^[A-Z0-9]{4}$', error_code):
        raise ValidationError("エラーコードは半角英数4文字で指定してください")

    result = {'troubleDescription': trouble_description}
    if construction_number:
        result['constructionNumber'] = construction_number
    if model:
        result['model'] = model
    if error_code:
        result['errorCode'] = error_code
    return result

def format_agent_input(validated_data: Dict[str, Any]) -> str:
    """Agent入力フォーマット"""
    lines = ["【現場情報】"]
    if 'constructionNumber' in validated_data:
        lines.append(f"工事番号: {validated_data['constructionNumber']}")
    if 'model' in validated_data:
        lines.append(f"機種: {validated_data['model']}")
    if 'errorCode' in validated_data:
        lines.append(f"エラーコード: {validated_data['errorCode']}")
    lines.append(f"不具合内容: {validated_data['troubleDescription']}")
    lines.append("\n【処理要求】")
    lines.append("現場情報を取得し、トラブルシューティングを行ってください")
    return "\n".join(lines)


def invoke_agent(input_text: str) -> Dict[str, Any]:
    """Bedrock Agent呼び出し"""
    client = boto3.client('bedrock-agent-runtime')
    session_id = str(uuid.uuid4())
    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=input_text,
    )
    return response


def parse_agent_response(response: Dict[str, Any]) -> str:
    """Bedrock Agent EventStream からテキストを抽出"""
    output_parts = []
    for event in response.get('completion', []):
        if 'chunk' in event:
            chunk_bytes = event['chunk'].get('bytes', b'')
            if chunk_bytes:
                output_parts.append(chunk_bytes.decode('utf-8'))
    result = "".join(output_parts)
    return result if result else "応答を取得できませんでした"


def format_orchestration_response(status_code: int, response: Dict[str, Any]) -> Dict[str, Any]:
    """オーケストレーションレスポンス整形"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(response, ensure_ascii=False),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambdaハンドラ"""
    try:
        body = json.loads(event['body'])
        validated = validate_input(body)
        input_text = format_agent_input(validated)
        agent_response = invoke_agent(input_text)
        result_text = parse_agent_response(agent_response)
        return format_orchestration_response(200, {"result": result_text})
    except ValidationError as e:
        return format_orchestration_response(400, {"error": str(e)})
    except Exception as e:
        logging.error(f"Lambda error: {e}")
        return format_orchestration_response(500, {"error": "内部エラー"})