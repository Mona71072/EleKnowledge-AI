---
status: production
last-verified: 2026-07-29
related-code: infrastructure/, lambda/rag/, lambda/chat/, lambda/metrics/, lambda/announcements/
---

# データモデル

> 出典: 旧 [spec.md](../spec.md) §6（PR #10 で本ファイルに切り出し）  
> **正本の補足:** API 契約は [`docs/api/rag.md`](./api/rag.md) / [`docs/api/chat.md`](./api/chat.md)。  
> 本ページの S3 パス例など古い記述がある場合は API／コードを優先する。

## DynamoDB テーブル設計

### users テーブル

```typescript
{
  userId: string;           // Partition Key (Cognito Sub)
  email: string;            // Email
  username: string;         // ユーザー名
  createdAt: string;        // 作成日時（ISO 8601）
  lastLoginAt: string;      // 最終ログイン
  role: 'admin' | 'user';   // ロール
}
```

### eleknowledge-chatlogs テーブル（ホットウィンドウ）

> 最終検証: 2026-09-11 — 設計 design-2026-09-10-dashboard-v2.md と実装 PR #110 / #111 / #112 / #114 のコードと突合（実環境は未デプロイ）

```typescript
{
  sessionId: string;        // Partition Key
  messageId: string;        // Sort Key (ULID)
  userId: string;           // ユーザーID（GSI）
  role: 'user' | 'assistant' | 'product_wish';
  content: string;          // メッセージ内容
  timestamp: string;        // タイムスタンプ
  citations?: string[];     // 引用（AIのみ・レガシー）
  sourceDocuments?: object[]; // ソース文書（AI）
  // --- 2026-07-29 RAG 応答メタ（assistant）---
  responseType?: 'clarify' | 'pages' | 'not_found';
  pageCandidates?: object[];
  clarifyQuestions?: string[];
  queryFilters?: object;    // 当時の機種・カテゴリ等
  // --- フィードバック ---
  feedback?: 'good' | 'bad';
  feedbackReason?: 'wrong_doc' | 'unresolved' | 'bad_answer' | 'other' | 'wrong_page';
  // wrong_page は旧データのみ（新規 PUT 拒否）。unresolved は「資料が悪い」決め打ちではなく failures で振り分け
  feedbackComment?: string;
  feedbackAt?: string;
  // --- 2026-09-11 運用テレメトリ・振り分け（PR #111 / #114。設計 design-2026-09-10-dashboard-v2.md §4.3 I3 / §9.4）---
  documentOpens?: number;   // 引用文書を開いた回数（GET /rag/document?uri=&s=&m= が所有者確認のうえ加算。assistant のみ）
  lastOpenedAt?: string;
  reformulatedAt?: string;  // 回答（pages）直後 10 分以内に同じセッションで次の質問が来た印。👍 も資料クリックも無ければ「言い換え」＝暗黙の失敗として集計
  triage?: {                // 失敗・要望の振り分け（admin が PUT /chat/admin/messages/{sessionId}/{messageId}/triage で保存）。未設定 = open
    status: 'open' | 'in_progress' | 'done' | 'wontfix';
    cause?: 'search' | 'snippet' | 'writing' | 'clarify' | 'kb_missing' | 'scope' | 'user' | 'other';
    note?: string;          // 200 字まで
    ref?: string;           // #issue / ゴールデン ID / commit
    by: string;             // Cognito sub
    at: string;
  };
  deleted?: boolean;        // 論理削除
  ttl: number;              // TTL（保存時から約60日。Stream→S3 で保全）
}
```

**GSI (Global Secondary Index):**
- userId-timestamp-index: ユーザーごとの履歴取得

失敗一覧（`GET /chat/admin/failures`）は失敗専用 GSI を持たず Scan + Filter（試用初期向け）。詳細は [`docs/api/chat.md`](./api/chat.md)。

`role=product_wish`（利用者の「こうなってほしい」。`sessionId = wish-{sub}`）の行にも `triage` が付く。

### announcements テーブル

> 最終検証: 2026-09-11 — 設計 design-2026-09-10-dashboard-v2.md と実装 PR #110 / #111 / #112 / #114 のコードと突合（実環境は未デプロイ）

