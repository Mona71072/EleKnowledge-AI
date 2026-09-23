#!/usr/bin/env python3
"""利用者アカウントの事前発行（メール送信なし）。issue #99「300 人一斉展開」の案 B。

Cognito 既定のメール送信は 1 日 50 通（AWS アカウント単位、0900 UTC = 18:00 JST にリセット）で
止まるため、サインアップ + 確認コードの代わりに管理者が CSV から一括作成し、初期パスワードを
社内経路で配布する。

やること（1 行 = 1 人）:
  1. AdminCreateUser（MessageAction=SUPPRESS: 招待メールを送らない、email_verified=true）
  2. AdminSetUserPassword（Permanent=True: 初回ログインでの変更要求を出さない。
     フロント / login Lambda は NEW_PASSWORD_REQUIRED を扱えないため必須）
  3. users テーブルに signup Lambda と同じ形の項目を作成（userId=sub, email, username, createdAt, role=user）
  4. 生成した初期パスワードを --out の CSV に書く（リポジトリ外に置き、配布後に削除する）

再実行の扱い（PR #101 レビュー、途中失敗からの復旧）:
  - 手順 1 の後で失敗した（Cognito が FORCE_CHANGE_PASSWORD のまま）→ 手順 2〜4 をやり直す
    （status=resumed。新しい初期パスワードを発行し直す。この状態のアカウントは誰もログインできない）
  - 手順 3 で失敗した（Cognito は CONFIRMED、users テーブルに行が無い）→ 手順 3 だけ補う
    （status=repaired-table。パスワードは変更しない）
  - それ以外の既存ユーザー（CONFIRMED かつ users に行あり）は一切変更しない（status=skipped-exists）

--out は既存ファイルを上書きしない（初期パスワードを失わないため）。--dry-run では書き込まない。
処理できなかった行があれば終了コード 1 で終わる（作業完了と誤認しないため）。

PreSignUp トリガ（ドメイン制限）は AdminCreateUser でも動くため、許可ドメイン外のアドレスは
Cognito 側で拒否される。

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
PROVISIONED_BY = "scripts/ops/provision_users.py"

# Cognito のパスワードポリシー（最小 8 文字）を満たす 12 文字: 英大小・数字・記号を各 1 文字以上含める
_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*"

# 途中失敗からの復旧を含め、書き込みを伴った status
WRITE_STATUSES = ("created", "resumed", "repaired-table")


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


def get_user(cognito, email: str) -> dict | None:
    """存在すれば AdminGetUser の応答、無ければ None。"""
    try:
        return cognito.admin_get_user(UserPoolId=USER_POOL_ID, Username=email)
    except cognito.exceptions.UserNotFoundException:
        return None


def _sub_of(attributes: list[dict]) -> str:
    return next(a["Value"] for a in attributes if a["Name"] == "sub")


def users_row_exists(table, sub: str) -> bool:
    return "Item" in table.get_item(Key={"userId": sub})


def put_users_row(table, sub: str, email: str, name: str) -> None:
    table.put_item(Item={
        "userId": sub, "email": email,
        "username": name if name else email.split("@")[0],
        "createdAt": int(time.time()), "role": "user",
        "provisionedBy": PROVISIONED_BY,
    })


def _finish(cognito, table, email: str, name: str, sub: str, status: str) -> dict:
    """手順 2（恒久パスワード）→ 手順 3（users 行）を行い、結果行を返す。"""
    password = generate_password()
    cognito.admin_set_user_password(UserPoolId=USER_POOL_ID, Username=email, Password=password, Permanent=True)
    put_users_row(table, sub, email, name)
    return {"email": email, "status": status, "password": password, "userId": sub}


def provision(cognito, table, row: dict, dry_run: bool) -> dict:
    email, name = row["email"], row["name"]
    existing = get_user(cognito, email)

    if existing is None:
        if dry_run:
            return {"email": email, "status": "would-create", "password": ""}
        attrs = [{"Name": "email", "Value": email}, {"Name": "email_verified", "Value": "true"}]
        if name:
            attrs.append({"Name": "name", "Value": name})
        resp = cognito.admin_create_user(
            UserPoolId=USER_POOL_ID, Username=email, UserAttributes=attrs,
            MessageAction="SUPPRESS", TemporaryPassword=generate_password(),
        )
        return _finish(cognito, table, email, name, _sub_of(resp["User"]["Attributes"]), "created")

    sub = _sub_of(existing["UserAttributes"])
    user_status = existing.get("UserStatus")

    # 手順 1 の直後に失敗したアカウント: 一時パスワードのままで誰もログインできないので手順 2〜4 をやり直す。
    # FORCE_CHANGE_PASSWORD は AdminCreateUser でしか生じず、自己サインアップの利用者には現れない。
    if user_status == "FORCE_CHANGE_PASSWORD":
        if dry_run:
            return {"email": email, "status": "would-resume", "password": "", "userId": sub}
        return _finish(cognito, table, email, name, sub, "resumed")

    # 手順 3 で失敗したアカウント: users テーブルの行だけ補う（パスワードには触らない）
    if user_status == "CONFIRMED" and not users_row_exists(table, sub):
        if dry_run:
            return {"email": email, "status": "would-repair-table", "password": "", "userId": sub}
        put_users_row(table, sub, email, name)
        return {"email": email, "status": "repaired-table", "password": "", "userId": sub}

    return {"email": email, "status": "skipped-exists", "password": "", "userId": sub}


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def write_results(out_path: str, results: list[dict]) -> None:
    """結果 CSV を新規作成する。既存ファイルは上書きしない（初期パスワードを失わないため）。"""
    with open(out_path, "x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["email", "status", "password", "userId"], extrasaction="ignore")
        w.writeheader(); w.writerows(results)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--out", required=True, help="初期パスワードの出力先（リポジトリ外・新規ファイル）")
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-northeast-1"))
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    out_path = os.path.abspath(a.out)
    if out_path.startswith(_repo_root() + os.sep):
        raise SystemExit("--out はリポジトリの外を指定してください（パスワードを含むため）")
    if os.path.exists(out_path):
        raise SystemExit(f"--out {a.out} は既に存在します。前回の初期パスワードを失わないよう別名を指定してください")

    import boto3
    cognito = boto3.client("cognito-idp", region_name=a.region)
    table = boto3.resource("dynamodb", region_name=a.region).Table(USERS_TABLE)

    rows = read_rows(a.csv)
    print(f"{len(rows)} 件を処理します（dry-run={a.dry_run}）", file=sys.stderr)
    results, counts = [], {}
    for i, row in enumerate(rows, 1):
        try:
            r = provision(cognito, table, row, a.dry_run)
        except Exception as e:  # noqa: BLE001 - 1 件の失敗で止めず記録する（再実行で復旧できる）
            r = {"email": row["email"], "status": f"error: {type(e).__name__}: {e}", "password": ""}
        results.append(r)
        key = r["status"].split(":")[0]
        counts[key] = counts.get(key, 0) + 1
        print(f"[{i}/{len(rows)}] {r['email']} {r['status']}", file=sys.stderr)

    errors = counts.get("error", 0)
    if a.dry_run:
        print(f"dry-run done {counts}（ファイルは書きません）", file=sys.stderr)
        return 1 if errors else 0

    write_results(out_path, results)
    written = sum(counts.get(s, 0) for s in WRITE_STATUSES)
    print(f"done {counts} -> {a.out}（書き込みあり {written} 件、失敗 {errors} 件）", file=sys.stderr)
    if errors:
        print("失敗した行があります。原因を直してから同じ CSV で再実行すると、途中まで進んだアカウントも復旧します", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
