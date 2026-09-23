"""scripts/ops/provision_users.py / confirm_unconfirmed_users.py の途中失敗からの復旧（PR #101 レビュー）。

AWS には接続しない。Cognito / DynamoDB を最小の偽物に置き換えて、
各 AWS 操作の間で失敗したあと再実行すると復旧すること、既存の正常ユーザーを変えないこと、
既存の出力ファイルと dry-run を保護することを固定する。
"""
import csv
import importlib.util
import os
import sys
import types

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "scripts", "ops", f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NotFound(Exception):
    pass


class FakeCognito:
    exceptions = types.SimpleNamespace(UserNotFoundException=NotFound)

    def __init__(self):
        self.users = {}
        self.fail_set_password = False
        self.fail_update_attrs = False
        self.password_calls = []

    def admin_get_user(self, UserPoolId, Username):
        if Username not in self.users:
            raise NotFound()
        return self.users[Username]

    def admin_create_user(self, UserPoolId, Username, UserAttributes, MessageAction, TemporaryPassword):
        attrs = UserAttributes + [{"Name": "sub", "Value": "sub-" + Username}]
        self.users[Username] = {"Username": Username, "UserStatus": "FORCE_CHANGE_PASSWORD", "UserAttributes": attrs}
        return {"User": {"Attributes": attrs}}

    def admin_set_user_password(self, UserPoolId, Username, Password, Permanent):
        if self.fail_set_password:
            raise RuntimeError("set password failed")
        self.password_calls.append(Username)
        self.users[Username]["UserStatus"] = "CONFIRMED"

    def admin_confirm_sign_up(self, UserPoolId, Username):
        self.users[Username]["UserStatus"] = "CONFIRMED"

    def admin_update_user_attributes(self, UserPoolId, Username, UserAttributes):
        if self.fail_update_attrs:
            raise RuntimeError("update attrs failed")
        kept = [a for a in self.users[Username]["UserAttributes"] if a["Name"] not in {x["Name"] for x in UserAttributes}]
        self.users[Username]["UserAttributes"] = kept + UserAttributes


class FakeTable:
    def __init__(self):
        self.items = {}
        self.fail_put = False

    def put_item(self, Item):
        if self.fail_put:
            raise RuntimeError("put_item failed")
        self.items[Item["userId"]] = Item

    def get_item(self, Key):
        return {"Item": self.items[Key["userId"]]} if Key["userId"] in self.items else {}


@pytest.fixture
def pu():
    return _load("provision_users")


@pytest.fixture
def cu():
    return _load("confirm_unconfirmed_users")


def _row(email):
    return {"email": email, "name": ""}


# ---------- provision_users.py ----------

def test_provision_creates_and_returns_password(pu):
    c, t = FakeCognito(), FakeTable()
    r = pu.provision(c, t, _row("a@x.jp"), False)
    assert r["status"] == "created" and r["password"] and r["userId"] == "sub-a@x.jp"
    assert c.users["a@x.jp"]["UserStatus"] == "CONFIRMED" and "sub-a@x.jp" in t.items


def test_provision_resumes_after_set_password_failure(pu):
    c, t = FakeCognito(), FakeTable()
    c.fail_set_password = True
    with pytest.raises(RuntimeError):
        pu.provision(c, t, _row("a@x.jp"), False)
    assert c.users["a@x.jp"]["UserStatus"] == "FORCE_CHANGE_PASSWORD" and not t.items

    c.fail_set_password = False
    r = pu.provision(c, t, _row("a@x.jp"), False)
    assert r["status"] == "resumed" and r["password"]
    assert c.users["a@x.jp"]["UserStatus"] == "CONFIRMED" and "sub-a@x.jp" in t.items


def test_provision_repairs_table_after_put_item_failure_without_touching_password(pu):
    c, t = FakeCognito(), FakeTable()
    t.fail_put = True
    with pytest.raises(RuntimeError):
        pu.provision(c, t, _row("a@x.jp"), False)
    assert c.users["a@x.jp"]["UserStatus"] == "CONFIRMED" and not t.items

    t.fail_put = False
    before = list(c.password_calls)
    r = pu.provision(c, t, _row("a@x.jp"), False)
    assert r["status"] == "repaired-table" and r["password"] == ""
    assert c.password_calls == before  # パスワードは再設定しない
    assert t.items["sub-a@x.jp"]["provisionedBy"] == pu.PROVISIONED_BY


def test_provision_never_touches_existing_healthy_user(pu):
    c, t = FakeCognito(), FakeTable()
    c.users["ok@x.jp"] = {"UserStatus": "CONFIRMED", "UserAttributes": [{"Name": "sub", "Value": "sub-ok"}]}
    t.items["sub-ok"] = {"userId": "sub-ok", "role": "admin"}
    r = pu.provision(c, t, _row("ok@x.jp"), False)
    assert r["status"] == "skipped-exists" and r["password"] == ""
    assert c.password_calls == [] and t.items["sub-ok"]["role"] == "admin"


