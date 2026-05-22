# Phase 3 E2E テストガイド

## Orchestrator Lambda E2E テスト

### テストの目的
Orchestrator Lambda 経由で Bedrock Agent の全体的な動作確認

### テスト前提条件
- CloudFormation スタックでのデプロイ完了
- Lambda 関数の環境変数設定完了
- Bedrock Agent と Action Group の登録完了
- DynamoDB sites テーブルへのサンプルデータ投入完了

## テストシナリオ 1: 正常系テスト

### リクエスト内容

```json
{
  "constructionNumber": "12345678",
  "troubleDescription": "システムが起動しない",
  "model": "XXXXXX",
  "errorCode": "E001"
}
```

### テスト実行手順

1. **AWS Lambda コンソールで Orchestrator 関数を開く**
   - 関数名: `troubleshooting-orchestrator`

2. **テストイベント作成**
   - テスト名: `test_normal_case`
   - JSON ペースト:
   ```json
   {
     "constructionNumber": "12345678",
     "troubleDescription": "システムが起動しない場合の原因調査",
     "model": "XXXXXX",
     "errorCode": "E001"
   }
   ```

3. **テスト実行**
   - 「テスト」ボタンをクリック

4. **期待される結果**
   - statusCode: 200
   - 各 Action Group からの検索結果を統合したレスポンス
   - Citation 形式での参照文書情報

### ログの確認
- CloudWatch Logs: `/aws/lambda/troubleshooting-orchestrator`
- Bedrock Agent の実行ログを確認

## テストシナリオ 2: 入力検証テスト

### テストケース 2-1: constructionNumber 不正（8文字以外）

```json
{
  "constructionNumber": "123",
  "troubleDescription": "システムが起動しない",
  "model": "XXXXXX",
  "errorCode": "E001"
}
```

**期待される結果**: ValidationError（入力検証エラー）

### テストケース 2-2: troubleDescription 短すぎる（5文字未満）

```json
{
  "constructionNumber": "12345678",
  "troubleDescription": "短い",
  "model": "XXXXXX",
  "errorCode": "E001"
}
```

**期待される結果**: ValidationError

### テストケース 2-3: troubleDescription 長すぎる（2000文字超過）

```json
{
  "constructionNumber": "12345678",
  "troubleDescription": "[2001文字の文字列]",
  "model": "XXXXXX",
  "errorCode": "E001"
}
```

**期待される結果**: ValidationError

## テストシナリオ 3: 各 Action の動作確認

### Action 1: DB Search（DynamoDB sites テーブル検索）

**検証項目**:
- constructionNumber で sites テーブル照会
- 現場情報・設置機器・過去トラブル履歴の取得

**CloudWatch Logs で確認**:
```
DB Search response: {
  "construction_info": {...},
  "equipment_info": {...},
  "trouble_history": [...]
}
```

### Action 2: KB Search1（機種別トラブル事例検索）

**検証項目**:
- Model パラメータで Knowledge Base 検索
- Citation 形式での参照文書取得（1～3件）

**期待される出力**:
```json
{
  "source": "KB_ID",
  "relevance_score": 0.95,
  "uri": "s3://bucket/document_id"
}
```

### Action 3: KB Search2（全文検索）

**検証項目**:
- troubleDescription で全文検索
- 最大 3 件のマニュアル結果取得

### Action 4: KB Search3（C資料検索）

**検証項目**:
- errorCode で詳細技術資料検索
- Citation 情報の取得

## テスト結果記録

テスト実行後、以下の情報を記録：

| テスト項目 | 実行日時 | 結果 | 詳細 |
|-----------|--------|------|------|
| 正常系テスト | | | |
| 入力検証 - constructionNumber | | | |
| 入力検証 - troubleDescription | | | |
| Action 1: DB Search | | | |
| Action 2: KB Search1 | | | |
| Action 3: KB Search2 | | | |
| Action 4: KB Search3 | | | |

## トラブルシューティング

### Lambda タイムアウトエラー
- タイムアウト設定: 60秒
- Bedrock Agent 呼び出しが遅い場合は増加

### Bedrock Agent エラー
- Action Group の ARN が正しいか確認
- IAM ロール権限を確認

### Citation 情報が取得できない
- Knowledge Base ID が正しいか確認
- KB への文書インデックスを確認

## テストシナリオ 4: DynamoDB セッションストア検証

テストシナリオ 1 の正常系テスト実行後に確認する。

### 確認手順

1. **AWS DynamoDB コンソールで `troubleshooting-sessions` テーブルを開く**
2. **テスト実行後のアイテムを確認**

**期待されるアイテム構造:**

