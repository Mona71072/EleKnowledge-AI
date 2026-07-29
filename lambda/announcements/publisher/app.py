"""
EleKnowledge Announcements - Scheduled publisher

EventBridge schedule (every 5 min): promote due scheduled items to published.
Read Lambda also surfaces due scheduled items, so users see them immediately;
this job keeps admin list status badges accurate.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'))
ANNOUNCEMENTS_TABLE = os.environ.get('ANNOUNCEMENTS_TABLE')
table = dynamodb.Table(ANNOUNCEMENTS_TABLE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def promote_due(now_iso: Optional[str] = None) -> dict:
    """Flip status scheduled -> published for items whose publishAt has arrived."""
    now_iso = now_iso or _now_iso()
    promoted = []
    kwargs = {
        'IndexName': 'status-publishAt-index',
        'KeyConditionExpression': Key('status').eq('scheduled') & Key('publishAt').lte(now_iso),
    }
    while True:
        resp = table.query(**kwargs)
        for item in resp.get('Items', []):
            aid = item['announcementId']
            # Conditional update: only if still scheduled (avoid races with admin edits)
            try:
                table.update_item(
                    Key={'announcementId': aid},
                    UpdateExpression='SET #s = :pub, updatedAt = :now',
                    ConditionExpression='#s = :sched',
                    ExpressionAttributeNames={'#s': 'status'},
                    ExpressionAttributeValues={
                        ':pub': 'published',
                        ':sched': 'scheduled',
                        ':now': now_iso,
                    },
                )
                promoted.append(aid)
            except ClientError as e:
                if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                    raise
        lek = resp.get('LastEvaluatedKey')
        if not lek:
            break
        kwargs['ExclusiveStartKey'] = lek

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
