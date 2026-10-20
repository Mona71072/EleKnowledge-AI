---
status: draft
last-verified: 2026-10-20
related-code:
  - lambda/rag/rag-function/senpai_research_*.py
  - lambda/chat/chat-management/app.py
  - infrastructure/sam/phase2-template.yaml
  - tests/unit/test_senpai_research_*.py
  - tests/unit/test_senpai_history.py
---

# 工技先輩の調査ジョブ（試作）: バックエンド実装メモ

> 最終検証: 2026-10-20 — 単体テスト（moto・偽の Bedrock/KB）と cfn-lint まで。dev への実機デプロイと実モデルでの所要時間は未確認。

API・段階イベント・結果の形は [契約](./senpai-research-contract.md) が正本。ここでは実装の構成、パラメータ、デプロイ時の注意、契約との差、未対応を残す。画面側は別担当（`frontend/**`）。

## 構成

```
画面 ──POST/GET──> 受付 Lambda (senpai-research-api-<env>)        軽い。Bedrock・KB に触れない
                      │  非同期起動（Event・jobId だけ）
                      ▼
                  ワーカー Lambda (senpai-research-worker-<env>)    app.py を import して検索・生成を再利用
                      │            │
        ジョブ表 senpai-research-jobs-<env>      ChatLogs（完了時に質問と回答の2行を追加）
```

受付とワーカーを分けた理由:

- 権限を分けられる。受付は DynamoDB（ジョブ表）とワーカーの起動だけ。Bedrock・KB・ChatLogs を持たない。
- API Gateway の 29 秒制限を受けない。ワーカーは最大 120 秒。
- 受付は `app.py` を読み込まないので、進捗の取得が速い（cold start も軽い）。

ワーカーは `CodeUri` を RAG 関数と同じ `lambda/rag/rag-function/` にして、`app.py`（CRLF のまま未編集）の関数を import で再利用する。`app.py` の読み込みは副作用が大きい（boto3 クライアント生成）ため、`senpai_research_rag.py` が最初に使うときまで遅らせる。

### モジュール（すべて `lambda/rag/rag-function/`）

| ファイル | 責務 |
| --- | --- |
| `senpai_research_api.py` | 受付 `POST /rag/senpai/research` と進捗 `GET /rag/senpai/research/{jobId}`。ゲート・検証・冪等・ロック・日次上限・期限切れの回収 |
| `senpai_research_worker.py` | 非同期起動のワーカー。ジョブの開始・結果/失敗の保存・履歴行の保存・ロック解放 |
| `senpai_research_runner.py` | 調査の骨組み（整理 → ノウハウ → 技術と法令を同時 → 十分性 → 再検索 → まとめ → 照合） |
| `senpai_research_search.py` / `_context.py` | 検索の実行・段階イベントの記録・集めた根拠の保持 |
| `senpai_research_understand.py` / `_sufficiency.py` / `_synthesize.py` | 各段階のプロンプトと出力の検証（コード側で検証。JSON だけを受け付ける） |
| `senpai_research_citations.py` | `[T#][L#][K#]` の番号付け・照合・結果の `sources` |
| `senpai_research_rag.py` | `app.py` への接続（検索・選別・法令の全文補強・ノウハウ・モデル呼び出し） |
| `senpai_research_store.py` | ジョブ表（条件付き書き込み・ロック・日次回数・冪等・追記専用イベント） |
| `senpai_research_chatlog.py` | 完了した回答の ChatLogs 行 |
| `senpai_research_recorder.py` / `_budget.py` / `_log.py` / `_config.py` / `_http.py` / `_errors.py` / `_text.py` | 補助 |

## 流れ

1. **受付**: 管理者・dev・有効化の確認（満たさなければ DB に触れる前に 403）→ 入力検証 → `clientRequestId` の登録（同じ要求は同じ `jobId`）→ ユーザーごとのロック（実行中は 409）→ 日次回数（超過は 429。ロックと登録を戻す）→ ジョブ作成 → ワーカーを非同期起動（失敗は 502 `StartFailed`。ロック・回数・登録を戻す）。
2. **ワーカー**: `queued → running`（条件付き更新で二重実行を防ぐ）→ 調査 → 履歴行を保存 → `running → completed/failed` → ロック解放。
3. **進捗**: 本人のジョブだけ（他人・存在しない・UUID でないものは同じ 404）。`afterSeq` より新しい段階イベントだけ返す。進行中のまま期限（`expiresAt`）を過ぎたジョブは `failed / Timeout` に回収してロックを外す。`debug` は管理者にだけ返す（この API 自体が管理者限定）。

### 調査の手順と停止理由

