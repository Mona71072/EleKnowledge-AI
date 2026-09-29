# 📘 EleKnowledge-AI システム仕様書

## プロジェクト情報

**プロジェクト名:** EleKnowledge
**バージョン:** 1.2.0
**最終更新日:** 2026-04-24
**作成者:** Development Team
**ステータス:** Phase 1 完成・Phase 2 完成・Phase 3 開発中

---

## 1. システム概要

### 1.1 プロジェクト目的

EleKnowledgeは、昇降機に関する知識を集約し、AIを活用して以下の業務を支援するシステムです：

- 📚 **RAGチャット**: 技術資料・マニュアルの検索と質問応答
- 🔧 **トラブルシューティング**: 現場トラブルの原因分析と対処方法の提案
- ✅ **品質書類チェック**: 技評写真の自動判定と品質管理

### 1.2 対象ユーザー

- 現場代理人
- 品質管理担当者

### 1.3 システム特徴

- ✅ 社内ネットワーク限定アクセス（IP制限）
- ✅ Amazon Bedrock Claude 4による高精度AI応答
- ✅ マルチエージェント協調による複雑な問題解決
- ✅ セキュアなAWS環境での運用

---

## 2. ドキュメントマップ

> 仕様詳細はトピック別ドキュメントに分割しています。本ファイルは索引として機能します。
> 文書の正本・状態・旧資料の扱いは [ドキュメント管理方針（共同確認案）](docs/document-governance.md) を参照してください。本索引の旧資料へのリンクは今後確認・修正します。

### 🟢 稼働中の機能

| 機能 | ドキュメント |
|------|------------|
| Phase 1: 基盤整備（認証・ホーム画面・WAF） | [docs/features/production/phase1-foundation.md](docs/features/production/phase1-foundation.md) |
| Phase 2: RAGチャット（Knowledge Base + Claude 4） | [docs/features/production/phase2-rag-chat.md](docs/features/production/phase2-rag-chat.md) |

### 🟡 開発中の機能（Phase 3）

| 機能 | 仕様 | 補足資料 |
|------|------|---------|
| トラブルシューティング | [docs/features/development/phase3-troubleshooting-spec.md](docs/features/development/phase3-troubleshooting-spec.md) | PoC 設計: [docs/agent-spec.md](docs/agent-spec.md) ／ 実装ガイド: [docs/features/development/phase3-troubleshooting-implementation-guide.md](docs/features/development/phase3-troubleshooting-implementation-guide.md) |
| 品質書類チェック（Claude 4 Vision） | [docs/features/development/phase3-quality-check-spec.md](docs/features/development/phase3-quality-check-spec.md) | — |
| RAG の 2 モード化（通常モード＋じっくりモード。設計段階） | [docs/design-2026-09-24-rag-two-modes.md](docs/design-2026-09-24-rag-two-modes.md) | 決定: [docs/decisions-2026-09-24-rag-two-modes.md](docs/decisions-2026-09-24-rag-two-modes.md) ／ 調査: [docs/survey-2026-09-24-agentic-rag.md](docs/survey-2026-09-24-agentic-rag.md) ／ KB 修正依頼の台帳: [docs/kb-change-requests.md](docs/kb-change-requests.md) |

### 📐 アーキテクチャ

| ドキュメント | 内容 |
|------------|------|
| [docs/architecture/overview.md](docs/architecture/overview.md) | システム全体図 |
| [docs/architecture/components.md](docs/architecture/components.md) | コンポーネント構成 |

### 📚 横断的仕様

| ドキュメント | 内容 |
|------------|------|
| [docs/tech-stack.md](docs/tech-stack.md) | 技術スタック（フロント / バックエンド / AI/ML / インフラ） |
| [docs/security.md](docs/security.md) | セキュリティ（認証・暗号化・ネットワーク・入力検証） |
| [docs/data-model.md](docs/data-model.md) | データモデル（DynamoDB / S3 / ライフサイクル） |

### 🔌 API仕様

| ドキュメント | 内容 |
|------------|------|
| [docs/api/auth.md](docs/api/auth.md) | 認証API |
| [docs/api/rag.md](docs/api/rag.md) | RAG処理API |
| [docs/api/chat.md](docs/api/chat.md) | チャット管理API |
| [docs/api/troubleshooting.md](docs/api/troubleshooting.md) | トラブルシューティングAPI（Phase 3 / 開発中） |
| [docs/api/common.md](docs/api/common.md) | 共通仕様（エラーハンドリング・スロットリング） |

### 🚀 デプロイ

| ドキュメント | 内容 |
|------------|------|
| [docs/deployment.md](docs/deployment.md) | 旧デプロイ構成（`legacy`。現行手順には使用しない） |
