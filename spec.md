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

---

## 9. 開発ロードマップ

### 9.1 Phase 1: 基盤整備

**目標:** 認証基盤とホスト環境の構築

**タスク:**
- [ ] AWS環境セットアップ
  - [ ] Cognito User Pool作成
  - [ ] DynamoDBテーブル作成
  - [ ] S3バケット作成
- [ ] 認証機能実装
  - [ ] サインアップ機能
  - [ ] ログイン機能
  - [ ] パスワードリセット
- [ ] フロントエンド基盤
  - [ ] Next.js プロジェクトセットアップ
  - [ ] Amplify Hosting設定
  - [ ] WAF設定（IP制限）
- [ ] ホーム画面実装
  - [ ] レイアウト作成
  - [ ] ナビゲーション
  - [ ] 機能カード表示

**マイルストーン:**
- Week 4: 認証機能完成
- Week 8: Phase 1完了、Phase 2開始

### 9.2 Phase 2: RAGチャット機能

**目標:** RAGチャットの完全実装

**タスク:**
- [ ] Knowledge Base構築
  - [ ] S3にドキュメントアップロード
  - [ ] メタデータ設定
  - [ ] Knowledge Base作成・同期
- [ ] RAG Lambda実装
  - [ ] Bedrock SDK統合
  - [ ] Knowledge Base検索実装
  - [ ] Claude 4応答生成
- [ ] チャット管理Lambda実装
  - [ ] DynamoDB CRUD操作
  - [ ] セッション管理
  - [ ] TTL設定
- [ ] フロントエンド実装
  - [ ] チャット画面UI
  - [ ] リアルタイムメッセージ表示
  - [ ] 引用文書表示
  - [ ] フィードバック機能
  - [ ] フィルター機能

**マイルストーン:**
- Week 12: Knowledge Base完成
- Week 14: RAG Lambda完成
- Week 16: Phase 2完了、Phase 3開始

### 9.3 Phase 3: 新機能開発

**Phase 2完了後に詳細策定**

**概要:**
- トラブルシューティング機能
- 品質書類チェック機能（Claude 4 Vision API）
- Bedrock Agent統合

### 9.4 マイルストーン

| Phase | 期間 | 完了時期 | 主要成果物 |
|-------|------|---------|-----------|
| Phase 1 | 2ヶ月 | 2025年12月 | 認証基盤、ホーム画面 |
| Phase 2 | 2ヶ月 | 2026年2月 | RAGチャット機能 |
| Phase 3 | 3ヶ月 | 2026年5月 | 新機能（トラブル、品質） |

### 9.5 テスト戦略

#### Phase 1テスト項目

**単体テスト:**
- [ ] 認証Lambda関数（Jest）
- [ ] フロントエンドコンポーネント（React Testing Library）

**統合テスト:**
- [ ] Cognito認証フロー E2E
- [ ] API Gateway → Lambda連携

**セキュリティテスト:**
- [ ] WAF IP制限テスト
- [ ] 認証バイパステスト
- [ ] XSS/CSRF対策確認

#### Phase 2テスト項目

**単体テスト:**
- [ ] RAG Lambda（Pytest + mock Bedrock）
- [ ] チャット管理Lambda
- [ ] チャット画面コンポーネント

**統合テスト:**
- [ ] Knowledge Base検索テスト
- [ ] RAG処理フロー E2E
- [ ] セッション管理・履歴取得

**パフォーマンステスト:**
- [ ] 同時接続20ユーザー負荷テスト
- [ ] レスポンスタイム < 3秒
- [ ] Knowledge Base検索 < 1秒

**UAT（User Acceptance Test）:**
- [ ] 技術者3名による実地テスト
- [ ] フィードバック収集・改善

---

## 10. 運用・保守

### 10.1 バックアップ戦略

#### DynamoDB バックアップ

**PITR (Point-in-Time Recovery):**
- 有効化: 全テーブル
- 保管期間: 35日間
- RTO目標: 4時間

**オンデマンドバックアップ:**
- 頻度: 週次（日曜深夜）
- 保管: S3 Cross-Region Replication
- 保管期間: 90日

#### S3 バックアップ

**バージョニング:**
- eleknowledge-documents: 有効化
- 誤削除防止

**ライフサイクル:**
- 30日後 → Glacier
- 1年後 → Glacier Deep Archive

#### RTO/RPO目標

| メトリクス | 目標値 | 説明 |
|-----------|--------|------|
| RTO | 4時間 | 復旧時間目標 |
| RPO | 24時間 | データ損失許容時間 |

### 10.2 災害復旧（DR）

**戦略:**
- 同一リージョン内でAZ冗長化
- マルチAZ配置（Lambda、DynamoDB）
- S3自動レプリケーション

**復旧手順書:**
1. 障害検知（CloudWatch Alarm）
2. 影響範囲の特定
3. バックアップからの復元
4. 動作確認テスト
5. サービス再開
6. ポストモーテム作成

### 10.3 監視・アラート

#### CloudWatch ダッシュボード

**主要メトリクス:**
- Lambda実行時間（p50, p90, p99）
- Lambda エラー率
- API Gateway レイテンシー
- DynamoDB スロットリング
- Bedrock APIコール数・エラー
- WAF ブロック数

#### アラート設定

| メトリクス | 閾値 | アクション | 通知先 |
|-----------|------|-----------|--------|
| Lambda エラー率 | 5%以上 | Email通知 | 開発チーム |
| API Gateway 5xx | 10回/5分 | Email通知 | 開発チーム |
| Bedrock タイムアウト | 3回連続 | Email通知 | 開発チーム |
| DynamoDB スロットリング | 発生時 | Email通知 | インフラ担当 |
| WAF ブロック | 100回/時 | Email通知 | セキュリティ担当 |

#### ログ保管

**CloudWatch Logs:**
- 保管期間: 30日
- ログレベル: INFO（本番）、DEBUG（開発）

**S3アーカイブ:**
- 保管期間: 90日
- Glacier移行: 30日後

**セキュリティログ:**
- 保管期間: 3年（コンプライアンス要件）
- 改ざん防止: S3 Object Lock

### 10.4 保守スケジュール

#### 定期メンテナンス

| 項目 | 頻度 | 内容 |
|------|------|------|
| 依存パッケージ更新 | 月次 | セキュリティパッチ適用 |
| Knowledge Base再同期 | 週次 | 新規ドキュメント追加 |
| バックアップ検証 | 月次 | 復元テスト |
| セキュリティ監査 | 四半期 | 脆弱性スキャン |
| パフォーマンステスト | 四半期 | 負荷テスト |

#### インシデント対応

**レベル定義:**
- **Critical:** サービス停止、データ損失
- **High:** 一部機能停止、大幅な性能低下
- **Medium:** 軽微な機能障害
- **Low:** UI/UX改善要望

**対応時間:**
- Critical: 即座（24時間対応）
- High: 4時間以内
- Medium: 1営業日以内
