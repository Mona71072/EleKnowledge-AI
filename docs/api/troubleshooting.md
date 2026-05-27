---
status: development
phase: 3
last-verified: 2026-05-26
related-code: lambda/troubleshooting/orchestrator/, lambda/troubleshooting/history/, lambda/troubleshooting/authorizer/
---

# トラブルシューティング API — Ver 1.1

Phase 3 のトラブルシューティング機能が使用するエンドポイント。  
**専用 API Gateway**: `troubleshooting-api`（chat-api とは別 Gateway）

フロントエンド環境変数: `NEXT_PUBLIC_TROUBLESHOOTING_API_URL`

## バージョン履歴

| Ver | 日付 | 変更概要 |
|-----|------|----------|
| 1.0 | 2026-05-22 | PoC 完了時点の API 仕様 |
| **1.1** | **2026-05-26** | **`sourceDocuments` に `source_action` フィールドを追加** |

---

## 認証

全エンドポイントで Cognito ID トークンが必要。Lambda Authorizer（`troubleshooting-authorizer`）が JWT を検証し、`sub` クレームを `userId` として後段 Lambda に渡す。

```
Authorization: Bearer <Cognito ID Token>
```

User Pool: `us-east-1_fCbgU2FR9` / Client ID: `5e3penrp89bbscs1001b246tqj`

---

## POST /analyze

トラブル情報を受け取り、Bedrock Agent 経由で観点別の原因分析と対処方法を返す。  
セッションを `troubleshooting-sessions` テーブルに保存し、`sessionId` をレスポンスに含める。

**Lambda:** `troubleshooting-orchestrator`  
**Bedrock Agent:** `D6FAGLJPPO` (alias: `TSTALIASID` = DRAFT)

### Request

```json
{
  "constructionNumber": "EIK54801",
  "troubleDescription": "エレベーターが動かない。制御盤のランプが全部消えている。",
  "model": "KE-LG",
  "errorCode": "E34"
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `constructionNumber` | string | △ | 工事番号（半角英数8文字）。`model` と片方は必須 |
| `troubleDescription` | string | ✓ | 不具合内容（5〜2000文字） |
| `model` | string | △ | 機種名。`KE-LG` / `KM-LD` / `CM-MA` / `ME-CH` のいずれか |
| `errorCode` | string | — | エラーコード（半角英数字3文字） |

### Response 200

```json
{
  "sessionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "result": "【サイト情報】\n工事番号: EIK54801\n現場名: ○○川崎\n...\n\n【トラブル事例】\n...\n\n【マニュアル】\n...\n\n【C資料】\n...\n\n【推奨アクション】\n...",
  "sourceDocuments": [
    {
      "documentName": "KE-LG_troubleshoot.pdf",
      "title": "KE-LG トラブルシューティングガイド",
      "sourceUri": "https://s3.amazonaws.com/...（presigned URL, 30日有効）",
      "documentType": "Trouble-Cases",
      "model": "KE-LG",
      "relevance": 0.85,
      "source_action": "trouble_cases"
    },
    {
      "documentName": "manual_v2.pdf",
      "title": "トラブルシュートマニュアル Vol.2",
      "sourceUri": "https://s3.amazonaws.com/...",
      "documentType": "Manual",
      "model": "KE-LG",
      "relevance": 0.78,
      "source_action": "manual"
    },
    {
      "documentName": "C-material_KE.pdf",
      "title": "KE-LG C資料",
      "sourceUri": "https://s3.amazonaws.com/...",
      "documentType": "C資料",
      "model": "KE-LG",
      "relevance": 0.72,
      "source_action": "c_material"
    }
  ]
}
```

**フィールド定義:**

| フィールド | 型 | 説明 |
|---|---|---|
| `sessionId` | string | セッション ID（UUID）。履歴取得時に使用 |
| `result` | string | Bedrock Agent が生成した回答（Markdown・観点別構成） |
| `sourceDocuments` | array | 参照文書リスト（source_action 付き） |

**`sourceDocuments` 要素の型（Ver 1.1）:**

| フィールド | 型 | 説明 |
|---|---|---|
| `documentName` | string | S3 オブジェクトキーのファイル名部分 |
| `title` | string \| null | KB メタデータの `title` フィールド |
| `sourceUri` | string | S3 presigned URL（有効期限 30 日）。生成失敗時は `s3://` URI |
| `documentType` | string | KB メタデータの `document` フィールド（例: `Trouble-Cases`, `C資料`） |
| `model` | string | KB メタデータの `model` フィールド |
| `relevance` | number | 検索スコア（0.0〜1.0） |
| `source_action` | string | **★ Ver 1.1 追加。** 取得元アクションの識別子。`"trouble_cases"` / `"manual"` / `"c_material"` |

**`source_action` の値と意味:**

| 値 | 取得元アクション | 対応 KB 検索 Lambda | UI バッジ |
|---|---|---|---|
| `trouble_cases` | ② searchTroubleCases | kb-search1 | `② トラブル事例` |
| `manual` | ③ searchTroubleshootManuals | kb-search2 | `③ マニュアル` |
| `c_material` | ④ searchCMaterialDocs | kb-search3 | `④ C資料` |

> **仕組み（Ver 1.1）**: 各 KB 検索 Lambda が `source_action` タグ付きで DynamoDB セッションストアに書き込み、orchestrator が読み出して統合する。  
> Bedrock Agent EventStream `chunk.attribution.citations` からの引用も併用し、URI で重複排除する。  
> `.md` ファイルは除外。

