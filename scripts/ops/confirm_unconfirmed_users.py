#!/usr/bin/env python3
"""未確認（UNCONFIRMED）アカウントの一覧表示と、管理者による確認済み化。issue #99。

Cognito 既定メールの日次上限（50 通 / AWS アカウント、0900 UTC = 18:00 JST リセット）に当たると、
サインアップの確認コードが届かないままアカウントだけ UNCONFIRMED で作成されることがある。
その場合、管理者が確認済みにすれば利用者はサインアップ時に自分で決めたパスワードで
そのままログインできる（メール不要）。

前提（PR #101 レビュー、mona 2026-09-11）:
  サインアップ時のメールアドレスは所有確認ができていない。確認済みにしてよいのは、
  **信頼できる社内情報・経路で、正式な社内 ID と対象メールを照合できた場合に限る**。
  本人の「登録しました」という自己申告だけでは確認しない。
  照合した担当・日時・照合根拠の参照・対象・結果は社内の記録に残す（社員 ID や証明資料そのものを
  GitHub や本スクリプトの引数に載せない）。confirm には照合担当（--verified-by）と社内記録の参照
  （--evidence-ref）が必須で、標準出力の実施ログに残る。

再実行の扱い:
  - UNCONFIRMED             → 確認済み化 + email_verified=true（status=confirmed）
  - CONFIRMED で未検証のまま → email_verified=true だけ補う（status=verified-email。前回の途中失敗の復旧）
  - CONFIRMED で検証済み     → 何もしない（status=skipped-CONFIRMED）
  処理できなかった行があれば終了コード 1 で終わる。

使い方:
  # 1) 未確認アカウントの一覧（既定は本日 UTC 作成分。--all で全期間）
  AWS_PROFILE=<profile> AWS_REGION=ap-northeast-1 python scripts/ops/confirm_unconfirmed_users.py list [--all]
  # 2) 照合済みのアドレスを確認済みにする（--dry-run で対象だけ表示）
  python scripts/ops/confirm_unconfirmed_users.py confirm --emails a@meltec.co.jp b@meltec.co.jp \
      --verified-by <照合担当> --evidence-ref <社内記録の参照> [--dry-run]
  #    または照合済みの CSV（email 列）から
  python scripts/ops/confirm_unconfirmed_users.py confirm --csv confirmed.csv --verified-by ... --evidence-ref ...
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone

USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "ap-northeast-1_DN17ekXik")


def _client(region: str):
    import boto3
    return boto3.client("cognito-idp", region_name=region)


def list_unconfirmed(cognito, today_only: bool) -> list[dict]:
    users, kwargs = [], {"UserPoolId": USER_POOL_ID, "Filter": 'cognito:user_status = "UNCONFIRMED"', "Limit": 60}
    while True:
        r = cognito.list_users(**kwargs)
        users.extend(r.get("Users", []))
        if not r.get("PaginationToken"):
            break
        kwargs["PaginationToken"] = r["PaginationToken"]
    today = datetime.now(timezone.utc).date()
    out = []
    for u in users:
        created = u["UserCreateDate"]
        if today_only and created.astimezone(timezone.utc).date() != today:
            continue
        attrs = {a["Name"]: a["Value"] for a in u.get("Attributes", [])}
        out.append({"username": u["Username"], "email": attrs.get("email", ""), "name": attrs.get("name", ""),
                    "created": created.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    return sorted(out, key=lambda x: x["created"])


def _email_verified(user: dict) -> bool:
    attrs = {a["Name"]: a["Value"] for a in user.get("UserAttributes", [])}
    return attrs.get("email_verified", "").lower() == "true"


def _set_email_verified(cognito, email: str) -> None:
    cognito.admin_update_user_attributes(UserPoolId=USER_POOL_ID, Username=email,
                                         UserAttributes=[{"Name": "email_verified", "Value": "true"}])


def confirm(cognito, email: str, dry_run: bool) -> str:
    """確認状態（UserStatus）とメール検証状態（email_verified）を別々に見て、足りない方だけ進める。"""
    try:
        u = cognito.admin_get_user(UserPoolId=USER_POOL_ID, Username=email)
    except cognito.exceptions.UserNotFoundException:
        return "not-found"
    status = u["UserStatus"]
    if status == "UNCONFIRMED":
        if dry_run:
            return "would-confirm"
        cognito.admin_confirm_sign_up(UserPoolId=USER_POOL_ID, Username=email)
        _set_email_verified(cognito, email)
        return "confirmed"
    if status == "CONFIRMED" and not _email_verified(u):
        # 前回 admin_confirm_sign_up の後で属性更新に失敗した場合の復旧
        if dry_run:
            return "would-verify-email"
        _set_email_verified(cognito, email)
        return "verified-email"
    return f"skipped-{status}"


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["list", "confirm"])
    p.add_argument("--all", action="store_true", help="list: 本日分だけでなく全期間")
    p.add_argument("--emails", nargs="*", default=[])
    p.add_argument("--csv", help="照合済みの email 列を持つ CSV")
    p.add_argument("--verified-by", help="confirm: 社内 ID とメールを照合した担当（記録用）")
    p.add_argument("--evidence-ref", help="confirm: 照合根拠を残した社内記録の参照（記録用。資料そのものは渡さない）")
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-northeast-1"))
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    cognito = _client(a.region)

    if a.command == "list":
        rows = list_unconfirmed(cognito, today_only=not a.all)
        print(f"UNCONFIRMED users ({'all' if a.all else 'created today UTC'}): {len(rows)}")
        for r in rows:
            print(f"  {r['created']}  {r['email']}  {r['name']}")
        return 0

    if not a.verified_by or not a.evidence_ref:
        raise SystemExit("confirm には --verified-by（照合担当）と --evidence-ref（社内記録の参照）が必要です。"
                         "正式な社内 ID と対象メールを照合した対象だけを渡してください")
    emails = [e.strip().lower() for e in a.emails if e.strip()]
    if a.csv:
        with open(a.csv, encoding="utf-8-sig", newline="") as f:
            emails += [(r.get("email") or "").strip().lower() for r in csv.DictReader(f)]
    emails = [e for e in dict.fromkeys(emails) if e]
    if not emails:
        raise SystemExit("confirm には --emails か --csv が必要です")

    ran_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"confirm run={ran_at} verified-by={a.verified_by} evidence-ref={a.evidence_ref} dry-run={a.dry_run}")
    counts = {}
    for e in emails:
        try:
            status = confirm(cognito, e, a.dry_run)
        except Exception as ex:  # noqa: BLE001 - 1 件の失敗で止めず記録する（再実行で復旧できる）
            status = f"error: {type(ex).__name__}: {ex}"
        key = status.split(":")[0]
        counts[key] = counts.get(key, 0) + 1
        print(f"{e}: {status}")
    errors = counts.get("error", 0)
    print("done", counts, file=sys.stderr)
    if errors:
        print("失敗した行があります。原因を直してから同じ対象で再実行すると、確認済みだが未検証の状態も復旧します", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
