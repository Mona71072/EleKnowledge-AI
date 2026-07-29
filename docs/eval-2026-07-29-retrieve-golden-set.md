# 検索評価: ゴールデン質問セット + 2層評価（2026-07-29）

> **状態: 第1層は実装済み / 第2層は方針合意のみ（未実装）**  
> 高速 PDCA の Check を「デプロイして人が触る」から「スクリプト1本」へ置き換えるための仕組み。  
> **運用の落とし穴・是正:** [decisions-2026-07-29-layer1-eval-ops.md](./decisions-2026-07-29-layer1-eval-ops.md)（必読）  
> 関連: `docs/PRODUCT_INTENT.md`／`docs/survey-2026-07-29-hard-to-retrieve-counts.md`

## 合意した方針（2026-07-29 会話）

評価は 2 層に分ける。

| 層 | 何で測るか | 対象 | コスト |
|---|---|---|---|
| 第1層（主指標） | **機械採点**。期待資料への到達・ゲート判定 | retrieve 結果 | ほぼゼロ。日常のチューニングごとに回す |
| 第2層（補助指標） | **LLM-as-a-judge**（Amazon Bedrock Evaluations） | Context relevance / coverage、Faithfulness 等 | ジャッジ推論費。節目で回す |

- 主指標が機械採点なのは、成功条件が「該当資料・頁に届いたか」であり作文の上手さではないため
- 第2層は **BYOI**。KB 直指定だと `rag-function` のフィルタ・ゲートを通らず実アプリ評価にならない

### 出荷判断に使う数字（是正後）

| 優先 | 指標 | 使い方 |
|---|---|---|
| 主 | `hit_in_candidates`（ラベル済みのみ） | 悪化していなければ変更可。可能なら改善 |
| 必須確認 | タグ `hard` 付きの到達 | 全体平均だけ見ない |
| 副 | `page_hit`（`expected_pages` がある問） | 資料は当たるが頁違いを検知 |
| 回帰防止 | `gate_accuracy` | **単独で出荷判断しない** |
| 参考 | `hit@k` / `mrr` | 検索側の診断用 |

## ゴールデンラベリング手順（失敗一覧から）

1. `/admin/failures` で 👎 / not_found を確認する
2. 「ゴールデン候補をコピー」で jsonl 1行を取得する
3. 質問文の固有名・工事番号を一般化する
4. `expected_documents` に期待資料名（ファイル名または部分一致）を入れる
5. 必要なら `chat_history`（聞き返し後の追記評価用）を足す
6. `tests/eval/golden_set.jsonl` に追記し、第1層 eval を回す

**ラベル済み N&lt;10 のときは率を意思決定に使わない**（ラベリング作業フェーズ）。

チャットで会話を確認するときは失敗行の「チャットで開く」（`/chat?session=...`）を使う。

## 第1層の使い方

```bash
# dev KB に対して全問採点（KB ID は SSM /eleknowledge/dev/knowledge-base-id から自動解決）
AWS_PROFILE=<dev用プロファイル> python3 scripts/eval/run_retrieve_eval.py

# 変更前後の比較（A/B。例: HYBRID vs SEMANTIC）
python3 scripts/eval/run_retrieve_eval.py --search-type SEMANTIC \
  --compare eval-results/retrieve-eval-<前回>.json

# スモーク（先頭2問 / ゲート回帰）
python3 scripts/eval/run_retrieve_eval.py --limit 2
python3 scripts/eval/run_retrieve_eval.py --only G001,G103
```

- スクリプトは `lambda/rag/rag-function/app.py` を import し、**本番と同系統路**
  （正規化 → 聞き返しゲート → 本命優先 retrieve → 略語展開 → 弱い検索ゲート）で検索する
- **通さないもの:** Claude 本文・フロント UX・prd KB 差分  
  → 詳細は [layer1-eval-ops](./decisions-2026-07-29-layer1-eval-ops.md) §D
  （golden 行に `chat_history` を置けば `compose_search_query` 経由で追記結合も評価する。省略時は単発）
- 出力: `eval-results/retrieve-eval-<時刻>.json` と `*-byoi.jsonl`（gitignore 済み）
- DynamoDB 非書き込み。権限: `bedrock:Retrieve` + `ssm:GetParameter`

### 指標の読み方

| 指標 | 意味 |
|---|---|
| `hit@k` | 期待資料が検索結果の上位 k 資料（ユニーク・.md 除外）に入った割合 |
| `mrr` | 期待資料の平均逆順位（1位=1.0、2位=0.5…） |
| `hit_in_candidates` | UI 候補頁（上位5件）に期待資料が出た割合＝**利用者到達の主指標** |
| `page_hit` | `expected_pages` があるラベル済み問だけ。期待資料かつ期待頁が retrieve に出た割合（副指標） |
| `hard_hit_in_candidates` | タグ `hard` 付きラベル済みの `hit_in_candidates` |
| `gate_accuracy` | clarify / not_found / pages の判定が期待どおりだった割合（回帰防止） |
| `decision_ready` / `warning` | ラベル済み N≥10 なら意思決定可。未満なら警告（率を意思決定に使わない） |


## ゴールデンセットの育て方

正本: `tests/eval/golden_set.jsonl`（1行1問。先頭 `skip:true` が記入例）。

- `expected_documents` は **図書番号フル**（例: `"C-591124"`）。短すぎる断片は偽陽性の原因 → 禁止
- **未ラベルのまま入れてよい**（上位候補を見て後からラベル）。確信がなければ空のまま
- 迷ったら現場代理人に確認。開発だけで無理に埋めない
- 出どころ優先: bad フィードバック → `not_found` → 現場メモ →（補助）難問枠の合成
- 難問枠（据付場用図・災害事例・Qシート）を意図的に混ぜ、タグ `hard` 等を付ける
- `filters` にはそのときの機種・カテゴリを残す（現場操作との乖離防止）
- 実質問を git に入れるときは工事番号等を一般化

## 第2層（Bedrock Evaluations）— 次のステップ、未実装

1. `eval-results/*-byoi.jsonl` を S3 へアップロード
2. Bedrock Evaluations → RAG → BYOI（retrieve-only）
3. 評価者モデルのアクセスとジョブ用 IAM・出力 S3 が必要

BYOI 形式: [AWS ドキュメント](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-prompt-retrieve.html)

## 運用イメージ（PDCA・是正後）

```text
Plan  : /admin/failures または現場メモ → golden_set に追加（未ラベル可）→ ラベル
Do    : しきい値・フィルタ・クエリ処理を変更
Check : run_retrieve_eval.py → --compare
        （主: hit_in_candidates、必須: hard 枠、副: page_hit、回帰: gate）
        N<10 なら「緑」扱いにしない
Act   : 是正ルールを満たせば PR → itai さんへデプロイ。節目で第2層
```

変更を「良い」とみなす条件の全文: [layer1-eval-ops](./decisions-2026-07-29-layer1-eval-ops.md) §F

失敗信号の取得（👎 理由・admin 一覧）: 同メモ「Plan の入力源」／API `docs/api/chat.md`