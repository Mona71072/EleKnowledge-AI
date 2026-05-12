"""
DynamoDB sites テーブルにテストデータを投入するスクリプト

使い方:
  python tests/seed/load_sites.py [--table <table_name>] [--endpoint <endpoint_url>]

  # AWS 本番環境
  python tests/seed/load_sites.py

  # DynamoDB Local
  python tests/seed/load_sites.py --endpoint http://localhost:8000
"""
import argparse
import json
import os
from pathlib import Path
import boto3


SEED_FILE = Path(__file__).parent / "sites_seed.json"
DEFAULT_TABLE = os.environ.get("SitesTableName", "sites")
DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def load(table_name: str, endpoint_url: str | None) -> None:
    kwargs = {"region_name": DEFAULT_REGION}
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url

    dynamodb = boto3.resource("dynamodb", **kwargs)
    table = dynamodb.Table(table_name)

    items = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    for item in items:
        table.put_item(Item=item)
        print(f"  投入: {item['constructionNumber']} ({item['siteName']})")

    print(f"\n{len(items)} 件投入完了 → テーブル: {table_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="sites テーブルにシードデータを投入")
    parser.add_argument("--table", default=DEFAULT_TABLE, help="DynamoDB テーブル名")
    parser.add_argument("--endpoint", default=None, help="DynamoDB エンドポイント URL（ローカル用）")
    args = parser.parse_args()

    print(f"シードデータ投入開始: {SEED_FILE}")
    load(args.table, args.endpoint)


if __name__ == "__main__":
    main()
