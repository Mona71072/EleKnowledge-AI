---
status: draft
last-verified: 2026-09-10
related-code: lambda/rag/rag-function/app.py, lambda/chat/chat-management/app.py, infrastructure/sam/chat-archive-template.yaml, lambda/metrics/aggregator/app.py
---

# 設計: 検索トレース（retrievalTrace）の保存

> **状態:** 設計（実装前）。決定の経緯は issue #86（コメント 2・3・16）。実装は初週の P1。

## 1. 目的

「引用したデータが合っているか」を後から検証できるようにする。具体的には、👎 や not_found の回答について **何が検索され、何が除外され、何を根拠に生成したか** を原文付きで追える状態にする。あわせて **トークン数・段階レイテンシ・モデル ID** を記録し、推論コストを算出できるようにする。

Bedrock の invocation logging は採用しない（Retrieve 結果が記録されない、アカウント全体に及ぶ、messageId と結合できない。issue #86 コメント 2）。

## 2. 前提（2026-09-10 実測）

| 項目 | 値 |
|---|---|
| assistant メッセージ項目のサイズ | 平均 16 KB、最大 26 KB（pageCandidates の snippet と sourceDocuments が主） |
| retrieve 件数 | `numberOfResults=30`、マージ後 平均 26・最大 30 |
| 候補頁（UI に出す） | 最大 5（`build_page_candidates`） |
| DynamoDB 項目上限 | 400 KB |
| 保全経路 | chatlogs Stream → `eleknowledge-chat-archive-dev` → S3（バージョニング有効、failed/ 保全あり）→ Glue `chatlogs_archive` |
| Bedrock 応答の `usage` | `input_tokens` / `output_tokens`（現在は破棄） |

## 3. データ設計

assistant メッセージ項目に属性 `retrievalTrace`（Map）を追加する。**利用者向け API には返さない**（§5）。

```jsonc
"retrievalTrace": {
  "version": 1,
  "logicVersion": "ecc7d09",            // 環境変数 RAG_LOGIC_VERSION（SAM パラメータでデプロイ時に git sha を渡す）
  "kbId": "VQV81CNYU4",
  "searchType": "HYBRID",
  "modelId": "global.anthropic.claude-sonnet-5",
  "requestStyle": "new",                // is_new_api_model の判定結果
  "query": {
    "original": "…",                    // 利用者入力（content と同じ。冗長だが追記結合後の値と区別するため）
    "composed": "…",                    // compose_search_query の結果（聞き返し後の結合）
    "normalized": "…",
    "expanded": "…"                     // 略語展開（未使用なら null）
  },
  "gate": { "clarify": false, "weak": false },
  "retrieve": {
    "count1": 30, "count2": 0, "mergedCount": 26,
    "priorityExpanded": false, "usedAbbrevExpansion": false,
    "latencyMs": 820
  },
  "candidates": [                       // マージ後の全候補（最大 30）。順位順
    {
      "rank": 1, "sourceUri": "s3://…/x.pdf", "documentName": "x.pdf",
      "pageNumber": 12, "chunkId": "…", "score": 0.61,
      "modelType": "AXIEZ", "category": "spec", "hasImage": false,
      "selected": true,                 // 生成に渡した（select_retrieval_results の結果）
      "excludedBy": null,               // "model_scope" | "dedupe" | null
      "text": "…"                       // selected のときだけ。最大 4,000 文字で切る
    }
  ],
  "generation": {
    "inputTokens": 3748, "outputTokens": 578,
    "stopReason": "end_turn", "latencyMs": 9305
  },
  "latencyMs": { "retrieve": 820, "generate": 9305, "total": 10400 }
}
```

サイズ見積: 候補メタ 30 件 × 約 200 B = 6 KB、本文は selected 最大 10 件 × 4,000 文字（UTF-8 で最大 12 KB/件）= 最大 120 KB。実際の chunk は 1〜2 KB が多いので通常 20〜40 KB。**項目全体が 300 KB を超える場合は `text` を落として `textTruncated: true` を付ける**（400 KB 上限のガード）。IMAGE チャンクの base64 は保存しない（`hasImage` と URI のみ）。

`clarify` / `not_found` 応答でも `retrievalTrace` を保存する（not_found は candidates と gate のみ、generation は null）。

## 4. 実装箇所（`lambda/rag/rag-function/app.py`）

1. `time.perf_counter()` で retrieve（`retrieve_for_normal_query` 2 回分）と generate（`invoke_model`）を計測
2. `generate_response_with_claude` が `usage` と `stop_reason` を返せるように、戻り値を `(text, meta)` に変更（呼び出し側 1 か所）。`extract_response_text` は #90 で導入済み
3. `query_knowledge_base` の機種スコープ除外で落とした候補を捨てずに `excludedBy="model_scope"` として返す（現在は無言で除外。トレースにだけ載せ、UI と生成には渡さない）
4. `build_retrieval_trace(...)` を新設し、`save_message_to_dynamodb(..., retrieval_trace=...)` に渡す
5. CloudWatch Logs には **本文を出さず** 1 行の JSON を出す: `{"event":"rag_request","messageId","sessionId","responseType","mergedCount","selectedCount","excludedByModelScope","topScore","inputTokens","outputTokens","latencyMs":{...},"modelId"}`（AGENTS.md「ログと秘匿」）
6. `RAG_LOGIC_VERSION` を SAM パラメータ → 環境変数で渡す（デプロイ手順で `git rev-parse --short HEAD` を指定）

