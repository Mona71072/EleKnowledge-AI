#!/usr/bin/env python3
"""利用者アカウントの事前発行（メール送信なし）。issue #99「300 人一斉展開」の案 B。

Cognito 既定のメール送信は 1 日 50 通で止まるため、サインアップ + 確認コードの代わりに
管理者が CSV から一括作成し、初期パスワードを社内経路で配布する。

やること（1 行 = 1 人）:
  1. AdminCreateUser（MessageAction=SUPPRESS: 招待メールを送らない、email_verified=true）
  2. AdminSetUserPassword（Permanent=True: 初回ログインでの変更要求を出さない。
     フロント / login Lambda は NEW_PASSWORD_REQUIRED を扱えないため必須）
  3. users テーブルに signup Lambda と同じ形の項目を作成（userId=sub, email, username, createdAt, role=user）
  4. 生成した初期パスワードを --out の CSV に書く（リポジトリ外に置き、配布後に削除する）

既に存在するユーザーはスキップする（再実行しても安全）。PreSignUp トリガ（ドメイン制限）は
AdminCreateUser でも動くため、許可ドメイン外のアドレスは Cognito 側で拒否される。

使い方:
  AWS_PROFILE=<profile> AWS_REGION=ap-northeast-1 \
  python scripts/ops/provision_users.py --csv users.csv --out C:/secure/initial-passwords.csv [--dry-run]

CSV 形式（ヘッダ必須）: email[,name]
"""
from __future__ import annotations

import argparse
import csv
import os
import secrets
import string
import sys
import time

USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "ap-northeast-1_DN17ekXik")
USERS_TABLE = os.environ.get("USERS_TABLE", "users-dev")

# Cognito のパスワードポリシー（最小 8 文字）を満たす 12 文字: 英大小・数字・記号を各 1 文字以上含める
_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*"


def generate_password(length: int = 12) -> str:
    while True:
        pw = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        if (any(c.islower() for c in pw) and any(c.isupper() for c in pw)
                and any(c.isdigit() for c in pw) and any(c in "!@#$%^&*" for c in pw)):
            return pw


def read_rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "email" not in (reader.fieldnames or []):
            raise SystemExit("CSV に email 列がありません")
        rows = []
        for r in reader:
            email = (r.get("email") or "").strip().lower()
            if not email:
                continue
            rows.append({"email": email, "name": (r.get("name") or "").strip()})
    # 重複除去（後勝ちではなく先勝ち）
    seen, out = set(), []
    for r in rows:
        if r["email"] in seen:
            continue
        seen.add(r["email"]); out.append(r)
    return out


def user_exists(cognito, email: str) -> bool:
    try:
        cognito.admin_get_user(UserPoolId=USER_POOL_ID, Username=email)
        return True
    except cognito.exceptions.UserNotFoundException:
        return False


def provision(cognito, table, row: dict, dry_run: bool) -> dict:
    email, name = row["email"], row["name"]
    if user_exists(cognito, email):
        return {"email": email, "status": "skipped-exists", "password": ""}
    if dry_run:
        return {"email": email, "status": "would-create", "password": ""}

    attrs = [{"Name": "email", "Value": email}, {"Name": "email_verified", "Value": "true"}]
    if name:
        attrs.append({"Name": "name", "Value": name})
    password = generate_password()
    resp = cognito.admin_create_user(
        UserPoolId=USER_POOL_ID, Username=email, UserAttributes=attrs,
        MessageAction="SUPPRESS", TemporaryPassword=password,
    )
    sub = next(a["Value"] for a in resp["User"]["Attributes"] if a["Name"] == "sub")
    cognito.admin_set_user_password(UserPoolId=USER_POOL_ID, Username=email, Password=password, Permanent=True)
    table.put_item(Item={
        "userId": sub, "email": email,
        "username": name if name else email.split("@")[0],
        "createdAt": int(time.time()), "role": "user",
        "provisionedBy": "scripts/ops/provision_users.py",
    })
    return {"email": email, "status": "created", "password": password, "userId": sub}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--out", required=True, help="初期パスワードの出力先（リポジトリ外）")
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-northeast-1"))
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    if os.path.abspath(a.out).startswith(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))):
        raise SystemExit("--out はリポジトリの外を指定してください（パスワードを含むため）")

    import boto3
    cognito = boto3.client("cognito-idp", region_name=a.region)
    table = boto3.resource("dynamodb", region_name=a.region).Table(USERS_TABLE)

    rows = read_rows(a.csv)
    print(f"{len(rows)} 件を処理します（dry-run={a.dry_run}）", file=sys.stderr)
    results, counts = [], {}
    for i, row in enumerate(rows, 1):
        try:
            r = provision(cognito, table, row, a.dry_run)
        except Exception as e:  # noqa: BLE001 - 1 件の失敗で止めず記録する
            r = {"email": row["email"], "status": f"error: {type(e).__name__}: {e}", "password": ""}
        results.append(r); counts[r["status"].split(":")[0]] = counts.get(r["status"].split(":")[0], 0) + 1
        print(f"[{i}/{len(rows)}] {r['email']} {r['status']}", file=sys.stderr)

    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["email", "status", "password", "userId"], extrasaction="ignore")
        w.writeheader(); w.writerows(results)
    print(f"done {counts} -> {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
