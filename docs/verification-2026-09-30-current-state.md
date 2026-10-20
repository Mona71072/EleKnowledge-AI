---
status: draft
last-verified: 2026-09-30
related-code:
  - infrastructure/sam/
  - lambda/metrics/aggregator/app.py
  - frontend/package.json
  - docs/aws-resource-map.md
  - docs/ops-runbook.md
---

# 文書整備状況の確認記録（2026-09-30）

## 目的と確認範囲

開発環境の監視・改善リソース、稼働中機能、開発中・将来項目について、文書・IaC・コード・AWS の確認結果を分けて整理する。これは確認日時点のスナップショットであり、業務判断や利用者向け受け入れ確認を代替しない。

AWS は `ap-northeast-1` の開発環境を AWS CLI で読み取り専用確認した。リポジトリ側はこの文書整備ブランチの開始点である `origin/develop` を確認した。通知メールの到達試験、ユーザー操作 E2E、AWS への変更は行っていない。

## 実環境で確認した事項

| 対象 | 2026-09-30 の観測 | 未確認・留意点 |
|---|---|---|
| Phase 1 / 2 | 関連 CloudFormation stack は `UPDATE_COMPLETE`。Amplify `develop` の自動ビルドが有効。RAG Lambda のモデル・Knowledge Base 設定は運用ランブック記録と一致。 | この調査ではユーザー操作 E2E をしていない。 |
| 監視 | 監視 stack に CloudWatch alarm 27 件、Logs Insights 保存クエリ 6 件。監視 SNS のメール購読 2 件は確認済み。EleKnowledge 名の CloudWatch alarm 28 件は全件 `OK`、アクション有効。AWS Budget 通知も存在。 | SNS / Budget の通知到達、Budget 閾値・設定内容は未確認。 |
| KPI | 日次・毎時 EventBridge ルールが有効で、毎時ルールは aggregator Lambda をターゲットとしていた。`metrics-dev` の TTL は無効。 | 毎時ルールが有効でも、時間別 KPI の更新を意味しない。実装との差は下記参照。 |
| WAF | Regional Web ACL と API 関連付けを確認。 | EleKnowledge 用 WAF ログ配信・CloudWatch alarm・専用 SNS は存在を確認できず。リージョンにあるログ設定 1 件は別 Web ACL 向け。 |
| Phase 3 | troubleshooting stack、API、Lambda、テーブルが存在。 | 利用者向け提供と現在の全フロー E2E は未確認。 |

## IaC・コードとの照合

| 観測 | `origin/develop` の定義・コード | 文書での扱い |
|---|---|---|
| 監視 stack の alarm 27 件・保存クエリ 6 件 | `monitoring-template.yaml` は alarm 26 件、Logs Insights query definition 3 件、metric filter 2 件を定義。 | AWS 実数と `develop` の IaC 件数に差がある。CloudFormation 管理下の差分調査が終わるまで、27/6 を `develop` から再作成できると説明しない。 |
| 毎時 EventBridge ルールが有効 | `announcements-monitoring-template.yaml` は日次ルールのみ。aggregator は `date` の指定がなければ前日 UTC を集計し、JST 時間別処理を持たない。 | 毎時ルールは実環境で確認したが、KPI v2 は未実装。日次設計書の「実装前」は修正し、予定と実態を分ける。 |
| Web ACL は存在、WAF ログ・通知は未確認 | `security-waf-template.yaml` にはログ用 S3、LoggingConfiguration、WAF alarm と通知 topic の定義がある。 | 定義済みとデプロイ済みを分ける。WAF 監視計画は開発中として残す。 |
| Phase 3 のリソースは存在 | `phase3-template.yaml` に Lambda / API / DynamoDB の定義がある。 | stack の存在を利用者向け提供の証拠とせず、仕様・処理シーケンスを development に置く。 |
| 開発・評価項目 | RAG 2 モード設計は共同確認済み。ゴールデンセット v2 は候補データで、ラベル未確定。検索トレース設計は実装前。 | 合意、コード反映、環境反映、評価準備を別々に表示する。 |

## 次回確認事項

1. CloudFormation stack と `origin/develop` の監視定義の差（alarm 1 件・保存 query 3 件）をリソース単位で突合する。
2. 追加された hourly rule の作成元・イベント入力・意図を確認し、KPI を毎時更新する運用が必要なら別途コード仕様と実装計画を作る。
3. WAF ログ・アラーム・SNS を実装するかは、業務判断と変更確認を経て決める。文書上の記載でデプロイ状態を補わない。
4. Phase 3 は利用者向け E2E の確認後に提供状態を再評価する。
