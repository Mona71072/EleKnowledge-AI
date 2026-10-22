---
status: development
last-verified: 2026-10-15
related-code: scripts/ops/apply_cost_allocation_tags.py, infrastructure/sam/
---

# コスト配分タグの運用

各リソースのタグ値・分類根拠・管理元は [リソース別台帳](cost-allocation-resource-register.md) を参照する。タグ定義と運用手順の正本は本書とする。

## 決定と適用範囲

> 最終検証: 2026-10-20 — Envタグ付与停止・環境パラメーター維持と同日のAWS適用結果への案内を照合。

2026-10-15、ユーザーが本会話で3軸の採用、AWS反映、文書化を依頼した。monaの口頭承諾はユーザー申告として記録する（承諾日そのものは未確認）。この記録はPRマージの許可を兼ねない。

共用AWSアカウント内で管理部門がタグ名を識別できるよう、キーを `gyoumu012` で始める。Ele-Knowledge専用リソースを対象とし、他プロジェクトとの共用リソースは所有者・配賦方法を確認するまで一括帰属させない。検索対象・資料・ユーザーの業務スコープは変更しない。

## キーと値

| キー | 値 | 意味 |
|---|---|---|
| `gyoumu012Project` | `ele-knowledge` | プロジェクトへの費用帰属 |
| `gyoumu012Component` | `rag`, `legal-rag`, `monitoring`, `shared`, `troubleshooting`, `announcements` | 通常RAG、法令RAG、監視、機能横断の共通基盤、トラブルシューティング、お知らせ |
| `gyoumu012Usage` | `development`, `user`, `shared` | 開発専用、ユーザー利用専用、両者共用 |

値は小文字・ハイフン区切りとする。機能が増えた場合は本表へ定義を追加してから使用する。トラブルシューティングは `troubleshooting`、お知らせは `announcements` として機能別の費用を保持する。

`Component=shared` と `Usage=shared` はそれぞれ機能間共用、利用区分間共用を意味する。未設定・帰属未確認を `shared` へ自動変換しない。`dev` というリソース名だけで `Usage=development` と判断しない。

本アカウントは単一環境で、本番は別AWSアカウントへリリースするため、`Env` はコスト配分の軸に含めない。SAMテンプレートと `samconfig` から `Env` リソースタグ・スタックタグの付与をやめる。SAMの `Environment` / `ProjectName` パラメータと、それらを使うリソース名・アプリ設定は維持する。2026-10-20のAWS適用範囲と残るタグは「2026-10-20のAWS反映・追加確認」を参照する。

## 初期分類と変更手順

2026-10-15、本会話でユーザーが初期分類を確認した。専用PoCの法令RAG・トラブルシューティングは `development`、通常RAG・認証・画面・監視等は `shared` とする。お知らせ・チャット履歴等の既存共通サービスも `shared` とする。

機能分類はリソースの役割、CloudFormationのスタック・論理ID、専用バケット等の根拠で決める。APIの実行ログは対応APIの分類を継承する。CloudWatchの監視アラームは監視対象の機能によらず `monitoring` とする。

配布資材バケットは作業時のデプロイ設定の `s3_bucket` と所有アカウントを照合し、既存共通基盤として `Component=shared` / `Usage=shared` を付与した。現在の共有設定例は `samconfig-monitoring.example.toml` / `samconfig-announcements-monitoring.example.toml` で、実バケット名は各自の未追跡 `.local.toml` で管理する。旧ProjectタグがないSAM生成APIは、Projectタグ付きスタック内の物理リソースIDとの一致で所有を確認する。

1. 認証主体・対象アカウント・リージョンを確認する。
2. 既存タグと対象一覧をローカルの未追跡領域へ退避し、追加する3タグの計画を確認する。
3. 既存タグの値を上書きせず、競合時は停止する。タグのみを追加し、アプリ・データ・IAM権限は変更しない。
4. AWS APIの部分失敗を確認し、サービス別APIでタグを再読取して検証する。
5. 新規作成・再デプロイで欠落しないようIaCにも同じタグを設定する。SAM APIは `PropagateTags: true` で生成ステージにもタグを渡す。Lambdaが暗黙作成するログなど、宣言済みIaCの外にあるリソースはデプロイ後に本スクリプトの計画・適用・検証を行う。法令KB・保持済みS3・既存推論プロファイル等の外部管理リソースも運用時に再確認する。
6. 月次でタグ未設定費用・共用費・直接帰属額を確認する。直接帰属実額と推計按分額を混ぜない。

