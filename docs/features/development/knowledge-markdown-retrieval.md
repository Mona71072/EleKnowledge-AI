---
status: development
last-verified: 2026-10-20
related-code:
  - scripts/knowledge/build-senpai-index.mjs
  - lambda/rag/rag-function/knowhow_retrieval.py
  - lambda/rag/rag-function/app.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/lib/knowledge-research.mjs
  - frontend/src/components/knowledge/KnowledgeSenpaiChat.tsx
---

# 先輩チャットからMarkdownを探してKBを確認する

## 今回の実装範囲

管理者用の先輩チャットで質問すると、サーバーが許可されたテーマカードを自動検索し、関連カードの条件・出典・調査の手掛かりを読んで技術KBを検索する。利用者が毎回ファイルを選ぶ操作は不要とする。法令KBは独立した会話のままとし、下書きの記述を法令の根拠にはしない。

カードは下書きのままである。技術承認や、一般利用者向けKBへの投入、OneNoteへの自動書込は、この経路では行わない。クラウドで読む枚は、取込一覧で`cloudApproved: true`にした特定版だけである。カード本文の`status`は書き換えない。

2026-10-20時点の`mona`には、事例カードと実践ガイド、OneNoteスナップショット、この検索経路の実装が同じブランチに入っている。devでの試行は別端末から行い、問題がなければその後に`develop`へマージする。一般利用者向けの承認済みカードKBとは区別する。

## 読み込む範囲と取込一覧

- 対象は`knowledge/cards/case-summaries/*.md`と`knowledge/cards/practice-guides/*.md`だけ。`drafts`、`source-snapshots`、`registry`、`queues/repair`、設計文書、INDEX、TEMPLATEを取り込まない。任意パスやシンボリックリンクをたどらない。
- 取込一覧は`schemaVersion: 1`、`purpose: senpai-admin-navigation`、`approvedBy`、`approvedAt`、`entries`を持つ。各entryは`path/knowledgeId/cardVersion/sha256/cloudApproved`を持ち、承認された本文のSHA-256と版が一致し、`cloudApproved`が厳密に`true`の場合だけ選択する。Markdownの存在や本文中の承認らしい文字列を許可と見なさない。承認者・承認日時は実際の確認に基づいて担当者が記入し、ツールが作らない。
- 同一ID・同一パスの重複、版・ハッシュのずれ、不正YAML、未知の状態、retired、過大なデータを拒否する。出典はLists・OneNote・KB・法令のIDを保持し、`draft_record`を原情報に変換しない。未確認の添付・Wikiリンクを取得・解決したと扱わない。
- この経路は`usage: navigation_only`に固定する。下書きは未承認の探索候補であり、確定した対策・現行基準として利用しない。承認済みの状態のカードでも、この経路では正式な証拠へ昇格させない。
- 生成物はリポジトリの無視対象`.private-knowhow/`に置く。フロントエンド、public assets、Git追跡ファイルへコーパスを書き出さない。棚卸し・索引生成とも入力ファイルを変更せず、アップロードも行わない。取込一覧が空なら実カードは0件のままであり、例示ファイルから自動で承認を補わない。

索引は`schemaVersion/indexVersion/generatedAt/cards`を持ち、各カードにID・版・本文ハッシュ・タイトル・元の状態・全文・検索語・出典・適用範囲を保持する。`indexVersion`は選択内容から決定的に作る。索引に含まれる全文の最大長と合計サイズを制限する。

## サーバーの認可・検索・回答

