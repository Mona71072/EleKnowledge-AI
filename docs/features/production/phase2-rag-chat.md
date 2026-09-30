---
status: draft
phase: 2
last-verified: 2026-04-24
related-code: frontend/src/app/, lambda/rag/, lambda/chat/, infrastructure/sam/phase2-template.yaml
---

# Phase 2: RAGチャット機能 — 旧仕様（再検証中）

> [!WARNING]
> **本書は現行仕様の正本ではない。** Knowledge Base、メタデータ、RAG 処理、プロンプト、`SearchFilters` / `SourceDocument` は現行コードと照合が完了していない。過去に記載された KB 名・ID・メタデータキーを現行環境へ適用しないこと。
>
> **現行の契約・挙動を確認する参照先:**
> - API 契約: [`docs/api/rag.md`](../../api/rag.md) / [`docs/api/chat.md`](../../api/chat.md)
> - 聞き返し・頁候補・本命優先: [`docs/impl-log-2026-07-29-clarify-and-page.md`](../../impl-log-2026-07-29-clarify-and-page.md)
> - データモデル（chatlogs）: [`docs/data-model.md`](../../data-model.md)
> - コード↔docs 運用: [`docs/ops-ai-driven-dev.md`](../../ops-ai-driven-dev.md)
>
> 本書の全面改訂は RAG 仕様の見直し時に別途行う。現行の `responseType` / `pageCandidates` /
> 失敗一覧（`/admin/failures`）などは**ここには書かない**（上記正本を見る）。

> 最終検証: 2026-09-30 — frontmatter / 索引と開発環境の Phase 2 stack・モデル設定の存在を部分照合。本文の全機能・RAG E2E は未検証。

> 本ドキュメントは [spec.md](../../../spec.md) §3.2 から切り出された Phase 2 の機能仕様です。
> 全体索引は [spec.md](../../../spec.md) を参照してください。

## RAGチャット画面

**主要機能:**
- リアルタイムチャット
- チャット履歴表示
- セッション管理
- 引用文書表示
- 文書ダウンロード
- フィードバック機能（👍👎）
- メタデータフィルター検索

**UI構成:**
```
┌─────────────────────────────────────────────────────────┐
│ 📚 RAGチャット                    👤 user@example.com  │
├──────────┬──────────────────────────────────────────────┤
│ サイドバー │ メインチャット画面                           │
│          │                                             │
│ 💬 新規   │ 🤖 EleKnowledgeへようこそ！               │
│          │    技術資料を検索して質問にお答えします       │
│ 📚 履歴   │                                             │
│ session1 │ 👤 ユーザー: ○○の配線方法は？               │
│ session2 │                                             │
│ session3 │ 🤖 AI: ○○の配線方法は以下の通りです...      │
│          │    📄 配線マニュアルv2.pdf                   │
│ 🔍 検索   │    📄 技術仕様書.pdf                         │
│ フィルター │    👍 👎                                    │
│          │                                             │
│           │ 💬 質問を入力... [送信]                     │
│           │                                             │
└──────────┴──────────────────────────────────────────────┘
```

**機能詳細:**

### チャットインターフェース
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations?: string[];
  sourceDocuments?: SourceDocument[];
  feedback?: 'good' | 'bad' | null;
}

