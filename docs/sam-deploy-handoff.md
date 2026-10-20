---
status: draft
last-verified: 2026-10-20
related-code: infrastructure/sam/, .github/workflows/ci.yml, amplify.yml
---

# mona向け SAMデプロイ手順（itaiの運用記録をもとに）

検証範囲: リポジトリ内の設定・運用記録とAWS公式ドキュメントの照合。今回AWSへの接続、変更セット作成、デプロイ、実機試験は行っていない。現在のAWS状態は作業時に確認する。

## 1. 最初に押さえること

Gitへのマージと、バックエンドのAWS反映は別の作業。Amplifyは接続ブランチのフロントを自動配信するが、Lambda・API Gateway・DynamoDBなどのSAM変更は別途適用する。

itaiの記録に共通する流れは、**対象コミットを固定 → 現状保存 → ビルド → 変更セット作成 → 差分と適用範囲を確認 → 同じ変更セットを実行 → 実機確認 → 記録**。

- 通常の運用記録では `sam build` → `sam deploy --no-execute-changeset` → 確認 → `execute-change-set` を使用する。
- 2026-10-14〜15の作業記録では、既存パラメーターを `UsePreviousValue` で保持し、`sam package` とCloudFormationの変更セットを使っている。既存環境の差分を保つため、反映対象を限定した例もある。
- 本書では、値の保持を明示できる後者を詳しく説明する。特定の個人用スクリプトや認証設定のコピーを前提にしない。
- 既存dev環境の更新が対象。空環境の新規構築は [AWS Migration Runbook](aws-migration-runbook.md) を参照する。旧 [deployment-guide.md](deployment-guide.md) と [deployment.md](deployment.md) は非現行で、旧リージョンの手順を含む。

現行の担当・承認・時間帯の条件は [AGENTS.md](../AGENTS.md) と [AI駆動開発の運用](ops-ai-driven-dev.md) の「マージ担当」を参照する。本書はmonaへの説明用であり、SAM担当の変更や個別デプロイの承認を兼ねない。

## 2. どのテンプレートを使うか

以下はdevの既存名称の例。**実際のCloudFormationスタックとPRを照合してから選ぶ**。スタック名の打ち間違いで別スタックを作らないよう、後述の例は `UPDATE` に固定する。

| 変更するもの | テンプレート（`infrastructure/sam/` 配下） | スタック名の例 |
|---|---|---|
| 認証・基盤テーブル・S3 | `phase1-template.yaml` | `EleKnowledge-dev-phase1` |
| RAG・チャットAPI/Lambda | `phase2-template.yaml` | `EleKnowledge-dev-phase2` |
| トラブルシューティング | `phase3-template.yaml` | `troubleshooting-dev` |
| お知らせ・利用状況集計 | `announcements-monitoring-template.yaml` | `announcements-monitoring-dev` |
| 監視・アラーム | `monitoring-template.yaml` | `eleknowledge-monitoring-dev` |
| チャットアーカイブ | `chat-archive-template.yaml` | `eleknowledge-chat-archive-dev` |
| WAF | `security-waf-template.yaml` | スタック一覧から実名を確認 |

初回構築はPhase 1 → Phase 2 / Phase 3の参照関係を確認する。通常更新では必要なスタックだけを選ぶ。監視・WAF・アーカイブはAPI ID、通知先、DynamoDB Stream ARNなどの依存もあるので、上から全部を順番に実行しない。

## 3. 準備（最初の一度と作業ごとの確認）

### 3.1 ツールと作業場所

Windows PowerShellの例。AWS CLI v2、SAM CLI、テンプレートのRuntimeに合うPythonを用意する。今回参照したLambdaは主に `python3.13`。コンテナビルドを使う場合はDockerの起動も必要。

```powershell
git --version
aws --version
sam --version
python --version
```

各コマンドの失敗はその場で解消する。**PowerShellの `$ErrorActionPreference` だけでは外部コマンドの失敗で停止しない場合がある**ため、以下では重要なコマンドの直後に `$LASTEXITCODE` を確認する。

承認対象コミットを置いた、変更のない専用チェックアウトのリポジトリルートで作業する。既存作業があるディレクトリを `reset` / 一括 `stash` して準備しない。

```powershell
git status --short -uno
git rev-parse HEAD
git log -1 --oneline
```

未追跡ファイルも対象ディレクトリを絞って確認する。コミット、CI、PRの対象が一致し、Lint・Type Check・Test Passとドキュメント更新要否を確認済みであること。今回の手順書だけを作る場合はアプリのテストを再実行する必要はない。

### 3.2 個人設定はローカルだけに置く

各自のAWS認証方式でログインする。IAM Identity Center / SSOを使っている場合だけ `aws sso login --profile <自分のプロファイル>` を実行する。itaiのプロファイル名や認証情報をmonaへコピーしない。

以下の `<...>` を自分の環境の確認済み値に置き換える。アカウントID・バケット名・通知メール・IP制限値を共有文書やPRに貼らない。

```powershell
$DeployProfile = '<自分のAWSプロファイル>'
$ExpectedAccountId = '<反映先として確認したアカウントID>'
$DeployRegion = 'ap-northeast-1'
$StackName = 'EleKnowledge-dev-phase2'
$SourceTemplate = 'infrastructure/sam/phase2-template.yaml'
$ArtifactsBucket = '<既存のSAM成果物バケット>'
$DeployCommit = (git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'コミット取得失敗' }

$identityJson = aws sts get-caller-identity --profile $DeployProfile --region $DeployRegion --output json
if ($LASTEXITCODE -ne 0) { throw 'AWS認証失敗。ログインを確認する' }
$identity = $identityJson | ConvertFrom-Json
if ($identity.Account -ne $ExpectedAccountId) { throw '反映先アカウントが違う' }
# ローカル画面でAccountとArnの主体・ロールを確認する
$identity | Select-Object Account, Arn

aws s3api head-bucket --bucket $ArtifactsBucket --expected-bucket-owner $ExpectedAccountId --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) { throw '成果物バケットの所有者・権限・存在を確認する' }
```

