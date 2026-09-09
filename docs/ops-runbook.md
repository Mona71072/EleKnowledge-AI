---
status: draft
last-verified: 2026-09-10
related-code: infrastructure/sam/monitoring-template.yaml, infrastructure/sam/chat-archive-template.yaml, scripts/ops/set_log_retention.py, lambda/rag/rag-function/app.py, lambda/metrics/aggregator/app.py
---

# 運用ランブック（試行運用 2026-09-10〜）

正本の経緯は issue #86（監視・改善ループの棚卸し）。本書は「アラームが鳴ったら何を見るか」「毎日何を見るか」「戻すときどうするか」を 1 枚にまとめたもの。設計判断そのものは issue のコメントを参照する。

## 1. 体制と通知

| 項目 | 内容 |
|---|---|
| 体制 | 2 人（itai / morimoto）。当番・エスカレーションは置かない。通知は 2 人に届き、気づいた方が見る |
| 通知経路 | CloudWatch アラーム → SNS `eleknowledge-alerts-dev` → メール 2 件 |
| 件名の読み方 | `ALARM: "EleKnowledge-dev-P1-rag-api-5xx" in Asia Pacific (Tokyo)`。**P1 = 利用者影響あり・気づいたら即対応**、**P2 = 翌営業日でよい**。復旧時は `OK:` で始まる同名メール |
| 購読の有効化 | SNS の購読は受信者が「AWS Notification - Subscription Confirmation」のリンクを押すまで無効（3 日で失効）。新しい受信者を足したら必ず押してもらう |
| 通知先の変更 | 監視スタックを `AlertEmailPrimary` / `AlertEmailSecondary` を変えて再デプロイ（アドレスはリポジトリに書かない） |

## 2. アラーム一覧と最初に見る場所

