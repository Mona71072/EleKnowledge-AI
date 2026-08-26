# テスト

フロントの `npm run build` はまだ CI に入れていません。まずはユニットテストだけを緑に保ちます。

```bash
python3 -m venv .venv
.venv/bin/pip install -r tests/unit/requirements-test.txt
AWS_DEFAULT_REGION=ap-northeast-1 AWS_REGION=ap-northeast-1 \
  .venv/bin/python -m pytest tests/unit -q
```

`develop` 時点では上記でユニットテストが通ること。件数はブランチによって増えます。
