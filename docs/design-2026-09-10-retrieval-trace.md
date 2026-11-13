---
status: draft
last-verified: 2026-09-25
related-code: lambda/rag/rag-function/app.py, lambda/chat/chat-management/app.py, infrastructure/sam/chat-archive-template.yaml, lambda/metrics/aggregator/app.py
---

# 設計: 検索トレース（retrievalTrace）の保存

> 2026-09-25 改訂: 第 1 版の範囲を見直し（mona 決定）。
> review.md 要旨: U1/U2/U4 に必要な検索試行・ゲート・候補情報が不足。
> #137 の設定と KB 版を含め、AI に渡した抜粋だけを保存する必要がある。
> CloudWatch の会話 ID はログ契約に反し、「KB に無い」は同期済み内容との照合なしに確定できない。

> 2026-11-12 改訂（itai）: 9/25 の実装（`feature/retrieval-trace`）は PR にならず develop に入っておらず、dev の会話記録・アーカイブに `retrievalTrace` は 0 件だった。その間に develop の RAG は法令モード（#158）・Converse 対応（#153）・ログ共通項目（#181）・日別集計 GSI（#183）で大きく変わったため、現行 develop の上で作り直す。本改訂は作り直しに必要な差分（§3.1 法令モード、§3.2 値の決め方、§5 読み出し経路、§9 分割、§10 決定、§11 配備後の確認）だけを足し、第 1 版の項目一覧（§3）は変えない。

> **状態:** 設計。第 1 版の実装は作り直し中（2026-11-12）。決定の経緯は issue #86（コメント 2・3・16）。

## 1. 目的

検索トレースを保存し、失敗原因の切り分け、評価セットでの比較、費用・遅延の把握、設定変更前後の比較に使う。検索試行・候補・ゲート・実効設定と、生成に渡した抜粋を後から確認できる状態にする。

Bedrock の invocation logging は採用しない（Retrieve 結果が記録されない、アカウント全体に及ぶ、messageId と結合できない。issue #86 コメント 2）。

## 2. 前提（2026-09-10 実測）

| 項目 | 値 |
|---|---|
| assistant メッセージ項目のサイズ | 平均 16 KB、最大 26 KB（pageCandidates の snippet と sourceDocuments が主） |
| retrieve 件数 | `numberOfResults=30`、マージ後 平均 26・最大 30 |
| 候補頁（UI に出す） | 最大 5（`build_page_candidates`） |
| DynamoDB 項目上限 | 400 KB |
| 保全経路 | chatlogs Stream → `eleknowledge-chat-archive-dev` → S3 → Glue `chatlogs_archive`。バージョニングと失敗保全は develop にマージ済みの #96 の内容（ハンドラの `failed/` 保存ではなく S3 OnFailure の `payload`） |
| Bedrock 応答の `usage` | `input_tokens` / `output_tokens`（現在は破棄） |

> 最終検証: 2026-11-12 — develop `bea56ee7` のコード照合と dev Lambda の設定読み取り（下の追記行だけ。上の表は 9/10 実測のまま）

| 項目（2026-11-12 追記） | 値 |
|---|---|
| 生成の呼び出し | `invoke_generation` が本文・`usage`・停止理由を返す（InvokeModel と Converse の両方。`model_profile` の `api` で切替） |
| dev の RAG 設定 | リランク無効（`RERANK_MODEL_ARN` 空）、検索語の書き換え無効（`QUERY_REWRITE_MODEL_ID` 空）、法令モード有効、`RAG_LOGIC_VERSION` は配備済み |
| chatlogs の GSI | `userId-timestamp-index` と `metricDayShard-timestamp-index`。どちらも `ProjectionType: ALL` のため、トレースは GSI にも複製される |
| トレースを読む既存コード | 失敗一覧（#114）の `traceSummary`（管理者向け）。項目名は確定版より前のもの |

## 3. データ設計

assistant メッセージ項目に属性 `retrievalTrace`（Map）を追加する。**利用者向け API には返さない**（§5）。第 1 版の範囲・保存項目は本書 §3 を正本とする（mona 決定 2026-09-25）。