この環境には、SAMの自動バケット作成が組織SCPの `s3:PutBucketPublicAccessBlock` 拒否で失敗した記録がある。**既存成果物バケットを使う**。`resolve_s3 = true` が設定から混入しないよう、下記の独立した最小設定と `--no-resolve-s3` を使う。SCPの現状は再検証していない。バケット新設・組織制御変更は、この更新手順に混ぜない。

## 4. 反映前の現状を保存する

以下は同じPowerShellセッションで順に実行する。保存先はGit管理外の `.aws-sam/`。実値やテンプレートを含むため添付・コミットしない。`git check-ignore` で実際に除外されることも確認する。

```powershell
$RunId = Get-Date -Format 'yyyyMMdd-HHmmss'
$EvidenceDir = Join-Path (Get-Location) ".aws-sam/handoff/$StackName-$RunId"
New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

git check-ignore "$EvidenceDir/before.json"
if ($LASTEXITCODE -ne 0) { throw '証跡の保存先がGit除外対象でない' }

$beforeJson = aws cloudformation describe-stacks --stack-name $StackName --profile $DeployProfile --region $DeployRegion --output json
if ($LASTEXITCODE -ne 0) { throw '既存スタックを取得できない。新規作成へ切り替えない' }
[IO.File]::WriteAllText("$EvidenceDir/before.json", ($beforeJson -join "`n"), $Utf8NoBom)
$BeforeStack = ($beforeJson | ConvertFrom-Json).Stacks[0]
if ($BeforeStack.StackStatus -notin @('CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE')) {
    throw "更新できる状態でない: $($BeforeStack.StackStatus)"
}

$originalJson = aws cloudformation get-template --stack-name $StackName --template-stage Original --profile $DeployProfile --region $DeployRegion --output json
if ($LASTEXITCODE -ne 0) { throw '旧テンプレート保存失敗' }
[IO.File]::WriteAllText("$EvidenceDir/original.json", ($originalJson -join "`n"), $Utf8NoBom)
```

ローカルで次も控える。

- 既存パラメーター、Outputs、リソースの実体ID。
- 更新対象Lambdaの `CodeSha256`、Runtime、環境変数、ロール、タイムアウト・メモリ。
- Phase 2ならKB ID、モデルID、モデル能力設定、法令モードなどのフラグ。CloudFormationパラメーターと実Lambdaの値を照合する。コードを更新するときは、`RagLogicVersion` を今回の検証済みソースのGit SHAに更新する。
- お知らせ・集計ならテーブルごとのTTL。**`metrics-dev` は無効、`announcements-dev` は有効**という記録・テンプレートを混同しない。
- アーカイブなら現行Stream ARN、イベントソースマッピング、S3失敗先、Glue定義、削除予定キューの滞留数。

**パラメーター保持だけでは、手作業で変更されたLambda環境変数やコードは保持できない。** 実環境とソースに差がある場合は、次節の全体ビルドをそのまま適用せず、8章へ進む。

## 5. 検証・ビルド・アップロード

対象ソースと現状の差が整理できている場合の例。`build` はローカル、`package` からはS3への書込みが発生する。まだLambdaやテーブルは更新しない。

```powershell
$SamConfig = "$EvidenceDir/samconfig.toml"
[IO.File]::WriteAllText($SamConfig, "version = 0.1`n", $Utf8NoBom)
$BuildDir = "$EvidenceDir/build"
$BuiltTemplate = "$BuildDir/template.yaml"
$PackagedTemplate = "$EvidenceDir/packaged.yaml"

sam validate --lint --template-file $SourceTemplate --config-file $SamConfig --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) { throw 'SAM検証失敗' }

sam build --template-file $SourceTemplate --build-dir $BuildDir --no-cached --config-file $SamConfig
if ($LASTEXITCODE -ne 0) { throw 'SAMビルド失敗' }
if (-not (Test-Path -LiteralPath $BuiltTemplate)) { throw 'ビルド済みテンプレートがない' }

sam package --template-file $BuiltTemplate --output-template-file $PackagedTemplate --s3-bucket $ArtifactsBucket --s3-prefix "handoff/$StackName/$RunId" --no-resolve-s3 --config-file $SamConfig --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) { throw 'パッケージ失敗' }

$TemplateKey = "handoff/$StackName/$RunId/packaged.yaml"
aws s3 cp $PackagedTemplate "s3://$ArtifactsBucket/$TemplateKey" --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) { throw 'テンプレートアップロード失敗' }
$TemplateUrl = "https://$ArtifactsBucket.s3.$DeployRegion.amazonaws.com/$TemplateKey"
```

`sam validate --lint` に必要な `cfn-lint` がない場合は開発環境に用意する。Lambda実行依存へ追加しない。Pythonやネイティブ依存の互換性問題は、Runtimeとアーキテクチャを合わせて `sam build --use-container` を検討する。ビルド後は**ソース版ではなく `$BuiltTemplate` をpackageする**。依存ライブラリの入っていないコードだけを送る事故を防ぐ。

WAFのようにLambdaコードを持たない通常のCloudFormationテンプレートは、`sam build` の代わりに通常のテンプレート検証を行い、元テンプレートをアップロードする。上のLambda用ブロックをそのまま使わない。

## 6. 変更セットを作り、内容を読む

### 6.1 既存値は維持、変更する値だけ明示する

以下は既存パラメーターをすべて `UsePreviousValue = true` とし、`$PlannedOverrides` の項目だけを変更する。`NoEcho` の秘匿値も読み出して再入力する必要がない。テンプレートから削除したパラメーターは送信対象から外し、新しい必須パラメーターは承認済み値を追加してから作成する。

```powershell
# 原則として既存値を保持する。Phase 2の版は今回のソースへ更新する。
$PlannedOverrides = @{}
if ((Split-Path -Leaf $SourceTemplate) -eq 'phase2-template.yaml') {
    $PlannedOverrides['RagLogicVersion'] = $DeployCommit
}
# 例: $PlannedOverrides['PresignedUrlExpiresIn'] = '300'
# 例示値を今回の承認済み変更と取り違えないこと。