操作例（プロファイル名・アカウントIDは各自のローカル設定から確認する）:

```powershell
$profileName = '<使用するプロファイル>'
$expectedAccount = '<確認済みの対象アカウントID>'
python scripts/ops/apply_cost_allocation_tags.py --profile $profileName --expected-account $expectedAccount --plan eval-results/cost-tags/review-plan.json
# JSON内の対象・既存タグ・desiredを確認してから実行する。
python scripts/ops/apply_cost_allocation_tags.py --profile $profileName --expected-account $expectedAccount --plan eval-results/cost-tags/review-plan.json --apply
python scripts/ops/apply_cost_allocation_tags.py --profile $profileName --expected-account $expectedAccount --plan eval-results/cost-tags/review-plan.json --verify
```

既定の初期分類は本書どおり。`--default-usage` / `--poc-usage` は利用実態を確認したときのみ指定する。既存の3キーと計画が競合した場合は上書きせず停止するため、分類変更は個別に差分を確認する。実行は `--expected-account` とSTSの一致を必須にする。対象リージョンの既定値は東京・バージニア・大阪であり、全AWSリージョンを監査したとは扱わない。

バックアップ・計画・結果はGit除外済みの `eval-results/cost-tags/` に置く。個別ARN・アカウントIDを含むためPRへ添付しない。戻す場合はバックアップと現在値を照合し、今回追加した3キーだけを復元対象としてレビューする。自動削除は行わない。

## コスト配分タグの有効化依頼

> 最終検証: 2026-10-20 — 19:41 JSTのCost Explorer API照会とAWS公式の管理アカウント条件を照合。有効化状態そのものは取得不可。

リソースへのタグ付与と、請求へのタグ有効化は別作業である。2026-10-15に続き、2026-10-20 19:41 JSTの `ce:ListCostAllocationTags` も `AccessDeniedException`（Linked account doesn't have access to cost allocation tags）だった。これは有効化状態を参照できないことを示し、無効であると判明したわけではない。

AWS Organizationsのメンバーアカウントからは、管理者権限があってもコスト配分タグ管理画面を利用できない。管理アカウントへログインできる担当者が「請求とコスト管理」→「コスト配分タグ」で3キーの `Active` を確認する。管理アカウントへのアクセスがなければ管理部門へ確認する。タグ付与成功を有効化済み・請求データ反映済みの証拠にはしない。

管理部門へ渡す依頼文（本タスクから送信はしない）:

> Ele-Knowledgeのコスト管理用として、アカウント識別接頭辞を付けた以下3キーをコスト配分タグとして有効化してください。
> `gyoumu012Project` / `gyoumu012Component` / `gyoumu012Usage`
> プロジェクト値は `ele-knowledge` です。環境はAWSアカウントで分離するため、コスト配分タグとして有効化するのは上記3キーのみです。`Env` はSAMから付与しません。
> 有効化日と、請求データで各キーを確認できた日をご連絡ください。

反映には時間差があるため、有効化後にCost Explorer / CURで確認する。バックフィルは管理アカウントから最大12か月を申請できるが、当時リソースに付いていたタグが対象であり、新キー付与前の期間を新キーで復元できるとは扱わない。

## 費用分離の限界と残作業

> 最終検証: 2026-10-20 — この節のCloudFormationタグ反映方法と法令KBスタックへの適用記録を照合。他の費用分離・モデル経路の残作業は再検証していない。

- 共用Lambda・API・S3等の開発／ユーザー利用はリソースタグだけでは分離できない。利用統計に基づく配賦、またはリソース分離が必要。配賦ルールは別途合意する。
- BedrockはApplication Inference Profileへタグを付け、実際にそのプロファイルを呼び出す経路の推論費を追跡する。KB・Lambdaへのタグのみで全推論費を帰属済みとはしない。埋め込み・再ランキング・Agent等も呼出経路別に確認する。
- 現在の `rag-dev` は `global.anthropic.claude-sonnet-5` を直接指定している。既存Application Inference Profileへ3タグを付けても、現在の生成推論費はそのプロファイルへ帰属しない。既存ランブック§7.2にはSCPによる利用拒否の記録があるため、今回はモデル・呼出経路・SCPを変更せず、従来のトークン数×単価による推計を継続する。SCP制約そのものは今回再現試験していない。
- 既存の外部スタック所有KB・S3・検索基盤は、他システムの費用を含み得るため今回の一括タグ付与対象外とする。
- CloudFormationスタック本体へのResource Groups Tagging APIによる変更は、更新処理を誘発する可能性があるため行わない。スタックタグは変更セットで適用範囲を確認して反映する。2026-10-20の法令KBスタックへの補完も、この方法で実施した。
- タグ非対応・継承タグのみの子リソース、税・サポート等は3タグだけで全額を直接帰属できるとはしない。
- プロジェクト予算・通知先・共用費の配賦方法は、タグ有効化と請求確認後に整備する。

