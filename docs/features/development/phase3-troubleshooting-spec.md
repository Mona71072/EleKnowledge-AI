# Phase 3: トラブルシューティング機能

> 本ドキュメントは [spec.md](../../../spec.md) §3.3.1 から切り出された Phase 3 トラブルシューティング機能の機能仕様です。
> 全体索引は [spec.md](../../../spec.md) を参照してください。
>
> **関連ドキュメント:**
> - PoC 詳細設計: [docs/agent-spec.md](../../agent-spec.md)
> - 実装ガイド: [phase3-troubleshooting-implementation-guide.md](phase3-troubleshooting-implementation-guide.md)
>
> **注:** Phase 3 の詳細仕様は、Phase 2 実装完了後に改めて策定します。現時点では概要・PoC 設計レベルの記載です。

## 目的

現場で発生したトラブルに対して、過去の事例と技術資料から原因分析と対処方法を提案

## 入力情報

```typescript
interface TroubleshootingInput {
  siteNumber: string;        // 現場番号
  troubleDescription: string; // トラブル内容
  equipmentModel?: string;    // 機器型番
  symptom?: string;          // 症状
  errorCode?: string;        // エラーコード
  photos?: File[];           // 現場写真
}
```

## 処理フロー

```
1. ユーザー入力（現場番号、トラブル内容）
   ↓
2. Bedrock Agent（メインオーケストレーター）起動
   ↓
3. Action Group 1: DB検索Lambda実行
   ├─ 現場番号から仕様データ取得
   │   └─ DynamoDB/RDS: sites テーブル
   ├─ 機器型番、設置環境、メンテナンス履歴
   └─ 過去のトラブル履歴
   ↓
4. Knowledge Base検索
   ├─ セマンティック検索で類似トラブル事例抽出
   │   └─ フィルター: document-type = "trouble-case"
   ├─ 関連技術資料の検索
   │   └─ フィルター: product = {該当製品}
   └─ トラブルシューティングマニュアル
   ↓
5. Claude 4による統合分析
   ├─ 入力情報の整理
   ├─ 類似事例との比較
   ├─ 原因推定（優先度順）
   └─ 対処方法の提案（ステップバイステップ）
   ↓
6. 結果出力
   ├─ トラブル分析サマリー
   ├─ 考えられる原因（Top 3）
   ├─ 推奨対処方法
   ├─ 参照資料
   └─ エスカレーション判断
```

## Bedrock Agent設定

```json
{
  "agentName": "troubleshooting-agent",
  "description": "現場トラブルの原因分析と対処方法提案",
  "foundationModel": "anthropic.claude-sonnet-4-20250514-v1:0",
  "instruction": "あなたは電気設備のトラブルシューティング専門家です...",
  "actionGroups": [
    {
      "actionGroupName": "db-search",
      "description": "現場情報とトラブル履歴の検索",
      "lambdaArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:db-search-lambda"
    }
  ],
  "knowledgeBases": [
    {
      "knowledgeBaseId": "KB_ELEKNOWLEDGE_001",
      "description": "技術資料とトラブル事例データベース"
    }
  ]
}
```

## DB検索Lambda (db-search-lambda)

```python
def lambda_handler(event, context):
    """
    Bedrock Agentから呼び出されるAction Group
    現場情報とトラブル履歴を検索
    """
    parameters = event['parameters']
    site_number = parameters[0]['value']
    
    # DynamoDBから現場情報取得
    site_info = get_site_info(site_number)
    
    # トラブル履歴取得
    trouble_history = get_trouble_history(site_number)
    
    return {
        'response': {
            'actionGroup': 'db-search',
            'function': 'get_site_info',
            'functionResponse': {
                'responseBody': {
                    'TEXT': {
                        'body': json.dumps({
                            'site_info': site_info,
                            'trouble_history': trouble_history
                        }, ensure_ascii=False)
                    }
                }
            }
        }
    }
```

## 出力フォーマット

```typescript
interface TroubleshootingResult {
  analysisId: string;
  siteNumber: string;
  timestamp: string;
  
  // トラブル分析
  analysis: {
    summary: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    estimatedCause: string[];
  };
  
  // 原因候補
  possibleCauses: Array<{
    cause: string;
    probability: number;
    evidence: string[];
    referenceDocuments: string[];
  }>;
  
  // 対処方法
  solutions: Array<{
    step: number;
    action: string;
    caution: string;
    estimatedTime: string;
    requiredTools: string[];
  }>;
  
  // 参照資料
  references: Array<{
    documentName: string;
    documentType: string;
    relevance: number;
  }>;
  
  // エスカレーション判断
  escalation: {
    required: boolean;
    reason?: string;
    department?: string;
  };
}
```

## UI画面

```
┌─────────────────────────────────────────────────────────┐
│ 🔧 トラブルシューティング                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 現場番号: [___________]  [検索]                         │
│                                                         │
│ トラブル内容:                                            │
│ ┌─────────────────────────────────────────────────┐     │
│ │                                                 │     │
│ │                                                 │     │
│ └─────────────────────────────────────────────────┘     │
│                                                         │
│ 機器型番: [___________]                                 │
│ エラーコード: [___________]                             │
│                                                         │
│ 📷 現場写真をアップロード [ファイル選択]                 │
│                                                         │
│                          [分析開始]                      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 📊 分析結果                                              │
│                                                         │
│ ✅ トラブル分析サマリー                                  │
│ 電源ユニットの故障が疑われます。                         │
│ 重要度: 🔴 高                                           │
│                                                         │
│ 🔍 考えられる原因（確率順）                              │
│ 1. ヒューズ断線（70%）                                  │
│    📄 メンテナンスマニュアル p.42                        │
│ 2. 過電流保護回路の誤作動（20%）                         │
│    📄 トラブル事例集 #123                               │
│ 3. 接触不良（10%）                                      │
│                                                         │
│ 🛠️ 推奨対処方法                                          │
│ Step 1: 電源を切断する [重要] (5分)                     │
│ Step 2: ヒューズを点検する (10分)                       │
│ Step 3: テスターで導通確認 (5分)                        │
│                                                         │
│ ⚠️ エスカレーション: 不要                                │
│                                                         │
│ [レポートダウンロード] [履歴に保存]                      │
└─────────────────────────────────────────────────────────┘
```
