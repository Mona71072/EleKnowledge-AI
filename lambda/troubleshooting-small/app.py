import os
import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# 環境変数取得 (技術検証時はコメントアウト)
# TABLE_NAME = os.environ['SITES_TABLE_NAME']
TABLE_NAME = "sites"  # 技術検証用

def lambda_handler(event, context):
    """現場DB検索関数"""
    try:
        # 入力検証
        construction_number = event.get('constructionNumber')
        if not construction_number:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "constructionNumberは必須です"})
            }

        # DynamoDBクライアント初期化
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(TABLE_NAME)

        # クエリ実行
        query_result = table.query(
            KeyConditionExpression=Key('constructionNumber').eq(construction_number)
        )

        # 結果整形
        items = query_result.get('Items', [])
        sites = [
            {
                "constructionNumber": item['constructionNumber'],
                "sitesName": item.get('sitesName', '不明'),
                "model": item.get('model', '不明')
            } for item in items
        ]

        return {
            'statusCode': 200,
            'body': json.dumps({"sites": sites})
        }
    except ClientError as e:
        print(f"[ERROR] DynamoDBクエリ失敗: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "データベース接続エラー"})
        }

# テスト用エントリポイント
if __name__ == "__main__":
    test_event = {"constructionNumber": "EIK54801"}
    print(lambda_handler(test_event, None))