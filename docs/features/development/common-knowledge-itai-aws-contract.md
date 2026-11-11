---
status: development
last-verified: 2026-10-22
related-code:
  - lambda/knowledge/common-knowledge/
  - infrastructure/sam/common-knowledge-itai-template.yaml
  - tests/integration/test_common_knowledge_aws_adapters.py
  - frontend/src/lib/common-knowledge.mjs
  - frontend/src/components/knowledge/common-knowledge-inbox.tsx
  - scripts/knowledge/common-knowledge-cli.py
---

# 共通知識: itai専用AWS基盤の実装契約

> 最終検証: 2026-10-22 — 実装前にAWS読取（認証主体・既存itai/共有devスタック・WAF・Amplify itai）、#195/#200のhead・コメント、設計§17の保存hashを照合。実装・配備の結果は末尾の記録へ追記する。

[I1実装契約](common-knowledge-i1-contract.md)の業務ルールは変えず、保存・配布・正本・API配線をAWSで動く形へ移す。2026-10-22の[S3正本化の決定](common-knowledge-itai-s3-canonical-handoff.md)により、正本はGitではなくS3とする（次節。以降の節のGit記述は次節で置き換える）。方針の正本は設計worktreeのノウハウ設計§17。[引継ぎ](common-knowledge-itai-aws-handoff.md)の許可範囲（itai専用・非破壊・合成データのみ）を超える操作は本契約に含めない。

## S3正本化への改訂（2026-10-22）

> 最終検証: 2026-10-22 — ユーザー決定（引継ぎ§決定事項1〜8）と、共有Cognitoの読取（2アカウントのsub・グループ）に基づく実装前の契約。

| 項目 | 契約 |
| --- | --- |
| 作業用バケット（新設 `WorkBucket`） | `drafts/{knowledgeId}.md` が編集の場。バージョニング有効。開発エージェントが直接書けるのはここだけ。台帳は作業版を **VersionId＋sha256** で固定し、以後その特定版だけを確認・承認する（後から作業用を編集しても承認対象は変わらない）。バケットポリシーで全主体の `DeleteObjectVersion` を拒否し、固定した版を消せないようにする |
| 正本バケット（既存 `DistributionBucket` を流用、置換なし） | `approved/{id}/{rev}/{bundleHash}.md`（承認時に作業用の特定版を不変コピー）と同名 `.json`（承認記録）。`published/{id}.md` と `published/{id}.md.metadata.json`（Bedrock KB用 `metadataAttributes`）は公開中だけ存在する。`manifests/{id}.json` は世代CASと読取ガード用で、公開中の版の束（domain・audience・根拠・hash）を持つ。旧 `artifacts/` は書かない。KBの作成・同期は行わない |
| 正本への書込境界 | バケットポリシーで `approved/*` はeditorial・recovery、`manifests/*`・`published/*` はpublication・recoveryのLambdaロール以外の Put/Delete を拒否。全主体の `DeleteObjectVersion` を拒否。台帳はService（API・CLI）経由でだけ書く |
| 公開・停止の順序 | 承認版を `approved/` から読みhashを照合 → manifest CAS（停止は active=null）→ `published/` を **最新manifestに合わせて再投影**（manifestがnullなら削除、そうでなければ `approved/` から複製）。投影後にmanifestが変わっていれば再投影を繰り返す（有限回、尽きたら操作は受付のまま再試行）。manifest先行のため、停止は投影の失敗や古い公開の再試行で覆らない |
| 読取（RAG・開発エージェント） | manifest → `published/{id}.md` の順に読み、本文hashがmanifestの束と一致し、読む前後でmanifestが同じ場合だけ返す。`drafts/`・`approved/` を直接読んで代用しない。readerロールは `manifests/*`・`published/*` の取得だけ |
| 作業版の登録（CLI） | `scripts/knowledge/common-knowledge-cli.py register` が同じServiceを呼び、作業用の指定版（既定は最新版）を読み、検証して作業版として登録する。編集者は呼出し元のIAM主体（`iam:` ＋ STS ARN）。CLIで行えるのは登録・確認依頼・状態確認・公開版の読取。承認・公開・停止は正本書込を伴うためAPI（画面）だけ（CLIで受け付けるとバケットポリシーの拒否で操作が受付のまま残り、同じ対象を塞ぐため） |
| admin条件 | 撤廃。編集・承認・公開・一覧は認可表の業務権限・分野・読者・期限だけで判定する。adminに属するだけでは何もできない（I1の「adminだけでは不可」は維持）。共有Cognitoのグループは変更しない |
| 画面 | `/admin/knowledge` は、共通知識が有効なビルドでは非adminのログイン利用者も入れる（他のadmin画面は従来どおり）。実データガードは `NEXT_PUBLIC_COMMON_KNOWLEDGE_VALIDATION_SCOPE` に一致する分野・読者に限って解除する。画面に接続先APIと、`GET /knowledge/me` で得た自分の業務権限・共有許可・根拠台帳を表示し、ボタンを権限で出し分ける |
| 試験主体 | 本アカウント（開発用・admin所属）＝投稿・編集・公開・閲覧・読取。2つ目のアカウント（adminなし）＝承認・閲覧・読取。CLIのIAM主体＝編集・閲覧・読取。分野・読者は `itai-validation`、共有許可と根拠台帳は各1件、期限14日。subはCognitoから読取り、未追跡の作業記録にだけ置く |
| 廃止 | `GitMode` パラメータ、`remote_git.py`（GitHub互換アダプター候補）、`LocalGit`。ローカル合成はSQLiteの作業用・正本アダプターに置き換える |