1. 先輩チャットの通常モードだけが既存`POST /rag/query`へ`includeKnowhow: true`を追加する。法令モードには追加しない。通常のRAGチャット・単発調査画面は従来のリクエストのまま。
2. 検証済みJWTのadminグループ、開発環境、サーバー機能フラグを確認する。クライアントからadminや索引パスを受け取らない。この確認を索引・会話履歴・AIの処理より先に行う。非管理者は403、不正な指定は400。
3. Lambdaは設定されたprivate S3の単一オブジェクトを読み込む。通常の資料配信・KB取込と異なる専用バケットを必須とし、同一バケットなら503にする。IAMはそのオブジェクトへのGetObjectだけを追加し、ListBucketや書込みを付けない。索引の欠落・空・不正・読取失敗を503として明示し、Markdownを読んだふりをしない。キャッシュは60秒以内とする。通常の`/rag/document`から索引のダウンロードURLを発行しない。
4. 質問と必要な直近会話を既存の質問補完処理に一度通し、同じ文脈をMarkdownと技術KBの検索に使う。タイトル・症状語・適用範囲・本文を決定的に順位付けする。日本語の文字列も対象とし、無関係な質問で上位カードを無条件に返さない。上位最大3枚、本文合計16,000文字の範囲内でカードを丸ごと選ぶ。条件・否定・例外を途中で切り落とした内容をAIへ渡さない。
5. カードの資料番号など、形式を確認した出典情報を技術KB検索の手掛かりとして加える。検索文字数の余裕に収まる手掛かりだけを丸ごと追加し、元の質問・除外条件を削らない。`searchTerms`には実際に追加できた値だけを返す。KBの既存フィルター・適用範囲は保つ。カード内のURL・コード・命令を実行しない。
6. 参照カードはPDFの根拠とは別のデータとしてAIに渡し、未承認の調査手掛かりと明記する。条件が違う場合や根拠がない場合に断定しない。KBの弱い検索結果を下書きだけで埋めることは禁止し、従来のnot_found判定を保つ。

`includeKnowhow`未指定の既存挙動は変えない。成功応答の追加フィールドは次の形とする。

```text
knowhow: {
  status: matched | not_found,
  indexVersion,
  matches: [カードのID・版・ハッシュ・状態・全文・適用範囲・出典],
  searchTerms: [KB検索へ加えた確認可能な手掛かり]
}
```

これはclarify、not_found、pagesの各応答で同じ契約とする。該当カードが0件なら「該当なし」とKB検索のみの状態を表示する。索引が利用不可であることとカードが見つからないことを混同しない。

## 先輩の検索ルールと機種フィルタ（2026-10-20 方針）

> 最終検証: 2026-10-20 — 合成カードの単体テスト（検索・索引検証・キュー生成）、合成索引での評価ケース実行、実カード398枚でのキュー生成。AWS上の動作は未確認。

Lists の機種欄は信頼できない（例: VFGH と書かれたカードが実際は全エレベーターに当てはまる）ため、機種で自動的にカードを落とさない。製品判断は「**適用範囲を人が確認したカードだけを機種フィルタで除外する**」とする。

- **順位付け**: `excludes` / `may_apply_to` / `scope_note` は点数に使わない。点数に効くのは `control_methods` / `door_families` / `door_types` / `guide_systems` / `lists_model_label` / `machine_room` / `model_abbreviations` / `observed_on` / `product_lines` / `conditions` とタイトル・検索語・本文だけ。検証用の3キー（`scope_status` / `scope_verified_by` / `scope_verified_at`）は点数にも検索語にも入れない。
- **機種フィルタ（画面の「機種（任意）」）**: 未選択なら何も除外しない。選択時は、`scope_status: verified` のカードのうち、`product_lines` / `model_abbreviations` / `lists_model_label` / `observed_on` で認識できる機種が**選んだ機種以外だけ**のものを除外する。`未検証`（省略を含む）のカード、認識できる機種が1つもないカード、選んだ機種・汎用ラベル（全エレ機種 等）を含むカードは除外しない。
- **制御コード**: VFGH・CM-MA などの未知のコードは判定に使わない。
- **検証済みの付け方**: `model_scope` に `scope_status: verified` / `scope_verified_by` / `scope_verified_at`（YYYY-MM-DD）を書く。`verified` で確認者・確認日が欠ける、または形式が不正だと、取込ツールとLambdaの索引検証のどちらも失敗する。定義は [knowledge/CONTRACT.md](../../../knowledge/CONTRACT.md)、訂正の仕方は [APPLICABILITY-TAXONOMY.md](../../../knowledge/registry/APPLICABILITY-TAXONOMY.md) の「適用範囲の訂正と検証」。
- **確認キュー**: `python scripts/knowledge/build_scope_review_queue.py` が [knowledge/queues/scope-review/QUEUE.md](../../../knowledge/queues/scope-review/QUEUE.md) を生成する。P1 矛盾の疑い（機種名があるのに適用範囲が広い）、P2 機種名あり・未検証、P3 制御方式・略称のみ（機種フィルタ対象外。全機種対応なら全エレ機種へ）、P4 汎用ラベル／空。件数は `QUEUE.md` の「件数」表を正とする（この文書に手で写さない。CI が `QUEUE.md` の鮮度を検査する）。
- **評価ケース**: `tests/fixtures/knowledge/senpai-eval-cases.json`。実カードは未検証のため SE-021・SE-022 は「除外されず返ること」を確認する。検証済みカードが除外される動作は `tests/unit/test_knowhow_retrieval.py` の合成カードで確認する。実行は次のとおり（結果の表示のみ、終了コードは常に0）。

