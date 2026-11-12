---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - frontend/src/components/knowledge/common-knowledge-inbox.tsx
  - scripts/knowledge/run-common-knowledge-local.py
---

# 共通知識I1のローカル実装契約

> 最終検証: 2026-10-22 — 実装前に設計worktreeのノウハウ設計§17・引継ぎ§8/9と照合。検証結果は末尾の実装記録へ追記する。

参照設計は `.worktrees/domain-knowledge-design-20261021/docs/design-2026-10-01-knowhow-flywheel.md` §17（未コミット、保存hash `2d803b8c33375087341b0eb42471db1d99ef3f689e896f05a2e09704f60cd877`）。方針本文を複製せず、以下は合成I1だけの実装選択とする。会社承認Git、実ロール、保持年限、単元・読者は共同決定待ち。

## 境界と契約

- 共通候補（現場報告・不明用語・訂正・要望）と単元・公開版を分離。`term_foundation`を試行識別子とし、既存カード・索引を移行しない。
- 認証済みAPI Gateway claimsからsubを取得（2026-10-22改訂: admin所属は要求しない。[itai AWS契約](common-knowledge-itai-aws-contract.md)のS3正本化節）。業務権限・共有許可・保持・分野・読者はサーバー注入設定。本文のsub/role/approved等は400。adminだけでは編集・承認・公開不可。自己承認禁止（2026-11-11 改訂: §4.3 の例外の印が付いた版だけ。下の「自己承認の例外と抜き取り確認」）。
- `/knowledge/contributions` POST/GET、`/{id}` GET/PATCH、`/cards/{id}/draft` PUT、`/review-requests`・`/decisions`・`/sample-checks`・`/publish`・`/withdraw` POST、`/published/{id}` GET、`/operations/{id}` GET。変更はIdempotency-Key必須、更新はIf-Match（候補版／作業版／manifest generation）。
- 投函は許可IDと投稿本文のSHA256確認を要求。本人と許可をサーバー照合し、原文revisionを保存。元報告の本人APIには変更・書戻しなし。共有一覧は状態必須・最大50、本文なし。本人投影は担当者情報を返さない。
- SQLiteはI1の永続候補・操作journal・監査・manifestアダプター。会社Gitの代替として、専用一時領域のローカルGitへ`proposals/`と`cards/`、サーバー生成の承認記録をcommitする。アプリrepoへ本文を保存しない。
- 訂正は既存の承認単元ID・版を固定し、閲覧権限と共有範囲を確認して次版を作る。編集中・技術承認後でも旧公開版を上書きせず、公開CASで初めて切り替える。確認依頼は同一単元のGit treeにも固定し、別クライアントの変更で失効する。
- GitはUTF-8/LF固定。raw SHA256とsnake_caseへ変換した意味メタデータの束hash（`i1-json-lf-v1`）を別記録。APIはcamelCase、Gitのmetadata・承認記録はsnake_caseへ明示変換する。特定版・出典hash・対象条件・読者・期限・基準commitを承認へ固定。編集すると確認依頼失効。承認済み前版は保存する。
- 操作受付を耐久保存し、Git成功後DB失敗も同operationIdと要求hashで再開。同キー異要求409、同じ対象の未完了操作を別キーで上書きしない。Git操作のcommitを照合して二重commitを防ぐ。
- 本人の`GET /knowledge/operations`と`POST /knowledge/operations/{id}/retry`で、再起動後も保存済み要求を再認可して復旧する。完了後はjournalの要求本文を保持せず、hash・結果・actor・role・理由へ縮約する。
- 配布アダプターは台帳とは別のSQLiteファイルを使い、artifact書込やmanifest CASの成功を台帳rollbackで取り消さない。artifactのみ成功、manifest成功後の応答喪失を再現し、停止済み世代を古い公開再試行で復活させない。
- 承認と公開は別操作。不変artifactとmanifest generation CASで公開する。停止もCASし、古い公開要求による復活を拒否。全読取はmanifest・版・hash・期限・読者を照合、不能時503、停止404、no-store。両AIは同じ読取アダプターを使用し、入力前・出力前にも再照合する。
- 外部検索・モデル生成・S3・会社Git接続を実装時に自動起動しない。機能は既定オフ。ローカルサーバーだけが明示`--enable-synthetic`で合成人物を認証する。合成認証をLambdaで有効にする環境変数は設けない。SAMへの配線はせず、実保存・認証設定が無いLambdaは503。