$Parameters = @(
    foreach ($p in $BeforeStack.Parameters) {
        if (-not $PlannedOverrides.ContainsKey($p.ParameterKey)) {
            @{ ParameterKey = $p.ParameterKey; UsePreviousValue = $true }
        }
    }
    foreach ($key in $PlannedOverrides.Keys) {
        @{ ParameterKey = $key; ParameterValue = [string]$PlannedOverrides[$key] }
    }
)
$ChangeSetName = "handoff-$RunId"
$request = @{
    StackName = $StackName
    ChangeSetName = $ChangeSetName
    ChangeSetType = 'UPDATE'
    TemplateURL = $TemplateUrl
    Capabilities = @('CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM')
    Parameters = $Parameters
    Description = "commit=$DeployCommit; reviewed backend update"
}
$RequestPath = "$EvidenceDir/create-change-set.json"
[IO.File]::WriteAllText($RequestPath, ($request | ConvertTo-Json -Depth 20), $Utf8NoBom)

aws cloudformation create-change-set --cli-input-json "file://$RequestPath" --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) { throw '変更セット作成要求失敗' }

aws cloudformation wait change-set-create-complete --stack-name $StackName --change-set-name $ChangeSetName --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) {
    aws cloudformation describe-change-set --stack-name $StackName --change-set-name $ChangeSetName --profile $DeployProfile --region $DeployRegion --query '{Status:Status,Reason:StatusReason}'
    throw '変更セットを確認する。変更なしと実エラーを区別する'
}

$changeJson = aws cloudformation describe-change-set --stack-name $StackName --change-set-name $ChangeSetName --include-property-values --profile $DeployProfile --region $DeployRegion --output json
if ($LASTEXITCODE -ne 0) { throw '変更セット取得失敗' }
[IO.File]::WriteAllText("$EvidenceDir/change-set.json", ($changeJson -join "`n"), $Utf8NoBom)
$ChangeSet = $changeJson | ConvertFrom-Json
$ChangeSetId = $ChangeSet.ChangeSetId
$ChangeSet.Changes | ForEach-Object { $_.ResourceChange } |
    Select-Object Action, LogicalResourceId, ResourceType, Replacement
```

CLIが `--include-property-values` に未対応ならCLI v2の更新を確認するか、コンソールの変更セット詳細でプロパティ差分を見る。変更セット作成自体もAWS操作で、S3成果物と変更セットが残る。

### 6.2 実行前に読む場所と止まる条件

| 確認する場所 | 見る内容・止まる条件 |
|---|---|
| Parameters | 維持する値と変更する値が意図どおり。テンプレートのDefault変更だけで既存値が変わるとは考えない |
| Changesの全行 | Add / Modify / Removeが依頼範囲と一致。無関係なLambdaのCodeや環境変数が変わるなら止める |
| Replacement | `True` / `Conditional` は止めて影響確認。`False` でもTTL・IAM・コード差分は読む |
| データ資源 | テーブル、S3、Cognitoの置換・削除、TTL有効化、名前変更は独断で進めない |
| IAM / WAF | 権限拡大、Resource条件の消失、IP制限変更を確認。IAM承認フラグは安全性の保証ではない |
| API Gateway | 新ルート、認証、permissionを確認。SAM生成DeploymentのAdd/Removeは起こり得るが、想定したAPI更新かを読む |
| 依存関係 | Export利用、Stream ARN、通知先、失敗先などを維持。GSI追加と既存データ移行を別々に確認 |

変更セットは実行成功の保証ではない。権限・クォータ・実行時依存によって適用が失敗することもある。

実行前に、対象コミット・スタック・変更一覧・影響・戻し方・必要な未完了試験を共有して、**この具体的なAWS適用**の承認範囲を確認する。PRの内容承認やマージ許可だけをAWS適用許可へ読み替えない。既にその範囲の明示承認があるなら、重ねて承認を求める必要はない。

作成後に時間が空いた、別の人がデプロイした、対象ソースを変更した場合は現状を再取得して作り直す。古い変更セットをそのまま実行しない。

## 7. 同じ変更セットを実行し、完了を確認する

**ここからLambda・API・テーブルなどの実環境に変更が入る。** 直前に認証主体・アカウントとスタック状態を再確認する。確認後に別の `sam deploy` を走らせず、レビューした `$ChangeSetId` を指定する。

```powershell
aws cloudformation describe-change-set --stack-name $StackName --change-set-name $ChangeSetId --profile $DeployProfile --region $DeployRegion --query '{Stack:StackName,Status:Status,Execution:ExecutionStatus}'
if ($LASTEXITCODE -ne 0) { throw '変更セット再確認失敗' }
# 対象一致、CREATE_COMPLETE / AVAILABLE、レビュー後の別更新なしを確認して次へ

aws cloudformation execute-change-set --stack-name $StackName --change-set-name $ChangeSetId --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) { throw '変更セット実行要求失敗' }