```jsonc
"retrievalTrace": {
  "schemaVersion": 1,
  "logicVersion": "ecc7d09",            // SAM パラメータ RAG_LOGIC_VERSION
  "promptVersion": "rag-prompt-v1",     // 生成プロンプトの版またはハッシュ
  "requestId": "…",                    // API Gateway request ID。実装値 apiRequestId
  "kb": {"kbId": "VQV81CNYU4", "profileHash": "…", "dataSourceSyncAt": null},
  "questionRef": {"messageId": "…", "composedQuery": null},
  "searchAttempts": [                    // 実際に行った Retrieve ごと
    {"stage": "initial", "query": "…", "searchType": "HYBRID",
     "filters": {}, "scope": {"profileHash": "…"}, "requested": 30,
     "returned": 30, "afterPostFilter": 26, "latencyMs": 820}
  ],
  "rewrite": {"enabled": false, "status": "skipped", "reason": "disabled",
               "rewrittenQuery": null, "modelId": null, "callCount": 0, "latencyMs": 0},
  "rerank": {"enabled": false, "status": "skipped", "reason": "disabled",
              "modelId": null, "callCount": 0, "latencyMs": 0},
  "gate": {"responseType": "pages", "weak": false, "scores": [],
           "thresholds": [], "rankKey": "score", "selectedCount": 5,
           "excludedCounts": {"model_scope": 0, "dedupe": 0,
                              "below_threshold": 0, "limit": 0}},
  "candidates": [                       // 上位最大 30〜60 件。上限は定数化
    {"rank": 1, "sourceUri": "s3://…/x.pdf", "documentName": "x.pdf",
     "pageNumber": 12, "chunkId": "…", "score": 0.61, "rerankScore": null,
     "modelType": "AXIEZ", "category": "spec", "hasImage": false,
     "selected": true, "excludedBy": null, "dedupeCount": 0, "text": "…",
     "textTruncated": false, "originalLength": 640}
  ],
  "generation": {"modelId": "global.anthropic.claude-sonnet-5", "requestStyle": "new",
                 "thinking": {"type": "disabled", "effort": null},
                 "inputTokens": 3748, "outputTokens": 578,
                 "stopReason": "end_turn", "latencyMs": 9305},
  "latencyMs": {"total": 10400},
  "truncatedTrace": false,
  "truncationReason": null
}
```

`responseType` は `pages` / `clarify` / `not_found` のいずれか。`clarify` と `not_found` は生成モデルを呼ばないため `generation: null` とする。

以下を第 1 版の確定フィールド一覧とする。必須はキーが常に存在することを表し、値を取得できない場合は表の規則に従って `null`（または空配列・空オブジェクト）を格納する。`generation` だけは応答種別に応じてオブジェクトまたは `null`。