## 実施記録

2026-10-15: 東京108件、バージニア1件、大阪0件の既存 `Project=EleKnowledge` タグ付きリソースを棚卸し。旧 `Project=EleKnowledge-AI` の法令専用S3、未タグの専用Lambdaログ、SAM生成API・ステージ、配布資材S3を追加で確認した。

**東京104件へ3タグを付与し、104件すべての再読取一致と既存タグ保持を確認。失敗0件。** 内訳:

| Component | 件数 | Usage |
|---|---:|---|
| `rag` | 9 | `shared` |
| `legal-rag` | 2 | `development` |
| `monitoring` | 38 | `shared` |
| `shared` | 35 | `shared` |
| `troubleshooting` | 12 | `development` |
| `announcements` | 8 | `shared` |

Usage別は `shared` 90件、`development` 14件、`user` 0件。これはタグ付与リソース数であり、課金明細数・費用比率ではない。CloudFormationスタック本体7件、DynamoDB Stream2件、予算メタデータ1件を直接書込から除外した。IAMロール等の非課金メタデータを含めた全リソース棚卸しではない。

初回は書込直後のResource Groups Tagging API再読取でLambda・DynamoDBに遅延が見られたため、サービス別APIによる再確認で一致を確認した。API・ステージもサービス別APIで検証した。管理アカウントでの有効化、請求データへの出現、共有基盤の配賦、生成推論費の直接帰属は未完了であり、この104件の成功と区別する。

変更前・計画・実行結果はローカルの `eval-results/cost-tags/` に保存した。最終結果は `final-plan-results.json`。アプリコード・モデル・データ・IAM権限は変更していない。SAMのテンプレート変更は次回の通常デプロイ向けで、今回はスタック更新を実行していない。

検証: 専用Unit Test14件成功、変更したSAMテンプレート7件の `sam validate --lint` 成功。テンプレートの構造比較で、差分がコストタグ・関連パラメータ・APIタグ伝播設定に限定されること、samconfig4ファイルの差分が3タグ追加に限定されることを確認した。`git diff --check` と新規ファイルの空白チェックも成功。

PR作成時には最新developへ差分を移し、廃止済みの共有個人設定を復活させず `.example.toml` へタグを反映した。SAM・運用スクリプト・テストの変更は文書と分離した実装PRで管理し、ここに記載したAWSタグ付与の実施記録と、今後のIaC反映を区別する。

## 2026-10-20のAWS反映・追加確認

> 最終検証: 2026-10-20 — CloudFormation変更セット・適用後読取り、サービス別タグAPI、Cognito設定、Bedrock KB / データソース設定、保存済み実行証跡を照合。機能E2Eと請求側の有効化は未確認。

ユーザーが本会話で#193のAWS適用を依頼した。続いて、残る19件もEle-Knowledgeリソースであれば新しいコストタグを付与するよう依頼した。検索対象や利用者の追加・除外、法令KBの移行対象決定を兼ねない。

### #193の旧Envタグ削除

