---
status: production
phase: 2
last-verified: 2026-07-29
related-code: lambda/chat/, frontend/src/app/chat/, frontend/src/app/admin/failures/
---

# チャット管理API

> Phase 2 のチャットセッション管理エンドポイント。

**Base URL:** Phase 2 `ChatApiUrl` output, e.g. `https://{api-id}.execute-api.{region}.amazonaws.com/{env}`

認可: Cognito Authorizer（ID トークン）。セッション操作は **呼び出し元 sub の所有セッションのみ**（ボディ／クエリの userId は使わない）。

## GET /chat/sessions
セッション一覧取得（自分の分のみ）

## GET /chat/sessions/{sessionId}/messages
メッセージ一覧

## DELETE /chat/sessions/{sessionId}
論理削除（`deleted` フラグ。TTL と Stream→S3 アーカイブで保全）

## PUT /chat/messages/{messageId}/feedback
👍 / 👎。セッション所有者のみ。

**Request:**
```json
{
  "sessionId": "session_xxxxx",
  "feedback": "bad",
  "reason": "wrong_page",
  "comment": "（任意・最大200文字）"
}
```

| フィールド | 必須 | 説明 |
|---|---|---|
| `sessionId` | yes | 対象セッション |
| `feedback` | yes | `good` \| `bad` |
| `reason` | no | `bad` のときのみ。`wrong_doc` \| `wrong_page` \| `bad_answer` \| `other` |
| `comment` | no | 自由記述（任意） |

- `good` のときは既存の `feedbackReason` / `feedbackComment` をクリアする
- `reason` なしの `bad` も有効（ワンタップ後に理由を選ばなくても信号は残る）
- CloudWatch EMF（`EleKnowledge/Feedback`）へ件数を送出

## GET /chat/admin/failures
失敗一覧（**admin グループのみ**。UI ガードだけでは不十分・サーバー側 403）

**Query:**
- `kind` = `all` \| `bad` \| `not_found`（既定 `all`）
- `limit` = 1〜100（既定 50）

**Response（抜粋）:**
```json
{
  "failures": [
    {
      "sessionId": "session_xxxxx",
      "messageId": "msg_xxxxx",
      "timestamp": "2026-07-29T12:00:00",
      "signals": ["bad"],
      "responseType": "pages",
      "feedback": "bad",
      "feedbackReason": "wrong_doc",
      "userQuery": "火災管制の解除条件は？",
      "queryFilters": { "modelType": "AXIEZ" },
      "topDocuments": ["C-123.pdf"],
      "assistantPreview": "..."
    }
  ],
  "count": 1,
  "scannedCount": 120,
  "kind": "all",
  "note": "hot window (TTL〜60日)。Scan ベースのため件数増で遅くなる場合は Athena へ移行。"
}
```

実装メモ: chatlogs に失敗専用 GSI は無いため Scan + Filter。試用初期向け。`queryFilters` は RAG Lambda が assistant 行に保存する（2026-07-29〜）。
