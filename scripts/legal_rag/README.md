# e-Gov法令データ取込（開発PoC）

本ツールは対象カタログの現行版53法令だけを処理します。原文XMLは`raw/egov/<law-id>/<version-folder>.xml`へ保存し、検索本文は`kb/egov/<law-id>/<version-folder>/<provision_type>/<unit-number>.txt`へ生成します。本文には章節、項・号構造を保持し、各ファイルの`.metadata.json`に`source_url`と`provision_reference`を記録します。このスクリプトはKB Syncを実行しません。

既定カタログ`docs/features/development/legal-rag-target-laws.md`を提供する#155と、実装#156は2026-10-09にdevelopへマージ済みです。既存devの試行・計測は[プレリリース手順](../../docs/legal-chat-prerelease.md)を参照してください。本番有効化・範囲拡大・追加同期・データ削除は引き続き今回の範囲外です。マージ前に初回Sync・実利用を待つとしていた計画と、下記の過去dev実験、今回の反映確認を区別します。

`retrieved_at`はXMLの取得日（ISO日付）で、アップロード時刻ではありません。`uploaded_at`は実行時にUTCで記録します。取得日が分からない場合、アップロード日を代用せず、取得記録を確認してから実行してください。

## Dry-run

リポジトリルートから実行します。AWSには接続せず、53 XML、条文本文、sidecarを検証します。

```powershell
python .\scripts\legal_rag\upload_egov_laws.py `
  --source-dir .\legal\all_xml `
  --retrieved-at 2026-10-01
```

2026-10-02にローカルの53 XMLで実行したdry-runは、条文/別表の検索本文10,321件（15,374,504 bytes）を生成しました。実費と運用工数を記録し、フィードバック/検索品質の価値が見合わないとmona / itaiが共同確認した場合はPoC終了を提案します。終了時はdev gateをOFFにし、Knowledge Base/DataSourceの削除方法・保持設定を確認してから片付けます。

## PoC Knowledge Baseの作成

法令PoCでは旧stack `eleknowledge-legal-rag-dev`を削除/再deployせず、保持済みbucketもCloudFormationへimportしません。KB用の独立stack `eleknowledge-law-kb-dev`が既存bucketを参照します。bucketは同じaccount/東京regionにあり、SSE-KMS、Versioning、全BPA、BucketOwnerEnforced、HTTPS拒否policyをupload前にread-back検証します。

- `infrastructure/sam/legal-rag-kb-template.yaml`はTitan Text Embeddings V2、1024次元/FLOAT32、300 tokens/20% overlap、Managed S3 connectorを定義します。Connectorは`kb/egov/`prefixを同期し、service roleの`GetObject`は同prefixに限定、`ListBucket`は同一accountに限定します。Bedrock filterとRAG post-filterは`document_granularity=provision_unit`と新形式`<version-folder>/<provision_type>/<5桁>.txt`を必須とするため、旧形式106文書はS3に保持したまま回答候補から除外します。
- `infrastructure/sam/phase2-template.yaml`の`LawKnowledgeBaseId`と`LawRagEnabled`でRAG Lambdaへ接続します。`LawRagEnabled`は既定false、Lambda gateは`Environment=dev`でなければ拒否します。Amplifyの`itai` branchだけ`NEXT_PUBLIC_LAW_RAG_ENABLED=true`を設定し、本番には設定しません。
- CloudFormationのKnowledge Base/DataSource resourcesにはRetainを設定します。Managed Knowledge BaseのDataSourceは`DataDeletionPolicy=DELETE`のみ対応するため、DataSourceを明示削除するとmanaged index dataは削除されます。終了時の削除は別途確認してから実施し、source bucket/XML/manifestは明示合意なしに削除しません。

CloudFormation change setを作成し、Law Knowledge Base、service role、S3 DataSource以外の意図しない変更がないことを確認してから実行します。旧stack/bucketの削除・importはこのPoCでは行いません。

## Upload

書き込みには`--upload`、AWS profile、期待するaccount ID、取得日が必要です。起動前に意図した開発profileでSTS identityを確認してください。ツールはS3書き込み前にbucket owner、SSE-KMS、Versioning、全4つのBPA、BucketOwnerEnforced、TLS拒否policyを検証します。policy未設定やHTTPを拒否しない状態では停止します。

```powershell
$profile = "DEVELOPMENT_PROFILE"
$identity = aws sts get-caller-identity --profile $profile | ConvertFrom-Json
$accountId = $identity.Account

python .\scripts\legal_rag\upload_egov_laws.py `
  --source-dir .\legal\all_xml `
  --retrieved-at 2026-10-01 `
  --bucket "EXISTING_LAW_BUCKET_NAME" `
  --expected-account-id $accountId `
  --region ap-northeast-1 `
  --profile $profile `
  --upload
