"""
トラブルシューティング エージェント Action 4: KB Search3 Lambda
C資料（詳細な技術資料）を検索
メタデータフィルター: document (C資料), model, control-system
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
    region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))

# 環境変数
KB_ID = os.environ.get('KB_ID')


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
    メタデータフィルターを構築
    
    Args:
        params: 検証済みパラメータ
        
    Returns:
        メタデータフィルター
    """
    filters = {}
    
    # document フィルター: C資料
    filters['document'] = {
        'equals': {'key': 'document', 'value': 'C資料'}
    }
    
    # model フィルター（指定された場合）
    if 'model' in params:
        filters['model'] = {
            'equals': {'key': 'model', 'value': params['model']}
        }
    
    # control-system フィルター（指定された場合）
    if 'controlSystem' in params:
        filters['controlSystem'] = {
            'equals': {'key': 'control-system', 'value': params['controlSystem']}
        }
    
    return filters


def search_knowledge_base(query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Knowledge Base を検索（C資料）
    
    Args:
        query: 検索クエリ
        filters: メタデータフィルター
        
    Returns:
        検索結果リスト
        
    Raises:
        KBSearchError: 検索失敗
    """
    try:
        logger.info(f"Searching KB for C-Materials with query: {query}")
        
        # Bedrock Retrieve API を呼び出し
        response = bedrock_client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 10,
                    'overrideSearchType': 'SEMANTIC'
                }
            },
            text=query
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


def lambda_handler(event, context):
    """
    Action 4: KB Search3 Lambda ハンドラー
    Bedrock Agent からのアクション実行要求に応答
    C資料（詳細な技術資料）検索用
    
    Args:
        event: Lambda イベント
        context: Lambda コンテキスト
        
    Returns:
        レスポンス
    """
    logger.info(f"KB Search3 Action invoked: {json.dumps(event)}")
    
    try:
        # パラメータ抽出
        action_group = event.get('actionGroup', '')
        action_invocation = event.get('actionInvocation', {})
        parameters = {}
        
        if 'parameters' in action_invocation:
            for param in action_invocation['parameters']:
                parameters[param.get('name')] = param.get('value', '')
        
        logger.info(f"Parameters: {parameters}")
        
        # パラメータ検証
        validated_params = validate_parameters(parameters)
        
        # メタデータフィルター構築
        filters = build_metadata_filter(validated_params)
        
        # Knowledge Base 検索
        results = search_knowledge_base(validated_params['query'], filters)
        
        # 結果フォーマット
        formatted_result = format_results(results)
        
        logger.info("KB Search3 completed successfully")
        
        # Bedrock Agent 用レスポンス
        return {
            'actionGroup': action_group,
            'actionInvocation': action_invocation,
            'responseBody': {
                'TEXT': {
                    'body': formatted_result
                }
            }
        }
        
    except KBSearchError as e:
        logger.error(f"KB Search error: {str(e)}")
        return {
            'actionGroup': event.get('actionGroup', ''),
            'actionInvocation': event.get('actionInvocation', {}),
            'responseBody': {
                'TEXT': {
                    'body': f"エラー: {str(e)}"
                }
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'actionGroup': event.get('actionGroup', ''),
            'actionInvocation': event.get('actionInvocation', {}),
            'responseBody': {
                'TEXT': {
                    'body': f"予期しないエラーが発生しました: {str(e)}"
                }
            }
        }