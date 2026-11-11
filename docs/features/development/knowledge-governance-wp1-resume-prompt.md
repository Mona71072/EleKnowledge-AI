---
status: development
last-verified: 2026-11-11
related-code:
  - knowledge/registry/applicability-vocabulary.json
  - tests/unit/test_applicability_vocabulary.py
---

# 再開プロンプト: ノウハウ管理の見直し WP1（語彙ファイルからコードの値を生成する）

次のセッションの最初に、下の「プロンプト」をそのまま渡す。

## プロンプト

```text
ノウハウ管理の見直しの WP1（語彙ファイルからコードの値を生成する）を実装してください。

## 最初に読むもの（この順。全文を読まず必要な節だけ）
1. リポジトリルートの AGENTS.md
2. 設計書 .worktrees/docs-knowledge-governance-20261111/docs/design-2026-11-11-knowledge-governance.md
   の §4.9（タグの語彙の置き場）と §6 WP1。他の節は必要になったときだけ
3. 語彙ファイル knowledge/registry/applicability-vocabulary.json と
   テスト tests/unit/test_applicability_vocabulary.py（作業ツリー .worktrees/common-knowledge-itai-20261022）

## 作業場所
- 作業ツリー: .worktrees/common-knowledge-itai-20261022（ブランチ itai。itai の検証用の場）
- 開始時に git status と git log -1 を確認する。前セッションの未コミットの変更が残っている想定:
  語彙ファイル（新規）、テスト（新規）、knowledge/ の 7 文書の status: production、
  APPLICABILITY-TAXONOMY.md の冒頭・§4、CONTRACT.md の 1 行、この再開プロンプト。
  まずこれらを WP1 の前提として 1 つのコミットにまとめてよいか、私に確認してからコミットする。
- 設計書のある docs の作業ツリー（.worktrees/docs-knowledge-governance-20261111）は触らない。

## 決まっていること（変えない）
- 語彙の値の正本は knowledge/registry/applicability-vocabulary.json。
  コードの値はここから生成する（方法 A）。開発 AI はファイルを直接読み、Ele-Knowledge は生成した定数を使う。
- 対象は 7 軸（製品系列・機械室・制御方式・機種略称・ガイド方式・ドアの大分類・ドア型式）。
  症状・部位・条件は対象外。
- WP1 では値を変えない。画面の機種一覧と検索の挙動は、置き換え前と同じにする。
  MELCITY・MELWIDE を検索の別名に足すこと、カードの「置き場違い」を直すことは WP1 の範囲外（WP3・WP4）。

## やること
1. 生成スクリプト scripts/knowledge/generate_vocabulary.py を作る。語彙ファイルから次を生成する。
   生成物の先頭に「生成物。直接編集しない。元: knowledge/registry/applicability-vocabulary.json。
   再生成: python scripts/knowledge/generate_vocabulary.py」を書く。改行は LF。
   - lambda/rag/rag-function/vocabulary_generated.py
     UI_MODEL_FILTERS、MODEL_ALIASES（検索の別名。kb_model_types と extra_card_aliases を NFKC・小文字化）、
     QUESTION_MODEL_ALIASES（question_aliases）、GENERIC_ELEVATOR_LABEL、GENERIC_ESCALATOR_LABEL
   - scripts/knowledge/vocabulary.generated.mjs
     MODEL_ALIASES と汎用ラベル（build-senpai-index.mjs が import する）
   - frontend/src/data/kb-model-types.generated.ts
     画面の機種一覧（value・label・targets）と、機種キーの一覧
2. 手書きの定数を、生成物の import に置き換える（値は今と同じであること）。
   - lambda/rag/rag-function/app.py の UI_MODEL_FILTERS
   - lambda/rag/rag-function/knowhow_retrieval.py の MODEL_ALIASES・GENERIC_*_LABEL
   - lambda/rag/rag-function/senpai_research_understand.py の MODEL_ALIASES
   - scripts/knowledge/build-senpai-index.mjs の MODEL_ALIASES・GENERIC_*_LABEL
   - frontend/src/data/kbModelTypes.ts の ALL_MODEL_TYPES（型と export 名は保つ。利用側 5 か所は変えない）
   - frontend/src/lib/knowledge-research.mjs の KNOWHOW_MODEL_PRODUCTS
   既存の同期テストが正規表現で定数を読んでいる場合は、生成物を読む形に直す。
3. テストを足す: 生成スクリプトを実行すると、Git の生成物と一致すること（差分が無いこと）。
4. 文書: APPLICABILITY-TAXONOMY.md の冒頭と CONTRACT.md に、
   語彙を変えたら生成スクリプトを実行することを 1〜2 行で書く。
   設計書 §6 WP1 には触らない（実装記録は本ブランチの文書に書く）。

## 完了条件
- 生成物以外に、機種の値を手で書いた箇所が無い（grep で確認し、結果を報告する）。
- 生成をやり直しても差分が出ない。
- 次がすべて通る（コマンドは作業ツリーのルートで実行）:
  ../../venv/Scripts/python.exe -m pytest tests/unit/test_applicability_vocabulary.py tests/unit/test_knowhow_contract_sync.py tests/unit/test_knowhow_api.py tests/unit/test_knowhow_retrieval.py tests/unit/test_senpai_research_grounding.py tests/unit/test_senpai_research_steps.py -q -p no:cacheprovider --basetemp=<作業用一時領域>
  （test_knowhow_contract_sync.py の test_committed_card_version_ledger_matches_every_card_file は
   変更前から失敗している既知の失敗。Windows の作業ツリーで改行が CRLF になるため。これ以外の失敗は直す）
  npm --prefix frontend run typecheck
  npm --prefix frontend run lint
  npm --prefix frontend test
  node scripts/knowledge/build-senpai-index.mjs check .
- 値を変えていないので、画面の機種一覧と検索の別名が置き換え前と同じであることを、テストの結果で示す。

## してはいけないこと
- 語彙の値の変更、カードの変更、SAM・AWS の操作、デプロイ、push、develop へのマージ。
- 有料のモデル呼び出し・検索。
- 機密情報・カード本文の出力。

## 終わったら
- 変更をコミットしてよいか私に確認する（日本語のコミットメッセージ。push はしない）。
- 報告: 変えたファイル、生成物、テストの結果（失敗は既知の 1 件だけか）、grep の結果、
  次の WP（WP2 状態・資格の契約）へ進む前に決める必要があることがあれば、それを短く。
```

## 補足（人が読む用）

- 設計の全体は、設計書の §6（WP1〜WP8）と §7（決定事項・確認事項）にある。
- WP1 は他の WP に依存しない。PR #200（承認の 2 段階）との優先が未決でも着手できる。
- Windows の注意: pytest は `--basetemp` を作業用の一時領域に向ける。Python で書くファイルは `newline="\n"` で書く（CRLF だと生成物の比較がずれる）。
