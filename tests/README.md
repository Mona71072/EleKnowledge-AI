# テスト

CI（`.github/workflows/ci.yml`）は PR ごと＋ `develop` への push で次の2つを実行する。
フロントの `npm run build` はまだ CI に入れていない。まずはテストだけを緑に保つ。

## 1. Python ユニットテスト

Python は **3.13**（Lambda ランタイム `python3.13` に合わせる）。

```bash
python3 -m venv .venv
.venv/bin/pip install -r tests/unit/requirements-test.txt
AWS_DEFAULT_REGION=ap-northeast-1 AWS_REGION=ap-northeast-1 \
  .venv/bin/python -m pytest tests/unit -q
```

## 2. フロントの純粋ロジックテスト（node:test）

`frontend/src/lib/*.mjs` に切り出した純粋ロジックを `frontend/tests/*.test.mjs` で固定する。
依存インストール不要（Node 20+ の組み込み `node:test` のみ）。

```bash
node --test frontend/tests/*.test.mjs
```

`develop` 時点では上記がすべて通ること。件数はブランチによって増える。
