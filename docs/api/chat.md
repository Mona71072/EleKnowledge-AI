---
status: production
phase: 2
last-verified: 2026-09-09
related-code: lambda/chat/, frontend/src/app/chat/, frontend/src/app/admin/failures/, frontend/src/lib/chat-failures.ts
---

> **frontmatter の `status: production`:** 2026-09-10 以前から運用中の節を指す。2026-09-11 以降に追加した節は develop マージと SAM デプロイ前 — 各節の「最終検証」行を正とする。

# チャット管理API

> Phase 2 のチャットセッション管理エンドポイント。

**Base URL:** Phase 2 `ChatApiUrl` output, e.g. `https://{api-id}.execute-api.{region}.amazonaws.com/{env}`

認可: Cognito Authorizer（ID トークン）。セッション操作は **呼び出し元 sub の所有セッションのみ**（ボディ／クエリの userId は使わない）。

## GET /chat/sessions

> 最終検証: 2026-09-22 — #84 実装（sessionTitle は非同期完了後。それまでは最初のユーザー質問）

セッション一覧取得（自分の分のみ）

各セッションは `sessionId` / `title` / `messageCount` / `createdAt`（最古メッセージ）/ `lastMessageTime`（最新メッセージ）/ `ttl` / `daysUntilDeletion` を返す。`wish-` で始まるセッション（改善要望）は含めない。

**`title` の決め方**（優先順に採用。2026-09-09 更新）:

1. メッセージに保存された `sessionTitle` — RAG が**最初のやりとりの非同期処理で書いた**見出し（完了前は未保存。その間は 2。[`docs/api/rag.md`](./rag.md) の `sessionTitle` 参照）
2. そのセッションの**最初のユーザー質問**（見出し生成前の既存セッション・生成失敗時）
3. 最古メッセージの本文 — 先頭の「※」注意書き段落と Markdown の見出し・強調記号を除いて先頭50文字

> **WHY:** 直近メッセージ（多くは AI 回答）の先頭50文字を使っていたため、機種未指定時に回答冒頭へ付く「※機種未指定のため、一般資料…」で一覧が埋まり、会話を判別できなかった（PR #84）。注意書き自体は断定防止のため回答に残す。

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

> 最終検証: 2026-09-25 — failures 応答・走査上限・triage 未設定値を #142 最新実装と照合（未デプロイ。#111 / #114 / #142 のマージ・SAM デプロイ後に有効）

失敗一覧（**admin グループのみ**。UI ガードだけでは不十分・サーバー側 403）

**Query:**
- `kind` = `all` \| `bad` \| `not_found` \| `reformulated`（既定 `all` = bad + not_found。`reformulated` は「言い換え」＝回答直後に次の質問が来て 👍 が無いもの）
- `limit` = 1〜100（既定 50）
- `since` / `until` = `YYYY-MM-DD`（**JST の日付**、両端含む。不正な形式は 400）
- `triage` = `open` \| `in_progress` \| `done` \| `wontfix` \| `all`（既定 `all`。`open` は triage 未設定も含む）

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
      "assistantPreview": "...",
      "opened": 2,
      "reformulated": false,
      "triage": { "status": "in_progress", "cause": "snippet", "note": "表崩れ", "ref": "#112", "by": "sub-...", "at": "..." },
      "traceSummary": null,
      "hints": ["資料は開かれた（2 件）→ 検索は当たり、snippet か作文"]
    }
  ],
  "count": 1,
  "matchedCount": 1,
  "truncated": false,
  "scannedCount": 120,
  "incomplete": false,
  "kind": "all",
  "since": "2026-09-23",
  "until": "2026-09-23",
  "triage": "all",
  "note": "hot window (TTL〜60日)。Scan ベースのため件数増で遅くなる場合は Athena へ移行。"
}
```

| 追加フィールド | 意味 |
|---|---|
| `signals` | `bad` / `not_found` に `reformulated` が加わることがある |
| `opened` | 引用文書を開いた回数（chatlogs `documentOpens`） |
| `reformulated` | `reformulatedAt` があり、👍 も資料クリックも無い |
| `triage` | 振り分け。未設定は `{ "status": "open", "cause": null, "note": null, "ref": null, "by": null, "at": null }` |
| `traceSummary` | `retrievalTrace`（別設計、未実装）の要約。無ければ `null` |
| `hints` | 機械的な手がかり（判断ではない）。機種スコープ除外 / 上位スコアが弱い（仮 0.45）/ 資料は開かれた / 言い換え後に評価なし / カテゴリ過絞り / 聞き返し後 |

`count` は返却件数、`matchedCount` は今回の Scan で得た一致件数（`limit` 適用前）です。`truncated` は一致件数が `limit` を超えたこと、`incomplete` は25ページ上限で未走査分が残ることを示します。`incomplete=true` の場合、`matchedCount` は全件数ではありません。

実装メモ: chatlogs に失敗専用 GSI は無いため Scan + Filter。試用初期向け。`queryFilters` は RAG Lambda が assistant 行に保存する（2026-07-29〜）。

**改善提案パネル（v0）:** `/admin/failures` 上部で failures レスポンスをクライアント集計し定型提案を表示。`GET /chat/admin/improvement-summary` は**未実装**（後続）。設計: [design-2026-07-29-improvement-proposals.md](./design-2026-07-29-improvement-proposals.md)

## PUT /chat/admin/messages/{sessionId}/{messageId}/triage

> 最終検証: 2026-09-11 — 設計 design-2026-09-10-dashboard-v2.md と実装 PR #110 / #111 / #112 / #114 のコードと突合（実環境は未デプロイ）

失敗・要望の振り分けを保存する（**admin のみ**）。対象は `role=assistant` と `role=product_wish` の行。存在しなければ 404。

**Request:**
```json
{ "status": "done", "cause": "search", "note": "年度で絞ると落ちる。ゴールデンに追加", "ref": "G017" }
```

| フィールド | 必須 | 説明 |
|---|---|---|
| `status` | yes | `open` \| `in_progress` \| `done` \| `wontfix` |
| `cause` | no | `search` \| `snippet` \| `writing` \| `clarify` \| `kb_missing` \| `scope` \| `user` \| `other` |
| `note` | no | 200 字まで |
| `ref` | no | 100 字まで（#issue / ゴールデン ID / commit） |

**Response (200):** `{ "sessionId", "messageId", "triage": { ...上記 + "by": "<sub>", "at": "<ISO>" } }`

- 行は `triage` 属性に **置き換え**で保存する（前回の cause / note / ref は送らなければ消える。画面は下書きを埋めてから送る）
- Stream → S3 アーカイブへ MODIFY として流れるため、Athena で原因別の件数や対応までの日数を後から出せる
- 設計: [design-2026-09-10-dashboard-v2.md](../design-2026-09-10-dashboard-v2.md) §9.4

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
      "sessionId": "wish-sub-...",
      "messageId": "wish-1730...",
      "userId": "sub-...",
      "text": "機種なしでも検索してほしい",
      "timestamp": "2026-07-29T12:00:00",
      "contextSessionId": "session_xxxxx",
      "triage": { "status": "open" }
    }
  ],
  "count": 1
}
```

- `sessionId` と `triage` は 2026-09-11 に追加（PR #114）。要望の既読 / 対応済みは上記 PUT triage で保存する（`in_progress` = 既読）