```sh
python scripts/knowledge/eval_senpai_retrieval.py --index .private-knowhow/index.json
# 実カードから一時索引を作って評価し、終了時に削除する（取込一覧は不要）
python scripts/knowledge/eval_senpai_retrieval.py --from-cards .
```

## 改善の回し方（2026-10-20）

> 最終検証: 2026-10-20 — `check`（実カード398枚で全件成功・台帳一致）、`eval_senpai_retrieval.py --from-cards .` の実カード実行、キュー鮮度・語彙同期・合成契約索引のテスト、下記ガードを破る変異（誤字・語彙のずれ・フォルダー外・版上げ忘れ・重複除去の削除・未来日・ファイル名・重複ID・無効カード・title の URL）がすべて検出されることの再確認。CI での実行結果は未確認。

手書きの合成索引だけで評価すると、取込ツールが本物の索引に何を入れるかのずれを見逃す（実際に、`excludes` / `may_apply_to` が検索語へ混入して順位修正を無効にしていた）。そこで、実カードと同じ生成コードを通る検査を回す。

1. **カードを直す**。内容（本文・frontmatter）を変えたら **`card_version` を上げる**。
2. **台帳を再生成**する（`node scripts/knowledge/build-senpai-index.mjs ledger .`）。`knowledge/registry/card-versions.jsonl` に、カードごとの `card_version` と内容 sha256 を記録する（版を上げずに内容だけ変えた場合は再生成を拒否する）。台帳もコミットする。
3. **`node scripts/knowledge/build-senpai-index.mjs check .`**。取込一覧なし・何も書き出さず、全カードを索引生成と同じ検証で1枚ずつ確認し、失敗カードと理由を出す（1枚でも失敗なら終了コード1）。台帳との照合（版上げ忘れ・台帳の再生成忘れ）もここで検出する。CI でも実行する。
4. **確認キューを再生成**する（`python scripts/knowledge/build_scope_review_queue.py`）。古いままだと CI の鮮度テストが失敗する。
5. **`python scripts/knowledge/eval_senpai_retrieval.py --from-cards .`** で評価ケースを実カードの本物の検索語で流す。無効なカードがあると WARNING を出して終了コード2（評価ケースの FAIL だけなら 0）。評価は台帳を見ない（`--no-ledger`）。
6. **先輩チャットで利用する**。
7. （今後）利用者の結果入力を確認キューへ反映し、優先度付けに使う。未実装。

