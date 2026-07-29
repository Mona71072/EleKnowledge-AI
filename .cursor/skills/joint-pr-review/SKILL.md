---
name: joint-pr-review
description: >-
  mona と itai（@yukiworkspace）が根本仕様・ルール・安全関連の変更を
  Pull Request 経由で相互に共有し、双方確認してから進める。
  Use when creating or reviewing PRs for product intent, answer schema,
  safety gates, auth, cursor rules, deploy policy, or other foundational
  changes; when itai should open a PR for mona to review; or when the user
  mentions 共同確認, itai, いたい, or 根本変更のPR.
---

# 共同 PR 確認（mona ↔ itai）

根本に関わる変更は、片方だけでマージせず **PR で相手に飛ばして共同確認**する。

## いつ使うか

次のいずれかならこのスキルに従う。

- 製品思想・スコープ・回答 Schema・安全ゲート・権限
- `.cursor/rules` の根本ルール
- ブランチ／デプロイ運用の変更
- 破壊的な API / データモデル変更
- itai が mona 向けに確認を求める変更（逆方向も同じ）

通常のバグ修正・UI 微調整は、既存のデプロイ用 PR 運用（`working-branch.mdc`）でよい。迷ったら共同確認にする。

## 別 PR にする（必須）— デプロイと分け、共同確認同士は相乗り可

次は **機能実装・セキュリティ修正・デプロイ依頼の PR と混ぜない**。共同確認専用の PR を切る。

- 製品意図・ビジョン共有（例: `docs/PRODUCT_INTENT.md`）
- Cursor 運用ルール・スキル（`.cursor/rules` / `.cursor/skills`）
- ブランチ／デプロイ運用方針だけの変更
- AI 駆動運用メモ（例: `docs/ops-ai-driven-dev.md`）

**共同確認同士の相乗り:** 既に open な意図・運用の共同確認 PR があり、今回も同種ならその PR に載せてよい。ユーザーが「前の共同確認と一緒に」と明示したときも同様。

**禁止:** デプロイ用 PR の本文に共同確認だけを相乗りさせる（逆も不可）。

同じ `mona` に実装が載っていても、レビュー用には feature ブランチから **意図・運用だけの共同確認 PR** を `develop` 向けに作る。

## 登場人物

| 役割 | GitHub | メンション |
|---|---|---|
| mona（この PJ の主作業者） | `Mona-mebs` で操作 | PR レビュー依頼先 |
| itai（デプロイ・共同確認） | — | `@yukiworkspace` |

## mona → itai（mona 側エージェント）

1. 変更内容をユーザーに提案し、合意を得る（`ai-collaboration` ルール）
2. **意図共有・運用ルールだけ**なら feature ブランチを切り、デプロイ用 PR と分離する
3. コミット → `Mona-mebs` で push
4. base `develop` 向けに **専用 PR** を作成（既存のセキュリティ／UI／デプロイ PR に相乗りしない）。同種の共同確認が open なら相乗りを検討
5. PR 本文はテンプレに加え **`.cursor/rules/pr-clarity.mdc` の合格線**を満たす（目的一文・Yes/No・読む順）
6. `@yukiworkspace` をメンションし、何を確認してほしいかを具体的に書く
7. itai の Approve / コメント待ち。合意前に勝手にマージ方針を断定しない

## itai → mona（itai 側エージェント）

itai の作業でも、根本変更は **必ず PR で mona に飛ばす**。

1. 変更をブランチに載せて push
2. PR を作成（base は運用に合わせ `develop` または合意したブランチ）
3. PR 本文の先頭で **mona 向けに確認依頼**する（下記テンプレの「itai → mona」）
4. mona（`Mona-mebs` / レビュアー）が内容を確認できる状態にする
5. mona の合意なしに根本仕様を確定扱いにしない

## PR 本文テンプレ

### mona → itai（意図・運用ルール専用 PR）

```markdown
@yukiworkspace cc: 共同確認依頼（意図・運用ルール）

## この PR の目的
（例: 製品意図のドラフト共有 + AI 共同開発ルールの合意。アプリ実装は含まない）

## マージで決まること / 決まらないこと
**決まる:**
- （箇条書き）

**決まらない（別 PR・別会話）:**
- （箇条書き）

## itai に確認してほしいこと（Approve 条件）
1. （Yes/No で答えられる具体質問）
2. …

## ファイル別レビュー観点
| ファイル | 見るポイント |
|---|---|
| `docs/PRODUCT_INTENT.md` | … |
| `.cursor/rules/...` | … |

## 承認後
- デプロイ: なし / あり
- 次にやること: …
```

### mona → itai（その他の根本変更）

## 共同確認（itai 向け）
- [ ] 製品意図・スコープとの整合
- [ ] セキュリティ・認可・破壊的変更の有無
- [ ] マージ方針の合意（この PR で進めてよいか）

## 変更の種類
- [ ] 製品思想 / PRODUCT_INTENT
- [ ] 回答 Schema / 安全ゲート
- [ ] 権限・認可
- [ ] Cursor rules / 運用
- [ ] API / データモデル
- [ ] その他: （記述）

## サマリ
（何をなぜ変えるか。未確定点があれば明記）

## デプロイ
（必要なら既存のデプロイ依頼テンプレも続ける）
```

### itai → mona

```markdown
cc: mona 共同確認依頼（根本変更）

## 共同確認（mona 向け）
- [ ] 意図の理解が合っているか
- [ ] この変更で進めてよいか
- [ ] 追加で決めたい点の有無

## 変更の種類
- [ ] 製品思想 / スコープ
- [ ] 回答 Schema / 安全ゲート
- [ ] 権限・認可
- [ ] ルール / 運用
- [ ] API / データモデル
- [ ] デプロイ / インフラ
- [ ] その他: （記述）

## サマリ
（何をなぜ変えるか。未確定点があれば明記）

## 確認してほしいポイント
（具体的に 1〜3 個）
```

## エージェントの振る舞い

- 根本変更をローカルだけのコミットや口頭合意で終わらせない
- **デプロイ依頼と共同確認が両方必要なら、PR を分ける**（同じ PR に両方のチェックリストを載せない）
- 共同確認同士なら既存の意図・運用 open PR への相乗りを検討する
- PR を送る前に `.cursor/rules/pr-clarity.mdc` の合格線を満たす（テンプレ埋めだけでは不十分）
- ユーザーが「PR にして itai に共有して」と言ったら、このスキルのテンプレで **共同確認 PR** を作成する
- itai 側から飛んできた PR をレビューするときは、意図メモ（`docs/PRODUCT_INTENT.md`）とのずれを優先して指摘する

## 関連

- 意図メモ: `docs/PRODUCT_INTENT.md`
- AI 駆動の共同運用: `docs/ops-ai-driven-dev.md`
- PR わかりやすさ: `.cursor/rules/pr-clarity.mdc`
- 確認してから変更: `.cursor/rules/ai-collaboration.mdc`
- コード↔docs 同期: `.cursor/rules/docs-code-sync.mdc`
- ブランチ・デプロイ PR: `.cursor/rules/working-branch.mdc`