| 項目名 | 型 | 必須 | 取得できない場合 |
|---|---|---:|---|
| `schemaVersion` | integer | はい | 固定値 `1` |
| `logicVersion` | string | はい | `unknown` |
| `promptVersion` | string | はい | `unknown` |
| `requestId` | string \| null | はい | `apiRequestId` が無ければ `null` |
| `kb` | object | はい | 空オブジェクト。以下の子キーは必須 |
| `kb.kbId` | string \| null | はい | `null` |
| `kb.profileHash` | string \| null | はい | `null` |
| `kb.dataSourceSyncAt` | string \| null | はい | `null` |
| `questionRef` | object | はい | 空オブジェクト。以下の子キーは必須 |
| `questionRef.messageId` | string \| null | はい | `null` |
| `questionRef.composedQuery` | string \| null | はい | `null` |
| `searchAttempts` | array of object | はい | `[]`（実行した Retrieve がない場合） |
| `searchAttempts[].stage` | string | はい | `unknown` |
| `searchAttempts[].query` | string \| null | はい | `null` |
| `searchAttempts[].searchType` | string \| null | はい | `null` |
| `searchAttempts[].filters` | object | はい | `{}` |
| `searchAttempts[].scope` | object | はい | `{}` |
| `searchAttempts[].requested` | integer \| null | はい | `null` |
| `searchAttempts[].returned` | integer \| null | はい | `null` |
| `searchAttempts[].afterPostFilter` | integer \| null | はい | `null` |
| `searchAttempts[].latencyMs` | integer \| null | はい | `null` |
| `rewrite` | object | はい | 空オブジェクト。以下の子キーは必須 |
| `rewrite.enabled` | boolean | はい | `false` |
| `rewrite.status` | string | はい | `skipped` |
| `rewrite.reason` | string \| null | はい | `null` |
| `rewrite.rewrittenQuery` | string \| null | はい | `null` |
| `rewrite.modelId` | string \| null | はい | `null` |
| `rewrite.callCount` | integer | はい | `0` |
| `rewrite.latencyMs` | integer \| null | はい | `null`（未呼び出し時は `0`） |
| `rerank` | object | はい | 空オブジェクト。以下の子キーは必須 |
| `rerank.enabled` | boolean | はい | `false` |
| `rerank.status` | string | はい | `skipped` |
| `rerank.reason` | string \| null | はい | `null` |
| `rerank.modelId` | string \| null | はい | `null` |
| `rerank.callCount` | integer | はい | `0` |
| `rerank.latencyMs` | integer \| null | はい | `null`（未呼び出し時は `0`） |
| `gate` | object | はい | 空オブジェクト。以下の子キーは必須 |
| `gate.responseType` | string | はい | `pages` / `clarify` / `not_found` の実値 |
| `gate.weak` | boolean | はい | `false` |
| `gate.scores` | array | はい | `[]` |
| `gate.thresholds` | array | はい | `[]` |
| `gate.rankKey` | string \| null | はい | `null` |
| `gate.selectedCount` | integer | はい | `0` |
| `gate.excludedCounts` | object | はい | 空オブジェクトではなく、以下の理由別件数をすべて含める |
| `gate.excludedCounts.model_scope` | integer | はい | `0` |
| `gate.excludedCounts.dedupe` | integer | はい | `0` |
| `gate.excludedCounts.below_threshold` | integer | はい | `0` |
| `gate.excludedCounts.limit` | integer | はい | `0` |
| `candidates` | array of object | はい | `[]` |
| `candidates[].rank` | integer | はい | 記録時の順位 |
| `candidates[].sourceUri` | string \| null | はい | `null` |
| `candidates[].documentName` | string \| null | はい | `null` |
| `candidates[].pageNumber` | integer \| null | はい | `null` |
| `candidates[].chunkId` | string \| null | はい | `null` |
| `candidates[].score` | number \| null | はい | `null` |
| `candidates[].rerankScore` | number \| null | はい | `null` |
| `candidates[].modelType` | string \| null | はい | `null` |
| `candidates[].category` | string \| null | はい | `null` |
| `candidates[].hasImage` | boolean \| null | はい | `null` |
| `candidates[].selected` | boolean | はい | `false` |
| `candidates[].excludedBy` | string \| null | はい | `null`（採用候補）または除外理由 |
| `candidates[].dedupeCount` | integer | はい | `0`（重複が無い場合） |
| `candidates[].text` | string \| null | はい | 選択済みで本文が取れない場合 `null`。未選択候補は常に `null` |
| `candidates[].textTruncated` | boolean | はい | `false` |
| `candidates[].originalLength` | integer \| null | はい | `null` |
| `generation` | object \| null | はい | `clarify` / `not_found` は `null`。生成済みで値が取れなければ子値を `null` |
| `generation.modelId` | string \| null | 生成時 | `null` |
| `generation.requestStyle` | string \| null | 生成時 | `null` |
| `generation.thinking` | object | 生成時 | `{}` |
| `generation.thinking.type` | string \| null | 生成時 | `null` |
| `generation.thinking.effort` | string \| null | 生成時 | `null` |
| `generation.inputTokens` | integer \| null | 生成時 | `null` |
| `generation.outputTokens` | integer \| null | 生成時 | `null` |
| `generation.stopReason` | string \| null | 生成時 | `null` |
| `generation.latencyMs` | integer \| null | 生成時 | `null` |
| `latencyMs` | object | はい | 空オブジェクト。以下の子キーは必須 |
| `latencyMs.total` | integer \| null | はい | `null` |
| `truncatedTrace` | boolean | はい | `false` |
| `truncationReason` | string \| null | はい | `null` |