IAM（改訂後）: editorialは作業用 `drafts/*` の Get/GetVersion/Put と正本 `approved/*` の Get/Put。publicationは `approved/*` の Get、`manifests/*` の Get/Put、`published/*` の Get/Put/Delete。readerは `manifests/*`・`published/*` の Get。recoveryはeditorialとpublicationの和。404判定のため各バケットの `ListBucket`（キー一覧はコードで使わない）。DynamoDBの権限は従来どおり。

## 配置と既存資源との関係

| 判断 | 内容 | 理由 |
| --- | --- | --- |
| 分離スタック | 新規 `EleKnowledge-itai-common-knowledge`。既存 `EleKnowledge-itai-phase2`（T2のRAG/チャット/調査）は更新しない | 既存itaiはT2生成テンプレートで、更新するとRAG側へ差分が波及する。役割（候補台帳・Git承認・公開）が異なる |
| 共有物 | Cognito User Pool ARNはExport参照、Regional WAFは既存ACLへの関連付けのみ、IP制限はAPI ResourcePolicy。WAF本体・IPSet・Cognito・共有devは変更しない | T2と同じ参照方式。共有devへの書込IAMを持たない |
| 名前 | 物理名はCloudFormation自動生成。stage `dev`。タグは `gyoumu012Project=ele-knowledge` / `gyoumu012Component=rag` / `gyoumu012Usage=development` / `Purpose=itai-common-knowledge-validation` | 既存区分値を流用し、新しい区分値は台帳の判断として作らない |
| 機能フラグ | `CommonKnowledgeEnabled=false`（既定・今回の配備値）。`GitMode` は `unconfigured` のみ許可 | 実ロール・保持・会社Gitが未決。Git必須操作は503 `GitNotConfigured` |

APIのフロント接続先（Amplify itai）は切り替えない。itaiブランチは自動配信ONで、API URLはアプリ共通値＝共有devを使っているため、接続切替はブランチ環境変数の追加という別操作になる。

## 保存の移植

Service内の直接SQLを廃し、台帳を「作業単位（unit）」と「一覧Query」のドメイン操作に分ける。SQLiteとDynamoDBの両アダプターが同じ契約を満たす。

