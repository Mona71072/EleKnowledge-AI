# 🔧 トラブルシューティング エージェント実装ガイド

## ドキュメント情報

**バージョン:** 1.0.0  
**作成日:** 2026-01-26  
**ステータス:** 実装ガイド  
**対象:** PoC実装フェーズ

---

## 1. 概要

本ドキュメントは、`agent-spec.md` の仕様に基づいて、PoC実装を進めるための詳細ガイドです。

### 1.1 実装構成

```
┌─────────────────────────────────────────────────┐
│ Orchestrator Lambda                             │
│ ├─ 入力検証（constructionNumber, model等）     │
│ ├─ Bedrock Agent Manager起動                   │
│ └─ 結果統合・フロントエンド返却                │
└──────────────┬────────────────┬────────────────┘
               │                │
      ┌────────▼────────┐  ┌────▼──────────┐
      │ Action 1        │  │ Action 2/3/4  │
      │ DB Search       │  │ KB Search群   │
      │ (DynamoDB)      │  │ (OpenSearch)  │
      └─────────────────┘  └───────────────┘
```

---

## 2. Action 1: DB Search（現場情報取得）

### 2.1 入力パラメータ

```python
{
    "actionType": "db-search",
    "constructionNumber": "EQL0001",
    "filters": {
        "includeHistory": True,
        "maxResults": 1
    }
}
```

### 2.2 処理フロー

```python
def lambda_handler(event, context):
    """
    DB検索Action - 現場情報と設備仕様を取得
    """
    try:
        construction_number = extract_parameter(event, 'constructionNumber')
        
        # DynamoDB sites テーブルから現場情報取得
        site_info = dynamodb.query(
            TableName='sites',
            KeyConditionExpression='constructionNumber = :cn',
            ExpressionAttributeValues={':cn': construction_number}
        )
        
        # 返却データ構造
        result = {
            'constructionNumber': construction_number,
            'siteName': site_info['siteName'],
            'installedEquipment': [
                {
                    'sitesName': '現場名',
                    'model': 'KE-LG',
                    'controlSystem': 'VFGLF',
                    'installationDate': '2024-01-15',
                    'lastMaintenanceDate': '2026-01-20'
                }
            ],
            'contactPerson': {
                'name': '山田太郎',
                'phone': '090-xxxx-xxxx'
            }
        }
        
        return format_bedrock_response(result)
        
    except Exception as e:
        logger.error(f"DB Search Error: {str(e)}")
        return error_response("現場情報の取得に失敗しました")
```

### 2.3 DynamoDB テーブル設計

**sites テーブル:**
- PK: constructionNumber (String)
- Attributes: siteName, installedEquipment, contactPerson

---

## 3. Action 2/3/4: KB Search（ナレッジベース検索）

### 3.1 共通構造

3つのKB検索Actionの共通実装パターン：

```python
def kb_search_action(query, document_type, equipment_model, include_citation=True):
    """ナレッジベース検索の共通関数"""
    
    response = bedrock_client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 10,
                'overrideSearchType': 'SEMANTIC'
            }
        },
        text=query
    )
    
    # メタデータフィルター適用
    filtered_results = [
        r for r in response['retrievalResults']
        if matches_filters(r, document_type, equipment_model)
    ]
    
    # Citation形式で返却
    formatted_results = []
    for r in filtered_results:
        result_item = {
            'content': r['content'],
            'relevance': r['score'],
            'uri': r['location']['s3Location']['uri']
        }
        
        # citationが不要な場合はスキップ
        if include_citation:
            result_item['citation'] = {
                'source': r['metadata'].get('title', 'Unknown'),
                'relevance_score': r['score']
            }
        
        formatted_results.append(result_item)
    
    return formatted_results
```

### 3.2 Action 2: KB Search1（機種別トラブル検索）

**目的**: 同一機種のトラブル事例検索

**メタデータフィルター:**
- document: Trouble-Cases, Trouble-Reports
- model: KE-LG, CM-MAなど

### 3.3 Action 3: KB Search2（トラブルシュートマニュアル検索）

**目的**: エラーコードと不具合情報からマニュアルを検索

**特徴:**
- メタデータが未整備のため、フィルターなしでKB全体を検索
- Citationは取得しない（参考情報としてのみ使用）

```python
def action_3_kb_search2(event, context):
    """
    Action 3: トラブルシュートマニュアル検索
    メタデータ未整備のため全文検索を実施
    """
    
    error_code = extract_parameter(event, 'errorCode')
    trouble_description = extract_parameter(event, 'troubleDescription')
    
    # クエリ生成
    query = f"エラーコード {error_code} {trouble_description} トラブルシュート 対処方法"
    
    # KB全体から検索（メタデータフィルターなし）
    response = bedrock_client.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 5,
                'overrideSearchType': 'SEMANTIC'
            }
        },
        text=query
    )
    
    # 最上位1-3件のみ返却（citationなし）
    results = response['retrievalResults'][:3]
    
    return format_bedrock_response({
        'action': 'kb_search2',
        'query': query,
        'results': [
            {
                'content': r['content'],
                'relevance': r['score']
            }
            for r in results
        ]
    })
```