```

このPoCでは`--prune-legacy-derived`を付けません。旧形式のTXT/sidecarはS3 Versioningを含めて保持します。Connectorはprefix全体を同期し、旧形式は`document_granularity=provision_unit`検索filterとRAG post-filterで回答候補から除外します。旧オブジェクトを削除する場合は別途明示承認を得てから実行してください。

```powershell
python .\scripts\legal_rag\upload_egov_laws.py `
  --source-dir .\legal\all_xml `
  --retrieved-at 2026-10-01 `
  --bucket "EXISTING_LAW_BUCKET_NAME" `
  --expected-account-id $accountId `
  --region ap-northeast-1 `
  --profile $profile `
  --upload `
  --prune-legacy-derived
```

アップロードとKB初回SyncはいずれもAWS書き込みです。dev用の承認済みaccount/bucketだけで実施し、Sync前に新形式のsidecarへ`document_granularity=provision_unit`を付け、検索filterとRAG post-filterの旧形式除外を確認してください。Sync scheduleは設定せず、手動Syncだけを使います。本番KB/本番利用者では使用しません。

## 開発PoCの実測記録

> 最終検証: 2026-10-02 — S3 upload完了、CloudFormation、Managed KB実取得、unit tests、SDK同梱修正後の認証済み法令送信を確認。全E2Eシナリオは未実施。

- KB/DataSource: `1F28EBODSH` / `PCPKDZDGTV`。prefix-only更新後も同じDataSource IDを維持。
- S3: raw XML 53件、条文本文・sidecar各10,321件、旧aggregate本文・sidecar各106件、manifest 1件。prune/deleteなし。
- regex設定で0件scanだったためprefix-onlyへ更新。同期job `0SGJYH3M2F`は`COMPLETE`、本文・metadata各10,427件scan、10,427件新規索引、失敗・削除・skipは0件。
- Managed KB実応答は`_source_uri` / `_chunk_id`を使用し、S3 URIはHTTPS形式。法令取得入口だけで共通metadataキーと内部`s3://`形式へ正規化する。通常KBの契約は変更しない。
- 公開後のLambdaログで`ParamValidationError`を確認。ランタイム標準SDKが`managedSearchConfiguration`を認識していなかったため、RagFunctionへ検証済み`boto3==1.43.38` / `botocore==1.43.77`を固定・同梱する。ローカルSDKでの取得成功だけをLambda実行の検証とは扱わず、build成果物のSDKモデルとデプロイ後の実送信を確認する。
- SDK修正は`law-sdk-fix-20261002` change setでdevへ反映し、`UPDATE_COMPLETE`。変更はRagFunction/RagApiだけで置換なし、gate true・既存パラメータ・IAMを保持。build成果物のみを使ったSDKモデル検証と、共有ブラウザーの認証済み法令送信で回答・e-Gov出典・履歴表示を確認。修正反映後のログに同じSDK検証エラーはない。
- 完成した索引で労働時間、昇降機、高所作業の代表3質問を実装経由で取得し、各post-filter後5件、e-Gov出典5件、出典へのS3 URI混入0件を確認。全法令の回答品質評価ではない。
- Phase2は`UPDATE_COMPLETE`、dev gate `true`、Sonnet5とLaw KB IDを保持。`itai` branchだけ公開flagを追加し、RELEASE job 25のBUILD/DEPLOY/VERIFYがすべて`SUCCEED`。ブラウザー描画で法令カードとプレリリース表示を確認。本番は変更していない。
- 実コードで法令取得からSonnet5回答生成まで確認し、e-Gov出典10件、内部S3 URI漏出0件、履歴書込み0件。デプロイ済みLambda roleの法令KB Retrieve権限は`allowed`。JWTなしの公開法令APIは401。
- backend unit tests 442件成功（既存deprecation warnings 6件）。Next.js buildは18 routes成功。直接Lambdaのgate-off確認は`403 FeatureUnavailable`であり、Cognito認証UI E2Eの代替にはしない。

## 条文リンク改修（dev反映済み）

> 最終検証: 2026-10-02 — 回帰テスト、S3 metadata読み戻し、KB再同期完了、認証済みitai法令チャットの正式見出し/直接リンク表示とe-Gov対象条文への移動を確認

本則の条文には版指定URLを維持した直接リンクを生成し、本文の出典とsidecarの`source_url`へ同じURLを保存します。例:`https://laws.e-gov.go.jp/law/325CO0000000338/20251201_507CO0000000377#Mp-Ch_5_4-Se_2-At_129_13_3`。

- 確認済み8階層のみ対応します。本則直下の条、章/条、章/節/条、章/節/款/条、章/節/款/目/条、編/章/条、編/章/節/条、編/章/節/款/条が対象です。
- 附則・経過措置・別表・未知の階層・番号欠損/不正値は、元の版指定法令URLに戻します。
- `Num="29:31"`などの範囲指定も全体URLへ戻し、正式見出しを保持します。対象本則7,229文書のうち24文書が範囲指定のため、直接リンクの対象は7,205文書です。
- 本則の表示と`provision_reference`はXMLの`ArticleTitle`を使います。見出しが欠けた場合は省略し、数字から条文名を推測しません。
- 回答時のAPI呼出しは増やしません。既存API/画面が`source_url`と正式見出しを受け渡します。
- 反映には派生本文/sidecarの再生成・S3更新と手動KB同期が必要です。原文XMLや旧aggregateを削除せず、保存済みの過去回答も書き換えません。上の公開・索引記録は改修前の結果であり、この改修の実環境反映を意味しません。