## 5. 露出制御

| 経路 | 扱い |
|---|---|
| `GET /chat/sessions/{id}/messages`（利用者） | `retrievalTrace` を **除外**（chat-management `get_session_messages` で pop） |
| `GET /chat/admin/failures`（管理者） | 要約のみ追加: `traceSummary: {mergedCount, selectedCount, excludedByModelScope, topScore, inputTokens, outputTokens, latencyMs}` |
| 新規 `GET /chat/admin/messages/{sessionId}/{messageId}/trace`（管理者） | 全文を返す（Cognito admin グループ + IP 許可リストの内側）。初月で実装、初週は Athena で参照 |
| S3 アーカイブ / Athena | 全文を保持。バケットは既存のアクセス制御（管理者ロール・Athena ワークグループ） |
| CloudWatch Logs | 件数・スコア・トークン・レイテンシのみ |

## 6. Athena（Glue テーブル）

`chatlogs_archive` の `newimage` / `oldimage` の struct に `retrievaltrace` を追加する（OpenX JSON SerDe は未宣言のキーを無視するため、宣言しない限り参照できない）。

```
retrievaltrace: struct<
  version:int, logicversion:string, kbid:string, searchtype:string, modelid:string, requeststyle:string,
  gate:struct<clarify:boolean, weak:boolean>,
  retrieve:struct<count1:int, count2:int, mergedcount:int, priorityexpanded:boolean, usedabbrevexpansion:boolean, latencyms:int>,
  candidates:array<struct<rank:int, sourceuri:string, documentname:string, pagenumber:int, chunkid:string, score:double,
                          modeltype:string, category:string, hasimage:boolean, selected:boolean, excludedby:string, text:string>>,
  generation:struct<inputtokens:int, outputtokens:int, stopreason:string, latencyms:int>,
  latencyms:struct<retrieve:int, generate:int, total:int>
>
```

代表クエリ（👎 と検索結果の突合）:

```sql
SELECT a.newimage.messageid, a.newimage.feedbackreason, c.rank, c.documentname, c.pagenumber, c.score, c.selected, c.excludedby
FROM eleknowledge_analytics.chatlogs_archive a
CROSS JOIN UNNEST(a.newimage.retrievaltrace.candidates) AS t(c)
WHERE a.dt >= '2026-09-10' AND a.newimage.feedback = 'bad'
ORDER BY a.newimage.messageid, c.rank;
```

## 7. コスト算出

- 単価は SSM `/eleknowledge/dev/bedrock-unit-price`（String, JSON）: `{"global.anthropic.claude-sonnet-5": {"inputPerMTok": 2.0, "outputPerMTok": 10.0}, "jp.anthropic.claude-haiku-4-5-20251001-v1:0": {"inputPerMTok": 1.1, "outputPerMTok": 5.5}}`（地域指定は 1.1 倍込み。改定時はパラメータだけ更新）
- 日次集計 Lambda が当日分の assistant 項目の `retrievalTrace.generation` を合計し、`inputTokens` / `outputTokens` / `estimatedBedrockCostUsd` を `metrics-dev` の行に書く（[metrics-v2 設計](./design-2026-09-10-metrics-v2.md)）
- Athena では 1 クエリあたりコストを `inputtokens/1e6*単価 + outputtokens/1e6*単価` で算出

## 8. テスト

- `build_retrieval_trace`: selected のみ text を持つ、30 件上限、300 KB 超で text を落とす、not_found でも生成できる
- `generate_response_with_claude` の戻り値変更（既存テストの更新）
- chat-management: 利用者向け応答に `retrievalTrace` が含まれない、admin failures に `traceSummary` が付く
- 保存項目のサイズ試算（実 KB で 5 問流して項目サイズを記録し、本設計の見積と比較する）

## 9. 実装分割（PR）

| 順 | PR | 内容 | デプロイ |
|---|---|---|---|
| 1 | `feat(rag)` | 計測・トレース組み立て・保存・構造化ログ 1 行・`RAG_LOGIC_VERSION` | phase2 |
| 2 | `fix(chat)` | 利用者向け応答から除外、admin failures に traceSummary | phase2 |
| 3 | `feat(chat-archive)` | Glue テーブルに retrievaltrace 列 | chat-archive |
| 4 | `feat(metrics)` | 単価 SSM + トークン集計 + 推定コスト（metrics-v2 と同時） | announcements-monitoring |
| 5 | `docs` | `docs/data-model.md`（production、事前確認要）、`docs/api/chat.md` | — |

## 10. 決めておくこと（実装前）

- `text` の上限 4,000 文字で足りるか → **足りる**（2026-09-10 実測: KB `VQV81CNYU4` の 3 データソースはいずれも既定チャンク（約 300 トークン）、うち 1 つは FMP 解析。1 チャンクは日本語で数百〜1,500 文字程度）
- 除外候補（`excludedBy=model_scope`）の本文は保存しない（メタのみ）でよいか → よい（本文が要るときは KB から引ける）
- `RAG_LOGIC_VERSION` の運用（デプロイ手順に組み込む）