- **unit**: `get` / `put` / `delete`、操作の `operation_by_key` / `operation` / `target_pending` / `accept_operation` / `finish_operation`。SQLiteは `BEGIN IMMEDIATE`。DynamoDBは強整合GetItemで読んだ版番号 `v` を記録し、書込を `TransactWriteItems` 1回へまとめる。読んだ項目は版一致、未存在で読んだ項目と新規項目は `attribute_not_exists` を条件にし、書かずに読んだ項目もConditionCheckで再検証する。条件不成立・競合は `Contention` とし、操作を拒否確定にせず503で同じ操作IDの再試行へ戻す。
- **冪等・ロック**: 操作本体、`actor+key` の一意項目、同一対象の未完了ロック項目を受付時に同じtransactionで作成。完了／拒否でロックを外す。完了後のjournalはI1と同じく要求本文を残さない。
- **一覧**: 候補は `StateIndex`（状態）と `SubmitterIndex`（本人＋状態）、未完了操作は `PendingIndex`（本人）。GSIは `KEYS_ONLY` で本文を投影しない。1回のQueryで得たキーを基底表から強整合で読み直し、状態・本人・期限・共有範囲を再検証する。無効項目はページから除き、短いページとcursorで続行する。cursorは最後の並び順キーをHMAC付きで返し、offsetは使わない。
- **期限**: APIが期限切れを返さない。保持年限は未決のため、業務データにTTL物理削除を設定しない。TTL属性は合成受入の名前空間だけが設定する。
- **配布**: 台帳と別のprivate S3。artifactは `If-None-Match: *` で不変、既存と同一内容なら成功・異なれば拒否。manifestは `If-Match` ETagでCAS。公開・停止の受付票を操作IDごとに保存し、次のCAS実行者は置き換える前に現行manifestの受付票を必ず作る。これにより、manifest成功後に応答や受付票の保存が失われても、停止後に古い公開の再試行が復活しない。412/409は再読込のうえ有限回で判定する。
- **Git**: `GitMode=unconfigured` では書込・読取・tree照合をすべて503で拒否する。GitHub互換REST（blob/tree/commit/非forceのref更新）のアダプターを実装候補として持つが、配備では選択できない。会社Gitの製品・ホスト・repo・path・資格情報が決まったら、ホスト許可・path許可・操作マーカーcommitの照合・ref競合時の有限再基底を受入してから有効化する。Lambdaの `/tmp` やローカルGitを正本にしない。

## API・Lambda・IAM（責任別）

| Lambda | ルート | 台帳 | 配布S3 | その他 |
| --- | --- | --- | --- | --- |
| intake | `POST/GET /knowledge/contributions`、`GET/PATCH .../{id}`、`GET /knowledge/operations`、`GET .../operations/{id}` | 読取・Query・transaction内の書込 | なし | cursor秘密のGetSecretValue |
| editorial | `GET /cards/{id}`、`PUT .../draft`、`POST .../review-requests`・`/decisions`・`/sample-checks`（2026-11-11 追加・未配備。[I1 契約](common-knowledge-i1-contract.md)の自己承認の例外） | 同上 | なし | Git（未設定のため権限なし） |
| publication | `POST .../publish`・`/withdraw` | 同上 | artifact/manifest/受付票のGet・Put | Git読取（同上） |
| reader | `GET /knowledge/published/{id}` | なし | artifact/manifestのGetのみ | なし |
| recovery | `POST /knowledge/operations/{id}/retry` | 同上 | publicationと同じ | 保存済み要求を元の操作として再認可する。新規操作は受けない |

全関数は認可表（別DynamoDB表）を `GetItem` だけで読む。認可表が空なら全操作403、共有許可も無いので投函も403。書込は `dynamodb:EnclosingOperation=TransactWriteItems` の条件付きで、単独の Put/Delete を許さない。Scanは許可しない。各Lambdaは自分の責任外のルートを404にする（API Gatewayの配線誤りへの二重防御）。

APIはCognito Authorizer必須、OPTIONSのみ認証なし。CORSは指定したHTTPS originだけ。stageのスロットリングを設定し、アクセスログはphase2と同じ本文・トークンなしの形式。応答は `no-store`。タイムアウト10秒・メモリ256MBはDynamoDB/S3の単発I/Oだけを前提にした暫定値で、Git連携方式を決めた時点で根拠を取り直す。