`excludedBy` は `model_scope` / `below_threshold` / `limit` を記録し、重複候補は次節の規則により候補配列には入れない。全候補を保持できない場合も理由別件数は `gate.excludedCounts` に残し、候補配列の上限超過は `truncatedTrace` と `truncationReason` に記録する。

`searchAttempts` は実行された Retrieve ごとに検索語・検索方式・フィルタ・スコープ・件数・時間を持つ。固定の `count1/count2` や `usedAbbrevExpansion` は置かない。`rewrite` / `rerank` は実効設定と適用・スキップ・フォールバック結果を記録する。`gate` は応答種別、弱検索の判定材料、閾値、ランクキー、選別数を持つ。質問本文は複製せず、user メッセージへの参照と必要な `composedQuery` のみを保存する。

本文は `selected` 候補だけに保存し、**AI に渡した抜粋だけ**を `text` に入れる。現行の 1,200 文字切り詰め後の文字列とし、切り詰め前の文字数を `originalLength`、切り詰めの有無を `textTruncated` に記録する。候補全件の本文・画像 base64 は保存しない。

サイズ見積: 選択済み抜粋 10 件 × 1,200 文字 × 最大約 3 byte/文字で **約 36 KB**。候補メタデータとその他のトレース情報が加わる。DynamoDB 項目サイズを実測し、400 KB に近づいた場合は本文を黙って落とさず `truncatedTrace: true` と理由を記録する。S3 退避は後続とする。

`clarify` / `not_found` 応答でも `retrievalTrace` を保存する（not_found は実際に存在する検索試行・候補・gate を記録する。どちらも `generation` は null）。

| 用途 | 内容 | 主な項目 |
|---|---|---|
| U1 失敗原因の切り分け | 検索・除外・弱検索・生成入力の確認 | `questionRef`、`searchAttempts`、`gate`、`candidates`、`kb` |
| U2 評価セットでの比較 | Retrieve と生成に渡した根拠の比較・BYOI | `searchAttempts`、`candidates`、選択済み `text`、`generation` |
| U3 費用・遅延 | トークン数と処理時間の集計 | `generation.inputTokens` / `outputTokens`、各呼出しの `latencyMs`、`latencyMs.total` |
| U4 設定・版の前後比較 | コード・プロンプト・KB・検索／生成設定の比較 | `logicVersion`、`promptVersion`、`kb`、`searchAttempts`、`rewrite`、`rerank`、`generation` |

各項目の保存先・用途は次のとおり。質問本文や検索語を含むトレースは CloudWatch ではなく、アクセス制御された DynamoDB／アーカイブに限定する。

| 項目 | 用途 |
|---|---|
| `schemaVersion`、`logicVersion`、`promptVersion` | 形式識別、U4 |
| `kb`（`kbId`、`profileHash`、`dataSourceSyncAt`） | U1、U2、U4 |
| `questionRef` | U1、U2、U4 |
| `searchAttempts[]` | U1、U2、U3、U4 |
| `rewrite`、`rerank` | U1、U2、U3、U4 |
| `gate` | U1、U2、U4 |
| `candidates[]` の順位・資料・スコア・選択／除外情報 | U1、U2、U4 |
| 選択済み候補の `text`、`textTruncated`、`originalLength` | U1、U2 |
| `generation` | U1、U2、U3、U4 |
| `latencyMs.total` | U3 |

後回しにする項目: 候補全件の本文、S3 退避、管理者向け trace API／画面、1 件ごとの USD 推定値と単価管理、AI 振り分け結果の保存、じっくりモード用の拡張。`searchAttempts[]` は将来の検索段階を表せる形にする。

