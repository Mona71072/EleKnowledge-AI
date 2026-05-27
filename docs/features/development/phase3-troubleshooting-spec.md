---
status: development
phase: 3
last-verified: 2026-05-26
related-code: lambda/troubleshooting/, frontend/src/app/troubleshooting/
---

# Phase 3: トラブルシューティング機能 — Ver 1.1 仕様

> 本ドキュメントは [spec.md](../../../spec.md) §3.3.1 から切り出された Phase 3 トラブルシューティング機能の機能仕様です。
> 全体索引は [spec.md](../../../spec.md) を参照してください。
>
> **関連ドキュメント:**
> - エージェント詳細仕様: [docs/agent-spec.md](../../agent-spec.md)
> - API 仕様: [docs/api/troubleshooting.md](../../api/troubleshooting.md)
> - 実装ガイド: [phase3-troubleshooting-implementation-guide.md](phase3-troubleshooting-implementation-guide.md)
> - 処理シーケンス図: [docs/features/production/troubleshooting-sequence.md](../production/troubleshooting-sequence.md)
>
> **PoC 検証状況（2026-05-21）:** E2E テスト完了。orchestrator → Bedrock Agent → 4 action groups の全フロー動作確認済み。

## バージョン履歴

| Ver | 日付 | 変更概要 |
|-----|------|----------|
| 1.0 | 2026-05-22 | PoC 完了時点の仕様（DynamoDB セッションストア方式で引用取得を信頼性向上） |
| **1.1** | **2026-05-26** | **条件分岐フロー・機種優先順位・source_action タグ・UIバッジ対応を追加** |

---

## 目的

現場で発生したトラブルに対して、過去の事例と技術資料から原因分析と対処方法を提案する。

---

## 入力情報

```typescript
interface TroubleshootingInput {
  constructionNumber?: string; // 任意: 工事番号（半角英数8文字）
  model?: string;              // 任意: KE-LG / KM-LD / CM-MA / ME-CH
  troubleDescription: string;  // 必須: 不具合内容（5〜2000文字）
  errorCode?: string;          // 任意: エラーコード（半角英数字3文字）
  // constructionNumber か model のいずれかは必須
}
```

---

## 処理フロー（Ver 1.1）

```
1. ユーザー入力（工事番号・機種・不具合内容・エラーコード）
   ↓
2. POST /analyze → Orchestrator Lambda
   ├─ 入力バリデーション
   ├─ DynamoDB セッション初期化
   └─ Bedrock Agent invoke（ReAct ループ開始）
   ↓
3. [条件付き] Action 1 — GetSiteInfo (db-search Lambda)
   └─ 工事番号がある場合のみ実行
   └─ DynamoDB sites テーブル → 現場名・機種・制御システム・担当者
   └─ 取得した機種を以降の検索で優先使用

   [機種確定: ①取得値 → ユーザ入力値 → フィルターなし]

4. Action 2 — searchTroubleCases (kb-search1 Lambda)
   └─ クエリ: 不具合内容
   └─ フィルター: control-system=VFGLF + エラーコード（あれば）★ Ver 1.1 temporary
   └─ KB Trouble-Cases/Trouble-Reports 上位5件
   └─ write_citations(source_action="trouble_cases") → DynamoDB

5. Action 3 — searchTroubleshootManuals (kb-search2 Lambda)
   └─ クエリ: 不具合内容
   └─ フィルター: control-system=VFGLF + エラーコード（あれば）★ Ver 1.1 temporary（フィルターなし→あり）
   └─ KB マニュアル 上位3件
   └─ write_citations(source_action="manual") → DynamoDB ★ Ver 1.1 新規追加

6. Action 4 — searchCMaterialDocs (kb-search3 Lambda)
   └─ クエリ: ②③の結果から Agent が抽出したキーワード ★ Ver 1.1（不具合内容→抽出キーワード）
   └─ フィルター: 機種（確定値）+ document=C資料
   └─ KB C資料 上位5件
   └─ write_citations(source_action="c_material") → DynamoDB

7. Claude Haiku による観点別統合分析・回答生成（★ Ver 1.1 構成変更）
   └─ 【サイト情報】【トラブル事例】【マニュアル】【C資料】【推奨アクション】の5観点

8. Orchestrator 後処理
   ├─ DynamoDB から source_action 付き引用情報を取得
   ├─ S3 presigned URL 生成（30日有効）
   └─ save_session_result → DynamoDB
```

---

## AWS リソース

| リソース | 値 |
|---|---|
| Bedrock Agent ID | `D6FAGLJPPO` |
| Agent Alias | `TSTALIASID`（DRAFT）|
| Foundation Model | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Knowledge Base ID | `OCLVRJDMAH` |
| DynamoDB: sessions | `troubleshooting-sessions`（TTL: 30日） |
| DynamoDB: sites | `sites`（PK: constructionNumber） |
| API Gateway | `troubleshooting-api`（chat-api とは別 Gateway） |

