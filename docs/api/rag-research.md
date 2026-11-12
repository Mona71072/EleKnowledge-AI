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

## 回答の安全の関門（段階 1'）

> 最終検証: 2026-11-12 — `itai` ブランチの `research_worker.py` を design-2026-09-24-rag-two-modes.md §11.3（PR #206）に合わせて改修し、単体テストで確認。実モデル・実 KB での確認は配備後に記録する。

設計 §11.3 の要件を、現行のじっくりモードのワーカーでコードとして強制する。エンジン統合・結果の契約・根拠の保持と再利用は段階 2' で扱う。

| # | 要件 | 受け入れ条件（単体テスト） |
|---|---|---|
| G1 | 主張の機種と根拠の機種は、語彙（`knowledge/registry/applicability-vocabulary.json` → `vocabulary_generated.py`）と取扱機種で正規化し、要素単位の完全一致で照合する | `AXIEZ` の主張が `AXIEZ-LINKs` だけの根拠を引くと不採用。辞書にない機種名の主張は不採用。主張が引く根拠は、すべて同じ機種か共通資料でなければならない。主張の機種が `*` / `general` / 全エレ機種 / 全エス機種なら、機種なしの主張として扱う |
| G2 | 共通資料（model_type が `*` / `general` / 無し）は機種付きの主張を裏付けてよい。根拠一覧に「共通資料」と表示する | 共通資料の根拠で機種付きの主張が採用され、根拠一覧に「共通資料」が出る |
| G3 | 機種の付かない主張が、異なる機種の根拠を引く場合は採用しない（確認できなかった点へ回す。機種ごとの欄への振り分けは 2'） | `AXIEZ` と `NEXCUBE` の根拠を同時に引く機種なしの主張は不採用 |
| G4 | 照合で否定された主張・照合できなかった主張は、本文を回答にも chatlogs にも出さない。件数だけを示す | 回答本文と `research` に否定された主張の文が含まれない。`research.unsupportedClaimCount` に件数が入る |
| G5 | 高リスクの質問では、結論を「■判断は確認先で行う」欄に置き、裏付けの状態を示す（裏付けあり / 未確認 N 件） | 照合で裏付けのある結論が「裏付けあり」として確認先の欄に出る。未確認の結論は件数だけ |
| G6 | リスク判定に失敗した場合（計画の JSON 不正・値が範囲外）は `high` として扱う | `normalize_plan({})` の `risk` が `high` |
| G7 | 根拠ごとに本文の SHA-256 と版を持つ。版のメタデータキーは `KB_PROFILE_JSON` の `version_key`（既定は空＝版なし）。同じ資料名で版が異なる根拠を 1 つの主張にまとめない | 版の異なる同名資料を引く主張は不採用。`research.evidence[]` に `textHash`・`version` が入る |
| G8 | 確認先は業務の種類（`safety` / `legal` / `work_permission` / `other`）ごとに `RESEARCH_ESCALATION_CONTACTS`（JSON）で持つ。未設定の種類は「未設定」と分かる表示にする | 設定なしで高リスクの回答に「確認先: 未設定」が出る。不正な JSON は空として扱う |
| G9 | 回答に出す資料名・ページは、保存した根拠のメタデータからコードで組み立てる。根拠 ID（E1〜E20）は回答本文に出さず、内部の照合と `research.claims[].evidenceIds` にだけ残す | 回答本文に `E1` などの番号が出ない。主張の末尾に資料名とページが出る。主張本文中の括弧付き根拠 ID は取り除く |

### 既知の欠落

- **KB に版のメタデータがない。** 共有 KB のメタデータキーは category / model_type / filename / file_path だけで（`app.py` の `build_kb_filter` の注記）、`version_key` を設定できる値がない。そのため G7 の版の照合は、現在は実質的に働かない（全根拠の `version` が `null`）。本文のハッシュは記録する。ファイル名から版を推定する方法は、KB の実データを調べてから判断する。
- 確認先の中身（業務の種類ごとの担当）は未決（design §11.11）。既定値は空で、表示は「未設定」になる。

### `research` の項目（段階 1' 時点）

`claims`（採用した主張。`evidenceIds` は内部 ID）、`differences`、`unknownPoints`、`unsupportedClaimCount`、`verificationStatus`（`complete` / `unavailable` / `not_needed`）、`risk`、`domain`、`searchCount`、`evidenceCount`、`searchFailures`、`evidence[]`（`id`・`documentName`・`page`・`modelScope`（`common` / `specific`）・`textHash`・`version`）。根拠の本文は保存しない。