### 3.1 法令モード（2026-11-12 追加）

> 最終検証: 2026-11-12 — develop `bea56ee7` の `query_law_knowledge_base`・`prepare_law_references`・`build_references_block` の照合

法令モード（`ragMode=law`）も同じスキーマで保存する。項目は増やさず、値で区別する。

| 項目 | 法令モードの値 |
|---|---|
| `kb.kbId` | 法令用 KB の ID（`LAW_KNOWLEDGE_BASE_ID`） |
| `searchAttempts[].stage` / `searchType` | `law` / `MANAGED` |
| `searchAttempts[].returned` / `afterPostFilter` | Retrieve の件数 / 現行条文に絞った後の件数 |
| `rewrite` / `rerank` | 使わないため `status=skipped`、`reason=law_mode` |
| `candidates[].selected` | 原文を補って AI に渡した資料（資料の URI で突き合わせる） |
| `candidates[].text` | AI に渡した全文補完済みの本文の**先頭 1,200 字**。`originalLength` に全文の文字数、`textTruncated` に切り詰めの有無を入れる（全文は保存しない） |

同じ資料の候補が複数あるときは、本文は最初の 1 件にだけ入れる（法令は資料ごとに 1 本へまとめて渡すため）。

### 3.2 値の決め方（2026-11-12 追加）

> 最終検証: 2026-11-12 — develop `bea56ee7` の `select_retrieval_results`・`is_weak_retrieval`・`merge_retrieval_results` の照合

- `excludedBy`: 機種スコープ・機種指定で落とした候補は `model_scope`。それ以外で選ばれなかった候補は、選別の最低スコア（normal 0.3、spec 0.2）未満なら `below_threshold`、以上なら `limit`（文書ごとの上限・同一本文・全体上限）。閾値は選別処理と同じ関数から取り、トレース側に直書きしない
- `gate.thresholds`: `[弱い検索の上位スコア閾値 0.22, 選別の最低スコア]`
- `gate.excludedCounts.dedupe`: 2 回の検索（初回・略語展開）と同一検索内の重複を統合して落とした件数。残した候補の `dedupeCount` にも入れる
- not_found: 生成モデルに何も渡さないため `selected` は全件 false、`selectedCount` は 0（画面に出す低信頼の手がかり 2 件は `pageCandidates` に残る）
- `generation.requestStyle`: `invoke` または `converse`。`thinking` は実際に送った設定（`build_generation_request` の結果）
- `promptVersion`: 実際に使ったシステムプロンプト（通常・法令で別）の SHA-256 先頭 12 桁。生成しない clarify / not_found は `unknown`
- `modelType` / `category`: KB のメタデータが配列のときはカンマ区切りの文字列にする（§6 の Athena 列を string に固定するため）
- トレースの組み立てや保存に失敗しても回答は返す。組み立ての失敗は `retrieval_trace_failed`、保存の失敗（項目サイズ超過など）は `retrieval_trace_dropped` を例外の型名だけでログに出し、トレースなしで保存し直す

## 4. 実装箇所（`lambda/rag/rag-function/app.py`）

> 最終検証: 2026-11-12 — 作り直しで現行 develop に合わせた点だけを下に注記。番号の項目は 9/25 の記述のまま

**作り直しでの読み替え（2026-11-12）:** 生成は `invoke_generation` が `usage` と停止理由を既に返すため、`generate_response_with_claude` は既定の戻り値（本文）を変えず、`return_meta=True` のときだけ `(本文, 生成メタ)` を返す（評価スクリプトなど既存の呼び出しを壊さない）。検索語の書き換えも同様に `return_trace=True` のときだけ結果の記述を返す。組み立ては `build_request_trace`（clarify / not_found / pages / 法令の共通）にまとめ、純粋関数は `retrieval_trace.py`（9/25 の実装を流用）に置く。

