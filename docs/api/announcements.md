---
status: draft
phase: 2
last-verified: 2026-09-11
related-code: lambda/announcements/, frontend/src/lib/announcements.ts, frontend/src/lib/announcement-templates.mjs, frontend/src/app/admin/announcements/, frontend/src/components/announcements/
---

# お知らせ API（announcements）

> これまで API 文書が無かったため新設。`showInChat` と表示終了は実装 PR #112（実環境での検証は未実施のため `draft`）。設計: [design-2026-09-10-dashboard-v2.md](../design-2026-09-10-dashboard-v2.md) §10

**Base URL:** announcements-monitoring `AppApiUrl` output（`NEXT_PUBLIC_APP_API_URL`）

## GET /announcements?limit=10

認証済み利用者向け。表示中（`status=published`、または期限到来の `scheduled`）で `endAt` 未経過の告知を、固定 → 公開日時の新しい順で返す。`activeMaintenance` は期間中のメンテナンス告知を一覧の件数とは独立に返す（issue #94 B1）。

```json
{ "announcements": [ { "announcementId": "anc_...", "type": "notice", "title": "…", "body": "…", "severity": "critical",
                       "status": "published", "publishAt": "…", "endAt": "…", "pinned": true, "showInChat": true } ],
  "activeMaintenance": [], "serverTime": "…" }
```

表示先の規則（フロント）:

| 画面 | 出すもの |
|---|---|
| ホーム | 一覧（`AnnouncementsSection`）+ 期間中のメンテナンスの帯（`MaintenanceBanner`） |
| チャット | `NoticeBanner`: 期間中のメンテナンス + `showInChat=true` の告知。`critical` は閉じられない |

## admin（Cognito admin グループ）

| メソッド | パス | 内容 |
|---|---|---|
| GET | `/admin/announcements` | 全状態の一覧 |
| POST | `/admin/announcements` | 作成 |
| PUT | `/admin/announcements/{id}` | 部分更新 |
| DELETE | `/admin/announcements/{id}` | 削除（存在しなければ 404） |

**フィールド**

| フィールド | 必須 | 説明 |
|---|---|---|
| `type` | yes | `notice` \| `update` \| `maintenance` |
| `title` / `body` | yes / no | 120 字 / 20,000 字。`body` は Markdown（保存前にサニタイズ） |
| `severity` | yes | `info` \| `warning` \| `critical` |
| `status` | yes | `draft` \| `scheduled` \| `published`。`scheduled` は未来の `publishAt` 必須。未来の `publishAt` を持つ `published` は `scheduled` に丸める |
| `publishAt` | no | 公開日時 |
| `startAt` / `endAt` | maintenance は yes | メンテナンスの期間。**`endAt` は全種別で「表示終了」として使える**（更新で空文字を送ると属性を消す） |
| `pinned` | no | 上部に固定 |
| `showInChat` | no | チャット画面の帯にも出す。**既定は `severity=critical` なら true** |

- 管理画面の「表示終了」は `endAt` を今にする PUT。削除ではないので履歴が残る
- テンプレート（障害中 / 復旧 / 登録受付停止 / メール上限 / メンテナンス予告 / モデル切替）はフロントの定数 `announcement-templates.mjs`。`{{ }}` の穴が残ったままの公開は画面側で止める
- `/admin/announcements?template=incident` でテンプレートを流し込んだ状態で開く（ダッシュボード「いま」の「利用者へ告知 →」）
