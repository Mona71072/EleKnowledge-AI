# 📋 AI開発ルール（v1.3.4）

本ファイルは、本プロジェクトにおける **設計・実装・運用の共通ガードレール** を定義するものです。
本ルールに従わないコード・設定・運用は **原則として実施しません**。

---

## 🔄 AIルール用Markdownの同期【Must】

### 正本

* AI開発ツール間で共有するルールの正本は、リポジトリルートの `AGENTS.md` のみとします
* AIルールの追加・変更・削除を依頼された場合は、必ず最初に `AGENTS.md` を更新します
* 同じルール本文を複数のMarkdownへコピーしません。重複による内容のずれを防ぐため、各ツールの参照機能を使用します

### 各ツールへの同期

* Cursor / Codex / Cline / Windsurf は、ルートの `AGENTS.md` を直接参照します
* Claude Code は `CLAUDE.md` の `@AGENTS.md` から参照します
* Gemini CLI は `GEMINI.md` の `@./AGENTS.md` から参照します
* 新しいAI開発ツールを追加する場合は、そのツールの公式な指示ファイルから `AGENTS.md` を参照させます
* 参照機能がないツールに限り、同じタスク内で専用ファイルも更新し、重複が必要な理由をユーザーへ報告します

### 更新時の確認

* `CLAUDE.md` と `GEMINI.md` には、ツール固有の最小限の記述以外は追加しません
* AIルール更新後は、各参照ファイルの参照先、Git追跡可否、`git diff --check` を確認します
* 完了報告では、正本と同期対象を明示します
* `README.md`、`spec.md`、`docs/` 配下など、AIルール以外のMarkdownはこの同期対象に含めません

---

## 🎯 本プロジェクトの不変条件（Guardrails）【Must】

以下は **設計判断の前提として常に固定** されます。

* 認証：Cognito User Pool + JWT
* 認可：API Gateway / Lambda 側で `userId` によるデータ分離を必須とする
* フロントエンド：Next.js（App Router）+ Amplify Hosting
* バックエンド：API Gateway + Lambda
* チャット履歴：DynamoDB（TTL により60日で自動削除。実装値 `60 * 24 * 60 * 60` 秒）
* ナレッジ検索：Amazon Bedrock（Knowledge Base / Agent）
* ネットワーク制御：CloudFront + WAF（IP制限）
* 本番環境での秘匿情報管理：AWS Secrets Manager を原則とする

---

## 📐 プロジェクト管理ルール

### 仕様管理【Must】

* 仕様は `spec.md` を**索引**として、トピック別に `docs/` 配下へ分割して管理します（2026-04 の分割 PR #7〜#13 以降の構成）
  * 🟢 稼働中: `docs/features/production/` ／ 🟡 開発中: `docs/features/development/` ／ 📐 `docs/architecture/` ／ 🔌 `docs/api/`
* 各ドキュメントの frontmatter（`status` / `last-verified` / `related-code`）を読んで扱いを決めます
* `status: production` のドキュメントは、**ユーザーの事前確認なしに編集しません**（変更理由・影響範囲・対応するコード変更の有無を提示して合意を得る）
* ドキュメント更新時は `last-verified` を更新し、ファイル移動は履歴を保つため `git mv` を使います
* 仕様変更が必要な場合は **必ず該当ドキュメントを先に更新** します
* 実装と仕様の乖離を禁止します（`related-code` のコード変更は同じ PR でドキュメント更新要否を確認）

### 開発計画管理【Must】

* 開発ロードマップと進捗は `spec.md` および `docs/features/` 配下で管理します
* 仕様・計画変更時は該当ドキュメントを更新してから着手します
* タスク完了条件（Done定義）には以下を含めます：

  * 実装完了
  * テスト実装
  * ドキュメント更新要否の確認

### 業務スコープ変更の共同確認【Must】

