# 📘 EleKnowledge-AI システム仕様書

## プロジェクト情報

**プロジェクト名:** EleKnowledge  
**バージョン:** 1.2.0  
**最終更新日:** 2026-01-22  
**作成者:** Development Team  
**ステータス:** Phase 1 完成・Phase 2 完成・Phase 3 準備中

---

## 目次

1. [システム概要](#1-システム概要)
2. [アーキテクチャ](#2-アーキテクチャ)
3. [機能仕様](#3-機能仕様)
4. [技術スタック](#4-技術スタック)
5. [セキュリティ](#5-セキュリティ)
6. [データモデル](#6-データモデル)
7. [API仕様](#7-api仕様)
8. [デプロイ構成](#8-デプロイ構成)
9. [開発ロードマップ](#9-開発ロードマップ)
10. [運用・保守](#10-運用保守)

---

## 1. システム概要

### 1.1 プロジェクト目的

EleKnowledgeは、昇降機に関する知識を集約し、AIを活用して以下の業務を支援するシステムです：

- 📚 **RAGチャット**: 技術資料・マニュアルの検索と質問応答
- 🔧 **トラブルシューティング**: 現場トラブルの原因分析と対処方法の提案
- ✅ **品質書類チェック**: 技評写真の自動判定と品質管理

### 1.2 対象ユーザー

- 現場代理人
- 現場作業員
- 品質管理担当者
- 保守・メンテナンス担当者

### 1.3 システム特徴

- ✅ 社内ネットワーク限定アクセス（IP制限）
- ✅ Amazon Bedrock Claude 4による高精度AI応答
- ✅ マルチエージェント協調による複雑な問題解決
- ✅ セキュアなAWS環境での運用

---

## 2. アーキテクチャ

詳細は以下に切り出しました。

- システム全体図: [docs/architecture/overview.md](docs/architecture/overview.md)
- コンポーネント構成: [docs/architecture/components.md](docs/architecture/components.md)

**概要:**
- 🌐 **入口**: 社内ネットワーク → AWS Amplify Hosting（WAF: IP 制限・レート制限・マネージドルール統合）
- ⚙️ **API/コンピュート**: API Gateway 3 系統（認証 / RAG / チャット管理）+ Lambda（Python 3.11 / Node.js 18）
- 🧠 **AI/ML**: Bedrock Claude 4.5 Haiku、Knowledge Base（Titan Embeddings G1 + OpenSearch Serverless）、Bedrock Agent（Phase 3）
- 💾 **データ**: DynamoDB（users / chatlogs / sites）、S3（documents / uploads）、Cognito User Pool、Secrets Manager

---

## 3. 機能仕様

### 3.1 Phase 1: 基盤整備（2ヶ月）【完成】

詳細仕様は [docs/features/production/phase1-foundation.md](docs/features/production/phase1-foundation.md) に切り出しました。

**実装済み機能の概要:**
- 🔐 **認証システム**: AWS Cognito 統合、MFA 対応、パスワードリセット
- 🏠 **ホーム画面**: 3 つの主要機能への導線、開発モード搭載
- 🛡️ **IP 制限**: AWS Amplify WAF v2 統合による社内ネットワーク限定アクセス

### 3.2 Phase 2: RAGチャット機能（2ヶ月）

詳細仕様は [docs/features/production/phase2-rag-chat.md](docs/features/production/phase2-rag-chat.md) に切り出しました。

**主要機能の概要:**
- 💬 **RAGチャット画面**: リアルタイムチャット、セッション管理、引用文書表示、フィードバック、メタデータフィルター検索
- 📚 **Knowledge Base**: Amazon Titan Embeddings G1 + OpenSearch Serverless、S3 データソース（eleknowledge-documents）
- 🔄 **RAG 処理フロー**: ベクトル検索 → Claude 4 による回答生成 → 引用付き DynamoDB 保存

### 3.3 Phase 3: 新機能開発（3ヶ月）

> **注:** Phase 3 の詳細仕様は、Phase 2 実装完了後に改めて策定します。現時点の記載は概要・PoC 設計レベルです。

#### 3.3.1 トラブルシューティング機能

詳細仕様は [docs/features/development/phase3-troubleshooting-spec.md](docs/features/development/phase3-troubleshooting-spec.md) に切り出しました。
PoC 詳細設計は [docs/agent-spec.md](docs/agent-spec.md)、実装ガイドは [docs/features/development/phase3-troubleshooting-implementation-guide.md](docs/features/development/phase3-troubleshooting-implementation-guide.md) を参照してください。

**機能概要:**
- 🔧 **現場トラブルの原因分析**: 現場番号・トラブル内容・エラーコード等を入力、Bedrock Agent が仕様データと類似事例を統合分析
- 🤖 **Bedrock Agent + Knowledge Base**: DB検索 Action Group + KB セマンティック検索（trouble-case / 技術資料）+ Claude 4 による原因推定
- 📊 **出力**: 分析サマリー、原因候補 Top 3〜5（確率・根拠付き）、ステップバイステップ対処方法、参照資料、エスカレーション判断

#### 3.3.2 品質書類チェック機能

詳細仕様は [docs/features/development/phase3-quality-check-spec.md](docs/features/development/phase3-quality-check-spec.md) に切り出しました。

**機能概要:**
- 📸 **技評写真解析**: Claude 4 Vision API で OCR・計測値読み取り・署名/管理番号確認
- 📋 **仕様照合**: 現場仕様データベースと測定値を照合、許容範囲・異常値・書類完全性をチェック
- ✅ **良否判定**: 合格 / 条件付き合格 / 不合格 の 3 段階判定と判定根拠・指摘事項の自動生成

---

## 4. 技術スタック

詳細仕様は [docs/tech-stack.md](docs/tech-stack.md) に切り出しました。

**概要:**
- 🖥️ **フロント**: Next.js 14 / React 18 / Tailwind CSS / shadcn/ui / Zustand / React Hook Form / Axios / AWS Amplify
- ⚙️ **バックエンド**: Lambda（Python 3.11 / Node.js 18）、API Gateway REST、AWS Cognito
- 🧠 **AI/ML**: Bedrock Claude 4 Sonnet、Titan Embeddings G1、OpenSearch Serverless、Bedrock Agent
- ☁️ **インフラ**: Amplify / WAF / DynamoDB / S3 / Secrets Manager / CloudWatch

---

## 5. セキュリティ

詳細仕様は [docs/security.md](docs/security.md) に切り出しました。

**概要:**
- 🔐 **認証・認可**: Cognito User Pool + JWT（Access 1h / Refresh 30d）、API Gateway Cognito Authorizer
- 🔒 **暗号化**: HTTPS（TLS 1.2+）、DynamoDB / S3 / Secrets Manager すべて保管時暗号化
- 🛡️ **ネットワーク**: Private Subnet + NAT Gateway、WAF IP Set による社内限定アクセス
- 🔑 **シークレット管理**: `.env`（dev）/ Secrets Manager（prod）
- ✅ **入力検証**: サニタイゼーション、XSS/SQLi 対策、TypeScript 型安全

---

## 6. データモデル

詳細仕様は [docs/data-model.md](docs/data-model.md) に切り出しました。

**概要:**
- 🗄️ **DynamoDB**: `users`（Cognito Sub をキー）、`eleknowledge-chatlogs`（sessionId + messageId、TTL 30日、userId-timestamp GSI）
- 🪣 **S3**: `eleknowledge-documents`（manuals/policies/reports/specifications）、`eleknowledge-uploads`（tmp は 24h で自動削除）
- ♻️ **ライフサイクル**: チャット履歴 30 日 TTL、S3 は 30d→Glacier / 90d→Deep Archive / 1y→削除、削除 7/1 日前に通知

---

## 7. API仕様

詳細は以下に切り出しました。

- 認証API: [docs/api/auth.md](docs/api/auth.md)
- RAG処理API: [docs/api/rag.md](docs/api/rag.md)
- チャット管理API: [docs/api/chat.md](docs/api/chat.md)
- 共通仕様（エラーハンドリング・スロットリング）: [docs/api/common.md](docs/api/common.md)

**概要:**
- 🔐 **認証API**: Cognito ベースの `POST /auth/signup` / `POST /auth/login`（Access/Refresh/ID トークン発行）
- 🧠 **RAG処理API**: `POST /rag/query` で sessionId + query + filters を受け、Claude 4 による回答と引用文書を返却
- 💬 **チャット管理API**: `GET /chat/sessions` 他、セッション一覧・履歴管理
- ⚠️ **共通**: 統一 `ErrorResponse` 形式（500系リトライ / 400系分類）、API Gateway スロットリング（認証 50/10、RAG 20/5、チャット 50/10 req/sec）、WAF レート制限（IP 500/5min、ユーザー 100/5min）

---

## 8. デプロイ構成

詳細仕様は [docs/deployment.md](docs/deployment.md) に切り出しました。

**概要:**
- 🌐 **リージョン**: us-east-1（Bedrock Claude 4 最新機能・サポート優位、日本から ~150ms）。マルチリージョン未予定、DR は同リージョン AZ 冗長
- 🔁 **環境**: Development（`dev.eleknowledge-ai.amplifyapp.com` / develop）・Production（`eleknowledge-ai.amplifyapp.com` / main）
- ⚙️ **CI/CD**: Amplify 自動デプロイ（push → build → test → deploy → Slack）、Lambda は AWS SAM + GitHub Actions（本番 Blue/Green）
- 🏗️ **IaC**: CloudFormation + SAM（`phase1-template.yaml`）で Cognito / DynamoDB / S3 / Lambda / API Gateway / CloudWatch を一括定義
- 💰 **コスト**: 月額概算 **$28.94**（年間 ~$347 / ~48,000円）。最適化策は On-Demand→Provisioned、S3 Intelligent-Tiering 等

