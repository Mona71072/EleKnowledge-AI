#!/usr/bin/env python3
"""chatlogs の既存行に日別集計キー（metricDay / metricDayShard）を付けるバックフィル（issue #130）。

日別 GSI metricDayShard-timestamp-index は、キー属性を持つ行しか載らない。GSI 追加より前に書かれた
TTL 内（約60日）の行にはキーが無いため、集計をこの GSI の Query へ切り替える前にこのスクリプトで埋める。

安全策:
  - 既定は dry-run（件数だけ出して何も書かない）。書き込みは --apply を付けたときだけ。
  - 更新は ConditionExpression で「行が存在し、かつ metricDayShard が未設定」の場合だけ行う。
    書込み側が既にキーを付けた行や、並行実行で付いた行は上書きしない（二重付与にならない）。
  - 新規行を作らない（attribute_exists(sessionId) を条件に含める）。
  - timestamp が解釈できない行は更新せず件数だけ数える。
  - 書込みは --rps で絞り、スロットリングは指数バックオフで再試行する。
  - 出力は件数だけ。本文（content）や sessionId / messageId は出さない。
  - --verify-days N は、直近 N 日について「全件 Scan + JST 日付での数え上げ」と「GSI の全シャード Query」の
    件数が一致するかを確認する（移行前後の値の一致の確認。読み取りのみ）。

Scan を使う（一回限りの運用作業）。Lambda には入れない（集計ロールから Scan を外すため）。

使い方（AWS 認証は運用者のローカル設定。対象は chatlogs-<env> のみ）:
  python scripts/ops/backfill_chatlogs_metric_day.py --table chatlogs-dev --region ap-northeast-1
  python scripts/ops/backfill_chatlogs_metric_day.py --table chatlogs-dev --apply --rps 20
  python scripts/ops/backfill_chatlogs_metric_day.py --table chatlogs-dev --verify-days 3
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEYS_MODULE_PATH = ROOT / "lambda" / "rag" / "rag-function" / "chatlog_metric_keys.py"
INDEX_NAME = "metricDayShard-timestamp-index"
RETRY_LIMIT = 6
THROTTLE_CODES = {"ProvisionedThroughputExceededException", "ThrottlingException", "RequestLimitExceeded"}


def _load_keys_module():
    spec = importlib.util.spec_from_file_location("chatlog_metric_keys", KEYS_MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


keys = _load_keys_module()
JST = keys.JST


def _retry(call, sleep=time.sleep):
    """スロットリングだけを指数バックオフで再試行する。それ以外の例外はそのまま投げる。"""
    delay = 0.5
    for attempt in range(RETRY_LIMIT):
        try:
            return call()
        except Exception as error:  # noqa: BLE001 - botocore の ClientError を code で判定する
            code = getattr(error, "response", {}).get("Error", {}).get("Code")
            if code not in THROTTLE_CODES or attempt == RETRY_LIMIT - 1:
                raise
            sleep(delay)
            delay = min(delay * 2, 16)


def scan_unkeyed(table, page_size: int = 200):
    """metricDayShard が無い行を Scan する（一回限り）。必要な属性だけ取り、本文は読まない。"""
    kwargs = {
        "ProjectionExpression": "sessionId, messageId, #ts, #del",
        "ExpressionAttributeNames": {"#ts": "timestamp", "#del": "deleted"},
        "FilterExpression": "attribute_not_exists(metricDayShard)",
        "Limit": page_size,
    }
    while True:
        resp = table.scan(**kwargs)
        for item in resp.get("Items", []):
            yield item
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            return
        kwargs["ExclusiveStartKey"] = lek


def plan_update(item: dict, shard_count: int):
    """1 行について (metricDay, metricDayShard) を決める。timestamp が解釈できなければ None。"""
    ts = keys.parse_chatlog_timestamp(item.get("timestamp"))
    if ts is None:
        return None
    return keys.metric_day_keys(ts, item["messageId"], shard_count=shard_count)


def run_backfill(table, apply: bool, rps: float, shard_count: int, sleep=time.sleep) -> dict:
    """未キーの行を走査し、dry-run なら件数だけ、apply なら条件付きで更新する。"""
    summary = Counter()
    per_day = Counter()
    interval = 1.0 / rps if rps > 0 else 0.0
    for item in scan_unkeyed(table):
        summary["scanned"] += 1
        planned = plan_update(item, shard_count)
        if planned is None:
            summary["skipped_bad_timestamp"] += 1
            continue
        per_day[planned["metricDay"]] += 1
        if not apply:
            summary["would_update"] += 1
            continue
        try:
            _retry(lambda: table.update_item(
                Key={"sessionId": item["sessionId"], "messageId": item["messageId"]},
                UpdateExpression="SET metricDay = :d, metricDayShard = :s",
                ConditionExpression="attribute_exists(sessionId) AND attribute_not_exists(metricDayShard)",
                ExpressionAttributeValues={":d": planned["metricDay"], ":s": planned["metricDayShard"]},
            ), sleep=sleep)
            summary["updated"] += 1
        except Exception as error:  # noqa: BLE001
            code = getattr(error, "response", {}).get("Error", {}).get("Code")
            if code == "ConditionalCheckFailedException":
                summary["already_keyed_or_gone"] += 1
            else:
                summary["errors"] += 1
                print(f"[backfill] write error code={code or type(error).__name__}", file=sys.stderr)
        if interval:
            sleep(interval)
    summary = dict(summary)
    summary["perDay"] = dict(sorted(per_day.items()))
    summary["mode"] = "apply" if apply else "dry-run"
    return summary


def _jst_day_of_item(item: dict):
    ts = keys.parse_chatlog_timestamp(item.get("timestamp"))
    return ts.astimezone(JST).date().isoformat() if ts else None


def verify_days(table, days: list[date], shard_count: int) -> list[dict]:
    """各日について、Scan で数えた件数と GSI 全シャードの Query 件数を比べる（deleted は除外。読み取りのみ）。"""
    wanted = {d.isoformat() for d in days}
    scanned = Counter()
    kwargs = {
        "ProjectionExpression": "sessionId, messageId, #ts, #del",
        "ExpressionAttributeNames": {"#ts": "timestamp", "#del": "deleted"},
        "Limit": 500,
    }
    while True:
        resp = table.scan(**kwargs)
        for item in resp.get("Items", []):
            if item.get("deleted") is True:
                continue
            day = _jst_day_of_item(item)
            if day in wanted:
                scanned[day] += 1
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
        kwargs["ExclusiveStartKey"] = lek

    report = []
    for d in sorted(days):
        queried = 0
        for shard in range(shard_count):
            kw = {
                "IndexName": INDEX_NAME,
                "KeyConditionExpression": "metricDayShard = :k",
                "ExpressionAttributeValues": {":k": f"{d.isoformat()}#{shard}"},
                "ProjectionExpression": "sessionId",
                # 集計 Lambda と同じ除外条件（論理削除の行は数えない）
                "FilterExpression": "attribute_not_exists(#del) OR #del = :false",
                "ExpressionAttributeNames": {"#del": "deleted"},
            }
            kw["ExpressionAttributeValues"][":false"] = False
            while True:
                resp = table.query(**kw)
                queried += len(resp.get("Items", []))
                lek = resp.get("LastEvaluatedKey")
                if not lek:
                    break
                kw["ExclusiveStartKey"] = lek
        report.append({"day": d.isoformat(), "scan": scanned[d.isoformat()], "query": queried,
                       "match": scanned[d.isoformat()] == queried})
    return report


def _build_table(table_name: str, region: str):
    import boto3  # 運用者のローカル実行専用（Lambda には含めない）

    return boto3.resource("dynamodb", region_name=region).Table(table_name)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--table", required=True, help="chatlogs-<env>")
    parser.add_argument("--region", default="ap-northeast-1")
    parser.add_argument("--apply", action="store_true", help="実際に書き込む（既定は dry-run）")
    parser.add_argument("--rps", type=float, default=20.0, help="書込みの上限（件/秒）")
    parser.add_argument("--shards", type=int, default=keys.METRIC_DAY_SHARD_COUNT,
                        help="シャード数（書込み側 CHATLOGS_METRIC_SHARDS と一致させる）")
    parser.add_argument("--verify-days", type=int, default=0, help="直近 N 日を Scan と Query で照合する")
    args = parser.parse_args(argv)

    if not args.table.startswith("chatlogs-"):
        parser.error("--table は chatlogs-<env> を指定する")
    if args.shards < 1:
        parser.error("--shards は1以上を指定する")
    if args.rps <= 0:
        parser.error("--rps は0より大きい値を指定する")
    if not 0 <= args.verify_days <= 60:
        parser.error("--verify-days は0から60を指定する")
    table = _build_table(args.table, args.region)

    if args.verify_days:
        today = datetime.now(JST).date()
        days = [today - timedelta(days=n) for n in range(1, args.verify_days + 1)]
        report = verify_days(table, days, args.shards)
        print(json.dumps({"verify": report}, ensure_ascii=False, indent=2))
        return 0 if all(r["match"] for r in report) else 2

    summary = run_backfill(table, apply=args.apply, rps=args.rps, shard_count=args.shards)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary.get("errors") or summary.get("skipped_bad_timestamp") else 0


if __name__ == "__main__":
    sys.exit(main())