| 段階 | 内容 | モデル |
| --- | --- | --- |
| `understand` | 質問を JSON に整理（機種は質問中の根拠語がある場合だけ採用。画面の機種が最優先）。失敗時は元の質問で全道具 | 小さいモデル 1 回 |
| `knowhow` | 既存の字句検索。無効・索引不達でも調査は続行（段階は `skipped` / `failed`） | なし |
| `tech_search` / `law_search` | 同時実行。原文（ノウハウの資料番号を付加）と整理語の両方で検索。法令は「法令に関係する」かつ法令機能が有効なときだけ。それ以外は `skipped` | なし |
| `sufficiency` | 要約（資料名・ページ・スコア・先頭 120 字）だけを見て JSON で判断。`retry_search` / `doc_page` / `clarify` | 小さいモデル 1 回（最大 2 回） |
| `retry_search` / `doc_page` | 追加の検索は最大 2 回。同じ検索語・新しい資料が増えない結果は打ち切り | なし |
| `synthesize` → `verify` | データはエスケープして非信頼として渡す。コードが実在しない参照を除去し `unverifiedRefs` に記録 | 本体モデル 1 回 |

`stopReason`: `sufficient`（十分と判断・判断不能）/ `no_new_results`（重複した検索語・新しい資料なし・追加の調べ方なし）/ `budget`（検索回数・モデル回数・時間・追加検索 2 回の上限）/ `clarify`。

予算: 検索 6 回、モデル 4 回（まとめ用の 1 回は常に残す）、ジョブ 60 秒。追加の検索や判断は、まとめ用に 20 秒（`SENPAI_RESEARCH_SYNTH_RESERVE_MS`）残せないとき始めない。60 秒はソフトな目標で、まとめが長引いても Lambda の 120 秒内に収まる。

## SAM パラメータ（`phase2-template.yaml`）

| パラメータ | 既定 | 意味 |
| --- | --- | --- |
| `SenpaiResearchEnabled` | `false` | `Environment=dev` かつ `true` のときだけ表・ロール・2 関数・経路を作る |
| `SenpaiResearchDailyLimit` | 20 | 1 人 1 日（JST）の起動回数 |
| `SenpaiResearchMaxSearches` | 6 | 1 ジョブの KB 検索回数（技術・法令・再検索の合計） |
| `SenpaiResearchMaxModelCalls` | 4 | 1 ジョブのモデル呼び出し回数 |
| `SenpaiResearchJobBudgetMs` | 60000 | ジョブ全体のソフトな時間予算 |
| `SenpaiUnderstandModelId` | 空 | 整理・十分性用の小さいモデル。空なら `BedrockModelId` |
| `SenpaiUnderstandModelIdType` | `system-profile` | 上記の種別（`QueryRewriteModelIdType` と同じ意味。値と合わせる） |

固定値（環境変数）: 受付 `SENPAI_RESEARCH_JOB_TTL_SECONDS=150`（進行中ジョブとロックの有効秒数。ワーカーの 120 秒より長く）、ワーカー `BEDROCK_READ_TIMEOUT=40`・`BEDROCK_MAX_ATTEMPTS=2`・`SENPAI_RESEARCH_SYNTH_RESERVE_MS=20000`。ワーカーは RAG 関数と同じ検索・生成の環境変数を持つ（`Rerank` と `QueryRewrite` は試作では使わない）。

### 権限（最小）

- 受付ロール: ジョブ表の `GetItem/PutItem/UpdateItem/DeleteItem`、ワーカー関数への `lambda:InvokeFunction` のみ。
- ワーカーロール: 技術 KB（と有効なとき法令 KB）への `bedrock:Retrieve`、`BedrockModelId`（と設定時は整理用モデル）への `bedrock:InvokeModel`、ジョブ表の `GetItem/UpdateItem/DeleteItem`、ChatLogs の `PutItem` のみ、ノウハウ索引の 1 オブジェクトと法令全文（有効なとき）の `s3:GetObject`（KMS 指定時は `kms:Decrypt`）。`Query/Scan`・Rerank・文書バケットの読み取りは無い。
- ジョブ表: ハッシュキー `pk` のみ、GSI なし、TTL（`ttl`）、SSE。ジョブ/冪等キーは 7 日、日次回数は 3 日で消える。

## itai へのデプロイメモ

- Lambda/SAM のデプロイは itai の作業。マージしても AWS には入らない。
- 既存のスタックを更新するときは、**これまでの `--parameter-overrides` に新パラメータを足す**（上書き一覧に無いパラメータは既定値に戻るため、既存の値を落とさない）。dev で試すときの追加分:
  - `SenpaiResearchEnabled=true`（必須）
  - `SenpaiUnderstandModelId=jp.anthropic.claude-haiku-4-5-20251001-v1:0` と `SenpaiUnderstandModelIdType=system-profile`（任意。小さいモデルを使うとき）
  - 予算を変えるなら `SenpaiResearchMaxSearches` / `SenpaiResearchMaxModelCalls` / `SenpaiResearchJobBudgetMs` / `SenpaiResearchDailyLimit`
