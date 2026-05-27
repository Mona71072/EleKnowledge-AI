"""
トラブルシューティング エージェント Action 3: KB Search2 Lambda
トラブルシュートマニュアル全文検索（メタデータフィルターなし）
エラーコードと不具合情報から対処方法を検索
Citation は取得しない（参考情報のみ）、1-3件のみ返却
"""
import json
import logging
import os
from typing import Dict, Any, List
import boto3

# ロギング設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS クライアント
bedrock_client = boto3.client('bedrock-agent-runtime', 
    region_name=os.environ.get('BEDROCK_REGION', 'ap-northeast-1'))
dynamodb_resource = boto3.resource('dynamodb', region_name=os.environ.get('BEDROCK_REGION', 'ap-northeast-1'))

# 環境変数
KB_ID = os.environ.get('KnowledgeBaseId', 'pending')
SESSIONS_TABLE = os.environ.get('SESSIONS_TABLE', 'sessions-dev')
DEFAULT_CONTROL_SYSTEM = os.environ.get('DEFAULT_CONTROL_SYSTEM', 'VFGLF')


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
    
    validated = {
        'query': query,
        'controlSystem': params.get('controlSystem', '').strip() or DEFAULT_CONTROL_SYSTEM,
    }

    if 'errorCode' in params and params['errorCode']:
        validated['errorCode'] = params['errorCode'].strip().upper()

    return validated


def build_metadata_filter(params: Dict[str, Any]) -> Dict[str, Any]:
    """Build the Bedrock KB metadata filter for manual retrieval."""
    conditions: List[Dict[str, Any]] = [
        {'equals': {'key': 'control-system', 'value': params.get('controlSystem') or DEFAULT_CONTROL_SYSTEM}}
    ]

    if 'errorCode' in params:
        conditions.append({'equals': {'key': 'error-code', 'value': params['errorCode']}})

    if len(conditions) == 1:
        return conditions[0]
    return {'andAll': conditions}


def build_search_query(params: Dict[str, Any]) -> str:
    """
    検索クエリを構築（エラーコード + トラブル情報）
    
    Args:
        params: パラメータ
        
    Returns:
        検索クエリ
    """
    query_parts = []
    
    # errorCode が含まれている場合は優先
    if 'errorCode' in params and params.get('errorCode'):
        query_parts.append(f"エラーコード {params['errorCode']}")
    
    # 基本クエリ
    query_parts.append(params['query'])
    
    # トラブルシュート関連キーワードを追加
    query_parts.append("トラブルシュート 対処方法 対応")
    
    return " ".join(query_parts)


def search_knowledge_base(query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Knowledge Base を全文検索（メタデータフィルターなし）
    
    Args:
        query: 検索クエリ
        
    Returns:
        検索結果リスト（最大3件）
        
    Raises:
        KBSearchError: 検索失敗
    """
    try:
        logger.info(f"Searching KB with query: {query}")
        
        vector_config: Dict[str, Any] = {
            'numberOfResults': 5,
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
                    'location': result.get('location', {}),
                    'metadata': result.get('metadata', {}),
                }
                results.append(result_item)
        
        logger.info(f"Found {len(results)} results, returning top 3")
        return results[:3]
        
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
        return "該当するトラブルシュート情報が見つかりませんでした"
    
    formatted = []
    formatted.append("【トラブルシュートマニュアル 検索結果】\n")
    
    for idx, result in enumerate(results, 1):
        formatted.append(f"【参考資料 {idx}】")
        formatted.append(f"関連度: {result.get('score', 0.0):.2%}\n")
        formatted.append(f"内容:\n{result.get('content', 'N/A')}\n")
        formatted.append("-" * 80)
    
    return "\n".join(formatted)


def write_citations(session_id: str, results: List[Dict[str, Any]]):
    """Write manual KB citation metadata into the troubleshooting session."""
    if not session_id:
        return
    citations = [
        {
            'uri': r.get('location', {}).get('s3Location', {}).get('uri', ''),
            'title': r.get('metadata', {}).get('title'),
            'document': r.get('metadata', {}).get('document', 'unknown'),
            'model': r.get('metadata', {}).get('model', ''),
            'score': str(r.get('score', 0.0)),
            'source_action': 'manual',
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
            'function': event.get('function', 'searchTroubleshootManuals'),
            'functionResponse': {
                'responseBody': {'TEXT': {'body': body}},
            },
        },
    }


def lambda_handler(event, context):
    """
    Action 3: KB Search2 Lambda ハンドラー
    Bedrock Agent からのアクション実行要求に応答
    トラブルシュートマニュアル全文検索用

    Args:
        event: Lambda イベント
        context: Lambda コンテキスト
        
    Returns:
        レスポンス
    """
    logger.info(f"KB Search2 Action invoked: {json.dumps(event)}")
    
    try:
        parameters = _extract_params(event)
        logger.info(f"Parameters: {parameters}")
        validated_params = validate_parameters(parameters)
        search_query = build_search_query({**parameters, **validated_params})
        filters = build_metadata_filter(validated_params)
        results = search_knowledge_base(search_query, filters)
        session_id = event.get('sessionAttributes', {}).get('session_id', '')
        write_citations(session_id, results)
        formatted_result = format_results(results)
        logger.info("KB Search2 completed successfully")
        return _make_response(event, 200, formatted_result)
    except KBSearchError as e:
        logger.error(f"KB Search error: {str(e)}")
        return _make_response(event, 400, f"エラー: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _make_response(event, 500, f"予期しないエラーが発生しました: {str(e)}")
