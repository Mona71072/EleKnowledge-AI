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

> **状態:** 設計（実装前）。決定の経緯は issue #86（コメント 2・3・16）。実装は初週の P1。

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

## 4. 実装箇所（`lambda/rag/rag-function/app.py`）

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
| `GET /chat/admin/failures`（管理者） | 第 1 版では変更しない。#104 が予定する `traceSummary` は出さない。#104 側の記述を合わせるのは、本設計に Yes が出たあとの #104 への追記で行う |
| 管理者向け専用 trace API／画面 | 後回し。第 1 版は Athena で参照 |
| S3 アーカイブ / Athena | 全文を保持。バケットは既存のアクセス制御（管理者ロール・Athena ワークグループ） |
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

## 9. 実装分割（PR）

| 順 | PR | 内容 | デプロイ |
|---|---|---|---|
| 1 | `feat(rag)` | 計測・トレース組み立て・保存・構造化ログ 1 行・`RAG_LOGIC_VERSION` | phase2 |
| 2 | `fix(chat)` | 利用者向け応答から除外 | phase2 |
| 3 | `feat(chat-archive)` | Glue テーブルに retrievaltrace 列 | chat-archive |
| 4 | 後続 | 単価管理 + USD 推定コスト（必要性を再確認して着手） | — |
| 5 | `docs` | `docs/data-model.md`（production、事前確認要）、`docs/api/chat.md` | — |

## 10. 第1版の決定

- 本文の上限は現行どおり 1,200 文字とし、モデルに渡した抜粋を保存する。切り詰め有無と元の文字数も保存する
- 項目サイズを実測し、400 KB に近づいた場合は本文を黙って落とさず `truncatedTrace` と理由を記録する。S3 退避は後続
- `RAG_LOGIC_VERSION` はデプロイ元 commit の短縮 SHA とする。SAM パラメータから環境変数へ渡し、未設定時は `unknown` を保存する
- `priorityExpanded`、`count1/count2`、`usedAbbrevExpansion` と重複レイテンシ項目は第 1 版の trace に保存しない。検索段階・計測は `searchAttempts[]` と `generation` にまとめる