```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "userId": "test-user-sub-001",
  "timestamp": "2026-05-22T10:30:00.123456+00:00",
  "ttl": 1750000000,
  "input": {
    "constructionNumber": "EIK54801",
    "model": "KE-LG",
    "troubleDescription": "昇降機が途中で停止..."
  },
  "citations": [
    {
      "uri": "s3://bucket/TroubleCase_KE-LG_E001.pdf",
      "title": "KE-LG 過電流トラブル事例",
      "document": "Trouble-Cases",
      "model": "KE-LG",
      "score": "0.87"
    }
  ],
  "result": "【現場情報】...",
  "sourceDocuments": [...]
}
```

**検証項目:**
- `citations` 属性が `[]` でなく 1 件以上ある
- `result` と `sourceDocuments` が存在する
- `ttl` が現在時刻 + 約 2592000 秒（30 日）

---

## テストシナリオ 5: sourceDocuments が空でないことの確認

テストシナリオ 1 の実行結果（Lambda コンソールのレスポンス）を確認。

**期待されるレスポンス:**

```json
{
  "sessionId": "3fa85f64-...",
  "result": "【現場情報】...",
  "sourceDocuments": [
    {
      "documentName": "TroubleCase_KE-LG.pdf",
      "title": "KE-LG トラブル事例",
      "sourceUri": "https://s3.amazonaws.com/...",
      "documentType": "Trouble-Cases",
      "model": "KE-LG",
      "relevance": 0.87
    }
  ]
}
```

**検証項目:**
- `sessionId` が UUID 形式で含まれること
- `sourceDocuments` が `[]` でない
- `documentType`, `model`, `relevance` が正しく入っている
- `sourceUri` を開いて PDF にアクセスできる（presigned URL 有効）

---

## テストシナリオ 6: GET /history 一覧取得

### テスト実行手順

1. **AWS Lambda コンソールで `troubleshooting-history` を開く**
2. **テストイベント作成**（`tests/events/history-list-event.json` を使用）:

```json
{
  "httpMethod": "GET",
  "path": "/history",
  "queryStringParameters": null,
  "requestContext": {
    "authorizer": {
      "userId": "test-user-sub-001"
    }
  }
}
```

3. **期待される結果:**

```json
{
  "sessions": [
    {
      "sessionId": "3fa85f64-...",
      "timestamp": "2026-05-22T10:30:00+00:00",
      "input": { "constructionNumber": "EIK54801", "model": "KE-LG", "troubleDescription": "..." },
      "preview": "【現場情報】..."
    }
  ]
}
```

**検証項目:**
- `sessions` 配列にシナリオ 1 で実行したセッションが含まれる
- 新しい順（`timestamp` 降順）で返ること

---

## テストシナリオ 7: GET /history?sessionId= 詳細取得

### テスト 7-1: 正常系（自分のセッション）

1. シナリオ 1 のレスポンスから `sessionId` を取得
2. `tests/events/history-detail-event.json` の `sessionId` を実際の値に書き換えて実行

**期待される結果:** statusCode 200、`result` と `sourceDocuments` を含む完全なセッション情報

### テスト 7-2: 異常系（他ユーザーのセッション）

```json
{
  "httpMethod": "GET",
  "path": "/history",
  "queryStringParameters": {
    "sessionId": "シナリオ1で取得したsessionId"
  },
  "requestContext": {
    "authorizer": {
      "userId": "different-user-sub-999"
    }
  }
}
```

**期待される結果:** statusCode 404

---

## ユニットテスト実行

```bash
cd c:/Users/PH11364/devspace/EleKnowledge-AI
pip install -r tests/unit/requirements-test.txt
pytest tests/unit/ -v
```

**対象テストファイル:**
- `tests/unit/test_orchestrator.py` — validate_input, extract_user_id, build_source_documents
- `tests/unit/test_kb_search_citations.py` — write_citations（DynamoDB モック）
- `tests/unit/test_history.py` — 一覧・詳細取得ロジック
- `tests/unit/test_authorizer.py` — JWT 検証ロジック（RSA 鍵生成）

---

## テスト結果記録

| テスト項目 | 実行日時 | 結果 | 詳細 |
|-----------|--------|------|------|
| 正常系テスト | | | |
| 入力検証 - constructionNumber | | | |
| 入力検証 - troubleDescription | | | |
| Action 1: DB Search | | | |
| Action 2: KB Search1 | | | |
| Action 3: KB Search2 | | | |
| Action 4: KB Search3 | | | |
| DynamoDB セッションストア | | | |
| sourceDocuments 非空確認 | | | |
| GET /history 一覧 | | | |
| GET /history 詳細（正常） | | | |
| GET /history 詳細（他ユーザー） | | | |
| ユニットテスト全件 | | | |

## 次のステップ

すべてのテストが完了したら：
1. テスト結果を `docs/features/development/phase3-troubleshooting-spec.md` に記録
2. 本番環境への移行準備
3. パフォーマンス最適化（キャッシング、並列処理）