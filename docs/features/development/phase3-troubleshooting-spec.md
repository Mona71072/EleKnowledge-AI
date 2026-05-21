---
status: development
phase: 3
last-verified: 2026-05-21
related-code: lambda/troubleshooting/, frontend/src/app/troubleshooting/
---

# Phase 3: トラブルシューティング機能

> 本ドキュメントは [spec.md](../../../spec.md) §3.3.1 から切り出された Phase 3 トラブルシューティング機能の機能仕様です。
> 全体索引は [spec.md](../../../spec.md) を参照してください。
>
> **関連ドキュメント:**
> - API 仕様: [docs/api/troubleshooting.md](../../api/troubleshooting.md)
> - 実装ガイド: [phase3-troubleshooting-implementation-guide.md](phase3-troubleshooting-implementation-guide.md)
>
> **PoC 検証状況（2026-05-21）:** E2E テスト完了。orchestrator → Bedrock Agent → 4 action groups の全フロー動作確認済み。

## 目的

現場で発生したトラブルに対して、過去の事例と技術資料から原因分析と対処方法を提案

## 入力情報

```typescript
interface TroubleshootingInput {
  constructionNumber?: string; // 工事番号（半角英数8文字）
  model?: string;              // 機種名（KE-LG / KM-LD / CM-MA / ME-CH）
  troubleDescription: string;  // 不具合内容（5〜2000文字）
  errorCode?: string;          // エラーコード（半角英数4文字）
  // constructionNumber か model のどちらかは必須
}
```

## 処理フロー

```
1. ユーザー入力（工事番号、不具合情報）
   ↓
2. POST /troubleshooting/analyze → troubleshooting-orchestrator Lambda
   ├─ 入力バリデーション
   └─ Bedrock Agent invoke (D6FAGLJPPO / TSTALIASID)
   ↓
3. Action 1 — GetSiteInfo (db-search Lambda)
   └─ DynamoDB sites テーブル → 現場名・機種・制御システム・担当者
   ↓
4. Action 2 — KB Search1 (kb-search1 Lambda)
   └─ KB (OCLVRJDMAH) セマンティック検索
       └─ フィルター: document = Trouble-Cases or Trouble-Reports, model, control-system
   ↓
5. Action 3 — KB Search2 (kb-search2 Lambda)
   └─ KB (OCLVRJDMAH) トラブルシュートマニュアル全文検索（フィルターなし）
   ↓
6. Action 4 — KB Search3 (kb-search3 Lambda)
   └─ KB (OCLVRJDMAH) セマンティック検索
       └─ フィルター: document = C資料, model, control-system
   ↓
7. claude-haiku-4-5 による統合分析・回答生成
   └─ 現場情報 + 検索結果 → 日本語テキスト形式の対処手順
```

## AWS リソース（PoC 環境）

| リソース | 値 |
|---------|-----|
| Bedrock Agent ID | `D6FAGLJPPO` |
| Agent Alias | `TSTALIASID`（DRAFT）|
| Foundation Model | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Knowledge Base ID | `OCLVRJDMAH` |
| DynamoDB テーブル | `sites` |
| API Gateway | `s8dbirs0m6`（chat-api と共用） |

## Lambda 構成

| Lambda 関数名 | 役割 | Bedrock Agent での呼び出し形式 |
|-------------|------|-------------------------------|
| `troubleshooting-orchestrator` | エントリーポイント。バリデーション + Agent invoke | API Gateway から直接呼び出し |
| `troubleshooting-db-search` | DynamoDB から現場情報取得 | apiSchema (POST /site-info) |
| `troubleshooting-kb-search1` | トラブル事例・報告書検索 | functionSchema (`searchTroubleCases`) |
| `troubleshooting-kb-search2` | マニュアル全文検索 | functionSchema (`searchTroubleshootManuals`) |
| `troubleshooting-kb-search3` | C資料（詳細技術資料）検索 | functionSchema (`searchCMaterialDocs`) |

## DynamoDB sites テーブルスキーマ

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `constructionNumber` | String (PK) | 工事番号（例: `EIK54801`） |
| `sitesName` | String | 現場名 |
| `sitesNumber` | String | 現場番号 |
| `model` | String | 機種名（例: `KE-LG`） |
| `controlSystem` | String | 制御システム名（例: `VFGLF`） |
| `constructionRep` | String | 担当者名 |

## 出力フォーマット

```typescript
interface TroubleshootingResult {
  result: string; // Bedrock Agent が生成した日本語テキスト（Markdown 形式）
}
```

レスポンスは構造化 JSON ではなく、Agent が生成した自然言語テキスト。
現場情報・対処手順・エラーコード解説などが含まれる（フォーマットは Agent が自律的に決定）。

## UI 画面

実装済み: `frontend/src/app/troubleshooting/page.tsx`

```
┌─────────────────────────────────────────────────────────┐
│ ← トラブルシューティング                                 │
├─────────────────────────────────────────────────────────┤
│ トラブル情報を入力                                       │
│ 工事番号か機種のどちらかは必須                           │
│                                                         │
│ 工事番号: [___________]（半角英数8文字）                 │
│ 機種: [選択してください v]                               │
│ エラーコード: [___________]（任意）                      │
│                                                         │
│ 不具合情報 *                                            │
│ ┌─────────────────────────────────────────────────┐     │
│ │                                                 │     │
│ └─────────────────────────────────────────────────┘     │
│                                    0 / 2000             │
│                                                         │
│           [  トラブルを分析する  ]                       │
│                （最大60秒）                              │
├─────────────────────────────────────────────────────────┤
│ 分析結果                          [もう一度分析する]     │
│                                                         │
│ （Bedrock Agent の回答テキスト）                         │
│                                                         │
│            [新しいトラブルを入力]                        │
└─────────────────────────────────────────────────────────┘
```

## 今後の対応（本実装フェーズ）

- [ ] Bedrock Agent 設定・アクション設定を `phase3-template.yaml` に IaC 化
- [ ] `TSTALIASID`（DRAFT）を本番用バージョン alias に切り替え
- [ ] KB データ（Trouble-Cases / C資料）の整備
- [ ] レスポンスタイムアウト対策（API Gateway 29 秒上限、非同期化の検討）
- [ ] 本ドキュメントを `docs/features/production/` に昇格