ローカル改修後の検証結果: unit tests 463件成功（既存deprecation warnings 6件）。対象53 XMLから10,321本文とsidecarを生成し、本則の直接リンク7,205件・範囲指定の全体リンク24件・非本則の全体リンク3,092件を確認しました。本文とmetadataの出典URLは一致し、元の版指定を維持、sidecar最大容量は2,065 bytes（上限10 KB）です。

2026-10-02のdev反映結果:

- S3更新時刻は`2026-10-02T11:43:06Z`。原文XML 53件（内容を保持）、本文/sidecar各10,321件、manifestを更新し、旧aggregate本文/sidecar各106件を保持。削除処理なし。
- 再同期job `DGXCWFHOWN`は`COMPLETE`。本文・metadata各10,427件scan、変更本文10,321件・metadata変更10,321件、新規・削除・失敗・skipは0件。
- 認証済みitaiの新規法令チャットで「第百二十九条の十三の三」の正式見出しと`#Mp-Ch_5_4-Se_2-At_129_13_3`付き出典を確認。そのURLからe-Govの対象条文へ移動できることも確認。
- 既存API/画面のmetadata受け渡しで反映できるため、今回はデータ更新によるデプロイのみ。Lambda/Amplifyのコード再デプロイ、本番変更、過去回答の書換えは行わない。ソース修正は実装PRでレビューする。

## 既知不具合と案Bのdev反映

> 最終検証: 2026-10-02 — 481 unit tests、cfn-lint、6条文の実S3/KB参照、認証済みitaiの5送信、実LambdaログとIAM境界を確認

既知の参照不足・原因・影響・A/B/C比較の正本は`docs/features/development/legal-rag-design.md`の「既知の不具合: 収録済み条文の参照不足」。KB取込失敗ではなく、関連チャンク検索と同一本文2チャンク制限により後半がモデルへ渡らない事象だった。

- 案Bは検索で採用した法令本文だけをS3から全文補完し、生成と引用に同じ参照集合を使う。全文6本文、単体8,000文字/32KB、合計20,000文字。補完時間枠は2秒、生成時間を確保できない場合は部分参照へ戻す。
- `LawDataBucketName` / `LawDataBucketKmsKeyArn`はdev法令有効時だけGetObject/Decryptを許可し、構成bucket・owner・版指定の派生TXTキーだけを読める。raw XML読取り・書込みは追加しない。通常RAGは変更しない。
- 上限/読取り失敗は部分参照としてプロンプトと出典へ状態/理由を渡す。`law_reference_coverage`ログはrequest IDと件数/理由/文字数のみ。質問・引用全文・個人情報は出さない。
- dev change set `law-full-text-20261002`は`UPDATE_COMPLETE`。実変更はRagFunctionのCode/EnvironmentとRagLambdaRoleのPolicies、置換なし。SDK同梱を維持し、本番変更・KB再同期・S3再uploadは行っていない。
- 481テスト成功、実S3/KBの6条文で最終項の参照保持、認証済みAPIの5送信で対象6条文の全文状態と後半の要件回答を確認。実ログのサーバー処理9.57〜25.95秒、参照本文3,455〜10,495文字/送信。これは速度目標達成や法的正確性の認定ではない。
- 残課題は速度/実費の継続評価、検索に当たらない名指し条文・関連条文の補完（案C）、巨大本文などの部分参照。実装と共同確認用設計は別PRでレビューする。

## develop向けPRの検証範囲

2026-10-02に最新developへ法令専用コミットとSDK/条文リンク/全文補完の修正だけを統合した。itaiの未マージ管理画面などの別テーマは取り込まない。PR用checkoutではunit tests 381件成功（既存deprecation warnings 6件）、4つの関連SAM templateのcfn-lint成功、Next.js build/lint/型検査は17 routes成功、diff check成功。上の481テスト・18 routesなどはデプロイ用integration checkoutの実測であり、PR checkoutの結果とは区別する。

既存frontend lockfileのnpm auditにはnext（moderate）、postcss（high）、tar（critical）の3件があり、このPRではpackage/lockを変更していない。マージ前の技術確認事項として残し、自動依存更新や修正済みとの記載はしない。dev backend/itaiの実測結果は保持するが、このレビューbranch単体を現在のitaiへデプロイして別テーマを巻き戻さない。次のSAMは合意後の統合済みbranchから既存モデル・IP/throttle・法令パラメータを保持して変更セットを検査する。

CIと同じfrontend logic testsは27件成功。`npm run audit:production`は既存のpostcss例外（Issue #120、2026-10-16まで）で通過し、新たな例外は追加していない。全依存auditの3件を解消済みとは扱わず、例外の期限と対応は引き続きレビュー対象とする。

## References

- [e-Gov XML一括ダウンロード](https://laws.e-gov.go.jp/bulkdownload/)
- [CloudFormation resource import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/import-resources-manually.html)
- [S3 default bucket encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