### 3.4 Action 4: KB Search3（C資料検索）

**目的**: 詳細な技術資料（C資料）を検索

**メタデータフィルター:**
- document: C資料
- model: model
- control-system: control_system

---

## 4. Orchestrator Lambda実装仕様

### 4.1 エンドポイント

```
POST /troubleshooting/analyze
Authorization: Bearer {cognito_token}
```

### 4.2 実装フロー

```python
def lambda_handler(event, context):
    """Orchestrator Lambda - エージェント全体制御"""
    
    try:
        # 1. リクエスト解析
        body = json.loads(event.get('body', '{}'))
        
        # 2. 入力検証
        validate_input(
            construction_number=body['constructionNumber'],
            trouble_description=body['troubleDescription'],
            model=body.get('model'),
            error_code=body.get('errorCode')
        )
        
        # 3. Bedrock Agent Manager起動
        agent_response = bedrock_client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=str(uuid.uuid4()),
            inputText=format_agent_input(body)
        )
        
        # 4. 結果統合
        result = parse_agent_response(agent_response)
        
        # 5. フロントエンドに返却
        return {
            'statusCode': 200,
            'body': json.dumps(result, ensure_ascii=False),
            'headers': {'Content-Type': 'application/json; charset=utf-8'}
        }
        
    except ValidationError as e:
        return error_response(400, str(e))
    except Exception as e:
        logger.error(f"Orchestrator Error: {str(e)}")
        return error_response(500, "分析処理中にエラーが発生しました")
```

### 4.3 入力検証ルール

```python
VALIDATION_RULES = {
    'constructionNumber': {
        'required': True,
        'pattern': r'^[A-Za-z0-9]{8}$',
        'message': '工事番号は半角英数8文字で指定してください'
    },
    'troubleDescription': {
        'required': True,
        'min_length': 5,
        'max_length': 2000,
        'message': '不具合情報は5～2000文字で入力してください'
    },
    'model': {
        'required': False,
        'allowed_values': ['KE-LG', 'KM-LD', 'CM-MA', 'ME-CH'],
        'message': '指定されたモデルのみ選択可能です'
    },
    'errorCode': {
        'required': False,
        'pattern': r'^[A-Z0-9]{4}$',
        'message': 'エラーコードは半角英数4文字で指定してください'
    }
}
```

---

## 5. Bedrock Agent設定

```json
{
  "agentName": "troubleshooting-agent",
  "foundationModel": "anthropic.claude-haiku-4.5-20250123",
  "actionGroups": [
    {
      "actionGroupName": "db-search",
      "lambdaArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:db-search-action"
    },
    {
      "actionGroupName": "kb-search-1",
      "lambdaArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:kb-search1-action"
    },
    {
      "actionGroupName": "kb-search-2",
      "lambdaArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:kb-search2-action"
    },
    {
      "actionGroupName": "kb-search-3",
      "lambdaArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:kb-search3-action"
    }
  ]
}
```

---

## 6. PoC実装スケジュール

### 6.1 Week 1: 基盤構築

- [ ] Orchestrator Lambda実装
- [ ] DB Search Lambda実装
- [ ] DynamoDB接続テスト
- [ ] Bedrock Agent設定

### 6.2 Week 2: Action実装・統合

- [ ] KB Search1/2/3 Lambda実装
- [ ] E2Eテスト（統合テスト）
- [ ] パフォーマンス測定（< 60秒確認）
- [ ] UAT実施・ドキュメント整備

### 6.3 成功基準

| 項目 | 基準 |
|------|------|
| エージェント起動 | 正常に起動・完了 |
| Action実行 | 全Action正常実行 |
| 分析出力 | 有効なJSON出力 |
| 応答時間 | < 60秒 |
| 信頼度スコア | 60%以上 |
| 原因候補 | 5件提示 |

---

## 7. テスト用サンプルデータ

### 7.1 テストケース

**TC-001: 正常系**
```json
{
  "constructionNumber": "SITE0001",
  "troubleDescription": "昇降機が途中で停止してしまう",
  "model": "KE-LG",
  "errorCode": "E001"
}
```

**TC-002: バリデーションエラー**
```json
{
  "constructionNumber": "INVALID",
  "troubleDescription": "xxx",
  "model": "UNKNOWN"
}
```

---

**作成日:** 2026-01-26  
**バージョン:** 1.0.0