Phase 1 / Phase 2 / アーカイブ / お知らせ・集計 / 監視 / WAF / トラブルシューティングの既存dev **7スタックすべてがUPDATE_COMPLETE**。適用後の検証は19:38 JSTまでに完了した。[#193のAWS反映記録](https://github.com/yukiworkspace/EleKnowledge-AI/pull/193#issuecomment-6289028676)も参照する。

稼働中Originalテンプレートを基準にEnvタグだけを除き、既存パラメーター・Outputs・実体ID、LambdaのコードSHA・環境変数・モデル設定、DynamoDBのTTL・GSI、WAF設定を保持した。Cognito固有の `UserPoolTags` も反映し、タグ以外の認証設定が不変であることを実読取りで照合した。再package、データ移行、KB同期、IAM権限変更は行っていない。#195の機能反映でもない。

既存110リソースのタグを照合し、このEnv削除では**Env以外のタグの変化0件**。照合対象のうち7スタック管理下でEnvがあった75件は、75件すべてで削除を確認した。残る19件は当該7スタックの管理範囲外であり、削除不要と判断したものではない。

途中でPhase 2の日本語パラメーター説明文3か所の文字化けを検出して後続を停止した。ASCIIエスケープしたJSONで元の説明文を復元し、最終テンプレートの完全一致・稼働設定の不変を確認して再開した。以後の変更セットも、AWS側で保持された適用予定テンプレートが準備内容と一致することを実行前に確認した。

### 残る19件の新3キー確認・補完

対象は自動生成等のログ14件、法令KBとそのスタック2件、Amplify・既存推論プロファイル・先輩チャット専用索引S3が各1件。Projectタグ、所有スタック、用途と既存分類を照合し、Ele-Knowledge所有として確認した。

**18件には新3キーが付与済みで、現在値も一致。** 不足していた `eleknowledge-law-kb-dev` スタック1件に、ユーザー依頼を受けて `gyoumu012Project=ele-knowledge` / `gyoumu012Component=legal-rag` / `gyoumu012Usage=development` を追加した。CloudFormationの `UsePreviousTemplate` と既存パラメーター保持でタグだけの変更セットを適用し、19:46 JSTにUPDATE_COMPLETEと読み戻しを確認した。KB・データソース設定、既存タグ、テンプレート、パラメーター、Outputs、実体IDは維持した。KB同期・データ取込はしていない。

最終再照合で**19件すべてに新3キーが揃い、不足0件**。個別の用途と分類は[リソース別台帳の追加確認](cost-allocation-resource-register.md#2026-10-20の追加確認19件)を参照する。新タグ補完は旧Envの追加削除ではないため、この19件のEnvは残っている。請求側の有効化状況は引き続き未確認。

110件はEnv削除後の照合母集団、19件はそこから切り出した追加確認対象、104件は10/15の初期台帳であり、相互に重なる。足し算して総リソース数や今回の新規付与件数にしない。

変更前・変更セット・読み戻し・追加タグ照合の詳細はGit除外済みの `eval-results/cost-tags/env193-20261020/` に保存した。内部ARN・アカウント値・個人の認証設定を共有文書へ転記していない。台帳・マップ・ランブックはこの実施記録を参照し、請求の有効化確認は別の残作業として管理する。

## 2026-10-22の追補: 110件の内訳

> 最終検証: 2026-10-22 — 10/20保存のresource-tags-verification-local.json全110行を再集計。今回のAWS再照会ではない。

10/20の110件は、Env削除を確認した75件、Env残存の別管理19件、読み戻し時点でEnvなしの残り16件に重複なく分かれる（75＋19＋16＝110）。この16件は今回さらに16件削除したという意味ではない。CloudFormation本体のowner判定やDynamoDB Streamを含む照会結果の分類であり、個別の削除時点までは断定しない。

| サービス | 件数 | 残り16件の識別・確認範囲 |
| --- | ---: | --- |
| CloudFormation | 6 | Phase1、Phase2、WAF、監視、お知らせ・集計、チャットアーカイブのスタック本体。照会結果のownerフィールドは空で、75件の判定には入らない |
| DynamoDB table | 6 | metrics-dev、chatlogs-dev、sessions-dev、sites-dev、users-dev、announcements-dev |
| DynamoDB Stream | 2 | chatlogs-dev、users-devのStream。テーブルと別行であり独立の直接タグ付与対象ではない |
| Athena | 1 | eleknowledge-analytics-devのworkgroup |
| S3 | 1 | 法令RAGの既存データバケット。適用前からEnvなし。実名・ARNは未掲載 |

16件はいずれも適用後Envなし、Env以外のタグ変更なし。16件すべてに新3キーがあると確認したものではない。104件の初期台帳や19件の追加確認へ加算しない。証跡は未追跡の `eval-results/cost-tags/env193-20261020/` に保持する。


## 一次情報

- [AWS TagResources API](https://docs.aws.amazon.com/resourcegroupstagging/latest/APIReference/API_TagResources.html): リージョン制約、20件上限、部分失敗、CloudFormation更新の注意点。
- [AWS SAM API](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html): `PropagateTags` による生成リソースへのタグ伝播。
- [コスト配分タグの有効化](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/activating-tags.html): リソースタグとは別の有効化作業。
- [ユーザー定義コスト配分タグ](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/custom-tags.html): 管理アカウント・組織に属さない単独アカウントに限定される管理画面のアクセス条件。
- [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html): 推論プロファイルによる推論費追跡。
- [コスト配分タグのバックフィル](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-allocation-backfill.html): 最大12か月と過去の付与条件。
- AWS実査: STS、Resource Groups Tagging API（東京・バージニア・大阪）、Bedrock ListInferenceProfiles、Cost Explorer ListCostAllocationTags。