### Response 400

```json
{ "error": "troubleDescription は必須です" }
```

バリデーションエラー。`error` フィールドに詳細メッセージが入る。

### Response 401

Cognito トークンなし / 期限切れ / 検証失敗。

### Response 500

```json
{ "error": "内部エラー" }
```

Bedrock Agent 呼び出しエラー等の予期しない例外。

---

## GET /history

ユーザーのトラブルシューティング履歴を取得する。  
`sessionId` 指定なし → 一覧。`sessionId` 指定あり → 詳細。

**Lambda:** `troubleshooting-history`

### GET /history（一覧）

**Response 200:**

```json
{
  "sessions": [
    {
      "sessionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "timestamp": "2026-05-26T10:30:00+00:00",
      "input": {
        "constructionNumber": "EIK54801",
        "model": "KE-LG",
        "troubleDescription": "エレベーターが動かない..."
      },
      "preview": "【サイト情報】\n工事番号: EIK54801\n..."
    }
  ]
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `sessions` | array | セッション一覧（最新50件、新しい順） |
| `sessions[].sessionId` | string | セッション ID |
| `sessions[].timestamp` | string | 実行日時（ISO 8601 UTC） |
| `sessions[].input` | object | リクエスト入力内容 |
| `sessions[].preview` | string | `result` の先頭 100 文字 |

### GET /history?sessionId={sessionId}（詳細）

**Response 200:**

```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "userId": "cognito-sub-uuid",
  "timestamp": "2026-05-26T10:30:00+00:00",
  "input": {
    "constructionNumber": "EIK54801",
    "model": "KE-LG",
    "troubleDescription": "エレベーターが動かない..."
  },
  "result": "【サイト情報】\n工事番号: EIK54801\n...",
  "sourceDocuments": [
    { "...", "source_action": "trouble_cases" }
  ]
}
```

**Response 404:**  
セッションが存在しない、または他ユーザーのセッションへのアクセス時。

---

## 処理フロー（Ver 1.1）

```
POST /analyze
  → troubleshooting-api (API Gateway)
      → Lambda Authorizer (troubleshooting-authorizer)
           └─ Cognito JWT 検証 → userId (sub) を context に付与
  → troubleshooting-orchestrator Lambda
      ├─ init_session(session_id, input, userId) → DynamoDB troubleshooting-sessions
      ├─ Bedrock Agent invoke (D6FAGLJPPO / TSTALIASID)
      │    │
      │    ├─ [工事番号ありの場合のみ] GetSiteInfo (db-search Lambda)
      │    │    └─ DynamoDB sites テーブル → 現場名・機種・制御システム
      │    │
      │    ├─ Action2 searchTroubleCases (kb-search1 Lambda)
      │    │    ├─ クエリ: 不具合内容
      │    │    ├─ フィルター: control-system=VFGLF + エラーコード（あれば）
      │    │    └─ write_citations(source_action="trouble_cases") → DynamoDB
      │    │
      │    ├─ Action3 searchTroubleshootManuals (kb-search2 Lambda)   ★ Ver 1.1
      │    │    ├─ クエリ: 不具合内容
      │    │    ├─ フィルター: control-system=VFGLF + エラーコード（あれば） ★ 変更（フィルターなし→あり）
      │    │    └─ write_citations(source_action="manual") → DynamoDB ★ 新規追加
      │    │
      │    └─ Action4 searchCMaterialDocs (kb-search3 Lambda)
      │         ├─ クエリ: ②③結果から Agent が抽出したキーワード     ★ 変更
      │         ├─ フィルター: 機種 + document=C資料
      │         └─ write_citations(source_action="c_material") → DynamoDB
      │
      ├─ fetch_citations(session_id) → DynamoDB（source_action 付き）
      ├─ build_source_documents(citations) → source_action フィールドを保持 ★ 変更
      └─ save_session_result(session_id, result, sourceDocuments) → DynamoDB

GET /history
  → troubleshooting-api (API Gateway)
      → Lambda Authorizer → userId 取得
  → troubleshooting-history Lambda
      └─ DynamoDB troubleshooting-sessions (userId-timestamp-index GSI)
```

---

## DynamoDB: troubleshooting-sessions テーブル

| 属性 | 型 | 説明 |
|---|---|---|
| `session_id` (PK) | String | UUID（orchestrator が生成） |
| `userId` | String | Cognito sub クレーム。GSI パーティションキー |
| `timestamp` | String | ISO 8601 UTC。GSI ソートキー |
| `ttl` | Number | Unix epoch + 30 日（DynamoDB TTL 自動削除） |
| `input` | Map | リクエスト入力（constructionNumber, model 等） |
| `citations` | List | kb-search1/2/3 が書き込んだ引用情報（uri, title, document, model, score, **source_action**） ★ Ver 1.1 |
| `result` | String | Agent が生成した回答テキスト |
| `sourceDocuments` | List | presigned URL 付き sourceDocuments（**source_action** 含む） ★ Ver 1.1 |

**GSI:** `userId-timestamp-index`

---

## CORS

| ヘッダー | 値 |
|---|---|
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Methods` | `GET, POST, OPTIONS` |
| `Access-Control-Allow-Headers` | `Content-Type, Authorization` |