フロントは `NEXT_PUBLIC_COMMON_KNOWLEDGE_API_URL` にHTTPSのstage付きURL（例 `https://<api>/dev`）を受け付ける。合成モードは従来どおりループバックだけ。実データの投函・保存は引き続き「受入待ち」で止める。

## 受入条件

ローカル: 既存I1の合成テストがSQLite台帳で全て通る。同じシナリオがDynamoDB／S3の挙動を模したアダプターでも通る（3入口の公開・停止、Git成功後の投影失敗の再開、承認時刻の固定、artifactのみ成功、manifest成功後の停止競走、期限、manifest不能、ページング、未完了操作の復旧、同時更新は拒否確定にしない）。Git未設定・設定欠落・責任外ルートは拒否。Lint・型検査・SAM変換/lint・`git diff --check`。

AWS: 新規stackのCREATE changesetが全Addで、共有・既存itaiスタックの変更なし。完了後、暗号化・TLS強制・公開ブロック・バージョニング・PITR、IAMが上表どおり、Lambdaの配備コードが対象コミットと一致、フラグoff・Git未設定であることを確認する。未認証401、フラグoffの403、責任外ルート404を配備版で確認する。台帳とS3アダプターは配備した表・バケットに対し、合成の名前空間（自動失効付き）で上記シナリオを通す。このときGit区間はローカル合成Gitであり、会社Git連携の受入ではない。

未受入として分けて記録するもの: 会社Git連携と知識の一往復、実Cognito主体での画面操作・業務ロール割当、実データ・保持方針、IP外からの拒否の実査、Amplify itaiの接続切替、RAG／開発エージェントの実接続と有料品質検証。

## 費用・停止・rollback（反映前の見積り）

- 固定費: Secrets Manager 1件（約0.40 USD/月）。DynamoDB 2表・S3・Lambda・API Gatewayは従量で、合成受入の量ではほぼ0。PITRとS3バージョンは保存量比例。既存WAFへの関連付けで追加の固定料金はなく、通過リクエスト分のみ。
- 停止: `CommonKnowledgeEnabled=false` が既定。API stageのスロットリングで上限を固定。
- rollback: 本スタックは他スタックからExport参照されない。changeset作成で失敗した場合は実行しない。作成後の撤去が必要になった場合は、Retain指定の台帳表・認可表・配布バケットが残ることを確認したうえで、スタック削除とRetain資源の扱いを別途確認する（今回は削除しない）。

## 実施記録（2026-10-22）

> 最終検証: 2026-10-22 — ローカル試験、SAM変換/lint、changeset全ページ、配備後のAWS実査（設定・権限・配備コードhash・API・合成受入）。会社Git・実主体・実データ・ブラウザの受入ではない。

### 実装とローカル検証（コミット `a8c36504`、ローカルitai）

- 台帳をunit／一覧Queryへ分け、Service内の直接SQLを除去。SQLite（I1合成）とDynamoDBの2アダプター、S3配布、Git未設定アダプター、GitHub互換RESTの候補アダプター、設定検証factory、責任別ルートを実装。
- 当初案の「操作ごとの受付票」は、manifestの世代が単調増加し、manifestに記録した操作IDで現行版の再試行を判定できるため不要と判明して削除した（変異試験で、操作ID判定を外すと試験が落ち、受付票を外しても落ちないことを確認）。
- Git未設定は操作受付の前に503 `GitNotConfigured` で拒否する。受付後に拒否すると同じ要求の再送が永久に拒否され、対象ロックも残るため。
- 結果: 共通知識I1 16件・AWSアダプター（模擬）35件・SAM契約5件を含む関連Python 645件成功。フロントは型検査成功、Lintエラー0（既存警告4）、`node --test` 414件のうち成功410・失敗3（残り1件は未実行扱い）。失敗3件は `knowledge-index-check`（索引ビルダー）で、変更前の同一コミットの別worktreeでも同じ3件が失敗するため本変更とは無関係。cfn-lint 1.52.1 終了0、SAM変換後39リソース・全非OPTIONSルートにCognito、`git diff --check` 成功。
- 端末固有: pytestの既定一時領域が書込不可、長いパスでGitが失敗するため、`--basetemp` を作業用一時領域へ移し `core.longpaths` を環境変数で付与して実行した。リポジトリ設定は変えていない。