def test_provision_dry_run_reports_without_writing(pu):
    c, t = FakeCognito(), FakeTable()
    c.users["half@x.jp"] = {"UserStatus": "FORCE_CHANGE_PASSWORD", "UserAttributes": [{"Name": "sub", "Value": "sub-half"}]}
    assert pu.provision(c, t, _row("new@x.jp"), True)["status"] == "would-create"
    assert pu.provision(c, t, _row("half@x.jp"), True)["status"] == "would-resume"
    assert "new@x.jp" not in c.users and c.password_calls == [] and not t.items


def _run_main(pu, monkeypatch, tmp_path, cognito, argv_extra=()):
    import boto3
    csv_in = tmp_path / "in.csv"
    csv_in.write_text("email\nu@x.jp\n", encoding="utf-8")
    table = FakeTable()
    monkeypatch.setattr(boto3, "client", lambda *a, **k: cognito)
    monkeypatch.setattr(boto3, "resource", lambda *a, **k: types.SimpleNamespace(Table=lambda n: table))
    out = tmp_path / "out" / "pw.csv"
    out.parent.mkdir()
    rc = pu.main(["--csv", str(csv_in), "--out", str(out), *argv_extra])
    return rc, out, table


def test_main_refuses_to_overwrite_existing_output(pu, monkeypatch, tmp_path):
    out = tmp_path / "pw.csv"
    out.write_text("email,status,password,userId\nold@x.jp,created,SECRET,sub-old\n", encoding="utf-8")
    csv_in = tmp_path / "in.csv"
    csv_in.write_text("email\nu@x.jp\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        pu.main(["--csv", str(csv_in), "--out", str(out), "--dry-run"])
    assert "SECRET" in out.read_text(encoding="utf-8")


def test_main_dry_run_writes_nothing(pu, monkeypatch, tmp_path):
    rc, out, _ = _run_main(pu, monkeypatch, tmp_path, FakeCognito(), ["--dry-run"])
    assert rc == 0 and not out.exists()


def test_main_exit_code_is_nonzero_when_a_row_failed(pu, monkeypatch, tmp_path):
    c = FakeCognito()
    c.fail_set_password = True
    rc, out, _ = _run_main(pu, monkeypatch, tmp_path, c)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert rc == 1 and rows[0]["status"].startswith("error:")


def test_main_exit_code_is_zero_when_all_rows_succeed(pu, monkeypatch, tmp_path):
    rc, out, _ = _run_main(pu, monkeypatch, tmp_path, FakeCognito())
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert rc == 0 and rows[0]["status"] == "created" and rows[0]["password"]


# ---------- confirm_unconfirmed_users.py ----------

def _unconfirmed(c, email):
    c.users[email] = {"UserStatus": "UNCONFIRMED", "UserAttributes": [{"Name": "email_verified", "Value": "false"}]}


def test_confirm_sets_both_states(cu):
    c = FakeCognito()
    _unconfirmed(c, "a@x.jp")
    assert cu.confirm(c, "a@x.jp", False) == "confirmed"
    assert c.users["a@x.jp"]["UserStatus"] == "CONFIRMED" and cu._email_verified(c.users["a@x.jp"])


def test_confirm_recovers_email_verified_after_partial_failure(cu):
    c = FakeCognito()
    _unconfirmed(c, "a@x.jp")
    c.fail_update_attrs = True
    with pytest.raises(RuntimeError):
        cu.confirm(c, "a@x.jp", False)
    assert c.users["a@x.jp"]["UserStatus"] == "CONFIRMED" and not cu._email_verified(c.users["a@x.jp"])

    c.fail_update_attrs = False
    assert cu.confirm(c, "a@x.jp", False) == "verified-email"
    assert cu._email_verified(c.users["a@x.jp"])


def test_confirm_skips_verified_user_and_reports_not_found(cu):
    c = FakeCognito()
    c.users["ok@x.jp"] = {"UserStatus": "CONFIRMED", "UserAttributes": [{"Name": "email_verified", "Value": "true"}]}
    assert cu.confirm(c, "ok@x.jp", False) == "skipped-CONFIRMED"
    assert cu.confirm(c, "none@x.jp", False) == "not-found"


def test_confirm_dry_run_changes_nothing(cu):
    c = FakeCognito()
    _unconfirmed(c, "a@x.jp")
    assert cu.confirm(c, "a@x.jp", True) == "would-confirm"
    assert c.users["a@x.jp"]["UserStatus"] == "UNCONFIRMED"


def test_confirm_main_requires_verification_record_and_reports_errors(cu, monkeypatch, capsys):
    c = FakeCognito()
    _unconfirmed(c, "a@x.jp")
    c.fail_update_attrs = True
    monkeypatch.setattr(cu, "_client", lambda region: c)
    with pytest.raises(SystemExit):
        cu.main(["confirm", "--emails", "a@x.jp"])  # 照合担当・記録参照が無い
    rc = cu.main(["confirm", "--emails", "a@x.jp", "--verified-by", "mona", "--evidence-ref", "社内台帳 #12"])
    out = capsys.readouterr().out
    assert rc == 1 and "a@x.jp: error: RuntimeError" in out and "verified-by=mona" in out
