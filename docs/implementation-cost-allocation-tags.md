---
status: development
last-verified: 2026-10-15
related-code: scripts/ops/apply_cost_allocation_tags.py, tests/unit/test_cost_allocation_tags.py, infrastructure/sam/
---

# コスト配分タグの継続管理：実装と受入条件

## 対象と反映状態

2026-10-15のユーザー依頼で採用した `gyoumu012Project` / `gyoumu012Component` / `gyoumu012Usage` を、次回以降のデプロイと運用時に維持するための実装メモ。分類の業務判断・口頭承諾・104件のリソース別台帳は別の共同確認文書PRで管理する。本書はそのルールを変更しない。

東京の既存104件へのタグ付与・再読取確認は別途実施済み。このPRのSAMテンプレートは未デプロイであり、マージでAWSへ反映されるとは扱わない。管理アカウントでのコスト配分タグ有効化、請求確認、モデル呼出経路・SCP・IAM権限の変更は含まない。

## 変更するコードの契約

- SAMのタグ対応リソースとFunction Globalsへ3キーを追加する。既存の `Project` / `Env`、環境変数・認証認可・関数コードは維持する。
- `CostProjectName` は `ele-knowledge`、`CostUsage` は `development` / `user` / `shared`。既定のUsageはトラブルシューティングが `development`、その他の現行スタックが `shared`。専用リソースのComponentを明記し、共用API・認証・履歴を共通分類にする。
- SAM APIの `PropagateTags: true` によって生成ステージへタグを渡す。共有samconfigと `.example.toml` も3キーを渡す。個人の `.local.toml`・実アカウントID・実バケット名は追加しない。
- 運用スクリプトは計画生成、`--apply`、`--verify` を分離する。STSのアカウント一致と既存タグ・所有根拠を確認し、既存の分類と競合したら停止する。S3等で他のタグを削除せず、部分失敗と再読取結果を保存する。
- 対象は旧Projectタグまたは新プロジェクトキー、所有確認したスタックのAPI、所有Lambda/APIと対応するログ。CloudFormationスタック本体・DynamoDB Stream・予算メタデータは直接書込しない。既定の調査範囲は東京・バージニア・大阪。
- ARNを含む計画・結果はGit除外済みの `eval-results/` へ保存する。デプロイ後の照合では新しい出力名を使い、確認済みの計画だけを適用する。

## 受入条件と検証方法

1. 別アカウント・他Project・既存分類の競合・不正キー・スタック/Streamへの適用を拒否するUnit Testが通る。
2. `dev` という名前だけでUsageを開発用にせず、旧法令バケットのProject値も認識する。Lambda・DynamoDB・Bedrock KBは対応するサービス別タグAPIで検証できる。
3. 変更した7テンプレートで `sam validate --lint` が成功する。最新developとの構造差分が3タグ、関連パラメータ、APIタグ伝播だけであることを確認する。
4. 既存Unit Testの通過と、共有ファイルへの実アカウントID・認証情報の新規混入がないことを確認する。`git diff --check` が成功する。

## デプロイ時の確認

PR作成前の検証結果: UTF-8モードで全Unit Test639件成功（追加14件を含む）、SAMテンプレート7件のlint成功。最新developとの構造比較でタグ・関連パラメータ・伝播以外の変更なし、samconfig4ファイルも3タグ追加だけと確認した。Windowsの既定cp932による既存テストの読取失敗は `python -X utf8` で解消し、既存テストやアプリを変更していない。

現行ランブックの通常デプロイ手順に従い、まず変更セットを作成して差分と置換なしを確認する。phase2は現行の `RagLogicVersion` 等の必須値を保持する。タグ以外のアプリ更新・設定変更が含まれる場合はこのPRだけを根拠に実行しない。

AWSへ反映するときは、タグ値・既存タグ保持を再読取確認する。Lambdaが暗黙作成するログ、外部管理の法令KB・保持S3・既存推論プロファイルはIaCだけで網羅できないため、運用スクリプトの計画で不足を確認する。今回のPR作成では追加のAWS変更・スタック更新は実行しない。