### AWSへの作成（itai専用・新規スタックのみ）

- 対象: スタック `EleKnowledge-itai-common-knowledge`（ap-northeast-1、SSOのitai利用者で実行）。`sam build` 後、配備物のファイルhashがコミットのblobと一致することを確認してから `sam package`（既存のSAM配備物バケットの専用prefixへ追加のみ）。
- changeset `create-a8c36504`（CREATE）: 1ページ・39件すべてAdd、Replacementなし、既存の物理リソースを指す変更なし。パラメータは `CommonKnowledgeEnabled=false`、`GitMode=unconfigured`。IP一覧は既存itaiスタックの現在値（共有devと同一の10件）を明示指定。実行後 `CREATE_COMPLETE`、失敗イベントなし。
- 作成物: 台帳表・認可表（いずれもRetain、SSE、PITR、台帳は3つのKEYS_ONLY GSIと合成専用TTL属性）、配布バケット（Retain、バージョニング、SSE-S3、所有者強制、TLS以外拒否、`acceptance/` だけ7日失効）、cursor用Secrets Manager 1件、REST API（stage `dev`、Cognito、IP ResourcePolicy、スロットリング 10/5、アクセスログ）、既存Regional WAFへの関連付け1件、Lambda 5・IAM Role 5・LogGroup 6・Lambda Permission 14。認可表は空のまま（実ロール未決のため何も書いていない）。
- 実行前後で共有dev phase1/phase2、既存itai phase2、itai KB v2の状態・最終更新時刻、WAF ACLのLockTokenとルール数が一致。

### 配備版の確認

| 項目 | 結果 |
| --- | --- |
| 配備コード | 5関数とも同一zip（CodeSha256 `VCqY97FFL/hyuPoSA8/SPJyCuJfEz0eTUSskwmwihTU=`）。zip内6ファイルのSHA256がコミット `a8c36504` のblobと一致 |
| 設定 | python3.13、10秒、256MB。全関数でフラグfalse・Git unconfigured。cursor秘密の参照はintakeだけ |
| IAM | 各Roleの実ポリシーが契約の表どおり。DynamoDBの書込はTransactWriteItems内に限定、Queryはintakeのindexのみ、readerは台帳権限なし |
| S3 | Block Public Access 4項目とも有効（SCPで明示設定できないため既定値を実査）、バージョニング、AES256、BucketOwnerEnforced、ポリシー非公開 |
| DynamoDB | 2表ともSSE・PITR有効。台帳のTTLは `acceptancePurgeAt` のみ、GSI 3つともKEYS_ONLY |
| API | トークンなし・不正形式・`synthetic-*`・署名なし（alg:none）の偽造JWTはすべて401。未定義ルート403。プリフライトとゲートウェイエラーのCORSはitai originだけ。新stageが既存Regional WAFに関連付け済み |
| Lambda直接呼出し | 合成イベント（書込なし）で5関数とも403 `FeatureUnavailable`・`no-store`。設定欠落の503ではなく、配備設定から実アダプターを構築できている |
| 合成受入（配備した表・バケット） | 3入口の公開→両AI読取→停止、Git成功後の投影失敗の再開（二重commitなし）、競合時に拒否確定せず再試行で完了、古い版の上書き拒否、artifactのみ成功／manifest成功後の応答喪失で停止後に復活しない、manifest取得不能503・期限切れ404、短いページ＋cursor、再起動後の未完了操作の復旧: 11件成功（2回実行）。データは合成名前空間のみで、S3は22オブジェクトすべて `acceptance/` 配下 |
| ログ | 5関数ともプラットフォーム行（INIT_START/START/END/REPORT）だけ。エラー・トークン・パス・本文なし |

接続値（アカウント、ARN、API URL、IP一覧、物理名）とchangeset全ページ・出力値は未追跡の `.private-knowhow/ck-aws/` に保存した。

### 未受入・判断待ち

