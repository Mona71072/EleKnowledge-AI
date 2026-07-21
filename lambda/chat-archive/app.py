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


def handler(event, context):
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
    return {"archived": len(lines), "key": key}