## 自己承認の例外と抜き取り確認（2026-11-11 改訂、ノウハウ管理の見直し WP2）

> 最終検証: 2026-11-11 — `itai` ブランチの合成試験（`tests/integration/test_common_knowledge_i1.py`・`test_common_knowledge_second_review.py`）。AWS への配備はしていない。

設計: `docs/design-2026-11-11-knowledge-governance.md` §4.2・§4.3（docs 側の作業ツリー、mona 確認待ち）。itai の指示で `itai` ブランチに検証用として実装した。確信度（§4.1）と資格（§4.2 の資格表）は今回の範囲外で、承認の可否は従来どおり認可表の `approve` 権限で判定する。

- **例外の印:** 作業版を保存するとき、サーバーが §4.3 の例外の印（`secondReview`）を台帳の版に付ける。`required` は、作成者の申告（`secondReview`: `safety_legal` / `nonstandard` / `scope_expansion` / `audience_expansion`）か、コードの規則（本文・適用範囲の安全・法令・作業可否の語、標準と異なることを示す語、訂正での適用範囲・読者の変更）のどれかで真になる。語は広めに取り、迷ったら印を付ける。規則の正本は `lambda/knowledge/common-knowledge/second_review.py`。
- **承認束の hash には入れない。** 印は台帳だけに持ち、`i1-json-lf-v1` の束 hash と既存の版の照合を変えない。印の無い古い版は例外として扱う。
- **自己承認:** 印が付いた版は、従来どおり編集者・投稿者と別の人だけが承認できる（`SelfApprovalDenied`）。印の無い版は、編集者・投稿者本人も承認できる。承認記録（正本の承認 JSON・台帳）に `selfApproved` と印を残す。
- **抜き取り確認:** 本人が承認した版は `sampleCheck: pending` になる。承認者・編集者以外で `approve` 権限を持つ人が `POST /knowledge/cards/{id}/sample-checks`（`If-Match`: 版、本文 `approvalId`・`result`: `confirmed` | `needs_fix`・`reason`）で結果を記録する。記録は 1 回だけ（2 回目は 409 `SampleCheckNotPending`）。`needs_fix` は記録だけで、公開は止めない（直しは訂正の流れで行う）。
- 公開・停止・再開・競合の挙動は変えていない。

## Git のカードの移行（2026-11-12 追加、ノウハウ管理の見直し WP3）

> 最終検証: 2026-11-12 — `itai` ブランチの合成試験（`tests/integration/test_common_knowledge_migration.py`）と、実カード 398 枚での `plan`（エラー 0）。AWS への配備・実行はしていない。

設計: `docs/design-2026-11-11-knowledge-governance.md` §4.11・WP3。2026-11-12 の itai の決定: 398 枚すべてを公開し、例外の印が付いた版は抜き取り確認待ちにする／移行は専用の操作で行い、確認依頼を通さない／分野・読者は `elevator-knowhow` / `all-users`／承認束の期限は 3 年（再検証の期限は WP8 で別に持つ）。確信度・所有者・再検証の期限は付けない（WP2 と同じく範囲外）。

