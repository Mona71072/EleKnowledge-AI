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

## 次のステップ

すべてのテストが完了したら：
1. テスト結果を roadmap.md に記録
2. 本番環境への移行準備
3. パフォーマンス最適化（キャッシング、並列処理）