"""
トラブルシューティング エージェント Orchestrator Lambda
入力検証、Bedrock Agent呼び出し、結果統合を担当
"""
import json
import logging
import os
import re
import uuid  # 追加
from typing import Dict, Any
import boto3

# 環境変数 (本番用)
# AGENT_ID = ssm.get_parameter(Name='/eleknowledge/bedrock/agent-id')['Parameter']['Value']
# AGENT_ALIAS_ID = ssm.get_parameter(Name='/eleknowledge/bedrock/agent-alias-id')['Parameter']['Value']

# 技術検証用 (本番環境では削除)
AGENT_ID = "D6FAGLJPPO"  # ダミー値
AGENT_ALIAS_ID = "WBXLCRHOCD"  # ダミー値

def validate_input(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """入力バリデーション"""
    # ... 省略 ...

def format_agent_input(validated_data: Dict[str, Any]) -> str:
    """Agent入力フォーマット"""
    return f"""
【現場情報】
工事番号: {validated_data['constructionNumber']}
不具合内容: {validated_data['troubleDescription']}

【処理要求】
現場情報を取得してください
"""

def invoke_agent(input_text: str) -> Dict[str, Any]:
    """Bedrock Agent呼び出し"""
    client = boto3.client('bedrock-agent-runtime')
    session_id = str(uuid.uuid4())
    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=input_text,
        agentRuntimeConfigurations=[
            {
                "actionGroup": {
                    "actionGroupId": "QEBTU9FRS1",  # 技術検証用
                    "actionGroupName": "GetSiteInfo"
                }
            }
        ]
    )
    return response

def format_orchestration_response(status_code: int, response: Dict[str, Any]) -> Dict[str, Any]:
    """オーケストレーションレスポンス整形"""
    return {
        'statusCode': status_code,
        'body': json.dumps(response)
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambdaハンドラ"""
    try:
        body = json.loads(event['body'])
        validated = validate_input(body)
        input_text = format_agent_input(validated)
        agent_response = invoke_agent(input_text)
        return format_orchestration_response(200, agent_response)
    except ValidationError as e:
        return format_orchestration_response(400, {"error": str(e)})
    except Exception as e:
        logging.error(f"Lambda error: {e}")
        return format_orchestration_response(500, {"error": "内部エラー"})