補足:
- `check --eval-index <path>` は未承認の全有効カード本文を含む評価用索引を出す。OS の一時フォルダ内（リポジトリ内は拒否）に権限0600でのみ書き、アップロード・共有・コミットしない。`--from-cards` が自動で作り、評価後に削除する。
- 同じ語彙一覧（適用範囲キー・順位に使うキー・出典キー）が Lambda・取込ツール・フロントの3か所にあるため、`tests/unit/test_knowhow_contract_sync.py` が一致を検査する。一覧を変えるときは3か所を同時に直す。
- **変異テストで確認済みのガード**（それぞれ、破ると `check` かテストが失敗する。`frontend/tests/knowledge-index-guards.test.mjs` と `tests/unit/test_knowhow_contract_sync.py`）:
  - `verified` なのに4つの分類キーに認識できる機種名・全機種ラベルが無い（誤字 `AXEIZ` 等）→ 失敗し、認識される値を表示
  - 出典キー・出典種別・`SOURCE_ID_KEYS`・`scope_status` の値・日付の正規表現・`MODEL_ALIASES`・全エレ/全エスラベルが Lambda と取込ツールでずれる
  - 承認済みフォルダー外（`knowledge/cards/newdir/` 等）のカード
  - 内容を変えたのに `card_version` が同じ／版を上げたのに台帳を再生成していない
  - 検索語の重複除去の削除（重複する検索語を持つ合成カード `KH-SYN-DUPTERMS`）
  - `scope_verified_at` が未来日・実在しない日付（分かりやすい文言で失敗）
  - ファイル名と `knowledge_id` の不一致、重複した `knowledge_id`（両方のパスを表示）
  - `title` に URL・制御文字・`\` を含む
  - `--from-cards` で無効カードがあるのに終了コード0になる
- 取込ツールの出力は合成カードから生成した `tests/fixtures/knowledge/synthetic/built-index.json` に固定し、JS（再生成結果と一致）と Python（Lambda が受理し、`excludes` 等だけの語で出ないこと）の両方で検査する。取込ツールの出力を変えたら `npm --prefix frontend run knowledge:regen-contract-fixture` で再生成する。

## 画面と記録

- 通常側の返答に「参照したノウハウMarkdown」を表示し、タイトル・安定ID・版・ハッシュ・元の状態を確認できる。折り畳み内の本文は文字表示とし、画像・生HTML・外部埋込を実行しない。適用範囲・除外条件・元情報の識別子も確認できる。
- 検索で使ったカードは未承認の探索候補と明示する。選んだだけでKB確認・技術承認・OneNote転記済みにはしない。OneNoteへの自動書込みは追加しない。
- リクエストにローカルMarkdown本文やファイル名を送らない。一方でサーバー側の取込済みカードが検索・AI処理に使われることは説明する。本文・トークン・内部URLをログに出さない。
- 相談ID・発言IDが付いた先輩チャットの回答では、カード参照情報も既存ChatLogsへ保存する。左側の相談履歴から開き直す際は、保存当時の版・本文・出典を復元し、現在の索引へ差し替えない。一般ユーザーの通常履歴経路からはこの情報を返さない。保存と取得の契約は[先輩チャットの相談履歴](knowledge-research-workspace.md#先輩チャットの相談履歴)を参照する。

## 検証と導入の境界

合成データで、厳密な取込一覧、版・ハッシュ、索引の上限、不正パス、認可順序、S3失敗、該当なし、カード付きKB検索、非信頼のプロンプト境界、通常・法令の互換性、画面の出典表示を検証する。実カードはローカルで棚卸しし、許可一覧がない現状で自動選択が0枚であることを確認する。架空データの成功を実データの公開承認や実KB受入へ読み替えない。

導入時は担当者が対象カードとクラウド処理先・用途・利用者を確認し、取込一覧を用意する。生成した索引をprivate S3へ配置し、Lambdaの機能フラグ・固定bucket/key・adminグループを設定してから会社ネットで実接続を確認する。機能は初期状態では無効であり、本番や一般利用者へ自動で拡大しない。

### ローカルでの取込手順

フロントエンドの依存導入後、リポジトリルートから実行する。`<知識リポジトリ>`は実際のMarkdownを置いたルート、取込一覧は担当者が確認したJSONファイルを指定する。

```sh
node scripts/knowledge/build-senpai-index.mjs inventory <知識リポジトリ>
node scripts/knowledge/build-senpai-index.mjs build <知識リポジトリ> <取込一覧.json>
```

棚卸し結果は`<知識リポジトリ>/.private-knowhow/inventory.json`、検索用索引は同フォルダーの`index.json`に作る。ファイルは権限0600で書き出す。取込一覧の各項目には棚卸し結果の`path/knowledgeId/cardVersion/sha256`と、実際の確認に基づく`cloudApproved: true`が必要になる。カードの修正後は新しい版・ハッシュで再確認・再生成する。古い許可一覧で変更後の本文を取り込めない。

AWS導入には`Environment=dev`、`KnowhowEnabled=true`、`KnowhowIndexBucket`、`KnowhowIndexKey`、既存adminグループ、画面の`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH=true`を対応させる。索引のS3配置はこのツールの機能に含めない。配置先を通常の資料配信へ公開しない。フラグを無効にすると先輩チャットの技術側は利用不可を案内するため、完全に停止する場合は画面のフラグも無効にする。

## 別端末から mona の dev を試す

> 最終検証: 2026-10-20 — Phase2のAWS反映、Lambda設定、Amplifyのビルド履歴を確認。管理者ログイン後の画面・認証付き検索は未確認。

正本の試行順はこれだけである。Phase2の一般手順は[運用ランブック](../../ops-runbook.md)の「デプロイとロールバック」と[移行ランブック](../../aws-migration-runbook.md)の Phase 2 を使う。ここには先輩チャットを足すときの差分だけを書く。

1. 別端末で`git fetch origin`し、`git checkout mona`、`git pull origin mona`する。先端に事例カードと`amplify.yml`の`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH=true`があることを確認する。
2. `cd frontend && npm ci`のあと、リポジトリルートで棚卸しする。

```sh
node scripts/knowledge/build-senpai-index.mjs inventory .
```

3. 棚卸しに出たカードのうち、索引生成が通るものだけを取込一覧にする。カード数と索引に入れられる枚数の最新は`check`の出力（`node scripts/knowledge/build-senpai-index.mjs check .`）を正とする。失敗するカードを1枚でも一覧に入れると索引ファイルはできない。2026-10-20に、法令の出典に`law_id`が欠けていた`KH-ALL-CABIN-ILLUMINANCE-62LX-282`へ、他カードと同じ建築基準法施行令の`law_id`を補い、版を2に上げた（`law_rag_status: pending`のまま）。
   - 編集者用の注記項目（`note`など6種）は`build`が索引へ出さずに捨てる。
   - 適用範囲の値と出典の`locator`・`law_title`に`/`があってもよい。`..`区間、先頭の`/`、`\`、URL形式は引き続き拒否する。
   > 最終検証: 2026-10-20 — 実カード398枚を1枚ずつ`build`し、282の補修前は397枚が成功、成功分でPython `parse_index`も通過（索引は検証後に削除）。
4. 取込一覧の`approvedBy`と`approvedAt`（UTCの`YYYY-MM-DDTHH:mm:ss.sssZ`）を担当者が記入し、各entryの`cloudApproved`を`true`にする。その後に索引を作る。

```sh
node scripts/knowledge/build-senpai-index.mjs build . <取込一覧.json>
```

生成先は`.private-knowhow/index.json`である。Gitには入れない。

5. そのJSONを、資料配信用バケットともKB取込バケットとも違うprivateバケットの固定キーへ置く。同じバケットだとLambdaは503にする。既存の専用privateバケットを優先し、無ければ組織ポリシーに従ってprivate専用バケットを用意する。公開バケットは作らない。暗号化・TLS必須・非公開状態を確認する。オブジェクトの中身はカード全文を含む。
6. いま動いている`EleKnowledge-dev-phase2`のパラメータを読み、同じ値をすべて`--parameter-overrides`へ戻す。`KnowledgeBaseId`、モデルID、法令ゲートをテンプレート既定のままにすると、devの通常チャットの接続先が変わる。そのうえで次だけを試行値にする。
   - `RagLogicVersion`は`git rev-parse --short=12 HEAD`（7〜40桁の小文字16進）
   - `Environment=dev`
   - `KnowhowEnabled=true`
   - `KnowhowIndexBucket`と`KnowhowIndexKey`は手順5の置き場所
7. 対象SHAを確認して`infrastructure/sam`で`sam build`する。SCPでSAMの自動S3解決が許可されない環境では、承認済みartifacts bucketを明示して`sam package`し、パッケージ済みtemplateからCloudFormation changesetを作る。`--resolve-s3`に頼らない。changesetのAdd/Modify/RemoveとReplacementを確認し、Replaceが出たら実行しない。問題なければchangesetを実行する。このデプロイはdevのRAG Lambda全体を`mona`のコードへ替える。カード索引を読まない通常質問でも、`mona`に入っている他のLambda変更は同じスタックに入る。
8. Amplifyは`develop`を自動ビルドする。`mona`の画面を試す間は、Amplifyの対象ブランチを`mona`にして、このコミットから再ビルドする。コンソール側でビルド定義を上書きしている場合は、`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH`が文字列`true`であることを確認する。
9. 管理者でそのブランチのURLを開き、先輩チャットでカードの症状語を質問する。返答に「参照したノウハウMarkdown」が出ること、非管理者は入口が出ないこと、通常の`/chat`がこれまでどおり資料検索できることを見る。索引が無い、またはバケットが資料配信と同じだと503になる。
10. 試してよければ`develop`へマージする。よくなければ`KnowhowEnabled=false`と、デプロイ前の`RagLogicVersion`・モデル・KB IDへ戻してPhase2を再デプロイし、Amplifyの対象を`develop`に戻す。

OneNoteの自動書込はこの試行に含めない。

### 2026-10-20 dev実反映記録と再発防止

> 最終検証: 2026-10-20 — CloudFormation変更セット・スタック完了イベント、RAG Lambda環境変数、Amplifyジョブ、S3オブジェクトを確認。管理者による受入試験は未完了。

- 実際に反映したソースは`origin/mona`の`e54f3fafb4ad`。作業開始時の`5a39b1cef8c2`を一度packageしたが、Amplifyの`mona`ブランチが既に新しいコミットをJob 32で配信していたため、そのpackageはdeployせず、最新コミットを取り直してSAM build/packageからやり直した。**build/packageの前とchangeset実行直前に、Git SHAとAmplifyの対象コミットを再照合する。** 古いpackageを最新コードだと見なさない。
- 398枚を棚卸しし、索引には320枚だけを選択した。78枚（未対応の出典項目44、適用範囲の`/`が33、出典値の`/`が1）は除外した。カードはすべてdraftで、`cloudApproved`はこの限定用途のクラウド処理許可であり、技術承認ではない。除外カードを修正なしに追加しない。
- 専用のprivate S3バケットへ`senpai/index.json`を配置した。SSE-S3 AES256、バージョニング、HTTPS必須ポリシーを設定し、オブジェクトの暗号化とバケットポリシー上の非公開状態を確認した。組織SCPにより`put-public-access-block`は拒否された（exit 254）。これは今回の環境で確認済みの制約であり、同APIを再試行したり、公開設定を変えて回避しない。`sam package`には既存のSAM artifacts bucketを明示し、`--resolve-s3`を使わない。
- Phase2の現行パラメータをすべて取得して引き継ぎ、変更したのは試行SHA・knowhow有効化・専用索引bucket/keyだけ。KB、モデル、法令ゲート、引用URIモード、スロットリング設定をテンプレート既定値で上書きしない。再デプロイ時も、まず稼働スタックの全パラメータを取得し、対象差分以外を維持する。
- SAM package後に作成したchangesetは24リソース変更、`Replacement=True`は0件。確認後に実行し、`EleKnowledge-dev-phase2`は`UPDATE_COMPLETE`となった。RAG Lambdaでは`KNOWHOW_ENABLED=true`、索引bucket/key、`RAG_LOGIC_VERSION=e54f3fafb4ad`と、既存のKB・モデル・法令設定を確認した。changesetに置換が1件でもあれば実行しない。
- Amplifyの`mona`ブランチは既存で自動ビルド有効、Job 32が`e54f3fafb4ad`で成功していた。配信ホームのクライアント資産に先輩チャットの表示文言が含まれることを確認した。`amplify.yml`の`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH=true`はビルド時設定なので、環境変数の変更後は必ず新しいビルドを行う。
- Lambdaを直接呼び出した簡易試験は、合成したadmin claimと検索語`エラー`で`200` / `knowhow.status=not_found`だった。これは該当カードが見つからなかった結果で、API Gateway/Cognito認証や画面操作の成功を示さない。応答にsession/message IDがあったため、テスト用ユーザーのChatLogsが作成された可能性もある。**この直呼び結果を受入済みと記録せず、同じ合成ユーザーで再試験しない。** 管理者ログインから実カードの症状語で検索し、ノウハウ候補表示、通常チャット、法令チャット、非管理者の非表示・拒否を確認する工程が残る。

#### Windowsでの実行時に注意すること

- SAM CLIが同梱Pythonを見つけられるよう、SAM runtimeを`PATH`の先頭に加えてからbuild/packageする。package/buildが動作中なら二重起動せず、プロセス終了と出力を確認してから次へ進む。
- PowerShell 5.1の`ConvertTo-Json | Set-Content`はUTF-8 BOM付きになり、AWS CLIの`file://` JSON読込で失敗することがある。JSON入力ファイルはUTF-8 BOMなしで保存し、CLIには`file://<path>`で渡す。JSONをコマンドラインへ直接埋め込まない。
- `--resolve-s3`やバケット公開アクセスブロックAPIの再試行でSCPを回避しようとしない。承認済みのartifacts bucketと、個別の変更セット確認を使う。

