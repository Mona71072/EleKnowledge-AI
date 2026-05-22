"""
トラブルシューティング エージェント Action 4: KB Search3 Lambda
C資料（詳細な技術資料）を検索
メタデータフィルター: document (C資料), model, control-system
"""
import json
import logging
import os
import time
from typing import Dict, Any, List
import boto3

# ロギング設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS クライアント
bedrock_client = boto3.client('bedrock-agent-runtime',
    region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
dynamodb_resource = boto3.resource('dynamodb')

# 環境変数
KB_ID = os.environ.get('KnowledgeBaseId')
SESSIONS_TABLE = os.environ.get('SESSIONS_TABLE', 'troubleshooting-sessions')


class KBSearchError(Exception):
    """Knowledge Base検索エラー"""
    pass


def validate_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    パラメータ検証
    
    Args:
        params: アクション用パラメータ
        
    Returns:
        検証済みパラメータ
        
    Raises:
        KBSearchError: パラメータ不正
    """
    query = params.get('query', '').strip()
    if not query:
        raise KBSearchError("query は必須です")
    
    validated = {'query': query}
    
    # オプションパラメータ
    if 'model' in params and params['model']:
        validated['model'] = params['model'].strip()
    
    if 'controlSystem' in params and params['controlSystem']:
        validated['controlSystem'] = params['controlSystem'].strip()
    
    return validated


def build_metadata_filter(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    メタデータフィルターを構築（Bedrock KB API 形式）

    S3 ドキュメントに .metadata.json が未設定のため document フィルターは使用しない。
    model / controlSystem が指定された場合のみ絞り込む。
    """
    conditions: List[Dict[str, Any]] = []

    if 'model' in params:
        conditions.append({'equals': {'key': 'model', 'value': params['model']}})

    if 'controlSystem' in params:
        conditions.append({'equals': {'key': 'control-system', 'value': params['controlSystem']}})

    if len(conditions) == 0:
        return {}
    if len(conditions) == 1:
        return conditions[0]

    return {'andAll': conditions}


def search_knowledge_base(query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Knowledge Base を検索（C資料）

    Args:
        query: 検索クエリ
        filters: メタデータフィルター（Bedrock KB API 形式）

    Returns:
        検索結果リスト

    Raises:
        KBSearchError: 検索失敗
    """
    try:
        logger.info(f"Searching KB for C-Materials with query: {query}")

        vector_config: Dict[str, Any] = {
            'numberOfResults': 10,
            'overrideSearchType': 'SEMANTIC',
        }
        if filters:
            vector_config['filter'] = filters

        # Bedrock Retrieve API を呼び出し
        response = bedrock_client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalConfiguration={
                'vectorSearchConfiguration': vector_config
            },
            retrievalQuery={'text': query}
        )
        
        results = []
        if 'retrievalResults' in response:
            for result in response['retrievalResults']:
                result_item = {
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0),
                    'location': result.get('location', {})
                }
                
                # Citation 情報取得
                if 'metadata' in result:
                    metadata = result['metadata']
                    result_item['citation'] = {
                        'source': metadata.get('title', 'Unknown'),
                        'relevance_score': result.get('score', 0.0),
                        'uri': metadata.get('uri', result.get('location', {}).get('s3Location', {}).get('uri', ''))
                    }
                
                results.append(result_item)
        
        logger.info(f"Found {len(results)} C-Material results")
        return results
        
    except Exception as e:
        logger.error(f"KB search error: {str(e)}")
        raise KBSearchError(f"Knowledge Base 検索失敗: {str(e)}")


def format_results(results: List[Dict[str, Any]]) -> str:
    """
    検索結果をテキスト形式にフォーマット
    
    Args:
        results: 検索結果リスト
        
    Returns:
        フォーマット済みテキスト
    """
    if not results:
        return "該当するC資料が見つかりませんでした"
    
    formatted = []
    formatted.append("【C資料（詳細技術資料） 検索結果】\n")
    
    for idx, result in enumerate(results[:5], 1):  # 上位5件
        formatted.append(f"【資料 {idx}】")
        formatted.append(f"関連度: {result.get('score', 0.0):.2%}\n")
        formatted.append(f"内容:\n{result.get('content', 'N/A')}\n")
        
        if 'citation' in result:
            citation = result['citation']
            formatted.append(f"出典: {citation.get('source', 'N/A')}")
            if citation.get('uri'):
                formatted.append(f"URI: {citation.get('uri')}")
            formatted.append("")
    
    return "\n".join(formatted)


def write_citations(session_id: str, results: List[Dict[str, Any]]):
    """KB 検索結果の引用情報を DynamoDB セッションに書き込む"""
    if not session_id:
        return
    citations = [
        {
            'uri': r.get('location', {}).get('s3Location', {}).get('uri', ''),
            'title': r.get('metadata', {}).get('title'),
            'document': r.get('metadata', {}).get('document', 'unknown'),
            'model': r.get('metadata', {}).get('model', ''),
            'score': str(r.get('score', 0.0)),
        }
        for r in results
        if r.get('location', {}).get('s3Location', {}).get('uri', '')
    ]
    if not citations:
        return
    try:
        dynamodb_resource.Table(SESSIONS_TABLE).update_item(
            Key={'session_id': session_id},
            UpdateExpression='SET citations = list_append(if_not_exists(citations, :empty), :c)',
            ExpressionAttributeValues={':c': citations, ':empty': []},
        )
        logger.info(f"Citations written: session_id={session_id}, count={len(citations)}")
    except Exception as e:
        logger.warning(f"Citations write failed: {e}")


def _extract_params(event: Dict[str, Any]) -> Dict[str, Any]:
    """Bedrock Agent (top-level list) / テストイベント (actionInvocation.parameters) 両対応"""
    raw = event.get('parameters', [])
    if isinstance(raw, list) and raw:
        return {p['name']: p.get('value', '') for p in raw}
    action_inv_params = event.get('actionInvocation', {}).get('parameters', [])
    return {p['name']: p.get('value', '') for p in action_inv_params}


def _make_response(event: Dict[str, Any], status: int, body: str) -> Dict[str, Any]:
    """Bedrock Agent functionSchema action group レスポンス形式"""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup', ''),
            'function': event.get('function', 'searchCMaterialDocs'),
            'functionResponse': {
                'responseBody': {'TEXT': {'body': body}},
            },
        },
    }


def lambda_handler(event, context):
    """Action 4: KB Search3 Lambda ハンドラー"""
    logger.info(f"KB Search3 Action invoked: {json.dumps(event)}")

    try:
        session_id = event.get('sessionAttributes', {}).get('session_id', '')
        parameters = _extract_params(event)
        logger.info(f"Parameters: {parameters}")
        validated_params = validate_parameters(parameters)
        filters = build_metadata_filter(validated_params)
        results = search_knowledge_base(validated_params['query'], filters)
        write_citations(session_id, results)
        formatted_result = format_results(results)
        logger.info("KB Search3 completed successfully")
        return _make_response(event, 200, formatted_result)
    except KBSearchError as e:
        logger.error(f"KB Search error: {str(e)}")
        return _make_response(event, 400, f"エラー: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _make_response(event, 500, f"予期しないエラーが発生しました: {str(e)}")