interface SourceDocument {
  documentName: string;
  sourceUri: string;
  documentType: string;
  product: string;
  model: string;
}
```

### セッション管理
```typescript
interface ChatSession {
  sessionId: string;
  title: string;
  createdAt: string;
  lastMessageTime: string;
  messageCount: number;
  messages: ChatMessage[];
}
```

### メタデータフィルター
```typescript
interface SearchFilters {
  documentType?: 'manual' | 'policy' | 'report' | 'specification';
  product?: string;
  model?: string;
  category?: string;
}
```

## Knowledge Base設定

**構成:**
- **Knowledge Base ID:** KB_ELEKNOWLEDGE_001
- **Embedding Model:** Amazon Titan Embeddings G1
- **Vector Database:** OpenSearch Serverless
- **データソース:** S3バケット (eleknowledge-documents)

**ドキュメント構造:**
```
s3://eleknowledge-documents/
├── C-manual/
├── D-manual/
├── EA-manual/
├── GM/
├── Installation-Notebooks/
├── Installation-Standards/
├── S-manual
└── yellow-book
```

**メタデータスキーマ:**
```json
{
  "metadataAttributes": {
    "title": {
      "value": {
        "type": "STRING",
        "stringValue": "三菱エレベーター AXIEZ-LINKs P形"
      },
      "includeForEmbedding": true
    },
    "document": {
      "value": {
        "type": "STRING",
        "stringValue": "C資料"
      },
      "includeForEmbedding": true
    },
    "product": {
      "value": {
        "type": "STRING",
        "stringValue": "エレベーター"
      },
      "includeForEmbedding": true
    },
    "model": {
      "value": {
        "type": "STRING",
        "stringValue": "KE-LG"
      },
      "includeForEmbedding": true
    },
    "control-system": {
      "value": {
        "type": "STRING",
        "stringValue": "VFGLF"
      },
      "includeForEmbedding": true
    },
    "keywords": {
      "value": {
        "type": "STRING_LIST",
        "stringListValue": [
          "AXIEZ-LINKs",
          "P形",
          "据付場用図",
          "機械部分",
          "標準図",
          "巻上機",
          "調速機",
          "非常止め",
          "ガイドシュー",
          "ドア装置",
          "釣合オモリ",
          "レール",
          "緩衝器",
          "ロープ掛け"
        ]
      },
      "includeForEmbedding": true
    },
    "description": {
      "value": {
        "type": "STRING",
        "stringValue": "AXIEZ-LINKs P形エレベーター（KE-LG/KE-LGM：P7～15）のVFGLF方式における据付場用標準図の機種別表。機械部分の据付調整に必要な図面番号と仕様を網羅した技術資料。"
      },
      "includeForEmbedding": true
    }
  }
}
```

## RAG処理フロー

**処理ステップ:**
```
1. ユーザー質問入力
   ↓
2. 入力検証・サニタイゼーション
   ↓
3. セッション管理
   ├─ 新規セッション: タイトル生成
   └─ 既存セッション: 履歴取得
   ↓
4. メタデータフィルター適用
   ↓
5. Knowledge Base検索（ベクトル検索）
   ├─ Top 10件の関連文書取得
   ↓
6. 生成モデルによる回答生成（この旧図はモデルを特定しない。開発環境の確認値は [運用ランブック](../../ops-runbook.md)を参照）
   ├─ プロンプト: システム指示 + 検索結果 + 履歴 + 質問
   ├─ Temperature: 0.3（安定性重視）
   └─ Max tokens: 4096
   ↓
7. 引用情報抽出
   ├─ 文書名
   ├─ 文書URI
   ↓
8. DynamoDB保存
   ├─ ユーザーメッセージ
   └─ AIメッセージ（引用付き）
   ↓
9. フロントエンド表示
   ├─ 回答テキスト
   ├─ 引用文書リスト
   ├─ ダウンロードボタン
   └─ フィードバックボタン
```

**プロンプトテンプレート:**
```
System Prompt:
あなたはEleKnowledge-AIの技術サポートアシスタントです。
電気設備・機械設備に関する専門知識を持ち、以下の資料を参照して正確に回答します。

【参照資料】
$search_results$

【チャット履歴】
$chat_history$

【回答ルール】
1. 必ず参照資料に基づいて回答する
2. 引用元の文書名を明記する
3. 不明な点は推測せず「資料に記載がありません」と答える
4. 安全に関わる情報は特に正確性を重視する
5. 技術用語は正確に使用する

ユーザーの質問: $user_query$
```