- ノウハウと法令は、ワーカーが RAG 関数と同じパラメータを読む。使うなら既存の `KnowhowEnabled` `KnowhowIndexBucket` `KnowhowIndexKey` `LawRagEnabled` `LawKnowledgeBaseId` `LawDataBucketName`（`LawDataBucketKmsKeyArn`）を同じ値で引き継ぐ。未設定なら該当の段階は `skipped` になるだけで調査は動く。
- prod では `SenpaiResearchEnabled` に何を指定しても何も作られない（`Environment=dev` の条件）。
- 画面は `NEXT_PUBLIC_ENABLE_SENPAI_RESEARCH=true` のときだけこの経路を使う（別担当）。
- 確認のしかた: `GET /rag/senpai/research/{jobId}` の `debug.budget` と `steps` で所要時間・回数を見る。CloudWatch には段階名・件数・時間・終了理由・エラー種別だけが出る（`event: senpai_research`、`stage` が `job` の行に `elapsedMs` `modelCalls` `searches` `stopReason`）。

## 契約からのずれ・解釈した点

1. **段階イベントは遷移ごとに 1 件**: 開始（`running`）と終了（`done`/`failed`）をそれぞれ別の `seq` で追記する（同じ `step` と `startedAt`。終了側に `endedAt`・`counts`）。追記専用で `afterSeq` が成り立つため。画面は `(step, startedAt)` が同じなら新しい `seq` を優先して 1 行にまとめる。`skipped` は 1 件だけ。
2. **ChatLogs は PutItem のみ**: 契約の「PutItem + query」のうち query はワーカーでは不要（履歴の読み取りは chat-management の既存権限）。
3. **履歴行**: 質問（`role=user`）と回答（`role=assistant`）の 2 行を `ragMode=senpai_research`・先輩タグ付き・TTL 60 日で保存。回答行の `researchResult` に結果全体（`answerMarkdown` と `sources` を含む）、`queryFilters.modelType` に採用した機種を保存。日別集計キー（`metricDay`）は付けない（まとめ行と同じ）。chat-management は変更不要で復元でき、機種キーを `ragMode=senpai_research` でも返すようにした。
4. **`sources.tech` / `sources.law` は本文で引用された参照だけ**。`sourceUri` は署名付き URL ではなく `s3://`（保存に署名 URL を残さない。開くのは既存の `/rag/document`）。許可外・`.md`・e-Gov の URL が確認できない法令は引用に使わない。
5. **`understanding.modelType` は実際に使った機種**（画面指定が最優先）。整理結果の機種は、質問の中に実在する根拠語（正規化して比較）を持ち、その機種の呼び名を含む場合だけ採用する。
6. **聞き返し・見つからない**: `clarify` は `clarifyQuestions`（最大 3 件）と定型文。根拠（技術・法令・ノウハウ）が 1 件も無ければ `not_found`（まとめは呼ばない）。
7. **ノウハウ索引が読めない**: RAG の 503 とは違い、調査は続行しノウハウなしで答える（段階 `knowhow` は `failed`）。
8. **`doc_page`**: 原資料のページ画像・全文は取得せず、資料名（とページ）を検索語に含めた KB 検索で、その資料の断片だけを追加する。
9. **POST の追加エラー**: `StartFailed`（502）。冪等の再送は 202 で現在の状態を返す。進捗の `pollAfterMs` は進行中 1500、終了後 0。
10. **法令に関係するかが不明**（整理の失敗・判定不能）なときは、法令検索を省略せず実行する。

## テスト

`tests/unit/test_senpai_research_*.py`（api / store / steps / runner / worker / adapter / flow / sam）と `tests/unit/test_senpai_history.py`（調査行の履歴）。偽物にするのは Bedrock と KB だけ（DynamoDB は moto）。`flow` は受付 → ワーカー → 進捗 → 履歴復元を通しで確認し、ログに質問・検索語・本文が出ないことも見る。

```
AWS_DEFAULT_REGION=ap-northeast-1 AWS_REGION=ap-northeast-1 python -m pytest tests/unit tests/integration
cfn-lint infrastructure/sam/phase2-template.yaml
```

## 未対応・次に確認すること

- **実機での所要時間**: 想定は 整理 2〜4 秒 + 検索 2〜3 秒（並列）+ 十分性 2〜4 秒 + まとめ 15〜20 秒 ≒ 30〜35 秒。再検索 1 回ごとに +5〜8 秒。60 秒の予算に収まるかは dev で実測が必要（`debug.tools[].ms` と `budget.elapsedMs`）。
- **JSON の安定性**: 整理・十分性は JSON だけを受け付け、壊れていれば元の質問・現状の結果で続行する。小さいモデルでの失敗率は実測が必要（失敗は `fallback: true`（debug）で分かる）。
- 直前の会話の文脈は使わない（1 質問 1 ジョブ）。聞き返しへの回答は新しい質問として送る。
- 進行中ジョブの取り消し、ストリーミング、プロンプトキャッシュ、評価ハーネス（`senpai-research-eval`）への接続、CloudWatch アラーム/ダッシュボードは未対応。
- 冪等の再送が、最初の要求の途中（ジョブ作成前）に届くと、`jobId` は返るが進捗が一瞬 404 になる。画面の再試行で解消する範囲。
- 日次回数は、失敗したジョブも 1 回として数える（受付後に戻すのは起動失敗のときだけ）。