機種・資料・対象部門・ユーザーなどを検索・表示・利用対象へ追加／除外する変更は、単なる実装修正として確定しません。実装・マージ前に mona と itai で共同確認し、`docs/decisions-*.md` または該当する正本ドキュメントへ次を記録します。

* 選定根拠と参照元（正式な一覧、対象部門、実測など）
* 決定者・確認者・決定日
* 追加／除外される対象と影響件数
* 対象外データの扱い（保持、検索除外、非表示、削除）と影響を受ける利用者・業務
* 暫定処置の場合は、見直し責任者・期限・解除／拡大／ロールバック条件

自動生成の一覧や実装コードは影響確認の証拠にはできますが、業務判断の決定記録の代わりにはしません。削除は明示合意なしに実施せず、未決事項があれば PR を質問／判断待ちとして止めます。

---

## 🔒 セキュリティルール

### 機密情報の管理【Must】

#### 環境別ルール

* ローカル開発：`.env` / `.env.local`
* 本番環境：Secrets Manager + Lambda 環境変数

#### 秘匿レベル分類

* **Tier S（絶対秘匿）**

  * JWT署名鍵
  * クライアントシークレット
  * APIキー
* **Tier A（秘匿推奨）**

  * 内部URL
  * アカウントID
  * IP Allowlist
* **Tier B（慎重に扱う）**

  * AWSリソースID

`.env` は `.gitignore` に含め、`.env.example` を必ず作成します。

---

### 入力検証・認可【Must】

* すべての入力値を検証・サニタイズします
* 認証と認可を明確に分離します
* `userId` をクライアントから信用しません（JWT から取得）

---

### ログと秘匿【Must】

* CloudWatch Logs に以下を出力しません

  * トークン
  * 個人情報
  * ナレッジ引用全文
* ログは構造化し、追跡可能な粒度にします

---

## 📝 コーディング規約

### 命名規則【Must】

フロントエンド（TypeScript）に適用:

* 変数・関数：camelCase
* 定数：UPPER_SNAKE_CASE
* クラス：PascalCase
* ファイル名：kebab-case

バックエンド（Python Lambda）は PEP 8 に従う（変数・関数は snake_case。既存の `app.py` 構成を踏襲）。

### コメント規約【Should】

* 公開関数は JSDoc を記述
* セキュリティ注意点は `// SECURITY:` を使用

---

## 🛡️ エラーハンドリング

### 方針【Must】

* すべての非同期処理でエラーハンドリングを実装
* 本番でスタックトレースを返さない
* エラーレスポンス形式を統一

---

## 🧪 テストルール

### テストピラミッド【Must】

* Unit Test：主要ロジック
* Integration Test：API + DynamoDB
* E2E：認証〜RAG最低動線

### Done定義

* main / develop へのマージは以下必須

  * Lint
  * Type Check
  * Test Pass

---

## 📦 依存関係管理

* 不要な依存関係を追加しません
* 脆弱性があるパッケージは使用禁止
* lockファイルを必ずコミット

---

## 🔄 Git ルール

### ブランチ