---

## Lambda 構成

| Lambda 関数名 | 役割 | Bedrock Agent 呼び出し形式 |
|---|---|---|
| `troubleshooting-orchestrator` | エントリーポイント・セッション管理・後処理 | API Gateway から直接 |
| `troubleshooting-db-search` | DynamoDB から現場情報取得 | apiSchema (POST /site-info) |
| `troubleshooting-kb-search1` | トラブル事例・報告書 KB 検索 | functionSchema (`searchTroubleCases`) |
| `troubleshooting-kb-search2` | マニュアル KB 検索 | functionSchema (`searchTroubleshootManuals`) |
| `troubleshooting-kb-search3` | C資料 KB 検索 | functionSchema (`searchCMaterialDocs`) |

---

## DynamoDB sites テーブルスキーマ

| フィールド | 型 | 説明 |
|---|---|---|
| `constructionNumber` | String (PK) | 工事番号（例: `EIK54801`） |
| `sitesName` | String | 現場名 |
| `sitesNumber` | String | 現場番号 |
| `model` | String | 機種名（例: `KE-LG`） |
| `controlSystem` | String | 制御システム名（例: `VFGLF`） |
| `constructionRep` | String | 担当者名 |

---

## 出力フォーマット（Ver 1.1）

```typescript
interface SourceDocument {
  documentName: string;     // S3 オブジェクトキーのファイル名
  title: string | null;     // KB メタデータの title フィールド
  sourceUri: string;        // S3 presigned URL（有効期限 30 日）
  documentType: string;     // KB メタデータの document フィールド
  model: string;            // KB メタデータの model フィールド
  relevance: number;        // 検索スコア（0.0〜1.0）
  source_action: string;    // ★ Ver 1.1 追加: "trouble_cases" | "manual" | "c_material"
}

interface TroubleshootingResult {
  sessionId: string;
  result: string;                    // Markdown 形式・観点別構成（★ Ver 1.1 変更）
  sourceDocuments: SourceDocument[]; // source_action 付き（★ Ver 1.1 変更）
}
```

---

## UI 画面（Ver 1.1）

```
┌─────────────────────────────────────────────────────────┐
│ ← トラブルシューティング                                 │
├─────────────────────────────────────────────────────────┤
│ トラブル情報を入力                                       │
│                                                         │
│ 工事番号: [___________]（半角英数8文字・任意）           │
│ 機種: [選択してください v]（任意）                       │
│ エラーコード: [___________]（任意）                      │
│                                                         │
│ 不具合情報 *                                            │
│ ┌─────────────────────────────────────────────────┐     │
│ │                                                 │     │
│ └─────────────────────────────────────────────────┘     │
│                                    0 / 2000             │
│                                                         │
│           [  トラブルを分析する  ]                       │
├─────────────────────────────────────────────────────────┤
│ 分析結果                          [もう一度分析する]     │
│                                                         │
│ ▼ サイト情報（工事番号入力時のみ表示）                   │
│ ▼ トラブル事例                                          │
│ ▼ マニュアル                                            │
│ ▼ C資料                                                │
│ ▼ 推奨アクション                                        │
│                                                         │
│ 参照ドキュメント                                         │
│ ┌──────────────────────────────────────┐               │
│ │ [② トラブル事例] KE-LG_trouble.pdf  │               │
│ │ [③ マニュアル  ] troubleshoot_v2.pdf│               │
│ │ [④ C資料      ] C-material_KE.pdf  │               │
│ └──────────────────────────────────────┘               │
│                            [新しいトラブルを入力]        │
└─────────────────────────────────────────────────────────┘
```

### source_action バッジ仕様

| source_action | バッジ表示 | 対応アクション |
|---|---|---|
| `trouble_cases` | `② トラブル事例` | kb-search1 |
| `manual` | `③ マニュアル` | kb-search2 |
| `c_material` | `④ C資料` | kb-search3 |

---

## 今後の対応（本実装フェーズ）

- [ ] Bedrock Agent システムプロンプトを Ver 1.1 仕様に更新（§6.1 of agent-spec.md）
- [ ] kb-search1/2/3 Lambda に `source_action` タグを追加
- [ ] kb-search2 Lambda に `write_citations()` を新規実装
- [ ] orchestrator Lambda の `build_source_documents()` を更新
- [ ] Frontend に ②③④ バッジを実装
- [ ] `TSTALIASID`（DRAFT）を本番用バージョン alias に切り替え
- [ ] KB データ（Trouble-Cases / C資料）の整備
- [ ] レスポンスタイムアウト対策（API Gateway 29 秒上限、非同期化の検討）
- [ ] 本ドキュメントを `docs/features/production/` に昇格（`git mv`）
- [x] sourceDocuments の引用取得を DynamoDB セッションストア方式で信頼性向上（PoC 完了）
- [x] Bedrock Agent E2E フロー動作確認（2026-05-21）
