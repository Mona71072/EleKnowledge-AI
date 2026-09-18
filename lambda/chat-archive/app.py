"""EleKnowledge chat archive.

Triggered by the DynamoDB stream on `chatlogs-dev`. Every change (INSERT /
MODIFY / REMOVE, including soft-delete flags and TTL expirations) is written to
S3 as gzipped JSON Lines, partitioned by date, for long-term retention and
analysis with Athena. Nothing is lost before TTL physically removes the item.
"""
import json
import os
import gzip
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer

s3 = boto3.client("s3")
BUCKET = os.environ["ARCHIVE_BUCKET"]
PREFIX = os.environ.get("ARCHIVE_PREFIX", "chatlogs")
_deser = TypeDeserializer()


def _plain(image):
    if not image:
        return None
    out = {}
    for k, v in image.items():
        try:
            out[k] = _deser.deserialize(v)
        except Exception:
            out[k] = None
    return out


class _Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o) if o % 1 == 0 else float(o)
        if isinstance(o, (bytes, bytearray)):
            return o.decode("utf-8", "replace")
        if isinstance(o, set):
            return list(o)
        return super().default(o)


FAILED_PREFIX = os.environ.get("ARCHIVE_FAILED_PREFIX", "failed")


def _preserve_failed_batch(event, context, error):
    """失敗したバッチの生レコードを S3 の failed/ に残す（issue #86 P0、PR #96 レビュー）。

    Lambda の OnFailure 宛先（SQS）にはシャード / シーケンス番号などのメタデータしか入らず、
    DynamoDB Streams 自体は 24 時間で失効するため、本文を別に保存しないと復旧できない。
    ここは最善努力（S3 自体が落ちている場合は SQS のメタデータと 24 時間以内の再処理に頼る）。
    """
    try:
        now = datetime.now(timezone.utc)
        key = f"{FAILED_PREFIX}/dt={now:%Y-%m-%d}/{now:%Y%m%dT%H%M%S}-{context.aws_request_id}.json"
        payload = json.dumps({
            "error": f"{type(error).__name__}: {error}",
            "requestId": context.aws_request_id,
            "records": event.get("Records", []),
        }, cls=_Enc, ensure_ascii=False)
        s3.put_object(Bucket=BUCKET, Key=key, Body=payload.encode("utf-8"),
                      ContentType="application/json")
        print(f"[chat-archive] batch failed; raw records preserved at s3://{BUCKET}/{key}")
        return key
    except Exception as e2:  # noqa: BLE001
        print(f"[chat-archive] batch failed AND could not preserve raw records: {type(e2).__name__}: {e2}")
        return None


def handler(event, context):
    # The event-source mapping retries and then writes the complete invocation
    # record to its S3 OnFailure destination. A handler-level best-effort write
    # cannot cover timeouts or initialization errors, so it is deliberately not
    # part of the recovery guarantee.
    return _archive(event, context)


def _archive(event, context):
    records = event.get("Records", [])
    if not records:
        return {"archived": 0}

    first_ts = records[0].get("dynamodb", {}).get("ApproximateCreationDateTime")
    dt = (datetime.fromtimestamp(float(first_ts), tz=timezone.utc)
          if first_ts else datetime.now(timezone.utc))

    lines = []
    for r in records:
        d = r.get("dynamodb", {})
        lines.append(json.dumps({
            "eventName": r.get("eventName"),
            "eventID": r.get("eventID"),
            "approximateCreationDateTime": d.get("ApproximateCreationDateTime"),
            "keys": _plain(d.get("Keys")),
            "newImage": _plain(d.get("NewImage")),
            "oldImage": _plain(d.get("OldImage")),
            "userIdentity": r.get("userIdentity"),
        }, cls=_Enc, ensure_ascii=False))

    body = gzip.compress(("\n".join(lines) + "\n").encode("utf-8"))
    key = f"{PREFIX}/dt={dt:%Y-%m-%d}/{dt:%Y%m%dT%H%M%S}-{context.aws_request_id}.jsonl.gz"
    s3.put_object(Bucket=BUCKET, Key=key, Body=body,
                  ContentType="application/json", ContentEncoding="gzip")
    print(f"[chat-archive] archived={len(lines)} key={key}")
    return {"archived": len(lines), "key": key}