aws cloudformation wait stack-update-complete --stack-name $StackName --profile $DeployProfile --region $DeployRegion
if ($LASTEXITCODE -ne 0) {
    aws cloudformation describe-stack-events --stack-name $StackName --profile $DeployProfile --region $DeployRegion --query 'StackEvents[0:25].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' --output table
    throw '更新未完了。失敗理由を確認する'
}

aws cloudformation describe-stacks --stack-name $StackName --profile $DeployProfile --region $DeployRegion --query 'Stacks[0].{Status:StackStatus,Outputs:Outputs}' --output json
if ($LASTEXITCODE -ne 0) { throw '更新後確認失敗' }
```

waitのタイムアウトは必ずしも更新失敗ではない。状態とイベントを見て、進行中なら監視を続ける。**executeの終了コード0は、更新完了を意味しない**。

その後、対象ごとに次を確認する。

- Lambda: `LastUpdateStatus=Successful`、`State=Active`、想定したCodeSha256・環境変数・モデル・KBを読み戻す。Phase 2は `RAG_LOGIC_VERSION` が今回指定したSHAであり、実行ログの `ragLogicVersion` がその値で `unknown` でないことも確認する。変更対象外の関数も必要に応じて前後比較する。
- API: 未認証401、権限不足403、正しい利用者の成功、不正入力400など、該当API仕様の期待値を確認する。WAFの403とアプリの403を分ける。
- RAG: ブラウザでログイン → 質問 → 引用を開く → 履歴の再表示。ほかの利用者のデータが見えないことも確認する。
- データ: 期待するTTL・GSI・Stream・失敗先を読み戻す。GSI追加完了と、旧データの移行完了は別。承認なしに移行を実行しない。
- 監視: CloudWatchのエラー・5xx・応答時間を確認。SNSは購読確認と実際の通知配信試験を区別する。
- フロント: 対応コミットのAmplifyビルドが成功したか確認。API先行が必要な変更はバックエンドを先に反映する。

合成claimsを使ったLambda直接試験は、認証済みHTTP試験やブラウザE2Eの代わりにはしない。未実施の試験は未実施と記録する。

## 8. 実環境とソースがずれていた場合（itaiの限定反映）

2026-10-15のお知らせAPI先行反映では、稼働中のOriginalテンプレートを基準にし、対象LambdaとIAMなど必要箇所だけを取り込んだ。集計移行や別機能の設定変更を混ぜずに反映した記録がある。

これは通常更新より判断が必要な対応なので、テンプレートの文字列を機械的にコピーして済ませない。

1. 現行OriginalテンプレートとRuntime設定、適用したいPRの差分を比較する。
2. 保持すべき設定・対象外リソース・今回の変更対象を明示する。
3. 対象Lambdaのビルド成果物、IAM、APIルート、permission、Globalsや参照先まで依存を確認して候補テンプレートを作る。
4. ローカルCodeUriは**候補テンプレートの保存位置からの相対パス**になる。別ディレクトリへ置く場合は絶対パスなどに調整し、既存のS3 CodeUriは保持する。
5. 検証・package後、6章と同様に変更セットを作る。対象外のコードSHA・環境変数・実体ID・TTLに変化がないことを確認する。
6. 承認済み範囲だけを適用し、採用ソースと保持した設定、後でソースへ整合させる課題を記録する。

「古いdevelopを丸ごとdeploy」「Lambdaのコードだけ直接更新」で場当たり的に解消しない。限定反映の候補を安全に説明できなければ、itaiと差分を確認してから続ける。

## 9. `sam deploy` を使う通常経路との対応

5〜6章のpackage＋CloudFormationを、通常は `sam deploy --no-execute-changeset` にまとめられる。**同じ作業で両方を重ねて実行する必要はない**。次はコマンド構成の例であり、今回用のパラメーター一覧を組み立ててから使用する。

```powershell
# $SamParameterOverrides は今回維持・変更する承認済み値の配列。
# Environment、ProjectName、KB、モデル、各機能フラグなどを確認して準備する。
# Phase 2では "RagLogicVersion=$DeployCommit" も必ず含める。
# 秘匿値・複雑なJSON値を含む場合は6章の方式を使う。
sam deploy --template-file $BuiltTemplate --stack-name $StackName --s3-bucket $ArtifactsBucket --no-resolve-s3 --s3-prefix "handoff/$StackName/$RunId" --config-file $SamConfig --profile $DeployProfile --region $DeployRegion --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --no-execute-changeset --parameter-overrides $SamParameterOverrides
if ($LASTEXITCODE -ne 0) { throw '変更セット作成結果を確認する' }
```

CLIの `--parameter-overrides` はsamconfig内の同名一覧と項目単位でマージされない。省いた既存値の扱いを推測せず、作られた変更セットのParametersで確認する。既存パラメーターが保持され、Defaultの変更だけでは反映されなかった実例もある。

既存の監視系ローカル設定を使う場合は、作業対象コミットの `samconfig-*.example.toml` から各自の `.local.toml` を作り、Git除外を確認する。設定の参照パスはテンプレート配置に依存するため、公式仕様と `sam ... --help` を確認する。本書の例は絶対パスの最小設定で、ルートや別スタックのsamconfig混入を避けている。

## 10. あるあるミスと対策

| ミス・症状 | 原因・対策 |
|---|---|
| マージしたのにAPIが古い | AmplifyとSAMは別。バックエンド適用とフロント反映をそれぞれ確認 |
| 違うアカウント・リージョンへ反映 | 全AWSコマンドでprofile/regionを明示。STSのAccount・Arnを毎回照合 |
| SSO期限切れ・AccessDenied | 自分のログインとロールを確認。SCPの明示Denyは権限追加だけでは解決しない |
| S3自動作成でROLLBACK_COMPLETE | 既存バケット指定＋ `--no-resolve-s3`。失敗した管理スタックを独断で削除しない |
| `--s3-bucket` とresolve_s3が競合 | samconfigからtrueが混入していないか確認。最小設定またはローカル設定を明示 |
| 別のsamconfig・スタックを拾う | 作業場所とtemplate/config/stackの組合せを確認。単に `sam deploy` だけを実行しない |
| Defaultを変えたのにTTLなどが変わらない | 既存値が保持される場合がある。変更値を明示し、Parametersと実環境を読み戻す |
| RAGログの版が古い / unknown | `RagLogicVersion` を検証済みソースのSHAへ更新し、Lambda環境変数と実行ログを読み戻す。旧版をUsePreviousValueで保持しない |
| KB・モデル・機能フラグが元に戻る | テンプレート、既存パラメーター、手動変更の違いを確認。UsePreviousValueだけではRuntimeの手動差分は守れない |
| 他のLambdaまで更新される | 同じスタックの全コードが候補になる。変更セット全行を読み、無関係な更新なら限定反映を検討 |
| ビルド成功なのにライブラリ不足 | ソーステンプレートをdeployした、または古い成果物を使用。ビルド済みtemplateからpackageする |
| PythonPipBuilder / ネイティブ依存エラー | Python版、PATH、Runtime、アーキテクチャを合わせる。必要ならDockerでビルド |
| PowerShellの途中行だけ実行される | Bashの `\` は継続文字ではない。長いコマンドは一行か引数配列で実行。バッククォート末尾の空白にも注意 |
| JSON/TOMLの文字化け・解析エラー | 証跡JSONはUTF-8 BOMなし。WindowsのSAM設定のコードページ差にも注意し、TOMLのコメントはASCIIを基本にする |
| `No changes to deploy` / 変更セットFAILED | 変更なしが理由か、権限・参照などの実エラーかをStatusReasonで区別。エラーを全部無視しない |
| Replace/Removeでデータが消える | 置換・削除・TTLを止めて影響確認。Retainがあっても無影響とは限らない |
| metricsのTTLを再有効化 | 無効化済み状態を候補へ保持。announcementsの有効なTTLと混同しない |
| Export cannot be deleted | 他スタックのImportが残っている。依存を調査して段階的に変更し、強引に削除しない |
| 新画面だけ先に公開して404 | 必要なAPI・権限を先行反映するか互換性を用意。前後双方のコミットを記録 |
| 更新完了なのに403 / 500 | WAF、JWT、アプリ認可、IAM、Bedrock、Lambdaエラーを分けて確認。制限を外して解消しない |
| 通知が来ない | SNSの購読がPendingではないか、発行許可・対象・実配信を確認 |
| GSI追加済みだから移行も完了と判断 | 旧行にキー属性がない場合は自動で索引化されない。別の移行手順・承認・件数照合が必要 |
| 実値入りの証跡をPRに添付 | Git除外されたローカル証跡に保持。共有するのは秘匿値を除いた変更概要と結果 |

## 11. 失敗時と戻し方

1. エラー後は連打せず、StackStatusとイベントの最初の失敗原因を確認する。
2. `UPDATE_ROLLBACK_IN_PROGRESS` は復旧完了を待つ。`UPDATE_ROLLBACK_COMPLETE` は更新失敗後に戻った状態で、今回の成功ではない。
3. `UPDATE_ROLLBACK_FAILED` はitaiと原因を確認してから `continue-update-rollback` を検討する。resources-to-skipは不整合を残すため通常手順にしない。
4. `ROLLBACK_COMPLETE` の既存業務スタックを復旧目的で削除しない。データ・依存・保持設定を確認して個別に判断する。
5. 更新成功後に不具合があった場合は、旧コミットだけでなく、**当時のモデル・環境変数・パラメーターを組にして**戻す候補を作る。旧ビルド成果物のS3存在も確認する。
6. 戻すときも変更セットを作って差分・承認範囲を確認する。データ移行・TTLによる削除などはコードを戻すだけでは復元できない。

共有KBは読取り利用の記録がある。デプロイの動作確認としてKB同期や共有S3への書込みを実行しない。

## 12. 完了記録（共有用テンプレート）

```text
日時: YYYY-MM-DD HH:mm JST
担当 / 対象: mona または itai / dev / スタック名
PR / コミット: #... / SHA
承認根拠: 対象変更セットのAWS適用を認めたコメント等
変更内容: 追加・更新・削除、保持した重要設定
変更セット: 名前（ARNや実値は必要な共有範囲に限定）
結果: UPDATE_COMPLETE / 失敗・復旧状態
確認: コード・設定の読み戻し、HTTP、ブラウザE2E、監視
未確認: 実施していない試験と次の対応
フロント: Amplifyの対象コミットと反映結果
戻し方: 旧コミット・成果物・設定の保存先（ローカル証跡は添付しない）
```

## 13. 根拠と参照先

プロジェクト固有の根拠:

- [運用ランブック §8](ops-runbook.md#8-デプロイとロールバック): 変更セット確認、TTL事故、設定とコードを組にしたロールバック。
- [AWS Migration Runbook](aws-migration-runbook.md): 既存S3成果物バケット、SCPによる制約、構築順、KB保持。過去時点の値は現在のAWSと再照合する。
- [2026-08-26実機確認記録](verification-2026-08-26-rag-citation-live-test.md): Default変更だけではTTL変更が反映されず、明示指定で反映した実例。
- `infrastructure/sam/` の各テンプレート、samconfigと `.github/workflows/ci.yml`: このチェックアウトの実装・設定。別コミットの設定を混ぜない。
- 端末限定の2026-10-14〜15引継ぎ記録も照合した。UsePreviousValue、package、変更セット、限定反映、適用後読取りの実施記録を本書へ一般化している。個人設定・実値・端末限定ファイルへの参照は共有手順へ持ち込んでいない。

AWS公式の確認先:

- [sam build](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html): ビルド出力とコンテナビルド。
- [sam package](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-package.html): コードと依存をS3へ送り、参照を置換したテンプレートを生成。
- [sam deploy](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html): 変更セット作成と実行、S3・config・パラメーター指定。
- [SAM設定ファイル](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-config.html): 設定の探索・優先関係。
- [create-change-set](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-change-set.html): UsePreviousValueとTemplateURLの指定。
- [変更セットの実行](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-execute.html): 確認した変更セットの適用。
- [ロールバックの再開](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-continueupdaterollback.html): UPDATE_ROLLBACK_FAILED時の復旧。

## 14. itaiがdevで実施した操作を順に追う

> 最終検証: 2026-10-20 — 10/14〜15の実行スクリプト、保存済み変更セット・読み戻し結果と照合。以下の再実行用コマンドは構文確認のみで、今回AWSへは実行していない。

### 14.1 成功した作業と、今回の再実行例の区別

実際にはWindowsの専用worktreeで対象版を固定し、AWS CLI / SAM CLIとPython（boto3）を組み合わせた。現状保存・変更セット作成・適用直前の条件照合・読み戻しは作業用Pythonで行い、`sam package`で既存の非公開成果物バケットへコードを送った。共有していない個人用スクリプトをmonaが持っている前提にはしない。以下は**その判断順を、3〜7章のPowerShellで追うための操作手順**であり、当時のコマンド文字列をそのまま再実行するものではない。

| 実施例 | 作業場所・入力 | 実際の変更と結果 |
|---|---|---|
| 10/14 法令全文補完（#177） | #177 `f80aee27`と当時のdevelop `20871803`を保持した専用チェックアウトのルート。`phase2-template.yaml`、既存`EleKnowledge-dev-phase2` | 既存パラメーターを保持し、既存法令データバケットの接続値を設定。API / Lambda / IAMのModify 5件、置換なしで適用。UPDATE_COMPLETE後、直接Lambda試験200・参照10件（全文6 / 部分4）。認証済みHTTP・ブラウザE2Eは未実施 |
| 10/15 アーカイブ復旧（#169） | マージ済み#169相当の専用チェックアウトのルート。`chat-archive-template.yaml`、`eleknowledge-chat-archive-dev` | 既存パラメーターとStreamを保持。失敗先をSQSからS3へ変更。空の旧キュー等を削除し、UPDATE_COMPLETE。S3 / IAM / EventBridge / SNS設定を読み戻した。失敗通知の実配信試験は未実施 |
| 10/15 お知らせAPI先行反映（#182） | #182と当時のdevelop `53c621f8`を保持した専用チェックアウトのルート。`announcements-monitoring-template.yaml`、`announcements-monitoring-dev` | 稼働中Originalを基準にwrite Lambda / ロールだけを更新。API・permissionも更新し、テーブルと集計コードは保持。UPDATE_COMPLETE後、未認証HTTP401、合成claimsによる直接Lambda試験403 / 200 / 400とページングを確認。認証済みHTTP・ブラウザE2Eは未実施 |

10/14の#177反映はGitHubマージ前の承認済みdev試行である。マージ済み・本番反映済みとは読み替えない。[#177の記録](https://github.com/yukiworkspace/EleKnowledge-AI/pull/177)、[#169の復旧記録](https://github.com/yukiworkspace/EleKnowledge-AI/pull/169)、[#182の先行反映記録](https://github.com/yukiworkspace/EleKnowledge-AI/pull/182)を実施範囲の根拠にする。これらの成功は、現在のPRを同じ変更一覧で適用できる保証ではない。

### 14.2 まず反映する1スタックとソースを固定する

RAG変更ならPhase 1からやり直さず、既存`EleKnowledge-dev-phase2`を選ぶ。アーカイブやお知らせ変更なら上表の対応スタックだけを選ぶ。承認対象コミットを専用チェックアウトへ用意し、その**リポジトリルート**を作業ディレクトリにする。`infrastructure/sam/`や別のworktreeをカレントにしたまま実行しない。

1. 3.1のツール確認と`git status` / `git rev-parse HEAD`で、対象ソースと未コミット差分なしを確認する。
2. 3.2の変数を今回の反映対象へ設定する。共通の選択はリージョン`ap-northeast-1`、既存スタックの更新、既存の非公開成果物バケット。**プロファイルはitaiの名前をコピーせず、自分が利用を許可された反映先アカウントのもの**を選ぶ。
3. `sts get-caller-identity`のAccountとArnをローカルで照合する。違う主体ならここで止める。
4. 成果物バケットは反映先で既に使用中のSAM用を選ぶ。アプリの資料バケットや法令データバケットへ置き換えない。所有者付き`head-bucket`で確認する。分からなければitaiとローカルで照合し、名前を推測しない。

次のメモを**各自の未追跡ローカル設定**へ記入してから進む。個人名・プロファイル名・実アカウントID・バケット名をこの共有文書へ転記しない（AGENTS.md「共有ルールと個人設定の境界」）。

| ローカルで確定する項目 | 照合先 |
|---|---|
| ソースの絶対パス、Git SHA、PR番号 | 専用チェックアウトとPRの検証済みhead |
| 自分のAWSプロファイル、期待するAccount・ロール | 利用を許可された認証設定とSTS結果 |
| 既存成果物バケット | 当該環境のSAMローカル設定・既存成果物の配置。所有者確認も行う |
| スタック、テンプレート、変更パラメーター | PRの適用範囲、上表、今回の現状保存 |

### 14.3 現状を保存し、保持する値を決める

4章を実行して`before.json`と`original.json`を保存する。当時の作業ではこれに加え、`list-stack-resources`と対象Lambdaの設定を保存していた。以下を4章の直後に実行する。

```powershell
$resourceJson = aws cloudformation list-stack-resources --stack-name $StackName --profile $DeployProfile --region $DeployRegion --output json
if ($LASTEXITCODE -ne 0) { throw '実体ID取得失敗' }
[IO.File]::WriteAllText("$EvidenceDir/resources-before.json", ($resourceJson -join "`n"), $Utf8NoBom)
$ResourceIds = @{}
($resourceJson | ConvertFrom-Json).StackResourceSummaries | ForEach-Object {
    $ResourceIds[$_.LogicalResourceId] = $_.PhysicalResourceId
}
# Phase 2の例。他スタックなら今回更新するLambdaの論理IDへ置き換える。
foreach ($logicalId in @('RagFunction', 'ChatManagementFunction')) {
    if (-not $ResourceIds.ContainsKey($logicalId)) { throw "対象Lambdaがない: $logicalId" }
    $configJson = aws lambda get-function-configuration --function-name $ResourceIds[$logicalId] --profile $DeployProfile --region $DeployRegion --output json
    if ($LASTEXITCODE -ne 0) { throw "Lambda設定保存失敗: $logicalId" }
    [IO.File]::WriteAllText("$EvidenceDir/$logicalId-before.json", ($configJson -join "`n"), $Utf8NoBom)
}
```

保持するのはスタックParametersだけではない。実Lambdaのモデル、KB、法令フラグ、CodeSha256、ロールも対象ソースと照合する。#177では既存法令データソースの所有者と`kb/egov/`を確かめ、接続値だけ追加し、KB新設・同期は行わなかった。#182では全体適用すると集計移行を混ぜるため、Originalからwrite Lambda / ロールのPropertiesだけを差し替える候補にした。**差が説明できなければ5章へ進まず、8章で限定反映を準備する。**

### 14.4 build / packageから変更セット作成まで

1. 5章を順に実行する。通常更新の再実行例は`sam validate --lint` → `sam build --no-cached` → **build配下のtemplateを**`sam package` → packaged templateを既存S3へ配置、の順。限定反映では8章で準備した候補と対応するビルド成果物を使い、稼働中S3 CodeUriを保持する。
2. `resolve_s3`混入を避け、最小設定と`--no-resolve-s3`を使う。10/15のアーカイブpackageでもこの指定が必要だった。ローカルの設定だけを変えてSCPを回避したり、バケットを作り直したりしない。
3. 6.1で`$PlannedOverrides`を決め、既存の他項目をすべて`UsePreviousValue`にする。**今回のPhase 2コード更新では`RagLogicVersion=$DeployCommit`を明示する。** 10/14の既存値保持を、そのまま版ラベルも保持する指示として使わない。既存機能フラグやモデルをテンプレートのDefaultへ戻さない。
4. 既存のCloudFormationサービスロールがある場合は、6.1の`$request`作成後・JSON保存前に次を加える。当時の作成スクリプトもRoleARNがある場合に引き継いでいる。

```powershell
if ($BeforeStack.RoleARN) { $request['RoleARN'] = $BeforeStack.RoleARN }
```

5. 6.1の`create-change-set`と作成待機・`describe-change-set`を実行する。当時はpackage後のテンプレートが51,200 bytes未満であることを確認して`TemplateBody`で送った。5〜6章の`TemplateURL`方式は大きいテンプレートにも対応するための再実行例である。両方を同時に指定しない。

### 14.5 実行してよいと判断した条件

当時は`CREATE_COMPLETE / AVAILABLE`だけでは進めず、全リソースのActionとReplacementを予定一覧へ照合し、実行直前のParametersが保存時から不変であることを再確認した。

| 実例 | 許容した差分・直前条件 |
|---|---|
| #177 | `ChatApi` / `ChatManagementFunction` / `RagApi` / `RagFunction` / `RagLambdaRole`のModify 5件だけ。全Replacement=False、Add / Removeなし。Environment=dev、法令モード有効、保存時からパラメーター不変 |
| #169 | ArchiveBucket / Role / Function / Stream mapping / Glue表のModify、EventBridgeルールAdd、旧キューとアラームRemove。旧キューの可視・処理中・遅延がすべて0。Stream ARN一致。Glue表のConditionalは列追加だけ・名前と保存先維持を個別確認した例外で、一般的な実行許可ではない |
| #182 | write Lambda / IAM / AppApi / StageのModify（置換なし）、GET用permission Add、SAM生成API DeploymentのAdd / Removeだけ。metrics TTL=DISABLED、利用するGSI=ACTIVE、対象外4関数のCodeSha256を保存 |

現在のPRでは現在の予定一覧を作り直す。上表を許可リストとして流用しない。追加・置換・削除、IAM拡大、TTL変更、無関係なLambda更新が出たら止める。#169のような削除を含む変更は具体的な変更セットへの承認を確認してから実行した。

7章の実行直前に、次の比較も行う。**NoEcho値はマスクされたままなので、この比較だけでその値の不変までは証明できない。** 他の更新が入った場合や不明点がある場合は作り直す。

```powershell
$latestJson = aws cloudformation describe-stacks --stack-name $StackName --profile $DeployProfile --region $DeployRegion --output json
if ($LASTEXITCODE -ne 0) { throw '実行直前のスタック確認失敗' }
$LatestStack = ($latestJson | ConvertFrom-Json).Stacks[0]
if ($LatestStack.StackId -ne $BeforeStack.StackId -or $LatestStack.StackStatus -ne $BeforeStack.StackStatus -or
    $LatestStack.LastUpdatedTime -ne $BeforeStack.LastUpdatedTime) { throw '保存後にスタック状態が変わった' }