### 2026-10-20 実装検証

> 最終検証: 2026-10-20 — 合成Markdownの実取込・実検索処理・ローカルHTTP・ブラウザー。AWSと会社KBへの実接続は未実施。

- フロントエンド151テスト、Python単体・結合687テストと11 subtestsが成功。取込処理→Python検索→画面用クライアントの契約を、同じ合成ファイルで通して検証した。
- 型検査・最適化ビルド成功。lintは既存の警告4件、エラー0件。全依存・本番依存の監査は成功した。SAMはYAML構造の読取を確認した段階であり、CloudFormationへの反映・IAMの実機検証は行っていない。
- 質問クライアントの行カバレッジ98.36%、分岐90.99%。取込処理の行92.61%、新規Python検索モジュールの行・分岐合算82%。全体のアプリに対する80%保証ではない。
- 実際の取込ツールで架空のカード1枚を索引化し、実際のRAGハンドラー・私有S3読取・検索・KBへの手掛かり追加・プロンプトのデータ境界・画面表示をローカルで確認した。Cognito、Bedrock、DynamoDBなどのクラウド接続部分はテスト用に置き換え、実AI回答品質の検証とは区別した。
- 追加質問の文脈、本文・出典・適用除外の展開表示、関連カードなし、索引欠落時の503案内と法令側の継続、非管理者403を確認した。
- 実カードのローカル棚卸し・索引生成の可否は`check`の出力を正とする（2026-10-20時点で、読取エラー0件・全件が索引生成まで通る）。すべてdraft、取込許可一覧なしの選択は0件。実カードのアップロード・技術承認・OneNoteへの追記は実施していない。
- 2026-10-20に、事例カードと実践ガイドを含む`mona`を別端末のdev試行に使う方針とした。実装だけを資料なしで移す、という以前の分離は、この試行では使わない。

