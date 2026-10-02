# e-Gov法令データ取込（開発PoC）

本ツールは対象カタログの現行版53法令だけを処理します。原文XMLは`raw/egov/`へ不変保存し、検索本文は条・附則条文・別表単位で`kb/egov/`へ生成します。本文には章節、項・号構造を保持し、各ファイルの`.metadata.json`に`provision_reference`を記録します。Bedrock KB側では設計書どおり固定サイズ300 tokens / 20% overlapで長い条文を分割してください。このスクリプトはKB Syncを実行しません。

`retrieved_at`はXMLの取得日（ISO日付）で、アップロード時刻ではありません。`uploaded_at`は実行時にUTCで記録します。取得日が分からない場合、アップロード日を代用せず、取得記録を確認してから実行してください。

## Dry-run

リポジトリルートから実行します。AWSには接続せず、53 XML、条文本文、sidecarを検証します。

```powershell
python .\scripts\legal_rag\upload_egov_laws.py `
  --source-dir .\legal\all_xml `
  --retrieved-at 2026-10-01
```

2026-10-02にローカルの53 XMLで実行したdry-runは、条文/別表の検索本文10,321件（15,374,504 bytes）を生成しました。Knowledge Baseの課金上限が未合意のため、この件数を費用見積りへ反映するまではKBを作成・Syncしません。PR #155が未mergeの間は、`--catalog`に#155の専用worktreeにあるカタログを明示してください。

## 既存開発bucketのCloudFormation import

2026-10-02のread-only確認では、旧stack `eleknowledge-legal-rag-dev` は`ROLLBACK_COMPLETE`、唯一のresource `LawDataBucket`は`DELETE_SKIPPED`でした。bucketには既存データがあり、ownerは開発profileと一致、SSE-KMS・Versioning・BPA・BucketOwnerEnforced・HTTPS拒否policyを確認しています。bucket policyは旧stack管理外です。stackを再deployしたり、同名bucketを作り直したり、保持データを削除したりしないでください。

既存bucketをIaC管理へ戻す案は、旧stackを整理して別stackへimportする二段階です。旧stackの削除はAWS操作です。実行前に全resourcesとDeletionPolicyを再確認し、ownerの明示承認を得てください。この手順書はAWS操作の承認を意味しません。

1. `describe-stacks` / `describe-stack-resources`を再確認し、旧stackが`ROLLBACK_COMPLETE`でbucket以外に残存resourceがないこと、bucketのRetainを確認する。想定と異なれば停止する。
2. 明示承認後のみ旧stackを削除し、S3 bucketとpolicyが残っていることを再確認する。削除前に現在のデータとpolicyを別途確認する。
3. 旧stackのlogical IDと実bucket名を取得し、`legal-rag-data-import-template.yaml`とresource identifierを使って、新stack `eleknowledge-legal-data-dev-managed` のIMPORT change setを作成する。import対象は`AWS::S3::Bucket`と`AWS::S3::BucketPolicy`。既存policyとtemplateが一致することを先に照合する。
4. change setにImport以外の作成・削除・更新がないことを確認してから実行し、完了後drift detectionを行う。import change setではresourceの作成・削除・property変更はできない。各import resourceには`DeletionPolicy`が必要。
5. import完了後、`legal-rag-data-template.yaml`で別stack updateを行い、bucket tagsを`Project=EleKnowledge`・`Env=dev`・`ManagedBy=SAM`に揃える。TLS policy、BPA、KMS、Versioning、ownership、tags、driftを再確認する。

AWS公式資料: [CloudFormation resource import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/import-resources-manually.html)、[import対応resource一覧](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html)。

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

初回KB Sync前に、`kb/egov/`内の新しい条文単位ファイル一覧と既存manifestを照合してください。旧形式のlaw-wide aggregate本文を置換する場合は、明示フラグ`--prune-legacy-derived`が必要です。このフラグは対象法令の旧形式の3種類の正確なファイル名とsidecarだけを、新しいファイルの書き込み後に削除します。S3 Versioningで過去versionは残ります。対象bucketとkey一覧を確認してから実行し、自動では削除しません。

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

旧派生ファイル整理と再アップロードはいずれもAWS書き込みです。承認済みの開発bucketだけで、KB Sync前に実施してください。PR #155の対象/費用合意と#156のレビューが完了するまで、KB Sync・法令の実利用は行いません。

## References

- [e-Gov XML一括ダウンロード](https://laws.e-gov.go.jp/bulkdownload/)
- [CloudFormation resource import](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/import-resources-manually.html)
- [S3 default bucket encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)