1. `time.perf_counter()` で retrieve（`retrieve_for_normal_query` 2 回分）と generate（`invoke_model`）を計測
2. `generate_response_with_claude` が `usage` と `stop_reason` を返せるように、戻り値を `(text, meta)` に変更（呼び出し側 1 か所）。`extract_response_text` は develop にマージ済みの #90 の変更を使う
3. `query_knowledge_base` と後続のマージ・選別を段階ごとに追跡する。①機種スコープ post-filter で落とした候補は `excludedBy="model_scope"` として候補に残す。②マージ前の重複候補は `candidates[]` に含めず、重複を統合した採用側候補の `dedupeCount` に落とした件数を加算する。③選別時は閾値未満を `excludedBy="below_threshold"`、文書別上限または全体上限で落としたものを `excludedBy="limit"` とする。各段階で `gate.excludedCounts` の該当理由（`model_scope` / `dedupe` / `below_threshold` / `limit`）を加算し、マージ前重複の総数も `dedupe` に残す。これらの候補はトレースにだけ載せ、UI と生成には渡さない。トレース候補の上限で個別項目を収録できない場合も理由別件数を失わない
4. #137 の `maybe_rewrite_search_query` と rerank 呼び出しを計測対象にし、各関数の戻り値に検索語／候補だけでなく trace 用 metadata（有効状態、`applied` / `skipped` / `fallback` の結果、理由、モデル ID、API 呼び出し回数、経過時間）を付ける。呼び出し側でこの metadata を回収し、`rewrite` / `rerank` に保存する。無効、履歴不足、期限不足、対象候補なし、例外時の fallback など、呼び出しを行わない・適用しない経路にも理由を設定する。費用集計のトークン対象は生成のみとし、書き換え・リランクはトークン数が返らないため、費用に含めず呼び出し回数と時間だけを記録する
5. `build_retrieval_trace(...)` を新設し、`save_message_to_dynamodb(..., retrieval_trace=...)` に渡す。`requestId` に API Gateway event の実装値 `apiRequestId` を保存し、§5 のログ相関に使う
6. CloudWatch Logs の項目・禁止項目・相関 ID は [RAG 運用ログ契約](./features/development/rag-observability-contract.md) に従う。CloudWatch に `sessionId` / `messageId` / `sub` / 本文 / 検索語を出さず、契約上の `requestId`（実装では `apiRequestId`）で相関する
7. `RAG_LOGIC_VERSION` を SAM パラメータ → 環境変数で渡す（デプロイ手順で `git rev-parse --short HEAD` を指定）

## 5. 露出制御

| 経路 | 扱い |
|---|---|
| `GET /chat/sessions/{id}/messages`（利用者） | `retrievalTrace` を **除外**（chat-management `get_session_messages` で pop） |
| `GET /chat/admin/failures`（管理者） | `traceSummary`（要約だけ）を返す。#114（2026-10-04 マージ）で画面まで実装済みのため、実態に合わせて第 1 版でも出す（2026-11-12 改訂）。要約は候補配列（上限 30）ではなく `gate` の集計値から作る: `mergedCount`＝採用＋閾値未満＋上限超過、`selectedCount`、`excludedByModelScope`、`topScore`＝`gate.scores` の最大、トークン数、`latencyMs`＝`{retrieve: 検索試行の合計, generate, total}`。トレース本体は返さない |
| `GET /chat/sessions`（会話一覧） | 一覧に使う属性だけを `ProjectionExpression` で読む（2026-11-12 追加）。Lambda へ運ぶ量は減るが、DynamoDB の読み取り容量と 1 MB のページ区切りは項目サイズで決まるため減らない |
| 管理者向け専用 trace API／画面 | 後回し。第 1 版は Athena で参照 |
| S3 アーカイブ / Athena | 全文を保持。バケットは既存のアクセス制御（管理者ロール・Athena ワークグループ） |