* main：本番（マージは develop 経由のみ）
* develop：開発
* feature/* / hotfix/*
* mona：実装・デプロイ向けの作業ブランチ（下記「PR の分離」参照）

### PR・コミュニケーション【Must】

* ブランチ命名・commit message・PR 本文は日本語
* PR はレビューしやすい粒度に細かく分ける（AI レビュー効率優先）

### PR の分離【Must】

実装デプロイと、共同確認用 Markdown は **必ず別 PR** にする。混ぜない。

| 種別 | ブランチ例 | base | 含めてよいもの |
| --- | --- | --- | --- |
| 実装・デプロイ | `mona` | `develop` | アプリ・Lambda・IaC・それに直結する実装メモ |
| 共同確認 Markdown | `docs/*` 等 | `develop` | 意図・運用・AIルール・製品方針など **デプロイ不要** の文書 |

* 「base は `develop`」は両者共通である
* 「`mona` → `develop`」は **デプロイ経路** の話であり、Markdown 共同確認まで `mona` に載せろという意味ではない
* 既存のデプロイ PR が開いていても、共同確認 Markdown をそこに追加しない
* 直近の訂正一文だけで、上記の分離ルールを捨てない。疑義があればユーザーに確認する

### マージ条件【Must】

* テスト通過
* spec / roadmap 更新確認
* ユーザー承認取得

### GitHub アカウント運用【Must】

**適用範囲は mona 側だけ。** itai（`yukiworkspace`）が本家を編集・push / PR するときは、この節のアカウント切替・両方 push・フォーク同期は **適用しない**。itai は本家 `yukiworkspace/EleKnowledge-AI` だけでよい。

mona 側のリモートは 2 つ使う。

| リモート | リポジトリ | 用途 |
| --- | --- | --- |
| `origin`（`yukiworkspace` も可） | `yukiworkspace/EleKnowledge-AI` | 本家。PR の送り先 |
| `Mona71072` | `Mona71072/EleKnowledge-AI` | 本家のフォーク。コピー |

`Mona71072` リモートが無い場合は追加する。

```bash
git remote add Mona71072 https://github.com/Mona71072/EleKnowledge-AI.git
```

マシン全体のデフォルトは **`Mona71072`**。本家向けの `git push` / PR 作成・更新 / `gh` は **`Mona-mebs`**。フォークへの push は **`Mona71072`**。

#### 作業開始時（本家向け操作のとき）

1. `gh auth status` でアクティブアカウントを確認する
2. `Mona-mebs` でなければ `gh auth switch --user Mona-mebs`
3. `gh api user --jq .login` が `Mona-mebs` であることを確認する

#### 通常の push（必須）

mona が push を依頼したら、**同じブランチを本家とフォークの両方へ push** する。片方だけで完了としない。itai の push には適用しない。

1. `Mona-mebs` で `origin`（本家）へ push する
2. **`Mona71072` へ切り替え**、フォークへ同じブランチを push する
3. `gh api user --jq .login` が `Mona71072` であることを確認する

```bash
gh auth switch --user Mona-mebs
git push -u origin HEAD
gh auth switch --user Mona71072
git push -u Mona71072 HEAD
gh api user --jq .login   # Mona71072 であること
```

PR 作成・更新・コメントなど本家の `gh` 操作も `Mona-mebs` で行い、**同じターン内で `Mona71072` へ戻す**。

* 本家 push 成功だけでタスク完了としない。**フォークへの push とアカウント復帰までが完了条件**
* `Mona-mebs` のまま放置しない（他プロジェクトの認証に影響する）
* 本家への push / PR / `gh` を `Mona71072` で行わない

#### フォークだけ進んでいる変更（必須）

`Mona71072/EleKnowledge-AI` にだけある変更を本家へ載せるのは、**mona が明示したときだけ**。itai の作業では発生させない。

* 「本家に同期」「origin にも push」「オリジナルに載せて」など指示がある場合のみ、本家へ push / PR する
* 指示が無いのに、フォークが進んでいるからといって本家へ合わせて push しない
* エージェントが独自判断でフォーク → 本家へ追従させない。mona が「push して」と言った **ローカルの作業コミット** は、通常どおり両方へ出す

#### 本家 `develop` がフォークより進んでいるとき（必須・mona 側）

itai が本家を更新すると、フォークの `develop` は遅れる。mona 側エージェントは **勝手にフォークへ同期せず、mona に報告する**。

確認タイミング: このリポジトリで fetch / push / PR するとき（mona 側）。itai の作業では確認しない。

```bash
git fetch origin develop
git fetch Mona71072 develop
git rev-list --left-right --count Mona71072/develop...origin/develop
```

右側（origin）が 1 以上なら遅れている。報告内容:

* 本家 `origin/develop` がフォーク `Mona71072/develop` より進んでいること
* 遅れているコミット数と、短いログ（先頭数件）
* フォークへは同期していないこと（指示待ち）

同期（GitHub の Sync fork、`develop` を本家に合わせる push など）は、**mona が明示したときだけ**行う。

---

## ⚙️ バックエンド規約

### Lambda【Must】

* 1関数1責任
* タイムアウト・メモリは根拠を持って設定
* ハードコード禁止

---

## 📊 パフォーマンス / SLO

### 目標指標【Should】

* RAG応答：p95 < 3s
* API 5xx率：< 1%

---

## 🔌 MCP / 運用ルール

### MCPサーバー利用（精度向上目的）【Should】

* 利用可能な環境では、タスクに適した MCP サーバー（AWS 公式ドキュメント参照等）の使用を推奨します
* MCP 利用の目的は **一次情報を参照し、設計・実装精度を向上させること** です
* MCP が使えない環境・タスクでは、公式ドキュメント等の一次情報を別の手段で参照します

### 設計根拠の追跡性【Must】

* 重要な設計判断・仕様解釈は、参照した一次情報（公式ドキュメント・実測・カタログ等）を PR や報告に明示し、後から追跡できるようにします
* MCP を使用した場合は、サーバー名・参照した情報・設計への反映内容を報告します（未使用時の理由報告は不要）

---

## 🚫 禁止事項【Absolute】

* 機密情報の直書き
* `.env` のコミット
* CloudWatch に秘匿情報出力
* console.log の本番残留

---

## 🔍 実装前・PR前チェックリスト

### 実装前

* [ ] spec / roadmap 確認
* [ ] セキュリティ検討

### PR前

* [ ] テスト
* [ ] ドキュメント更新

### リリース前

* [ ] ログ確認
* [ ] SLO影響確認

---

## 📝 変更履歴

* v1.3.4

  * 業務スコープ変更は、選定根拠・決定者・対象外データの扱い・見直し条件を記録して共同確認する
  * GitHub アカウント運用を mona 側だけに限定し、itai の本家編集には適用しない
  * mona の通常 push は本家とフォークの両方へ行い、本家先行時は勝手にフォーク同期しない

* v1.3.3（itai レビュー反映）

  * 事実修正: チャット履歴の TTL を実装どおり **60日** に訂正（旧記載は30日）
  * 仕様管理を spec.md 分割後の実構成（docs/ 分割・frontmatter 運用・production ドキュメントの事前確認・`git mv`）に更新
  * 命名規則の適用範囲を明確化（camelCase 等はフロントエンド TS。Python Lambda は PEP 8 / snake_case）
  * MCP 利用を Should 化し、「設計根拠の追跡性」を Must として整理（未使用時の理由報告義務を廃止）
  * Git ルールに日本語運用・細かめ PR・main へは develop 経由のみを明記

* v1.3.2

  * GitHub アカウント運用（作業は `Mona-mebs`、push/`gh` 直後に `Mona71072` へ戻す）を Must 化
  * アカウント復帰を push 成功後の完了条件として明記

* v1.3.1

  * 実装デプロイ（`mona` → `develop`）と共同確認 Markdown（別 PR → `develop`）の分離を Must 化
  * 「mona → develop」を Markdown 共同確認まで広げて解釈しない旨を明記

* v1.3.0

  * AIルール用Markdownの正本と同期方法を明文化
  * Claude Code / Gemini CLIの参照ファイル検証を更新時の必須条件に追加

* v1.2.0

  * ルールの正本を `AGENTS.md` に移し、複数のAI開発ツールで共有
  * MCP利用ルールを特定のAIツールに依存しない表現へ変更

* v1.1.0

  * プロジェクト固有ガードレール追加
  * Secrets Manager 前提に整理
  * MCPサーバー利用ルール追加
  * 変更報告義務を明文化
  * DynamoDB Scanの常用禁止

---

**本ルールに違反する実装は行いません。疑義があれば必ずユーザーに確認します。**
