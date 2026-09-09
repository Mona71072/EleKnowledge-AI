#!/usr/bin/env python3
"""未確認（UNCONFIRMED）アカウントの一覧表示と、管理者による確認済み化。issue #99。

Cognito 既定メールの日次上限（50 通）に当たると、サインアップの確認コードが届かないまま
アカウントだけ UNCONFIRMED で作成されることがある。その場合、管理者が確認済みにすれば
利用者はサインアップ時に自分で決めたパスワードでそのままログインできる（メール不要）。

注意: サインアップ時のメールアドレスは所有確認ができていない。確認済みにする前に、
そのアドレスの本人へ「登録しましたか」を確認すること（会社ドメイン限定のため実害は小さいが、なりすましの排除）。

使い方:
  # 1) 未確認アカウントの一覧（既定は本日 UTC 作成分。--all で全期間）
  AWS_PROFILE=<profile> AWS_REGION=ap-northeast-1 python scripts/ops/confirm_unconfirmed_users.py list [--all]
  # 2) 指定アドレスを確認済みにする（--dry-run で対象だけ表示）
  python scripts/ops/confirm_unconfirmed_users.py confirm --emails a@meltec.co.jp b@meltec.co.jp [--dry-run]
  #    または CSV（email 列）から
  python scripts/ops/confirm_unconfirmed_users.py confirm --csv confirmed.csv
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


def confirm(cognito, email: str, dry_run: bool) -> str:
    try:
        u = cognito.admin_get_user(UserPoolId=USER_POOL_ID, Username=email)
    except cognito.exceptions.UserNotFoundException:
        return "not-found"
    if u["UserStatus"] != "UNCONFIRMED":
        return f"skipped-{u['UserStatus']}"
    if dry_run:
        return "would-confirm"
    cognito.admin_confirm_sign_up(UserPoolId=USER_POOL_ID, Username=email)
    cognito.admin_update_user_attributes(UserPoolId=USER_POOL_ID, Username=email,
                                         UserAttributes=[{"Name": "email_verified", "Value": "true"}])
    return "confirmed"


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["list", "confirm"])
    p.add_argument("--all", action="store_true", help="list: 本日分だけでなく全期間")
    p.add_argument("--emails", nargs="*", default=[])
    p.add_argument("--csv", help="email 列を持つ CSV")
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

    emails = [e.strip().lower() for e in a.emails if e.strip()]
    if a.csv:
        with open(a.csv, encoding="utf-8-sig", newline="") as f:
            emails += [(r.get("email") or "").strip().lower() for r in csv.DictReader(f)]
    emails = [e for e in dict.fromkeys(emails) if e]
    if not emails:
        raise SystemExit("confirm には --emails か --csv が必要です")
    counts = {}
    for e in emails:
        status = confirm(cognito, e, a.dry_run)
        counts[status] = counts.get(status, 0) + 1
        print(f"{e}: {status}")
    print("done", counts, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
