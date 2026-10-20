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

> 最終検証: 2026-09-25 — `limit` の省略時・指定範囲を実装と照合（draft。未デプロイ）

認証済み利用者向け。表示中（`status=published`、または期限到来の `scheduled`）で `endAt` 未経過の告知を、固定 → 公開日時の新しい順で返す。`activeMaintenance` は期間中のメンテナンス告知を一覧の件数とは独立に返す（issue #94 B1）。

`limit` は省略時10、指定時は1〜50の範囲に制限します。

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

> 最終検証: 2026-10-10 — 管理一覧のページング（`limit` / `nextToken`）と「いま表示中」（`/admin/announcements/active`）を単体テストの模擬 GSI で照合。AWS 実環境での Query 応答は未確認（draft）

### dev反映の受け入れ条件・手順（#182）

フロントの`load()`は一覧と`/active`を同時に取得するため、API反映をフロント配信より先に行う。既存の`announcements-monitoring-dev`のパラメーター・認証・IP制限を保持し、変更セットで管理write Lambda、実行ロール、APIルートとSAMが生成する呼出し許可・デプロイだけの変更であることを確認する。

- writeロールは既存の項目操作権限を保持し、一覧用Scanを外して`status-publishAt-index`へのQueryを付ける。LambdaとIAMと新しいGETルートを同じ変更セットで反映する。
- `status-publishAt-index`がACTIVEであることを確認する。テーブルの追加・削除・置換は行わず、既存のTTL設定も保持する。
- #183の集計移行は別作業。既存デプロイ済みテンプレートを基準にwrite Lambdaとそのロールの変更を取り込み、metricsのコード・IAM・スケジュール・TTLを変更しない。最新developの集計コードだけを先に反映しない。
- 反映後はAPI GatewayのGETルートとCognito authorizer、Lambda呼出し許可、IAMを読み戻す。未認証HTTPは401、非管理者のLambda処理は403、管理者の一覧と表示中取得は200、`limit=1`の次ページは重複なし、不正limit/tokenは400を確認する。既存データは変更しない。
- JWTを通す実HTTP操作と、合成authorizer claimsによる直接Lambda統合試験は区別して記録する。後者だけでログイン済みブラウザE2Eを合格としない。
- フロント配信はこの確認後。ロールバックは反映前のテンプレート・コード成果物・パラメーターを保持した変更セットで管理APIとIAMを同時に戻す。フロントを既に配信した場合は先に旧フロントへ戻す。

#### dev反映・検証結果

> 最終検証: 2026-10-15 — 管理APIをdevへ先行反映し、CloudFormation・API Gateway・IAM・Lambda・DynamoDB設定の読み戻し、未認証HTTPと読み取り専用の直接Lambda統合試験で照合。

- 反映ソース: #182 `63c7a998`（最新develop統合済み、CI成功）。`announcements-monitoring-dev=UPDATE_COMPLETE`。
- 変更セットは管理write Lambda / ロール / API / stageのModify（すべてReplacement=False）、新GET用Lambda呼出し許可Add、SAM生成API deploymentのAdd / Removeのみ。既存パラメーター・テーブル・APIの実体IDとTTL設定を保持した。
- metrics read / aggregator、announcements read / publisherのCodeSha256が反映前後で一致。metricsの移行は未実施。
- GET `/admin/announcements/active`のCognito authorizer・Lambda proxy統合・呼出し許可を読み戻した。writeロールのGSI Query許可とScan除去を確認。
- 実HTTPの未認証GETは401。合成authorizer claimsによる直接Lambda試験では、非管理者は一覧・表示中とも403、管理者は200、不正limit/tokenは400。
- 管理一覧を`limit=1`で継続して2応答・合計1件（重複なし、末尾応答は空）を取得し、実GSIの全状態を直接Queryした件数と一致。表示中は1件。実データの少なさから大件数の実AWS試験ではなく、120件の全件取得は単体テストで確認した。
- 既存データへの書込みは0件。認証済みHTTP・ブラウザ操作のE2Eは未実施。件数・設定確認をログイン済み操作の合格に読み替えない。

共有証跡は#182の反映報告。詳細は実行端末の未追跡`announcements-api-verification-local.json`に保持する。本文・認証情報・実URLを共有記録へ貼らない。文書全体の検証日は進めない。

| メソッド | パス | 内容 |
|---|---|---|
| GET | `/admin/announcements` | 全状態の一覧（1 ページ。`limit` / `nextToken` でページング） |
| GET | `/admin/announcements/active` | いま表示中の全件（公開中・予約で公開日時到来・表示終了していない）。件数で切らず、ページングもしない |
| POST | `/admin/announcements` | 作成 |
| PUT | `/admin/announcements/{id}` | 部分更新 |
| DELETE | `/admin/announcements/{id}` | 削除（存在しなければ 404） |

**GET `/admin/announcements` のページング**

- クエリ: `limit`（1〜100 の整数。省略時 50）、`nextToken`（前回の応答の値。省略で先頭）。範囲外の `limit` や壊れた `nextToken` は 400（`ValidationError`）
- 応答: `{ "announcements": [...], "nextToken": "..." | null }`。`nextToken` が `null` なら末尾。`announcements` は `publishAt` の新しい順
- 状態（draft / scheduled / published）ごとに `status-publishAt-index` を降順に Query し、先頭から併合する。全件 Scan は使わない
- `nextToken` は各状態の GSI キーを base64url の JSON にしたもので、利用者が中身を組み立てる値ではない
- 管理画面は「さらに読み込む」で次ページを足す。保存・削除の後は先頭ページから読み直す
- `/admin/announcements/active` は公開一覧 API（`GET /announcements`、上限 50 件）とは別。`status-publishAt-index` を状態ごとに全ページ Query し、`publishAt` の新しい順で返す。管理画面の「いま表示中」欄はこれを使う（一覧のページ数に依存しない）

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
