---
status: development
phase: 3
last-verified: 2026-05-21
related-code: lambda/troubleshooting/orchestrator/
---

# トラブルシューティング API

Phase 3 のトラブルシューティング機能が使用するエンドポイント。
**Base URL は chat-api と共用**: `https://s8dbirs0m6.execute-api.us-east-1.amazonaws.com/development`

フロントエンド環境変数: `NEXT_PUBLIC_TROUBLESHOOTING_API_URL`

## 認証

全エンドポイントで Cognito ID トークンが必要。

```
Authorization: Bearer <Cognito ID Token>
```

User Pool: `us-east-1_fCbgU2FR9` / Client ID: `5e3penrp89bbscs1001b246tqj`

---

## POST /troubleshooting/analyze

トラブル情報を受け取り、Bedrock Agent 経由で原因分析と対処方法を返す。

**Lambda:** `troubleshooting-orchestrator`
**Bedrock Agent:** `D6FAGLJPPO` (alias: `TSTALIASID` = DRAFT)

### Request

```json
{
  "constructionNumber": "EIK54801",
  "troubleDescription": "エレベーターが動かない。制御盤のランプが全部消えている。",
  "model": "KE-LG",
  "errorCode": "E001"
}
```

| フィールド | 型 | 必須 | 説明 |
|-----------|------|------|------|
| `constructionNumber` | string | △ | 工事番号（半角英数8文字）。`model` と片方は必須 |
| `troubleDescription` | string | ✓ | 不具合内容（5〜2000文字） |
| `model` | string | △ | 機種名。`KE-LG` / `KM-LD` / `CM-MA` / `ME-CH` のいずれか |
| `errorCode` | string | — | エラーコード（半角英数4文字） |

### Response 200

```json
{
  "result": "【現場情報】\n工事番号: EIK54801\n現場名: ○○川崎\n...\n\n【トラブルシューティング】\n..."
}
```

| フィールド | 型 | 説明 |
|-----------|------|------|
| `result` | string | Bedrock Agent が生成したトラブルシューティング回答（Markdown 形式） |

### Response 400

```json
{ "error": "troubleDescription は必須です" }
```

バリデーションエラー。`error` フィールドに詳細メッセージが入る。

### Response 401

Cognito トークンなし / 期限切れ。

### Response 500

```json
{ "error": "内部エラー" }
```

Bedrock Agent 呼び出しエラー等の予期しない例外。

---

## 処理フロー

```
POST /troubleshooting/analyze
  → API Gateway (s8dbirs0m6) — CognitoAuthorizer (uum6s9)
  → troubleshooting-orchestrator Lambda
      ├─ 入力バリデーション
      └─ Bedrock Agent invoke (D6FAGLJPPO / TSTALIASID)
           ├─ GetSiteInfo (db-search Lambda)
           │    └─ DynamoDB sites テーブル → 現場名・機種・制御システム
           ├─ Action2-KB-Serch1 (kb-search1 Lambda)
           │    └─ KB (OCLVRJDMAH) Trouble-Cases/Trouble-Reports 検索
           ├─ Action3-KB-Serch2 (kb-search2 Lambda)
           │    └─ KB (OCLVRJDMAH) トラブルシュートマニュアル全文検索
           └─ Action4-KB-Serch3 (kb-search3 Lambda)
                └─ KB (OCLVRJDMAH) C資料（詳細技術資料）検索
```

---

## CORS

| ヘッダー | 値 |
|---------|-----|
| `Access-Control-Allow-Origin` | `*` |
| `Access-Control-Allow-Methods` | `POST, OPTIONS` |
| `Access-Control-Allow-Headers` | `Content-Type, Authorization` |
