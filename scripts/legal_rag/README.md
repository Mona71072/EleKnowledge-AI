# e-Gov law source upload

This PoC stores only the 53 current-version XML files listed in `docs/features/development/legal-rag-target-laws.md`. Other law versions remain local and are not uploaded. It stores immutable source XML under `raw/egov/`, generates UTF-8 search documents by provision type under `kb/egov/`, writes Bedrock metadata sidecars beside each text file, and uploads `manifest/laws.csv`. It does not synchronize a Knowledge Base.

## Preview

Run from the repository root. This validates all selected XML files, computes SHA-256 values, and performs no AWS calls:

```powershell
python .\scripts\legal_rag\upload_egov_laws.py --source-dir .\legal\all_xml
```

## Create the development bucket

The template enables versioning, SSE-KMS with the AWS-managed S3 key, bucket-owner-enforced ownership, all four S3 Block Public Access settings, and a TLS-only bucket policy. The bucket is retained if its stack is deleted.

```powershell
aws cloudformation deploy `
  --template-file infrastructure/sam/legal-rag-data-template.yaml `
  --stack-name eleknowledge-legal-rag-dev `
  --parameter-overrides Environment=dev `
  --region ap-northeast-1 `
  --profile <development-profile>
```

Read the `LawDataBucketName` stack output for the generated bucket name. Do not use production credentials for this PoC.

## Upload

`--upload` is required for writes. The command also requires the expected 12-digit account ID and checks it against the active STS identity before contacting S3. It then verifies the bucket owner, SSE-KMS, versioning, ownership controls, and all four public-access blocks before uploading any objects.

```powershell
python .\scripts\legal_rag\upload_egov_laws.py `
  --source-dir .\legal\all_xml `
  --bucket <LawDataBucketName-output> `
  --expected-account-id <development-account-id> `
  --region ap-northeast-1 `
  --profile <development-profile> `
  --upload
```

Each source object includes its SHA-256, law ID, and effective date as S3 user metadata. The manifest is uploaded only after all XML uploads succeed. S3 versioning preserves previous object versions on re-runs.

## References

- [Boto3 `S3.Client.upload_file`](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/upload_file.html)
- [Boto3 S3 upload `ExtraArgs`](https://docs.aws.amazon.com/boto3/latest/reference/customizations/s3.html#boto3.s3.transfer.S3Transfer.ALLOWED_UPLOAD_ARGS)
- [S3 default bucket encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)