```typescript
{
  announcementId: string;   // Partition Key（anc_<epoch ms>_<rand>）
  type: 'notice' | 'update' | 'maintenance';
  title: string;
  body: string;             // Markdown（保存前にサニタイズ）
  severity: 'info' | 'warning' | 'critical';
  status: 'draft' | 'scheduled' | 'published';
  publishAt: string;        // GSI status-publishAt-index の SK
  startAt?: string;         // maintenance の期間
  endAt?: string;           // 表示終了。全種別で使う（管理画面の「表示終了」は endAt を今にする更新。削除ではない）
  pinned?: boolean;
  showInChat?: boolean;     // チャット画面の帯にも出す（既定: critical なら true。PR #112。設計 §10.4）
  createdBy: string; createdAt: string; updatedAt: string; updatedBy?: string;
}
```

**GSI:** `status-publishAt-index`（PK=status, SK=publishAt）。利用者向け `GET /announcements` は published と期限到来の scheduled を返し、`endAt` 経過分を除く。

### metrics テーブル（日次 KPI）

> 最終検証: 2026-09-11 — 設計 design-2026-09-10-dashboard-v2.md と実装 PR #110 / #111 / #112 / #114 のコードと突合（実環境は未デプロイ）

PK `metricDate` / SK `scope`。GSI `scope-metricDate-index`（PK=scope, SK=metricDate）で範囲を Query する。**TTL は無効**（前年比較のため自動削除しない。PR #93）。日付は **JST**（固定オフセット +09:00）。ただし `scope=cost` だけは Cost Explorer に合わせて **UTC 日**。

| scope | metricDate | 内容 | 書き込み |
|---|---|---|---|
| `overall` | `YYYY-MM-DD` | 日次 KPI。chatlogs 由来（queries / userIds / notFound / clarify / pages / unreached / triageOpen / documentOpens / reformulated / feedbackReasons / topDocuments …）と CloudWatch 由来（API Gateway 4 本の Count / 5xx / 4xx、rag-api の Latency、Amplify、Cognito SignInSuccesses、Bedrock トークン、アラーム遷移 `alarmTransitions`、推定 Bedrock 費 `estimatedBedrockCostUsd`、`soleUserOk`）。当日は `partial: true` | 毎時（当日を上書き）+ 02:00 JST に D-1〜D-3 を再集計（後付けの 👍👎・資料クリックを回答日の行へ） |
| `hourly` | `YYYY-MM-DDTHH` | その 1 時間の件数（queries / notFound / clarify / pages / feedbackGood / feedbackBad / unreached / activeUsers） | 毎時 |
| `cost` | `YYYY-MM-DD`（UTC） | Cost Explorer のサービス別実額 `byService`、Bedrock 行の使用タイプ別 `bedrock.{input,output,cache}`、`settled`（D-2 以前で true） | 02:00 JST に直近 3 日を上書き |
| `eval` | `YYYY-MM-DD` | 週次ゴールデン評価（別設計。未実装） | — |

集計ロジックの版は `logicVersion`。定義は [`design-2026-09-10-metrics-v2.md`](./design-2026-09-10-metrics-v2.md) §4〜§5 と [`design-2026-09-10-dashboard-v2.md`](./design-2026-09-10-dashboard-v2.md) §6.1 / §6.2。

## S3 バケット構成

> 実バケット名／プレフィックスは環境の CloudFormation / SSM を正とする。  
> 下記は概念メモ。KB 再利用構成の詳細は phase2 KB レポート等を参照。

### Knowledge Base 用ドキュメント

本番／開発の Knowledge Base が参照するドキュメントバケット（既存 KB 再利用）。

### アップロード／アーカイブ

- 一時アップロード用プレフィックス（環境依存）
- chatlogs Stream → S3 アーカイブ（TTL 物理削除前の保全）

## データライフサイクル管理

### チャット履歴の保管期間

**ポリシー（現行コード）:**
- ホットウィンドウ: 保存時から **約60日**（DynamoDB TTL）
- 物理削除前に Stream → S3 アーカイブで保全
- UI: 各セッションに残り日数を表示しうる

**実装（RAG 保存時）:**
```python
# lambda/rag/rag-function/app.py
ttl_timestamp = int(time.time()) + (60 * 24 * 60 * 60)  # 60 days
```
