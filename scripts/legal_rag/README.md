# e-Gov法令データ取込（開発PoC）

本ツールは対象カタログの現行版53法令だけを処理します。原文XMLは`raw/egov/<law-id>/<version-folder>.xml`へ保存し、検索本文は`kb/egov/<law-id>/<version-folder>/<provision_type>/<unit-number>.txt`へ生成します。本文には章節、項・号構造を保持し、各ファイルの`.metadata.json`に`source_url`と`provision_reference`を記録します。このスクリプトはKB Syncを実行しません。

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

- `infrastructure/sam/legal-rag-kb-template.yaml`はTitan Text Embeddings V2、1024次元/FLOAT32、300 tokens/20% overlap、Managed S3 connectorを定義します。Connectorは`kb/egov/`だけを参照し、さらに`<version-folder>/<provision_type>/<5桁>.txt`の新形式のみを索引対象とします。旧形式106文書はS3に保持されますが、このPoC KBからは除外されます。
- `infrastructure/sam/phase2-template.yaml`の`LawKnowledgeBaseId`と`LawRagEnabled`でRAG Lambdaへ接続します。`LawRagEnabled`は既定false、Lambda gateは`Environment=dev`でなければ拒否します。Amplifyの`itai` branchだけ`NEXT_PUBLIC_LAW_RAG_ENABLED=true`を設定し、本番には設定しません。
- CloudFormation resourcesにはRetainを設定し、DataSourceのdata deletion policyもRETAINです。終了時の削除は別途確認してから実施し、source bucket/XML/manifestは明示合意なしに削除しません。

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

このPoCでは`--prune-legacy-derived`を付けません。旧形式のTXT/sidecarはS3 Versioningを含めて保持し、新しいManaged KBのinclusion patternで索引から除外します。旧オブジェクトを削除する場合は別途明示承認を得てから実行してください。

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

アップロードとKB初回SyncはいずれもAWS書き込みです。dev用の承認済みaccount/bucketだけで実施し、Sync前にinclusion patternが旧形式を除外することを確認してください。Sync scheduleは設定せず、手動Syncだけを使います。本番KB/本番利用者では使用しません。

## References

- [e-Gov XML一括ダウンロード](https://laws.e-gov.go.jp/bulkdownload/)
- [CloudFormation resource import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/import-resources-manually.html)
- [S3 default bucket encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)