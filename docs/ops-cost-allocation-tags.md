---
status: development
last-verified: 2026-10-15
related-code: scripts/ops/apply_cost_allocation_tags.py, infrastructure/sam/
---

# コスト配分タグの運用

各リソースのタグ値・分類根拠・管理元は [リソース別台帳](cost-allocation-resource-register.md) を参照する。タグ定義と運用手順の正本は本書とする。

## 決定と適用範囲

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

本アカウントは単一環境で、本番は別AWSアカウントへリリースするため、`Env` はコスト配分の軸に含めない。既存の `Project` / `Env` は互換性のため今回削除せず、SAMの `Environment` / `ProjectName` パラメータも維持する。

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

リソースへのタグ付与と、請求へのタグ有効化は別作業である。2026-10-15の実査では、このメンバーアカウントから `ce:ListCostAllocationTags` は拒否された（Linked account doesn't have access to cost allocation tags）。有効化済みとは扱わない。

管理部門へ渡す依頼文（本タスクから送信はしない）:

> Ele-Knowledgeのコスト管理用として、アカウント識別接頭辞を付けた以下3キーをコスト配分タグとして有効化してください。
> `gyoumu012Project` / `gyoumu012Component` / `gyoumu012Usage`
> プロジェクト値は `ele-knowledge` です。環境はAWSアカウントで分離するため `Env` の有効化は不要です。
> 有効化日と、請求データで各キーを確認できた日をご連絡ください。

反映には時間差があるため、有効化後にCost Explorer / CURで確認する。バックフィルは管理アカウントから最大12か月を申請できるが、当時リソースに付いていたタグが対象であり、新キー付与前の期間を新キーで復元できるとは扱わない。

## 費用分離の限界と残作業

- 共用Lambda・API・S3等の開発／ユーザー利用はリソースタグだけでは分離できない。利用統計に基づく配賦、またはリソース分離が必要。配賦ルールは別途合意する。
- BedrockはApplication Inference Profileへタグを付け、実際にそのプロファイルを呼び出す経路の推論費を追跡する。KB・Lambdaへのタグのみで全推論費を帰属済みとはしない。埋め込み・再ランキング・Agent等も呼出経路別に確認する。
- 現在の `rag-dev` は `global.anthropic.claude-sonnet-5` を直接指定している。既存Application Inference Profileへ3タグを付けても、現在の生成推論費はそのプロファイルへ帰属しない。既存ランブック§7.2にはSCPによる利用拒否の記録があるため、今回はモデル・呼出経路・SCPを変更せず、従来のトークン数×単価による推計を継続する。SCP制約そのものは今回再現試験していない。
- 既存の外部スタック所有KB・S3・検索基盤は、他システムの費用を含み得るため今回の一括タグ付与対象外とする。
- CloudFormationスタック本体へのResource Groups Tagging APIによる変更は、更新処理を誘発する可能性があるため行わない。スタックタグは次回の通常デプロイで反映する。
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

## 一次情報

- [AWS TagResources API](https://docs.aws.amazon.com/resourcegroupstagging/latest/APIReference/API_TagResources.html): リージョン制約、20件上限、部分失敗、CloudFormation更新の注意点。
- [AWS SAM API](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-api.html): `PropagateTags` による生成リソースへのタグ伝播。
- [コスト配分タグの有効化](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/activating-tags.html): リソースタグとは別の有効化作業。
- [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html): 推論プロファイルによる推論費追跡。
- [コスト配分タグのバックフィル](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-allocation-backfill.html): 最大12か月と過去の付与条件。
- AWS実査: STS、Resource Groups Tagging API（東京・バージニア・大阪）、Bedrock ListInferenceProfiles、Cost Explorer ListCostAllocationTags。
