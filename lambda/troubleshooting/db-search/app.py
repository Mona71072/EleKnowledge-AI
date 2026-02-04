"""
トラブルシューティング エージェント Action 1: DB Search Lambda
DynamoDB から現場情報と設置機器情報を取得
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
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# 環境変数
SITES_TABLE = os.environ.get('SITES_TABLE', 'sites')


class DBSearchError(Exception):
    """DB検索エラー"""
    pass


def validate_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    パラメータ検証
    
    Args:
        params: アクション用パラメータ
        
    Returns:
        検証済みパラメータ
        
    Raises:
        DBSearchError: パラメータ不正
    """
    construction_number = params.get('constructionNumber', '').strip()
    if not construction_number:
        raise DBSearchError("constructionNumber は必須です")
    
    return {'constructionNumber': construction_number}


def query_sites_table(construction_number: str) -> Dict[str, Any]:
    """
    DynamoDB sites テーブルをクエリ
    
    Args:
        construction_number: 工事番号
        
    Returns:
        現場情報
        
    Raises:
        DBSearchError: クエリ失敗
    """
    try:
        table = dynamodb.Table(SITES_TABLE)
        
        response = table.get_item(
            Key={'constructionNumber': construction_number}
        )
        
        if 'Item' not in response:
            logger.info(f"No site found for constructionNumber: {construction_number}")
            return {
                'found': False,
                'constructionNumber': construction_number,
                'message': '指定された工事番号の現場情報が見つかりません'
            }
        
        return {
            'found': True,
            'item': response['Item']
        }
        
    except Exception as e:
        logger.error(f"Error querying sites table: {str(e)}")
        raise DBSearchError(f"DynamoDB クエリ失敗: {str(e)}")


def format_result(query_result: Dict[str, Any]) -> str:
    """
    クエリ結果をテキスト形式にフォーマット
    
    Args:
        query_result: クエリ結果
        
    Returns:
        フォーマット済みテキスト
    """
    if not query_result.get('found'):
        return query_result.get('message', '現場情報が見つかりません')
    
    item = query_result['item']
    result = []
    
    result.append(f"【現場情報取得完了】")
    result.append(f"工事番号: {item.get('constructionNumber', 'N/A')}")
    result.append(f"現場名: {item.get('siteName', 'N/A')}")
    result.append(f"住所: {item.get('address', 'N/A')}")
    
    # 設置機器情報
    result.append(f"\n【設置機器情報】")
    if item.get('installedEquipment'):
        for idx, equipment in enumerate(item['installedEquipment'], 1):
            result.append(f"\n機器 {idx}:")
            result.append(f"  機種: {equipment.get('model', 'N/A')}")
            result.append(f"  制御システム: {equipment.get('controlSystem', 'N/A')}")
            result.append(f"  設置日: {equipment.get('installationDate', 'N/A')}")
            result.append(f"  最終メンテナンス日: {equipment.get('lastMaintenanceDate', 'N/A')}")
    else:
        result.append("設置機器情報なし")
    
    # 連絡先
    result.append(f"\n【連絡先】")
    if item.get('contactPerson'):
        contact = item['contactPerson']
        result.append(f"名前: {contact.get('name', 'N/A')}")
        result.append(f"電話: {contact.get('phone', 'N/A')}")
        result.append(f"メール: {contact.get('email', 'N/A')}")
    else:
        result.append("連絡先情報なし")
    
    # 過去のトラブル履歴（存在する場合）
    if item.get('troubleHistory'):
        result.append(f"\n【過去のトラブル履歴】")
        for idx, trouble in enumerate(item['troubleHistory'][:5], 1):  # 最新5件
            result.append(f"\n{idx}. {trouble.get('date', 'N/A')}")
            result.append(f"   内容: {trouble.get('description', 'N/A')}")
            result.append(f"   原因: {trouble.get('cause', 'N/A')}")
            result.append(f"   対処: {trouble.get('resolution', 'N/A')}")
    
    return "\n".join(result)


def lambda_handler(event, context):
    """
    Action 1: DB Search Lambda ハンドラー
    Bedrock Agent からのアクション実行要求に応答
    
    Args:
        event: Lambda イベント
        context: Lambda コンテキスト
        
    Returns:
        レスポンス
    """
    logger.info(f"DB Search Action invoked: {json.dumps(event)}")
    
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
        
        # DynamoDB クエリ実行
        query_result = query_sites_table(validated_params['constructionNumber'])
        
        # 結果フォーマット
        formatted_result = format_result(query_result)
        
        logger.info("DB Search completed successfully")
        
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
        
    except DBSearchError as e:
        logger.error(f"DB Search error: {str(e)}")
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