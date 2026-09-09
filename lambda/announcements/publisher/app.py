"""
EleKnowledge Announcements - Scheduled publisher

EventBridge schedule (every 5 min): promote due scheduled items to published.
Read Lambda also surfaces due scheduled items, so users see them immediately;
this job keeps admin list status badges accurate.
"""
from __future__ import annotations

import os
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from timeutil import normalize_utc_iso, now_utc_iso

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))
ANNOUNCEMENTS_TABLE = os.environ.get('ANNOUNCEMENTS_TABLE')
table = dynamodb.Table(ANNOUNCEMENTS_TABLE)


def _now_iso() -> str:
    return now_utc_iso()


def promote_due(now_iso: Optional[str] = None) -> dict:
    """Flip status scheduled -> published for items whose publishAt has arrived."""
    now_iso = normalize_utc_iso(now_iso) if now_iso else _now_iso()
    if not now_iso:
        raise ValueError('now_iso could not be normalized')
    promoted = []
    kwargs = {
        'IndexName': 'status-publishAt-index',
        'KeyConditionExpression': Key('status').eq('scheduled') & Key('publishAt').lte(now_iso),
    }
    # GSI のキー（status / publishAt）を更新しながら同じ GSI をページングすると項目を取りこぼすため、
    # 先に全件を取り出してから更新する（issue #94 R1）
    due_items = []
    while True:
        resp = table.query(**kwargs)
        due_items.extend(resp.get('Items', []))
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        kwargs['ExclusiveStartKey'] = lek

    if True:
        for item in due_items:
            aid = item['announcementId']
            # Defense: skip legacy rows whose normalized publishAt is still in the future
            try:
                pub = normalize_utc_iso(item.get('publishAt'))
            except (TypeError, ValueError):
                pub = item.get('publishAt')
            if pub and pub > now_iso:
                continue
            # Conditional update: only if still scheduled (avoid races with admin edits)
            try:
                table.update_item(
                    Key={'announcementId': aid},
                    UpdateExpression='SET #s = :pub, updatedAt = :now, publishAt = :pnorm',
                    ConditionExpression='#s = :sched',
                    ExpressionAttributeNames={'#s': 'status'},
                    ExpressionAttributeValues={
                        ':pub': 'published',
                        ':sched': 'scheduled',
                        ':now': now_iso,
                        ':pnorm': pub or item.get('publishAt'),
                    },
                )
                promoted.append(aid)
            except ClientError as e:
                if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                    raise

    return {'promoted': promoted, 'count': len(promoted), 'serverTime': now_iso}


def lambda_handler(event, context):
    try:
        result = promote_due()
        print(f"[announcements-publisher] promoted={result['count']} ids={result['promoted']}")
        return result
    except ClientError as e:
        print(f"[announcements-publisher] ClientError: {e}")
        raise
    except Exception as e:  # noqa: BLE001
        print(f"[announcements-publisher] Unexpected error: {e}")
        raise