| アラーム名（`EleKnowledge-dev-` 以下） | 意味 | 最初に見る場所 | 典型的な原因と対処 |
|---|---|---|---|
| **P1-rag-api-5xx** | RAG API が 5XX を返した | Logs Insights 保存クエリ `EleKnowledge/dev/rag-error-lines` | Bedrock スロットル / KB 障害 / DynamoDB 障害。ログの AWS エラーコードで切り分け。Bedrock 側なら [AWS Health](https://health.aws.amazon.com/) も確認 |
| **P1-chat-api-5xx** | 履歴・フィードバック API が 5XX | 保存クエリ `chat-error-lines` | DynamoDB 障害が主。チャット本文は RAG API なので、履歴一覧だけ壊れている状態 |
| **P1-auth-api-5xx** | ログイン系が 5XX | API Gateway 実行ログ `API-Gateway-Execution-Logs_mqsyka1v9j/dev` | Cognito 障害。利用者は全員ログインできない |
| **P1-app-api-5xx** / **P1-troubleshooting-api-5xx** | お知らせ・メトリクス / トラブルシューティング API が 5XX | 各 Lambda のログ | 業務影響は限定的（お知らせが出ない、管理画面が開かない） |
| **P1-rag-throttles** / **P1-chat-throttles** / **P1-login-throttles** | Lambda 同時実行の上限 | CloudWatch Lambda メトリクス `ConcurrentExecutions` | 同時利用が想定（20 人）を超えた。アカウントの同時実行上限を確認 |
| **P1-rag-duration-max** | 1 回の RAG が 25 秒超（API Gateway の 29 秒制限の手前） | 保存クエリ `rag-slow-requests` | Bedrock の遅延。利用者には 504 が出た可能性。連続するなら Bedrock 側の状況を確認し、代替モデル切替（§7）を検討 |
| **P1-rag-error-lines** / **P1-chat-error-lines** | Lambda ログにエラー行（500 を return する設計のため Lambda Errors には乗らない） | 同上の保存クエリ | 5XX アラームと同時に鳴るのが普通。単独で鳴ったらログ本文を読む |
| **P1-chat-archive-errors** / **P1-chat-archive-dlq** | 会話ログの S3 アーカイブが失敗 | §6.5 の復旧手順 | S3 障害か権限。**24 時間以内に対処**（Stream の保持期限） |
| P2-rag-api-4xx-spike / chat / auth | 5 分に 4XX が 30 件超 | API Gateway 実行ログ | 許可リスト外 IP からの 403 か、トークン失効の 401 が大半。§5.1 |
| P2-rag-duration-p90 | 15 分間の p90 が 20 秒超 | Bedrock メトリクス `InvocationLatency`（ModelId = 使用中プロファイル） | Bedrock の遅延傾向。単発なら様子見 |
| P2-metrics-aggregator-errors / P2-metrics-schedule-failed | 日次・毎時集計の失敗 | `/aws/lambda/metrics-aggregator-dev` | 管理画面の数字が止まる。翌日 02:00 の再実行で埋まるか、手動再実行（`{"date": "YYYY-MM-DD"}` で invoke） |
| P2-announcements-publisher-errors | 予約公開の昇格失敗 | `/aws/lambda/announcements-publisher-dev` | 予約した告知が「予約」のまま。read 側は期限到来分を表示するので利用者影響は小さい |
| P2-chatlogs-read/write-throttle / P2-sessions-write-throttle | DynamoDB スロットル | DynamoDB コンソールのメトリクス | オンデマンドのため通常は起きない。起きたら急激な負荷 |
| **P1-cognito-email-errors** | Cognito のサインアップ・再送・再設定が上限 / 配信失敗 / スロットルで失敗（CloudTrail 経由） | SNS 本文（API 名・エラーコード・本文） | §5.6 |
| P2-cognito-signups-40 / **P1-cognito-signups-45・50** | その日のサインアップ数が 40 / 45 / 50 に到達（メール 50 通/日の接近） | Cognito ユーザー一覧（作成日） | §5.6。40 で受付停止の告知を検討 |

「INSUFFICIENT_DATA」は「その 5 分間にデータが無かった」だけで異常ではない（データ欠損は正常扱いの設定）。

## 3. 見る場所

| 目的 | 場所 |
|---|---|
| アラーム状態の一覧 | CloudWatch → アラーム → 名前で `EleKnowledge-dev-` を検索 |
| エラーログ | CloudWatch Logs Insights → 保存クエリ `EleKnowledge/dev/rag-error-lines` / `chat-error-lines` / `rag-slow-requests` |
| 利用状況・いいね率・not_found | 管理画面 `/admin/dashboard`（日次集計。当日分は毎時更新の予定、初週は翌日 02:00 反映） |
| 失敗した回答・要望 | 管理画面 `/admin/failures` |
| Bedrock の呼び出し・トークン・遅延 | CloudWatch → メトリクス → `AWS/Bedrock` → ModelId = `global.anthropic.claude-sonnet-5` |
| 会話ログの長期分析 | Athena ワークグループ `eleknowledge-analytics-dev`、テーブル `eleknowledge_analytics.chatlogs_archive`（`dt=` で日付パーティション） |
| 処理リージョン（global プロファイル） | CloudTrail の `InvokeModel` イベント → `additionalEventData.inferenceRegion` |

## 4. 初週の日次点検（任意・朝 5 分）

1. アラーム一覧に ALARM が無い
2. `/admin/dashboard` の「今日 / 今週」に前日の利用件数・いいね率が出ている（0 のままなら集計の障害）
3. `/admin/failures` の新着（👎・not_found）を眺め、明らかな検索ミスがあれば issue #86 に一言残す
4. Bedrock メトリクスで前日の呼び出し数がチャット件数と合っている
5. アーカイブの失敗キュー（SQS `eleknowledge-chat-archive-dev-failures`）が空

## 5. 切り分け手順

### 5.1 「使えない」「開けない」と言われたら
1. 接続元が社内ネットワーク / VPN か確認。許可リスト外の IP からは **API が 403**（WAF の IP 許可リスト）。画面は開くが質問すると失敗する、が典型
2. ログインして長時間経過していれば **401（トークン失効）**。再ログインで直る
3. どちらでもなければ 5XX アラームの有無を確認

### 5.2 回答が返らない・遅い
1. `P1-rag-duration-max` / `P2-rag-duration-p90` の状態
2. Bedrock メトリクス `InvocationLatency`（正常時 平均 9〜12 秒、Sonnet 5）
3. 29 秒を超えると利用者には 504。連続するなら §7 の代替モデルへ切替

### 5.3 回答が空・変
1. `/admin/failures` に not_found が増えていないか（KB 側の変化）
2. rag ログにエラー行が無いか
3. 直前のデプロイ（§8 の記録）と時刻を突き合わせ、必要なら §8 でロールバック

### 5.4 管理画面の数字が止まった
1. `P2-metrics-*` アラーム
2. `metrics-aggregator-dev` を `{"date": "YYYY-MM-DD"}` で手動 invoke（同じ日付は上書きされる）

### 5.5 アーカイブ失敗（P1-chat-archive-*）
1. Lambda ログで原因（S3 権限 / 障害）を確認
2. 生レコードは `s3://eleknowledge-chat-archive-dev-<account>/failed/dt=YYYY-MM-DD/` に保存されている（最善努力）
3. 原因解消後、保存した JSON の `records` を payload にして `eleknowledge-chat-archive-dev` を手動 invoke → `chatlogs/dt=.../` に出力されたことと件数を確認
4. SQS のメッセージを削除し、アラームが OK に戻ることを確認
5. `failed/` に無い場合は Stream の保持（24 時間）内に Lambda の再処理で回収する

### 5.6 Cognito のメール送信上限（P1-cognito-email-errors / P1-cognito-signups-45・50 / P2-cognito-signups-40）
- 背景: サインアップ・確認コード再送・パスワード再設定の確認メールは Cognito 既定の送信で、**1 ユーザープールあたり 1 日 50 通**（境界は UTC 0 時 = 日本時間 9 時と想定）。SES 未設定のため増やせない（issue #99）
- 検知: (a) サインアップ数が 40 / 45 / 50 に達した（`SignUpSuccesses`、再送・再設定は含まない）、(b) Cognito が `Exceeded daily email limit` 等のエラーを返した（CloudTrail → EventBridge。SNS 本文に API 名・エラーコード・本文が入る）
- 利用者側の表示: 画面が自動で「本日のメール送信数が上限に達したため…明日以降に」を出す。サインアップの場合はアカウントが未確認で作成済みのことがあるため「翌日、確認画面の『確認コードを再送信』から」と案内される（PR #102）
- 対応:
  1. 問い合わせには「翌日 9 時以降に確認画面の再送から。『登録が完了していません』と出た人だけ新規登録をやり直す」と案内
  2. 登録が集中する見込みなら **事前発行**（`scripts/ops/provision_users.py`、CSV から招待メールなしで作成し初期パスワードを配布。PR #101）
  3. 恒久対策は SES への切替（送信元ドメイン検証 + 本番アクセス申請 + Cognito の `DEVELOPER` 設定）。issue #99
- 初回に到達したときは、SNS 本文のエラーコードと本文を issue #99 に記録し、画面側の判定（`classifyAuthError`）と一致しているか確認する

## 6. データ保全と保持期間

| データ | 保持 | 場所 |
|---|---|---|
| 会話ログ（利用者に見える） | 60 日（TTL、不変条件） | DynamoDB `chatlogs-dev` |
| 会話ログの正本 | 無期限（60 日で IA、180 日で Glacier）。バージョニング有効 | S3 アーカイブ + Athena |
| 日次 KPI | 無期限（TTL 無効） | DynamoDB `metrics-dev` |
| Lambda ログ | 365 日 | CloudWatch Logs |
| API Gateway 実行ログ | 90 日 | CloudWatch Logs |
| 保持期間の再設定 | `python scripts/ops/set_log_retention.py --env dev`（対象は EleKnowledge の関数名・API 名に限定） | — |

## 7. 生成モデルと推論プロファイル

### 7.1 現在の構成
- 生成モデル: **Sonnet 5**（`global.anthropic.claude-sonnet-5`、2026-09-09 23:02 JST 切替）。環境変数 `BEDROCK_MODEL_ID` で指定
- Sonnet 5 / Opus 4.7 以降は `temperature` 指定を 400 で拒否し、既定で適応思考が動くため、`app.py` がモデル世代に応じて本文を組み立てる（`thinking: disabled` 明示）。`BEDROCK_REQUEST_STYLE=auto|new|legacy`
- Fable 系は対象外（adaptive のみ対応）

### 7.2 推論プロファイルの仕組み（切替・費用分離のために知っておくこと）
- Bedrock のモデル呼び出し課金はモデルとトークン数で計上され、Lambda のようにリソース単位でタグを付けられない
- **システム定義プロファイル**（`jp.` / `global.` など）は AWS が用意した呼び出し口。`jp.` は国内リージョンで推論（+10%）、`global.` は世界分散（プレミアム無し）。Sonnet 5 は東京では `global.` のみ
- **アプリケーション推論プロファイル**は自分で作る呼び出し口で、タグを付けられる。これ経由の利用は請求にタグ付きで載り、CloudWatch のメトリクスも ModelId = プロファイル ARN で分離される
- ただし本アカウントでは **global を元にしたアプリケーションプロファイル経由の呼び出しが SCP で拒否される**（元モデル ARN がリージョン無しになるため）。`jp.` を元にしたものは通る。作成済みの `EleKnowledge-rag-dev-sonnet5-20260909` は SCP 見直し後に使う
- したがって当面は global を直接指定し、**推論コストはトークン数 × 単価で算出**する（P1 の検索トレースで実装）

### 7.3 モデルを切り替える手順
1. 候補: 速さ優先なら **Sonnet 4.6（`jp.anthropic.claude-sonnet-4-6`）**（比較記録 `docs/eval-2026-09-09-model-bakeoff-jp.md`）
2. `sam deploy`（phase2）で `BedrockModelId=<プロファイル ID>` を渡す。Sonnet 4.6 以前なら `BedrockRequestStyle=auto` のままで temperature が付く
3. 切替日時・モデル・環境変数を issue #86 に記録し、いいね率・not_found 率・レイテンシを前後比較

## 8. デプロイとロールバック

- **ルール**: develop へのマージ（＝Amplify が自動配信）と本番スタックの deploy は **定時後** に行う（AGENTS.md）
- 手順: 統合ブランチを作る → `sam build` → `sam deploy --no-execute-changeset` で changeset を作る → 内容（Add / Modify / Replace）を確認 → `execute-change-set`。Replace が出たら止まって確認
- **announcements-monitoring は必ず TTL 無効化を含むテンプレートから**（develop 単体から作ると TTL が再有効化される事故があった）
- 配信構成の記録は issue #86 のデプロイ記録に残す（Lambda の CodeSha256、環境変数、KB ID、モデル ID、フロントの commit）
- ロールバック: 旧コードだけでなく **モデル ID と環境変数の組合せ** を指定して phase2 を再デプロイする（例: `BedrockModelId=jp.anthropic.claude-haiku-4-5-20251001-v1:0` + 当時の commit）

## 9. コストの追い方

- リソース費: Cost Explorer で `Project=EleKnowledge` タグ（**コスト配分タグの有効化は管理アカウント側の作業**。有効化前の利用には遡及しない）
- Bedrock 費: 検索トレースのトークン数 × 単価（SSM パラメータ）を日次集計し、管理画面に「今月の推定 Bedrock 費」（P1 で実装）。CloudWatch の ModelId 別トークンは他システム混在のため参考値
- 共有 KB（OpenSearch Serverless）は他システムと共有のため按分しない

## 10. 変更履歴

- 2026-09-10 初版（issue #86 の P0 反映後）