現在の順位付けは文字列・検索語による候補探索であり、意味検索や技術的な適用判定ではない。会社ネットで、同義語・機種違い・適用除外・根拠不足を含む実質問と、担当者が選んだ期待カード・KB資料を照合して評価する。実際の検索品質、認証・IAM、資料閲覧、AWSデプロイの受入は残る。

### フロントエンドをデプロイしても入口が表示されない場合

> 最終検証: 2026-10-20 — リポジトリ内のAmplify設定・表示条件を確認。AWSのデプロイ履歴・配信画面は未確認。

先輩チャットと管理者の編集メニューは、ビルド時の`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH=true`とログイン利用者のadmin所属がそろった場合に表示する。環境変数を追加する前の成果物を再配信するだけでは表示は変わらない。

今回の設定漏れを修正し、dev APIを参照する既存`amplify.yml`に表示フラグを指定する。このビルド定義を使うブランチに適用されるため、別環境へ流用するときは対象APIと表示フラグを明示的に設定する。フラグ未指定のローカル設定では無効のまま、非管理者の入口も非表示を維持する。これは画面の表示設定であり、Lambdaの`KNOWHOW_ENABLED`、私有索引、実資料の取込許可を有効にするものではない。

再デプロイ時は次を確認する。

1. 接続リポジトリと対象ブランチが修正済みの`mona`であり、新しいコミットから**再ビルド**していること。別ブランチのデプロイでは修正は入らない。
2. リポジトリの`amplify.yml`を使用していること。Amplifyコンソールで別のビルド定義・環境変数を管理している場合は、実ビルドの`NEXT_PUBLIC_ENABLE_KNOWLEDGE_WORKBENCH`が文字列`true`になっていること。
3. ビルド成功後、そのブランチのURLへ管理者としてログインしていること。通常ホームの「先輩チャット」と管理画面の「ノウハウ確認」を確認する。
4. 画面が表示されても、Markdown検索にはバックエンドの反映・固定索引・認可設定が別途必要。フロントだけの更新を検索機能全体の稼働確認としない。

`NEXT_PUBLIC_`はビルド時にブラウザー用コードへ固定される。[Next.js公式仕様](https://nextjs.org/docs/app/guides/environment-variables#bundling-environment-variables-for-the-browser)を参照する。

設定漏れにより管理者の入口が空になるREDテストを確認し、修正後は管理者に表示・非管理者には非表示となることを確認した。フロント152テスト、型検査・最適化ビルド・依存監査が成功し、lintは既存の警告4件のみ。`amplify.yml`の環境変数を実際に渡した静的ビルドで、先輩チャットのコードが含まれ、無効専用の案内が除かれることも確認した。実際のAmplifyの接続ブランチ、コンソール側の上書き設定、配信結果は未確認である。