- 会社Gitの製品・repo・path・資格情報（決定後、GitHub互換アダプターの採否と `GitMode` の許可値追加を別途レビュー）。Git必須操作は配備環境では503で止まる。知識の一往復（Git込み）は未受入。
- 実Cognito主体での操作、業務ロール・兼務の割当、保持年限、試行単元・読者。認可表は空で、フラグもoff。
- IP外からの拒否の実査、実ブラウザ、Amplify itaiの接続切替（itaiブランチは自動配信ON、API URLはアプリ共通値＝共有dev）。RAG／開発エージェントの実接続と有料品質検証。いずれも未実施。
- LambdaランタイムのSDKが条件付きPutの引数を受け付けることは、関数内の実書込では未確認（フラグoffのため）。同じ処理をローカルSDKから配備バケットに対して実行した結果は上表のとおり成功。

### 費用・停止・rollback

- 固定費はSecrets Manager 1件（約0.40 USD/月）。他は従量で、現状はAPIに接続した画面がなく、合成受入の読み書き・ログ・保存量だけ。PITR・S3バージョンは保存量に比例。WAFは既存ACLの通過リクエスト分のみ。単価はAWS料金表を今回照会しておらず、概算として扱う。
- 停止: フラグoffのまま。必要ならAPI stageのスロットリングを下げる更新で止められる。
- rollback: 本スタックは他から参照されず、共有物の変更もない。撤去する場合はスタック削除で API・Lambda・Role・ログ・秘密・WAF関連付けが消え、台帳表・認可表・配布バケットはRetainで残る。削除操作は今回行っておらず、実施時は残すRetain資源の扱いを別途確認する。合成データはTTL・ライフサイクルで7日以内に自動失効する。

## S3正本化の反映と受入（2026-10-22）

> 最終検証: 2026-10-22 — ローカル試験、changeset全ページ、配備後のAWS実査（設定・権限・配備コードhash・バケットポリシーの拒否・API）、実AWSでの合成受入、Amplify itaiの配信バンドル実査、2アカウントの実ブラウザ操作と台帳・S3の照合。

### 実装とローカル検証（`6d247a40` ほか、ローカルitai → origin/itai）

- 本書「S3正本化への改訂」節のとおり実装。共通知識の試験はPython 52件・フロント6件（合成UIのe2e含む）成功、型検査・cfn-lint・`git diff --check` 成功、Lintエラー0。収束ループを外すと同時停止の試験が落ちることを変異試験で確認。
- 全体試験の残る失敗は本変更と無関係: node 3件（既存の索引ビルダー、前回記録と同じ）、Python 2件（未変更のカードがWindows作業ツリーでCRLF）、法令アップロード29件は一時領域のパス長が原因で短いパスでは全件成功。

### AWS（itai専用スタックの更新2回。いずれもchangesetを全ページ確認後にユーザーが実行）

| changeset | 内容 | 結果 |
| --- | --- | --- |
| `s3-canonical-6d247a40` | 1ページ17件。Add: 作業用バケット・同ポリシー・`/me` の呼出権限・API Deployment。Modify 12（Replacementなし）。Remove: 旧API Deployment（ルート追加時のSAM標準の付け替え） | UPDATE_COMPLETE、失敗イベントなし |
| `flag-on-6d247a40` | `CommonKnowledgeEnabled=true` のみ。5関数の環境変数、API本体は関数ARNの動的再評価（再作成なし） | UPDATE_COMPLETE |

- 前後で共有dev phase1/phase2・既存itai phase2・Regional WAF（LockToken・ルール数）が一致。Cognitoは読取のみ。
- 配備コード: 5関数同一zip、5ファイルのhashがコミットと一致。フラグtrue。
- 両バケット: バージョニング、公開ブロック4項目、SSE-S3、所有者強制、非公開。
- 境界の実査: 個人SSO主体から正本の `approved/`・`published/`・`manifests/` への書込と作業用の版削除はすべてAccessDenied。作業用 `drafts/` への書込だけ可。
- API: トークンなし・偽造JWTは401、未定義ルート403。
- 実AWSでの合成受入: 13シナリオ成功（3入口の公開→両AI読取→停止、作業版の書込後の投影失敗の再開、競合の再試行、古い版の上書き拒否、manifest後の投影前障害で停止が覆らない、同時停止で `published/` が消える、manifest取得不能・期限、ページング、未完了操作の復旧、固定版が後の編集で変わらない）。データは `acceptance#…`／`acceptance/` だけ。
- 認可表: 本アカウント（閲覧・編集・公開・読取＋共有許可）、2つ目（閲覧・承認・読取）、CLIのIAM主体（閲覧・編集・読取）、合成の根拠台帳1件。範囲 `itai-validation`、期限2026-11-05。投入はユーザーが実行。
- CLI: 配備環境で `pending`・`read` が動作。操作者は `iam:assumed-role/…`（アカウントIDなし）。

