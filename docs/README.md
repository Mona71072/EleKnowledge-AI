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