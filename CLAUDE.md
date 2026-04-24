# CLAUDE.md — AI アシスタント取扱いルール

本ファイルは、このリポジトリで AI アシスタント（Claude Code 等）と協働するときのルールを示します。

---

## 1. 仕様ドキュメントの構造

仕様は [spec.md](spec.md) を索引として、トピック別に `docs/` 配下へ分割されています。

- 🟢 **稼働中の機能**: [docs/features/production/](docs/features/production/)
- 🟡 **開発中の機能**: [docs/features/development/](docs/features/development/)
- 📐 **アーキテクチャ**: [docs/architecture/](docs/architecture/)
- 📚 **横断的仕様**: [docs/tech-stack.md](docs/tech-stack.md), [docs/security.md](docs/security.md), [docs/data-model.md](docs/data-model.md)
- 🔌 **API仕様**: [docs/api/](docs/api/)
- 🚀 **デプロイ**: [docs/deployment.md](docs/deployment.md)

各分割ドキュメントには以下の frontmatter が付与されています。AI はこれを読んで取扱い方針を決めること。

```yaml
---
status: production | development | deprecated
phase: 1 | 2 | 3   # 該当する場合のみ
last-verified: YYYY-MM-DD
related-code: path/to/src/, path/to/other/
---
```

---

## 2. ドキュメント編集ルール

### 2.1 `status: production` のドキュメント

**稼働中の仕様**を表します。変更はシステム挙動と乖離するリスクがあるため、**必ず事前にユーザーへ確認**してから編集すること。

- 対象: `docs/features/production/**`, `docs/architecture/**`, `docs/api/**`, `docs/tech-stack.md`, `docs/security.md`, `docs/data-model.md`, `docs/deployment.md`
- 変更理由・影響範囲・対応するコード変更の有無をユーザーに提示し、合意を得てから進める
- 対応する実装を更新せずにドキュメントだけ変更しない

### 2.2 `status: development` のドキュメント

**開発中の仕様**を表します。設計の提案・修正は自由に行ってよい。

- 対象: `docs/features/development/**`
- 提案ベースで編集してよいが、完了したら `last-verified` を更新すること
- Phase 完了時は `git mv` で `docs/features/production/` に昇格させ、`status` を `production` に変更

### 2.3 `status: deprecated` のドキュメント

廃止予定。新規参照しない。削除時期はユーザーと相談。

### 2.4 frontmatter 管理

- ドキュメントを更新したら **`last-verified` を更新日（YYYY-MM-DD）に書き換える**
- `related-code` に挙げたパスは、実装移動に追従してメンテナンスする
- 新規ドキュメント作成時は frontmatter を必ず付ける

---

## 3. コード編集ルール

### 3.1 ソースコードと仕様の一貫性

- `related-code` に挙がっているコードを変更したら、対応するドキュメントの更新要否を検討する
- 逆に仕様を変更するときは、`related-code` のコードへの反映を同じ PR で行う

### 3.2 ファイル移動は `git mv`

ドキュメント・ソース問わず、ファイル移動は履歴を保つため `git mv` を使う。

---

## 4. PR 運用

- base ブランチは `develop`
- ブランチ命名・commit message・PR 本文は **日本語**
- PR は細かめに分ける（AI レビュー効率優先）
- `main` へのマージは `develop` 経由のみ

---

## 5. 参考: 過去の大規模リファクタ

2026-04-24 完了: `spec.md` 1538 行の 7 分割 PR（#7〜#13）。frontmatter スキーマはこの分割で導入された。
