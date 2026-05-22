---
status: development
phase: 3
last-verified: 2026-05-22
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
interface SourceDocument {
  documentName: string;   // S3 オブジェクトキーのファイル名
  title: string | null;   // KB メタデータの title フィールド
  sourceUri: string;      // S3 presigned URL（有効期限 30 日）
  documentType: string;   // KB メタデータの document フィールド
  model: string;          // KB メタデータの model フィールド
  relevance: number;      // 検索スコア（0.0〜1.0）
}

interface TroubleshootingResult {
  sessionId: string;                 // セッション ID（UUID）。履歴取得 GET /history?sessionId= で使用
  result: string;                    // Bedrock Agent が生成した日本語テキスト（Markdown 形式）
  sourceDocuments: SourceDocument[]; // 参照文書リスト（DynamoDB セッションストア経由で確実に取得）
}
```

`result` は Agent が生成した自然言語テキスト。現場情報・対処手順・エラーコード解説などが含まれる。

`sourceDocuments` は DynamoDB セッションストア経由で取得する（action group KB: OCLVRJDMAH）。
`chunk.attribution.citations` からの引用も統合し URI で重複排除。`.md` ファイルは除外。

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
- [x] **sourceDocuments の引用取得を信頼性高く実装する**（DynamoDB セッションストア方式で実装済み、詳細は [docs/api/troubleshooting.md](../../api/troubleshooting.md)）

## 既知の制限事項

### sourceDocuments の非決定性（2026-05-21 確認）

`sourceDocuments` は Bedrock Agent EventStream の `chunk.attribution.citations` から取得しているが、**引用が返る頻度は非決定的**。

**原因:**

Agent `D6FAGLJPPO` には KB へのアクセス経路が2系統ある。

| 系統 | KB | 引用取得 | 使用頻度 |
|---|---|---|---|
| 直接紐付き KB | `UBDLEGMD6D`（技術資料）/ `HIFYJUGPOR`（マニュアル） | `chunk.attribution.citations` に出る | 非決定的（毎回とは限らない） |
| action group KB | `OCLVRJDMAH`（kb-search1/2/3 経由） | citations に**出ない** | 毎回呼ばれる |

Agent がどちらを使うかはその実行ごとに異なる。action group 経由の検索結果（毎回確実に使われる）は citations に含まれないため、`sourceDocuments` は空になることがある。

**後日対応候補:**

- **DynamoDB セッションストア案**: kb-search Lambda が session_id をキーに引用情報を DynamoDB に書き込み、orchestrator が読み出す。信頼性が高いが新テーブルが必要。
- **trace パース案**: `invoke_agent(enableTrace=True)` で action group の出力テキストを trace イベントから取得し、構造化引用データを埋め込んで解析する。新 AWS リソース不要だが実装が複雑。