### Amplify itai

- ブランチ環境変数だけでは、amplify.ymlに直書きのRAG/チャットURLが優先されることを配信バンドルで実査した。そのため amplify.yml に「`AWS_BRANCH=itai` かつ `ITAI_RAG_API_URL`／`ITAI_CHAT_API_URL` が両方HTTPSのときだけ上書き」する分岐を入れた（ユーザー承認、他ブランチの挙動は不変）。
- ブランチ変数: `ITAI_RAG_API_URL`・`ITAI_CHAT_API_URL`（itai phase2）、`NEXT_PUBLIC_COMMON_KNOWLEDGE_API_URL`、`NEXT_PUBLIC_ENABLE_COMMON_KNOWLEDGE=true`、`NEXT_PUBLIC_COMMON_KNOWLEDGE_VALIDATION_SCOPE=itai-validation`、既存の `NEXT_PUBLIC_LAW_RAG_ENABLED`。
- 配信バンドルにitai専用のRAG・チャット・共通知識APIだけが入り、共有devのRAG/チャットURLは0件。itai phase2のルートは共有devの全ルートを含む（RAGに先輩調査を追加）。チャット履歴はitai専用表になるため、共有devの過去の会話はitai画面に出ない。先輩調査・総合・現場報告のフラグはoffのまま。

### 実ブラウザ（2アカウント）

- 2つ目のアカウント（adminなし）が共通知識画面に入り、閲覧・承認できた。ホームの入口カードを追加し、URL直打ち不要にした。
- 一往復: 投函 → 編集引受 → 作業版保存 → 確認依頼 → 差し戻し → 再編集・再依頼 → 承認（2つ目）→ 公開 → 両アカウントで読取 → 停止 → 読取不可。台帳・S3の照合: 作業版4版がそれぞれ作業用バケットの別版に固定、承認は第4版で `approved/` に本文と承認記録、公開でmanifest世代1と `published/`（本文＋KB用metadata）、停止で世代2・active無し・`published/` は削除マーカー。
- 画面の改善（受入中に反映）: 権限の自動読込（未読込で編集欄が無効になる問題）、押せない理由の表示、操作結果を押したボタンの近くに成功・失敗・処理中で表示。
- 本アカウントで、itai専用APIでの先輩チャット（#195）の表示とチャット利用を確認。先輩チャットは「開発中・管理者限定」のままで、2つ目のアカウントでは表示されない（今回の決定範囲外）。

### 未受入・費用・停止・rollback

- 未受入: CLIでの作業版登録→確認依頼の実配備での一往復（ローカル試験のみ）、Bedrock KBの作成・同期（形式のみKB向け）、IP外からの拒否の実査、実データ・保持方針、専用編集画面（キーマン向け）。
- 費用: Secrets Manager 1件（約0.40 USD/月）に加え、作業用バケットの保存量・版数に比例する従量（現状数KB）。他は従来どおり従量で僅少。ブラウザ確認の質問によるBedrock呼出しのみ発生。料金表は今回照会していない概算。
- 停止: `CommonKnowledgeEnabled=false` の更新、または認可表の削除で全操作403。Amplifyは `ITAI_*` 変数を外せば共有devのRAG/チャットに戻る。
- rollback: スタックは他から参照されない。作業用バケットはRetain（固定した版を消さないため、版削除はポリシーで拒否）。公開中の知識はない（停止済み）。
