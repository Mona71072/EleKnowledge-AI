# トラブルシューティング エージェント ガイド

## 目次

1. [概要](#概要)
2. [Lambdaエラーハンドリング](#lambdaエラーハンドリング)
3. [環境変数管理](#環境変数管理)
4. [テストケース](#テストケース)
5. [参考情報](#参考情報)

---

## 概要

このドキュメントは、トラブルシューティングエージェントのテスト失敗を解決するためのガイドです。Lambda関数のエラーハンドリング、環境変数管理、テストケースの改善ポイントをまとめています。

---

## Lambdaエラーハンドリング

### 1. タイムアウト設定の確認

- **Orchestrator Lambda**: 
  - 現在のタイムアウト: 60秒
  - 改善ポイント: 
    - 各Actionの処理時間を見積もり、適切なタイムアウト値を設定
    - デフォルト値ではなく、SAMテンプレートで明示に指定

```yaml
# infrastructure/sam/phase3-template.yaml
TroubleshootingOrchestratorFunction:
  Type: AWS::Serverless::Function
  Properties:
    Timeout: 90 # 例: 90秒に延長
```

### 2. ログの粒度向上

- 現在のログ: エラーメッセージのみ
- 改善ポイント:
  - 入力パラメータのログ出力（個人情報はマスク）
  - 各処理ステップの開始/終了ログ
  - エラースタックトレースの削除（.clinerules準拠）

```python
# Lambda関数に追加
logger.info(f"Received request: {json.dumps(event, default=str)}")
logger.info(f"Site info retrieved: {site_info}")
```

### 3. 環境変数のSecrets Managerへの移行

- 現在の状態: 環境変数に直接設定
- 改善ポイント:
  - Secrets Managerに`troubleshooting/config`として保存
  - Lambda関数で動的に取得

```python
# Lambda関数に追加
secrets_client = boto3.client('secretsmanager')
config = json.loads(secrets_client.get_secret_value(SecretId='troubleshooting/config')['SecretString'])
AGENT_ID = config['AGENT_ID']
```

---

## 環境変数管理

- **.env.example** を更新

```env
# .env.example
AGENT_ID=
AGENT_ALIAS_ID=
SITES_TABLE_NAME=
KB_ID=
```

- Secrets Manager に登録

```bash
aws secretsmanager create-secret \
  --name troubleshooting/config \
  --secret-string '{"AGENT_ID":"D6FAGLJPPO","AGENT_ALIAS_ID":"YOUR_ALIAS_ID","SITES_TABLE_NAME":"sites","KB_ID":"HIFYJUGPOR"}'
```

---

## テストケース

### 正常系

```json
{
  "constructionNumber": "SITE0001",
  "troubleDescription": "昇降機が途中で停止する",
  "model": "KE-LG",
  "errorCode": "E001"
}
```

### 異常系

```json
{
  "constructionNumber": "INVALID",
  "troubleDescription": "x",
  "model": "UNKNOWN"
}
```

---

## 参考情報

- [AWS Lambdaベストプラクティス](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Bedrock Agent カスタムオーケストレーション](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-custom-orchestration.html)
- [.clinerules セキュリティルール](../.clinerules)

**作成日:** 2026-02-04
**バージョン:** 1.0.0