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
- 認証済みAPI Gateway claimsからsubを取得（2026-10-22改訂: admin所属は要求しない。[itai AWS契約](common-knowledge-itai-aws-contract.md)のS3正本化節）。業務権限・共有許可・保持・分野・読者はサーバー注入設定。本文のsub/role/approved等は400。adminだけでは編集・承認・公開不可。自己承認禁止。
- `/knowledge/contributions` POST/GET、`/{id}` GET/PATCH、`/cards/{id}/draft` PUT、`/review-requests`・`/decisions`・`/publish`・`/withdraw` POST、`/published/{id}` GET、`/operations/{id}` GET。変更はIdempotency-Key必須、更新はIf-Match（候補版／作業版／manifest generation）。
- 投函は許可IDと投稿本文のSHA256確認を要求。本人と許可をサーバー照合し、原文revisionを保存。元報告の本人APIには変更・書戻しなし。共有一覧は状態必須・最大50、本文なし。本人投影は担当者情報を返さない。
- SQLiteはI1の永続候補・操作journal・監査・manifestアダプター。会社Gitの代替として、専用一時領域のローカルGitへ`proposals/`と`cards/`、サーバー生成の承認記録をcommitする。アプリrepoへ本文を保存しない。
- 訂正は既存の承認単元ID・版を固定し、閲覧権限と共有範囲を確認して次版を作る。編集中・技術承認後でも旧公開版を上書きせず、公開CASで初めて切り替える。確認依頼は同一単元のGit treeにも固定し、別クライアントの変更で失効する。
- GitはUTF-8/LF固定。raw SHA256とsnake_caseへ変換した意味メタデータの束hash（`i1-json-lf-v1`）を別記録。APIはcamelCase、Gitのmetadata・承認記録はsnake_caseへ明示変換する。特定版・出典hash・対象条件・読者・期限・基準commitを承認へ固定。編集すると確認依頼失効。承認済み前版は保存する。
- 操作受付を耐久保存し、Git成功後DB失敗も同operationIdと要求hashで再開。同キー異要求409、同じ対象の未完了操作を別キーで上書きしない。Git操作のcommitを照合して二重commitを防ぐ。
- 本人の`GET /knowledge/operations`と`POST /knowledge/operations/{id}/retry`で、再起動後も保存済み要求を再認可して復旧する。完了後はjournalの要求本文を保持せず、hash・結果・actor・role・理由へ縮約する。
- 配布アダプターは台帳とは別のSQLiteファイルを使い、artifact書込やmanifest CASの成功を台帳rollbackで取り消さない。artifactのみ成功、manifest成功後の応答喪失を再現し、停止済み世代を古い公開再試行で復活させない。
- 承認と公開は別操作。不変artifactとmanifest generation CASで公開する。停止もCASし、古い公開要求による復活を拒否。全読取はmanifest・版・hash・期限・読者を照合、不能時503、停止404、no-store。両AIは同じ読取アダプターを使用し、入力前・出力前にも再照合する。
- 外部検索・モデル生成・S3・会社Git接続を実装時に自動起動しない。機能は既定オフ。ローカルサーバーだけが明示`--enable-synthetic`で合成人物を認証する。合成認証をLambdaで有効にする環境変数は設けない。SAMへの配線はせず、実保存・認証設定が無いLambdaは503。

## 受入条件

合成3入口を投函→一覧→編集→Git保存→異なる確認者の特定版承認→正本反映→別操作公開→両AI読取→停止まで通す。再起動後も候補・版・操作・公開状態を保持する。未認証、閲覧だけのadmin、共有範囲外、偽造本人、自己承認、未確認根拠、同語別機種、版競合、同キー異要求、Git障害、Git成功後投影障害、manifest競合、期限切れ、停止後の引用・履歴再利用、manifest取得不能を否定検証する。

I1合格はAWS・実ブラウザ・会社Git・実データの技術受入を意味しない。`navigation_only`、cloudApproved文字列、旧メモリ編集画面を公開経路へ転用しない。
