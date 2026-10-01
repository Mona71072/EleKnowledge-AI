# 📘 EleKnowledge-AI システム仕様書

## プロジェクト情報

**プロジェクト名:** EleKnowledge
**バージョン:** 1.2.0
**最終更新日:** 2026-09-30
**作成者:** Development Team
**ステータス:** Phase 1 / 2 の開発環境 stack は `UPDATE_COMPLETE`（機能仕様書と利用者向け E2E は再検証中）・Phase 3 は開発中（AWS リソースあり、利用者向け E2E 未確認）

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
- ✅ Amazon Bedrock を使った RAG 応答（使用モデルは環境設定に従う）
- 🟡 トラブルシューティング（開発中。AWS リソースの存在は提供確認を意味しない）
- ✅ セキュアなAWS環境での運用

---

## 2. ドキュメントマップ

> 仕様詳細はトピック別ドキュメントに分割しています。本ファイルは索引として機能します。

### 🟢 開発環境でリソース稼働を確認した機能

| 機能 | 現行契約・状態 | 文書 |
|------|--------------|------|
| Phase 1: 認証・基盤 | AWS stack を確認。機能仕様書は全面再検証中 | [認証 API](docs/api/auth.md) ／ [Phase 1 機能仕様（再検証中）](docs/features/production/phase1-foundation.md) |
| Phase 2: RAG・チャット | AWS stack と開発環境のモデル設定を確認。API 文書を契約の参照先とし、機能仕様書は現行正本にしない | [RAG API](docs/api/rag.md) ／ [チャット API](docs/api/chat.md) ／ [Phase 2 機能仕様（再検証中）](docs/features/production/phase2-rag-chat.md) |

### 🟡 開発中の機能（Phase 3）

| 機能 | 仕様 | 補足資料 |
|------|------|---------|
| トラブルシューティング | [docs/features/development/phase3-troubleshooting-spec.md](docs/features/development/phase3-troubleshooting-spec.md) | AWS リソースは存在するが利用者向け E2E 未確認。既存の[処理シーケンス](docs/features/production/troubleshooting-sequence.md)は現行との照合が必要。PoC 設計: [docs/agent-spec.md](docs/agent-spec.md) ／ [実装ガイド](docs/features/development/phase3-troubleshooting-implementation-guide.md) |
| 品質書類チェック | [docs/features/development/phase3-quality-check-spec.md](docs/features/development/phase3-quality-check-spec.md) | 開発仕様のみ。実装・E2E は未確認。 |
| RAG の 2 モード化 | [設計（合意済み・未実装）](docs/design-2026-09-24-rag-two-modes.md) | 決定: [docs/decisions-2026-09-24-rag-two-modes.md](docs/decisions-2026-09-24-rag-two-modes.md) ／ 調査: [docs/survey-2026-09-24-agentic-rag.md](docs/survey-2026-09-24-agentic-rag.md) ／ [KB 修正依頼台帳](docs/kb-change-requests.md) |

### 🔧 運用・改善・評価

| 項目 | 現在の状態 | 参照先 |
|------|------------|--------|
| AWS リソース・運用 | 2026-09-30 開発環境の読み取り専用スナップショット。IaC との差・未確認項目を含む | [AWS Resource Map](docs/aws-resource-map.md) ／ [運用ランブック](docs/ops-runbook.md) ／ [文書整備状況の確認記録](docs/verification-2026-09-30-current-state.md) |
| 日次 KPI v2 | 設計。AWS の毎時ルールは確認したが、現在の aggregator は日次 UTC 集計 | [KPI v2 設計](docs/design-2026-09-10-metrics-v2.md) |
| 検索トレース | 設計・実装前 | [検索トレース設計](docs/design-2026-09-10-retrieval-trace.md) |
| RAG 検索評価 | v2 候補はラベル確認前。正解資料・ページ確定前に採点しない | [評価セット v2](docs/eval-2026-09-25-golden-set-v2.md) ／ [評価運用の注意](docs/decisions-2026-07-29-layer1-eval-ops.md) |

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
| [docs/deployment.md](docs/deployment.md) | リージョン戦略・環境構成・CI/CD・IaC・コスト試算 |
