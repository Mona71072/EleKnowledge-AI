---
status: development
last-verified: 2026-11-04
related-code:
  - lambda/rag/rag-function/research_api.py
  - lambda/rag/rag-function/research_job_store.py
  - lambda/rag/rag-function/research_worker.py
  - frontend/src/app/chat/page.tsx
---

# じっくりモード API

## 提供条件

- `ResearchModeEnabled` が `beta` または `on` の開発環境で利用できる。既定値は `off`。
- dev以外では、設定値にかかわらずAPIは404を返す。SAMリソースもdevで明示的に有効化した場合だけ作成する。
- すべての経路は既存 `RagApi` のCognito Authorizer、WAF、スロットリングを通る。利用者IDはJWTの `sub` から取得し、リクエスト本文の `userId` は使わない。

## POST /rag/research

調査ジョブを作成し、workerを非同期起動する。

**Request:**

```json
{
  "query": "AXIEZとNEXCUBEで据付時の違いを比較してください",
  "clientRequestId": "550e8400-e29b-41d4-a716-446655440000",
  "sessionId": "session_xxxxx",
  "filters": { "category": ["spec", "tech_info"], "modelType": "AXIEZ" }
}
```

- `query`: 前後空白除去後に1〜2,000文字。
- `clientRequestId`: 必須UUID。同じ送信の再試行には同じIDを使う。既存要求があれば同じjobIdを返す。
- `sessionId`: 省略時は新規作成。指定時は所有者を確認し、他人・不存在を同じ404にする。
- `filters`: 任意。`category`（安定キー文字列または文字列配列）と `modelType` を受け付ける。
- userId、質問本文、検索語はジョブ表へ複製しない。質問本文はchatlogsのuserメッセージだけに保存し、worker起動ペイロードは `{ "jobId": "..." }` のみ。

**202 Accepted:**

```json
{
  "jobId": "<uuid>",
  "sessionId": "session_xxxxx",
  "userMessageId": "msg_...",
  "status": "queued",
  "quota": { "limit": 10, "used": 1, "remaining": 9, "resetsAt": "2026-11-05T00:00:00+09:00" }
}
```

聞き返しが必要な質問は同期 `200` の `responseType: "clarify"` を返し、日次回数を消費しない。

| Status | Error | 意味 |
|---|---|---|
| 400 | `ValidationError` | 入力不正 |
| 401 | `Unauthorized` | Cognito `sub` がない |
| 404 | `NotFound` | 機能off、dev以外、または所有しないセッション |
| 409 | `ResearchAlreadyRunning` | 同一利用者の別ジョブが進行中 |
| 429 | `DailyLimitExceeded` / `DailyAttemptLimitExceeded` | JST日次上限 |
| 503 | `ResearchUnavailable` | 予約・chatlogs保存・worker起動に失敗 |

回数、同時実行ロック、起動回数、冪等キー、job行はDynamoDB `TransactWriteItems` で原子的に確保する。上限は成功10回/日、起動20回/日、同時実行1件。起動失敗・workerタイムアウトは予約日の成功回数を1回だけ返す。

## GET /rag/research/{jobId}

所有者のjob状態だけを返す。他人・不存在は同じ404。

```json
{
  "jobId": "<uuid>",
  "sessionId": "session_xxxxx",
  "status": "running",
  "stage": "searching",
  "progress": { "step": 2, "totalSteps": 6, "searchesDone": 1, "searchesTotal": 4 },
  "pollAfterMs": 5000
}
```

`queued` は `pollAfterMs: 5000`、照合中は `3000`。期限超過のqueued/running jobはこの取得時に条件付きで失敗化し、quota返却とロック解除を行う。完了時は `message` に既存chatlogsのassistantメッセージを含む。検索語・根拠本文はjob状態APIへ返さない。

## GET /rag/research?sessionId=...

セッション所有者の実行中jobを最大1件返す。再表示時にフロントがpollingを再開する。他人・不存在のsessionIdは404。

## GET /rag/research/quota

利用者本人の当日JST quotaを返す。日付切替は `Asia/Tokyo` の午前0時。

```json
{ "limit": 10, "used": 1, "remaining": 9, "resetsAt": "2026-11-05T00:00:00+09:00" }
```

## Worker

固定手順で計画、並列検索、根拠選定、統合、照合を行う。検索は最大8回、根拠はscore 0.3以上・1資料3件まで・合計20件・各2,000文字まで。根拠0件では作文しない。計画・統合・照合の各JSONはスキーマと根拠IDを検査する。

workerはqueued状態・dispatch期限・ACTIVEロックを条件付きトランザクションでclaimし、以後の進捗・完了・失敗更新は自分のleaseTokenが一致する場合だけ受理する。回答assistantメッセージ保存、job完了、ACTIVEロック解除は1つのトランザクションで行う。非同期起動は再試行0回、最大イベント経過120秒、失敗記録は専用SQSへ送る。
