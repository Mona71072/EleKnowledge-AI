# Bedrock Agent カスタムオーケストレーション Lambda レスポンス形式

## 概要

Bedrock Agent がカスタムオーケストレーション Lambda を使用する場合、Lambda が返すレスポンスは特定の JSON 形式である必要があります。

## レスポンス形式

### 基本構造

```json
{
  "messageVersion": "1.0",
  "response": {
    "actionGroup": "string",
    "apiPath": "string", 
    "httpMethod": "string",
    "httpStatusCode": 200,
    "responseBody": {
      "TEXT": {
        "body": "string"
      }
    }
  }
}
```

### フィールド説明

| フィールド | 型 | 説明 |
|-----------|-----|------|
| messageVersion | string | メッセージバージョン（常に "1.0"） |
| response | object | レスポンスオブジェクト |
| actionGroup | string | アクショングループ名 |
| apiPath | string | API パス（例：`/search`） |
| httpMethod | string | HTTP メソッド（GET, POST など） |
| httpStatusCode | number | HTTP ステータスコード |
| responseBody | object | レスポンスボディ |
| responseBody.TEXT | object | テキスト形式のレスポンス |
| responseBody.TEXT.body | string | 実際のレスポンステキスト |

## 実装例

### 成功レスポンス

```json
{
  "messageVersion": "1.0",
  "response": {
    "actionGroup": "troubleshooting-actions",
    "apiPath": "/analyze",
    "httpMethod": "POST",
    "httpStatusCode": 200,
    "responseBody": {
      "TEXT": {
        "body": "トラブル分析が完了しました。原因は電源接続の不具合と考えられます。"
      }
    }
  }
}
```

### エラーレスポンス

```json
{
  "messageVersion": "1.0",
  "response": {
    "actionGroup": "troubleshooting-actions",
    "apiPath": "/analyze",
    "httpMethod": "POST",
    "httpStatusCode": 400,
    "responseBody": {
      "TEXT": {
        "body": "入力データが不正です：工事番号は8文字である必要があります。"
      }
    }
  }
}
```

## Orchestrator Lambda での実装

```python
def format_orchestration_response(action_group, api_path, http_method, status_code, body_text):
    """
    Bedrock Agent カスタムオーケストレーション用レスポンスを生成
    
    Args:
        action_group: アクショングループ名
        api_path: API パス
        http_method: HTTP メソッド
        status_code: HTTPステータスコード
        body_text: レスポンステキスト
        
    Returns:
        Bedrock Agent 互換のレスポンス JSON
    """
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": status_code,
            "responseBody": {
                "TEXT": {
                    "body": body_text
                }
            }
        }
    }
```

## 注意点

1. **messageVersion は常に "1.0"** - 変更しないこと
2. **必須フィールド** - すべてのフィールドが必須
3. **ステータスコード** - 400 系のエラーでもレスポンス形式は同じ
4. **文字エンコーディング** - UTF-8 で返すこと
5. **JSON 形式** - 必ず有効な JSON 形式であること

## トラブルシューティング

### エラー：「Orchestration Lambda response could not be processed」

以下を確認：
- messageVersion が "1.0" か
- すべての必須フィールドが含まれているか
- 返却する値が有効な JSON か
- responseBody が正しく構造化されているか