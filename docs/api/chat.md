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
成功定義に合わせ、UI の 👍＝「疑問が解けた」、👎理由で **何がダメだったか** を採取する。

**Request:**
```json
{
  "sessionId": "session_xxxxx",
  "feedback": "bad",
  "reason": "unresolved",
  "comment": "（任意・最大200文字）"
}
```

| フィールド | 必須 | 説明 |
|---|---|---|
| `sessionId` | yes | 対象セッション |
| `feedback` | yes | `good` \| `bad` |
| `reason` | no | `bad` のときのみ。下記のいずれか |
| `comment` | no | 自由記述（任意） |

**`reason`（新規）**

| 値 | UI 文言 | 意味 | 直す場所の目安 |
|---|---|---|---|
| `wrong_doc` | 資料が違う | 候補が別物 | 検索・フィルタ・KB |
| `unresolved` | 疑問が解けない | 資料は出た／見たが判断材料にならなかった | **決め打ちしない**。failures で人手振り分け（検索／snippet／作文／聞き返し／KB欠落） |
| `bad_answer` | 回答がおかしい | 断定・誤要約など作文の問題 | プロンプト・弱ゲート |
| `other` | その他 | 上記以外 | 人が見る |

- `wrong_page`（頁が違う）は **新規 400**（頁誘導仕様ではない）。旧データは failures で「頁が違う（旧）」表示可
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

**改善提案パネル（v0）:** `/admin/failures` 上部で failures レスポンスをクライアント集計し定型提案を表示。`GET /chat/admin/improvement-summary` は**未実装**（後続）。設計: [design-2026-07-29-improvement-proposals.md](./design-2026-07-29-improvement-proposals.md)

## POST /chat/suggestions
利用者の「こうなってほしい」自由記述（認証必須）。👎 とは別系統。

**Request:**
```json
{
  "text": "候補資料をもっと上に出してほしい",
  "sessionId": "session_xxxxx"
}
```

| フィールド | 必須 | 説明 |
|---|---|---|
| `text` | yes | 1〜1000 文字 |
| `sessionId` | no | 関連チャットセッション（所有する場合のみ保存） |

- chatlogs に `role=product_wish` として保存（`sessionId=wish-{sub}`）
- チャット履歴一覧には出さない

## GET /chat/admin/suggestions
改善要望一覧（**admin のみ**）

**Query:** `limit` = 1〜100（既定 50）

**Response（抜粋）:**
```json
{
  "wishes": [
    {
      "messageId": "wish-1730...",
      "userId": "sub-...",
      "text": "機種なしでも検索してほしい",
      "timestamp": "2026-07-29T12:00:00",
      "contextSessionId": "session_xxxxx"
    }
  ],
  "count": 1
}
```