**項目が大きくなる影響（2026-11-12 追記）:** トレースで assistant 項目は約 2〜3 倍（16〜26 KB → 50〜60 KB 見込み）になり、GSI 2 つにも複製される。現行の利用量（64 日で質問 224 件）では費用・遅延とも小さい。会話一覧（`userId` の GSI を Query）と失敗一覧（Scan、最大 25 ページ）は 1 MB ごとのページ数が増えるため、利用者 1 人あたりの会話が数百件を超える、または失敗一覧の取りこぼしが出たら、トレースを S3 へ逃がす（§3 の後回し項目）か GSI の射影を絞る。
| CloudWatch Logs | [RAG 運用ログ契約](./features/development/rag-observability-contract.md) のみ。詳細トレースとの相関には `requestId` を使う |

## 6. Athena（Glue テーブル）

`chatlogs_archive` の `newimage` / `oldimage` の struct に `retrievaltrace` を追加する（OpenX JSON SerDe は未宣言のキーを無視するため、宣言しない限り参照できない）。

```
retrievaltrace: struct<
  schemaversion:int, logicversion:string, promptversion:string, requestid:string,
  kb:struct<kbid:string, profilehash:string, datasourcesyncat:string>,
  questionref:struct<messageid:string, composedquery:string>,
  searchattempts:array<struct<stage:string, query:string, searchtype:string, filters:string, scope:string,
                              requested:int, returned:int, afterpostfilter:int, latencyms:int>>,
  rewrite:struct<enabled:boolean, status:string, reason:string, rewrittenquery:string, modelid:string, callcount:int, latencyms:int>,
  rerank:struct<enabled:boolean, status:string, reason:string, modelid:string, callcount:int, latencyms:int>,
  gate:struct<responsetype:string, weak:boolean, scores:string, thresholds:string, rankkey:string, selectedcount:int,
              excludedcounts:string>,
  candidates:array<struct<rank:int, sourceuri:string, documentname:string, pagenumber:int, chunkid:string,
                          score:double, rerankscore:double, modeltype:string, category:string, hasimage:boolean,
                          selected:boolean, excludedby:string, dedupecount:int, text:string, texttruncated:boolean, originallength:int>>,
  generation:struct<modelid:string, requeststyle:string, thinking:string, inputtokens:int, outputtokens:int,
                    stopreason:string, latencyms:int>,
  latencyms:struct<total:int>, truncatedtrace:boolean, truncationreason:string
>
```

`filters`、`scope`、`scores`、`thresholds`、`thinking` は Athena の列定義を固定するまでは JSON 文字列として格納し、トレース本体では仕様に従った値を保存する。

代表クエリ（👎 と検索結果の突合）:

```sql
SELECT a.newimage.messageid, a.newimage.feedbackreason, c.rank, c.documentname, c.pagenumber, c.score, c.selected, c.excludedby
FROM eleknowledge_analytics.chatlogs_archive a
CROSS JOIN UNNEST(a.newimage.retrievaltrace.candidates) AS t(c)
WHERE a.dt >= '2026-09-10' AND a.newimage.feedback = 'bad'
ORDER BY a.newimage.messageid, c.rank;
```

## 7. コスト算出

- 費用対象のトークンは生成の `inputTokens` / `outputTokens` のみとする。書き換え・リランクはトークン数が返らないため費用算出に含めず、呼び出し回数と遅延だけを U3 の分析用に記録する。1 件ごとの USD 推定値と単価管理は後回し
- Athena 等でコストを算出する場合は、モデル別トークン数に集計時点の単価を適用し、実額は Cost Explorer と照合する

## 8. テスト

- `build_retrieval_trace`: selected のみモデルに渡した text を持つ、最大 1,200 文字、`textTruncated` / `originalLength`、上位候補上限、400 KB に近づいた場合の `truncatedTrace` と理由、not_found でも保存できる
- `generate_response_with_claude` の戻り値変更（既存テストの更新）
- chat-management: 利用者向け応答に `retrievalTrace` が含まれない
- 保存項目のサイズ試算（実 KB で 5 問流して項目サイズを記録し、本設計の見積と比較する）
- **全経路の保存（2026-11-12 追加）:** clarify・not_found・pages・法令の 4 経路すべてで、ハンドラが `retrieval_trace` を保存に渡すこと。`app.py` の書き換えで保存の呼び出しが抜けたら落ちるテストにする（今回の未記録の再発防止）
- 組み立て・保存の失敗で回答が止まらないこと。ログに検索語・本文・ID が出ないこと
- 会話一覧がトレースを読まないこと

