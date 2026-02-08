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

# AWSクライアント
dynamodb = boto3.resource('dynamodb')

# 環境変数 (SAMパラメータから取得)
SITES_TABLE_NAME = os.environ.get('SitesTableName', 'sites')


class DBSearchError(Exception):
    """DB検索エラー"""
    pass


def validate_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """パラメータ検証"""
    construction_number = params.get('constructionNumber', '').strip()
    if not construction_number:
        raise DBSearchError("constructionNumber パラメータが不足しています")
    return {'constructionNumber': construction_number}


def query_dynamodb(construction_number: str) -> Dict[str, Any]:
    """DynamoDBクエリ"""
    try:
        table = dynamodb.Table(SITES_TABLE_NAME)
        response = table.get_item(
            Key={'constructionNumber': construction_number}
        )
        item = response.get('Item')
        if not item:
            raise DBSearchError("該工事番号の現場情報が見つかりません")
        return item
    except Exception as e:
        logger.error(f"DynamoDBエラー: {str(e)}")
        raise DBSearchError("データベース接続に失敗しました")


def format_response(site_info: Dict[str, Any]) -> str:
    """レスポンスフォーマット"""
    result = [
        f"工事番号: {site_info['constructionNumber']}",
        f"現場名: {site_info.get('siteName', '不明')}",
        f"住所: {site_info.get('address', '不明')}",
        "\n設置機器情報:",
    ]
    equipment = site_info.get('installedEquipment', [])
    if not equipment:
        result.append("  - なし")
    else:
        for idx, eq in enumerate(equipment, 1):
            result.append(f"  {idx}. 機種: {eq['model']}, 制御システム: {eq['controlSystem']}")
    return "\n".join(result)


def lambda_handler(event, context):
    """Lambdaハンドラー"""
    try:
        # パラメータ取得
        parameters = event.get('parameters', {})
        validated = validate_parameters(parameters)
        
        # DynamoDB検索
        site_data = query_dynamodb(validated['constructionNumber'])
        
        # 結果整形
        formatted = format_response(site_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'actionGroup': event['actionGroup'],
                'apiPath': event['apiPath'],
                'httpMethod': event['httpMethod'],
                'responseBody': {
                    'TEXT': {
                        'body': formatted
                    }
                }
            })
        }
    except DBSearchError as e:
        logger.error(f"処理エラー: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '内部エラーが発生しました'})
        }