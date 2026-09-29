---
status: draft
last-verified: 2026-09-25
related-code: tests/eval/golden_set_v2_candidates.jsonl, scripts/eval/run_retrieve_eval.py
---

# 初期評価セット候補 v2

## 目的

通常モードの改善（#137、既定 OFF）とじっくりモードの回答品質を比べるための初期候補24問。候補は `tests/eval/golden_set_v2_candidates.jsonl` に置く。正解資料・ページ・保留可否は未確定で、mona / itai の人手確認前は採点しない。

## ラベル付け

1. 各行の出典メモと質問を確認し、カタログ・原資料で `expected_documents`、`expected_pages`、`expected_gate` を確定する。不明な資料名は作らず、空配列のまま要調査事項を `notes` に書く。
2. 取扱外機種・資料に根拠がない質問は、検索対象外または保留が妥当かを確認する。
3. mona と itai が確認した行だけ `skip: true` を外す。判定が割れた行は未採点のまま残す。

## Bedrock RAG Evaluations（BYOI）

既存の評価計画（`docs/eval-2026-07-29-retrieve-golden-set.md` 第2層、および #136 評価計画 §7）に沿い、ラベル済み質問を使う。`run_retrieve_eval.py` が出す `*-byoi.jsonl` を S3 に置き、Bedrock Evaluations の RAG / BYOI（retrieve-only）から評価ジョブを作成する。通常モードとじっくりモードの比較では、同じ質問・ラベルを各モードの出力に対応づけ、モード・モデル設定・実行結果を混ぜずに保存する。BYOI は検索根拠の評価用であり、回答文の比較は同じ条件の回答を並べて別途人が確認する。

## 既存ランナーとの関係

`scripts/eval/run_retrieve_eval.py` は `--golden` で入力 JSONL を指定でき、`skip: true` を除外するため、この候補ファイルをそのまま読める。ラベル確認後の例:

```bash
python scripts/eval/run_retrieve_eval.py --golden tests/eval/golden_set_v2_candidates.jsonl
```

既存正本の `tests/eval/golden_set.jsonl` は変更しない。