$beforeParameters = $BeforeStack.Parameters | Sort-Object ParameterKey | ConvertTo-Json -Depth 10 -Compress
$latestParameters = $LatestStack.Parameters | Sort-Object ParameterKey | ConvertTo-Json -Depth 10 -Compress
if ($beforeParameters -ne $latestParameters) { throw '保存後にパラメーターが変わった' }
```

### 14.6 同じ変更セットを実行し、UPDATE_COMPLETEの後も読む

7章の`execute-change-set` → `wait stack-update-complete` → `describe-stacks`を実行する。失敗したら14.7へ進み、別の`sam deploy`を重ねない。次の読取りはPhase 2の例で、14.3の`$ResourceIds`を使う。

```powershell
foreach ($logicalId in @('RagFunction', 'ChatManagementFunction')) {
    $afterJson = aws lambda get-function-configuration --function-name $ResourceIds[$logicalId] --profile $DeployProfile --region $DeployRegion --output json
    if ($LASTEXITCODE -ne 0) { throw "Lambda読み戻し失敗: $logicalId" }
    [IO.File]::WriteAllText("$EvidenceDir/$logicalId-after.json", ($afterJson -join "`n"), $Utf8NoBom)
    $after = $afterJson | ConvertFrom-Json
    if ($after.State -ne 'Active' -or $after.LastUpdateStatus -ne 'Successful') { throw "Lambda更新未完了: $logicalId" }
    if ($logicalId -eq 'RagFunction' -and $after.Environment.Variables.RAG_LOGIC_VERSION -ne $DeployCommit) {
        throw 'RAGの反映版が対象ソースと一致しない'
    }
    # before/afterをローカルで照合。更新対象は期待したコード版、対象外はCodeSha256不変を確認する。
}
```

さらに`list-stack-resources`を再取得し、置換しない予定のテーブル・S3・API等の実体IDが一致すること、変更したパラメーター以外が維持されていることを確認する。#169ではmapping Enabled / LastProcessingResult OK、S3失敗先、versioning / AES256 / EventBridge、IAMのResourceAccount条件とListBucket、SNS対象と発行許可、Glue列を確認した。#182では対象外4関数のコードSHA、テーブル / API実体ID、metrics無効 / announcements有効のTTLを読み戻した。

その後の確認は、次の3つを別々に記録する。当時の合成claims試験だけで「ログインからのE2E成功」と書かない。

1. **直接Lambda試験**: 許可された合成データで所有者・admin境界、200 / 400 / 403、RAG参照やページングを確認。既存会話を操作しない。
2. **HTTP試験**: 実APIで未認証拒否を確認。認証済みHTTPは許可されたテストアカウントで別途実施する。JWT・質問回答本文を共有ログへ出さない。
3. **ブラウザE2E**: Cognitoログイン → 画面 → 対象API → 応答を別途確認する。未実施なら未実施と残す。Amplifyの対象コミットとBUILD / DEPLOY / VERIFY成功も、バックエンド試験と別に記録する。

### 14.7 止まったときに次に見るコマンド

| 止まった場所 | 次に確認する操作 | 再実行せず止める条件 |
|---|---|---|
| 認証・所有者確認 | `aws sts get-caller-identity`、所有者指定の`aws s3api head-bucket`（3.2のprofile / regionを付ける） | アカウント違い、未許可ロール、所有者不一致、SCPの明示Deny。権限を広げて押し通さない |
| build / package | 失敗したSAMコマンドのエラー、Runtimeと`python --version`、built templateのCodeUri、`sam package --help` | 依存未解決、別worktreeの成果物、S3自動作成要求。ソースtemplateの直接deployへ切り替えない |
| 変更セット作成 | 6.1の`describe-change-set`のStatus / StatusReason | 変更なしなら適用不要。権限・参照エラーは解消まで停止。失敗を全部「変更なし」と扱わない |
| 差分確認 | `describe-change-set --include-property-values`と保存済みOriginal・Parameters | 予定外のAdd / Remove / Replacement、未承認IAM・TTL・コード差分、保存後の別更新 |
| execute後のwait | 下記のスタック状態・イベント読取り | UPDATE_ROLLBACK中は待機。UPDATE_ROLLBACK_COMPLETEは失敗として記録。UPDATE_ROLLBACK_FAILEDは11章へ。スタック削除で復旧しない |
| UPDATE_COMPLETE後 | Lambda設定読取り、API / permission / authorizer、必要なDynamoDB GSI / TTLとIAMを対象ごとに確認 | 版不一致、AccessDenied、404、機能フラグの戻り。認可やWAFを外して回避しない |

```powershell
aws cloudformation describe-stacks --stack-name $StackName --profile $DeployProfile --region $DeployRegion --query 'Stacks[0].StackStatus'
if ($LASTEXITCODE -ne 0) { throw 'スタック状態取得失敗' }
aws cloudformation describe-stack-events --stack-name $StackName --profile $DeployProfile --region $DeployRegion --query 'StackEvents[0:25].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' --output table
if ($LASTEXITCODE -ne 0) { throw 'イベント取得失敗' }
```

イベントの理由にも実リソース値が含まれることがあるため、確認はローカルで行う。12章の完了記録には、成功・ロールバック・未確認試験・次の担当を区別して残す。
