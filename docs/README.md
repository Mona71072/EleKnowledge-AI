---
status: reference
last-verified: 2026-10-02
related-code: []
---

# Ele-Knowledge 文書案内

## この文書の目的と範囲

**目的:** Ele-Knowledgeのプロジェクト背景、利用者、製品ビジョン、原則、計画を区別し、それぞれの正本へ案内する。

**扱う情報:** Ele-Knowledgeに関する文書の役割と相互参照。

**扱わない情報:** 各文書が定義する背景、利用者ニーズ、方針、仕様、運用の本文。この案内はそれらの正本に代わらない。

## 文書の階層

```text
docs/project-context.md      事業・組織の背景
docs/user-needs.md           利用者の役割・業務課題
         \                  /
          docs/PRODUCT_INTENT.md  製品ビジョン・提供価値
             ├─ docs/product-principles.md  製品判断の原則
             └─ docs/product-roadmap.md     将来候補・展開予定（構想）

spec.md                      システム機能・API・構成などの技術仕様索引
docs/ops-ai-driven-dev.md    AIを用いた開発の共同運用
```

## 文書一覧

| 文書 | 扱う情報 |
|---|---|
| [プロジェクト背景](./project-context.md) | 施策の発端、組織背景、根拠情報の出典と確度 |
| [利用者と業務課題](./user-needs.md) | 利用者の役割、業務、課題認識と確認事項 |
| [製品意図](./PRODUCT_INTENT.md) | 製品目的、提供価値、対象領域、責任境界 |
| [製品原則](./product-principles.md) | 製品判断で優先する考え方 |
| [製品ロードマップ](./product-roadmap.md) | 発展候補、部門別予定、依存事項。未確定案を含む |
| [システム仕様索引](../spec.md) | 機能、API、アーキテクチャ、セキュリティ等 |
| [AI駆動開発の共同運用](./ops-ai-driven-dev.md) | 共同開発、レビュー、PRとマージの運用 |

## 法令チャットのdevelopプレリリース

> 最終検証: 2026-10-09 — #155 / #156のマージと文書の参照関係を確認。develop公開・実画面の確認結果は専用確認記録を参照。

[公開・受入手順](legal-chat-prerelease.md) → [利用者マニュアル](user-manual/eleknowledge-user-manual.html) → [管理者確認表](user-manual/admin-verification-sheet.md)の順に読む。APIは[法令チャット補足](api/legal-chat.md)、PR根拠・未確認の実測項目は[確認記録](verification-2026-10-09-legal-chat-prerelease.md)。正式対象部門の決定や本番提供とは区別する。

## ノウハウ確認画面の開発

> 最終検証: 2026-10-20 — 初期実装範囲の文書を追加。公開・実データ送信・KBへの索引化は対象外。

[担当者ワークスペースの実装範囲](features/development/knowledge-review-workbench.md)を参照する。元Markdownを選んで確認・編集し、OneNote追記案の確認・コピーと手動追加の記録を試す。構想と管理者への読取連携相談は[工技先輩の構想](concept-2026-10-19-kougi-senpai-knowledge-cycle.md)へ。知識データとその管理文書は資料ブランチ`feature/knowledge-reconcile-prep`に保持し、実装ブランチとは分ける。

技術KB・法令KBを調べながら編集する開発版は[工技先輩の照合画面](features/development/knowledge-research-workspace.md)へ。実検索の接続確認と、ローカルHTTPテストダブルによる画面検証を区別して記録する。

先輩チャットからの自動探索は[Markdown検索の実装範囲](features/development/knowledge-markdown-retrieval.md)を参照する。取込対象の版・ハッシュを固定した一覧と、サーバー側の管理者認可を用い、カード全件を静的画面へ埋め込まない。