## 9. 実装分割（PR）

> 最終検証: 2026-11-12 — 作り直しの分割（itai 決定）

| 順 | PR | 内容 | デプロイ |
|---|---|---|---|
| 1 | 実装（作り直し） | RAG の計測・組み立て・保存（4 経路）と、chat-management の利用者向け応答からの除外・失敗一覧の要約・会話一覧の属性指定を 1 本にまとめる（同時に入らないと利用者向け API にトレースが出るため）。`docs/data-model.md`・`docs/api/chat.md`（production）の更新も同じ PR に入れる（事前確認のうえ） | phase2 |
| 2 | `feat(chat-archive)` | Glue テーブルに retrievaltrace 列。分析は生の JSONL でもできるため急がない | chat-archive |
| 3 | 後続 | 単価管理 + USD 推定コスト（必要性を再確認して着手） | — |

`RAG_LOGIC_VERSION` は配備済みのため、この PR では足さない。mona の `feature/retrieval-trace` は、作り直しの PR がマージされたら閉じる（mona の Yes を得てから）。

## 10. 第1版の決定

- 本文の上限は現行どおり 1,200 文字とし、モデルに渡した抜粋を保存する。切り詰め有無と元の文字数も保存する
- 項目サイズを実測し、400 KB に近づいた場合は本文を黙って落とさず `truncatedTrace` と理由を記録する。S3 退避は後続
- `RAG_LOGIC_VERSION` はデプロイ元 commit の短縮 SHA とする。SAM パラメータから環境変数へ渡し、未設定時は `unknown` を保存する
- `priorityExpanded`、`count1/count2`、`usedAbbrevExpansion` と重複レイテンシ項目は第 1 版の trace に保存しない。検索段階・計測は `searchAttempts[]` と `generation` にまとめる
- （2026-11-12 itai）法令モードも第 1 版の対象にする（§3.1）。本文は他と同じく 1,200 字まで
- （2026-11-12 itai）失敗一覧の `traceSummary` は出す（§5）。会話一覧は属性を絞って読む
- （2026-11-12 itai）再発防止は指標を足さず、全経路のテスト（§8）と配備後の 1 件確認（§11）で行う

## 11. 配備後の確認（2026-11-12 追加）

phase2 の配備後、合成質問を 1 問流し、その回答の項目を `sessionId`（パーティションキー）と回答の `messageId`（ソートキー）で 1 件だけ読む。整合性のある読み取りで、取り出す属性は `retrievalTrace.logicVersion` と `retrievalTrace.gate.responseType` の 2 つに絞る（トレースの中身は画面に出さない）。

- `logicVersion` が今回配備した SHA（`RagLogicVersion` に渡した値）と一致すること
- `responseType` が、流した質問で想定した経路（clarify / not_found / pages / law のいずれか）と一致すること

どちらかが違う、または項目に `retrievalTrace` が無ければ、配備を記録する PR・issue に「未記録」と書く。

```bash
aws dynamodb get-item --table-name chatlogs-dev --consistent-read \
  --key '{"sessionId":{"S":"<合成質問の sessionId>"},"messageId":{"S":"<回答の messageId>"}}' \
  --projection-expression "retrievalTrace.logicVersion, retrievalTrace.gate.responseType"
```

表全体の件数（`Scan` で `attribute_exists(retrievalTrace)` を数える）は使わない。過去のトレースが TTL（60 日）まで残るため、2 回目以降の配備では壊れていても 1 件以上になり、今回の配備を判定できない（mona 指摘・itai 合意 2026-11-13）。

9/25 の実装が入ったと思われたまま 7 週間記録されなかった反省から、指標・アラームは置かず、この確認とテストで代える（itai 2026-11-12）。