- **手順:** `scripts/knowledge/migrate_cards_to_s3.py` の `plan` → 認可表の準備 → `apply` → `verify`。
  - `plan`: 指定コミットの Git の blob（作業ツリーの改行に依存しない）を読み、`card-versions.jsonl` と版・hash を照合する。frontmatter だけを変換する（旧項目 `review_status`・`publication_status`・`cloud_approval` を外す、`status: approved`、語彙ファイルの置き場違いのうち移し先があるものを移して `card_version` を 1 上げる。移し先が要確認のものは変えない）。変換は再解析して期待値と一致することを確かめる。出力は `inventory.jsonl`（ID・Git の版と hash・移行後の版と hash・例外の印・直した値）、変換後のカード、`plan.json`、認可表の根拠に足す 1 件（`policy-evidence-entry.json`）。AWS には触れない。
  - 認可表（運用者が手で行う）: 根拠 `GIT-CARDS-MIGRATION`（version = コミット、sha256 = `inventory.jsonl` の hash、`independent: true`、期限は束と同じ）と、移行する人の `edit`・`approve`・`publish`（`elevator-knowhow` / `all-users`）。
  - `apply`: 変換後のカードを作業用 `drafts/` に書き（同じ内容の現行版があれば再利用）、復旧用 Lambda を **直接呼び出し**（API Gateway には出さない）で 1 枚ずつ移行する。
  - `verify`: manifest と `published/` を読み、件数・ID・本文の hash を `inventory.jsonl` と照合する（読み取りのみ）。
- **移行の操作（`Service.migrate`）:** 1 枚を 1 つの冪等な操作で「作業版の登録 → 承認（`approved/` へ不変コピー、承認記録の理由は「移行による一括登録（Git コミット）」、`selfApproved: true`、`migration` に元の版・根拠・Git 上の位置）→ 公開（manifest generation 0 → 1）」まで行い、最後に台帳（種類 `migration` の候補・単元の版 1）を書く。呼び出す人に `edit`・`approve`・`publish` の 3 つが要る。作業用の版は sha256 で固定し、本文の `knowledge_id` が対象と一致しなければ 400。台帳に同じ ID の単元が既にあれば 409 `AlreadyExists`（作り直しで上書きしない）。冪等キーは ID・本文 hash・期限・分野・読者から作るため、中断しても同じコマンドで再実行すれば同じ結果になる。
- **根拠:** 出典ごとの根拠台帳は作らず、`sourceRefs` は根拠 `GIT-CARDS-MIGRATION` の 1 件（locator = Git 上のパス、`claimType: technician_statement`）にする。カードの `source_refs` と `model_scope` は公開本文の frontmatter にそのまま残る（検索の機種フィルタは WP4 でここを読む）。
- **例外の印:** 通常の作業版と同じ規則（`second_review.assess`）で付ける。印が付いた版（2026-11-12 時点の plan で 71 枚）は `sampleCheck: pending` にし、もう 1 人が `/sample-checks` で記録する。公開は止めない。印の無い版には抜き取り確認を付けない（通常の自己承認と違う点。全件を検証済みで移す決定に合わせた）。
- **直接呼び出しの境界:** `lambda_handler` は、`httpMethod`・`requestContext` が無く `commonKnowledgeMigration` だけを持つイベントを、復旧用の関数でだけ受ける（他の関数は 404）。呼べるのは `lambda:InvokeFunction` を持つ IAM 主体だけ。イベントの `actor`（Cognito sub）は認可表で判定する。Lambda からは呼び出した IAM 主体を確かめられないため、記録されるのは `actor` だけである。

## 受入条件

合成3入口を投函→一覧→編集→Git保存→異なる確認者の特定版承認→正本反映→別操作公開→両AI読取→停止まで通す。再起動後も候補・版・操作・公開状態を保持する。未認証、閲覧だけのadmin、共有範囲外、偽造本人、自己承認、未確認根拠、同語別機種、版競合、同キー異要求、Git障害、Git成功後投影障害、manifest競合、期限切れ、停止後の引用・履歴再利用、manifest取得不能を否定検証する。

I1合格はAWS・実ブラウザ・会社Git・実データの技術受入を意味しない。`navigation_only`、cloudApproved文字列、旧メモリ編集画面を公開経路へ転用しない。
