# 🤖 トラブルシューティング エージェント詳細仕様書

## ドキュメント情報

**バージョン:** 1.0.1 Draft  
**作成日:** 2026-01-26  
**ステータス:** PoC設計  
**対象:** Phase 3 トラブルシューティング機能

---

## 1. 概要

### 1.1 目的

現場トラブルに対して、過去の事例と技術資料から原因分析と対処方法を提案するBedrock Agent。

### 1.2 主要要件

- 原因候補を上位5件提示（信頼度スコア付き）
- 段階的な対処方法生成
- 平均応答時間 < 60秒
- PoC実施後に本実装へ移行

---

## 2. エージェント全体アーキテクチャ

### 2.1 システム構成

```
フロントエンド入力
  ↓
Orchestrator Lambda
  ├→ 入力検証・正規化
  └→ Bedrock Agent Manager起動
       ├→ [Action 1] DB検索 (DynamoDB)
       ├→ [Action 2] KB検索 (OpenSearch)
       ├→ [Action 3] KB検索 (OpenSearch)
       ├→ [Action 4] KB検索 (OpenSearch)
       └→ Claude 4.5Haiku 統合分析
       
出力: 原因候補 + 対処方法
```

### 2.2 主要コンポーネント

| コンポーネント | 技術 | 責務 |
|--------------|------|------|
| Orchestrator Lambda | Python 3.11 | 入力検証、エージェント制御、結果統合 |
| Action 1: DB Search | Python 3.11 + boto3 | 現場情報・昇降機仕様取得 |
| Action 2: KB Search1 | Python 3.11 | 現場仕様と同一機種でのトラブル検索 |
| Action 3: KB Search2 | Python 3.11 | ナレッジベース検索(トラブルシュートマニュアル) |
| Action 4: KB Search3 | Python 3.11 | ナレッジベース検索(C資料) |
| Claude 4.5Haiku | Bedrock | 統合分析・原因推定 |
Action 2はVer2で実装

---

## 3. 入出力仕様

### 3.1 入力（Request）

```typescript
interface TroubleshootingRequest {
  constructionNumber: string;      // 必須: 工事番号（半角英数8文字指定）
  troubleDescription: string;      // 必須: 不具合情報（5-2000文字）
  model?: string;                  // 可選: KE-LGなどリストから選択（一項目のみ選択可能）
  classification?: string;         // 可選: トラブル分類（機械的or電気的を選択）
  errorCode?: string;              // 可選: E001など（半角英数4文字指定）
  troubleOccurredAt?: string;      // ISO 8601
}
```

### 3.2 出力（Response）

```typescript
interface TroubleshootingResponse {
  analysisId: string;              // UUID
  constructionNumber: string;      // 工事番号（号機ごと）
  siteName: string;                // 現場名
  timestamp: string;
  
  analysis: {
    summary: string;               // 300文字以内
    estimatedCause: string;
    confidence: number;            // 0.0-1.0
  };
  
  possibleCauses: Array<{          // 最大5件
    rank: number;
    cause: string;
    probability: number;           // 0.0-1.0
    evidence: string[];
    references: Array<{documentName, relevance}>;
  }>;
  
  solutions: Array<{               // ステップバイステップ
    step: number;
    title: string;
    action: string;
    caution: string;
    estimatedTime: string;
    requiredTools: string[];
  }>;
  
  escalation: {
    required: boolean;
    reason?: string;
  };
}
```

---

## 4. Action Group仕様

### 4.1 Action 1: DB Search

**目的:** 現場情報、設備仕様を取得

**DynamoDBテーブル:**
- sites: constructionNumber (PK) → 現場番号

### 4.2 Action 2: KB Search1

**目的:** 現場仕様・トラブル情報と合致する類似事例を検索

**メタデータフィルター:**
- document: Trouble-Cases,Trouble-Reports
- model: KE-LG,CM-MAなど
- control-system: VFGLF,VFGHなど
---

### 4.3 Action 3: KB Search2

**目的:** エラーコード及び不具合情報からトラブルシュートマニュアルを検索

**メタデータフィルター:**
- document: Trouble-Cases,Trouble-Reports
- model: KE-LG,CM-MAなど
- control-system: VFGLF,VFGHなど
---

### 4.4 Action 4: KB Search3

**目的:** Action1~3で得た情報をもとにC資料を検索

**メタデータフィルター:**
- document: C資料
- model: KE-LG,CM-MAなど
- control-system: VFGLF,VFGHなど
---

## 5. プロンプト設計

### 5.1 System Prompt

```
あなたはトラブルシューティング専門家です。
電気設備に関する深い知識を持ち、複数の情報源を統合して
現場トラブルを迅速かつ正確に分析・解決します。

【職務】
1. トラブル情報を詳細に分析
2. 複数情報源から関連情報を収集
3. 類似事例との比較で原因推定
4. 実行可能な対処方法を段階的に提案
5. 必要に応じてエスカレーション判定

【原則】
- 安全性を最優先
- 推測を避ける
- 根拠を明示
- 確信度の低さを明記
```

### 5.2 Analysis Context Prompt

```
【現場情報】{site_info}
【トラブル】{trouble_description}, {symptom}, {error_code}
【参考資料】{Action2_results},{Action3_results},{Action4_results}

【出力要求】
- 原因候補（上位5つ）
- 各原因の確率（0-1.0）
- 根拠情報
- 段階的対処方法
- エスカレーション判定

【形式】JSON
```

---

## 6. PoC実装計画

### 6.1 PoC目標（1-2週間）

**実装:** Orchestrator, Action 1, Action 2,Action 3,Action 4, 統合テスト  
**テスト:** 3トラブル類型 × 2現場

### 6.2 成功基準

| 項目 | 基準 |
|------|------|
| エージェント起動 | ✅ 正常に起動・完了 |
| Action実行 | ✅ 両Action正常実行 |
| 分析出力 | ✅ 有効なJSON出力 |
| 応答時間 | ✅ < 60秒 |
| 信頼度 | ✅ 60%以上 |

### 6.3 本実装への移行

```
PoC完了（1-2週間）
  ↓
設計改善（3-5日）
  ↓
本実装開始（Phase 3）
```

---

## 7. API仕様

```
POST /troubleshooting/analyze
Authorization: Bearer {token}
Content-Type: application/json

Request: {constructionNumber, troubleDescription, ...}
Response: {analysisId, analysis, possibleCauses, solutions, escalation}
```

---

## 8. テスト戦略

- 単体テスト: Orchestrator, Action各Lambda
- 統合テスト: E2E フロー検証
- パフォーマンス: 応答時間 < 60秒

---

**作成日:** 2026-01-23  
**バージョン:** 1.0.0 Draft
