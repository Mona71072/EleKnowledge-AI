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
        f"現場名: {site_info.get('sitesName', '不明')}",
        f"現場番号: {site_info.get('sitesNumber', '不明')}",
        "\n設置機器情報:",
        f"  機種: {site_info.get('model', '不明')}",
        f"  制御システム: {site_info.get('controlSystem', '不明')}",
    ]
    if site_info.get('constructionRep'):
        result.append(f"\n担当者: {site_info['constructionRep']}")
    return "\n".join(result)


def _extract_params(event: Dict[str, Any]) -> Dict[str, Any]:
    """Bedrock Agent (list/requestBody) / テストイベント (dict) 両フォーマット対応"""
    # POST requestBody 形式 (Bedrock Agent API Schema)
    req_body = event.get('requestBody', {}).get('content', {}).get('application/json', {})
    if req_body.get('properties'):
        return {p['name']: p.get('value', '') for p in req_body['properties']}
    # GET query parameters 形式 (top-level list)
    raw = event.get('parameters', [])
    if isinstance(raw, list):
        return {p['name']: p.get('value', '') for p in raw}
    return raw  # dict 形式 (テストイベント用)


def _make_response(event: Dict[str, Any], status: int, body: str) -> Dict[str, Any]:
    """Bedrock Agent action group レスポンス形式"""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup', ''),
            'apiPath': event.get('apiPath', '/site-info'),
            'httpMethod': event.get('httpMethod', 'GET'),
            'httpStatusCode': status,
            'responseBody': {'TEXT': {'body': body}},
        },
    }


def lambda_handler(event, context):
    """Lambdaハンドラー"""
    try:
        parameters = _extract_params(event)
        validated = validate_parameters(parameters)
        site_data = query_dynamodb(validated['constructionNumber'])
        formatted = format_response(site_data)
        return _make_response(event, 200, formatted)
    except DBSearchError as e:
        logger.error(f"処理エラー: {str(e)}")
        return _make_response(event, 400, f"エラー: {str(e)}")
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        return _make_response(event, 500, "内部エラーが発生しました")