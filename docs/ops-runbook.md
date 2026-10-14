---
status: draft
last-verified: 2026-09-10
related-code: infrastructure/sam/monitoring-template.yaml, infrastructure/sam/chat-archive-template.yaml, infrastructure/sam/phase2-template.yaml, scripts/ops/set_log_retention.py, lambda/rag/rag-function/app.py, lambda/rag/rag-function/model_profile.py, lambda/metrics/aggregator/app.py
---

# 運用ランブック（試行運用 2026-09-10〜）

正本の経緯は issue #86（監視・改善ループの棚卸し）。本書は「アラームが鳴ったら何を見るか」「毎日何を見るか」「戻すときどうするか」を 1 枚にまとめたもの。設計判断そのものは issue のコメントを参照する。

## 0. 開発環境の確認スナップショット

> 最終検証: 2026-09-30 — AWS CLI 読み取り専用確認（CloudFormation / CloudWatch / SNS / EventBridge / DynamoDB / WAF。通知到達・機能 E2E は未確認）

この節は確認日時点の開発環境の観測記録であり、恒久的な保証ではない。監視スタックには 27 アラームと 6 件の保存クエリがあり、別スタックのアーカイブ失敗アラームを含む EleKnowledge アラーム 28 件はすべて `OK`、アクション有効だった。監視 SNS のメール購読 2 件は確認済みだが、メール到達試験はしていない。AWS Budget 通知も存在したが、IaC 定義外であり通知到達は未確認。

`origin/develop` の `monitoring-template.yaml` は 26 アラーム・クエリ定義 3 件、`announcements-monitoring-template.yaml` は日次集計ルールのみを定義する。AWS では毎時ルールも有効だったが、現行 aggregator は event の `date` がなければ前日の UTC 日付を集計する。毎時ルールの存在を時間単位 KPI の実装・更新とみなさない。`metrics-dev` の DynamoDB TTL は無効だった。

EleKnowledge の WAF ログ配信・WAF アラーム・専用通知 SNS は確認できなかった。テンプレートに定義されているリソースも、環境で確認できるまでは運用手順として利用しない。

## 1. 体制と通知

> 最終検証: 2026-10-05 — 2026-09-30 の AWS 読み取り専用観測記録と develop の監視テンプレートを照合

| 項目 | 内容 |
|---|---|
| 体制 | 2 人（itai / morimoto）。当番・エスカレーションは置かない。通知は 2 人に届き、気づいた方が見る |
| 通知経路 | CloudWatch アラーム → SNS `eleknowledge-alerts-dev` → メール 2 件 |
| 件名の読み方 | `ALARM: "EleKnowledge-dev-P1-rag-api-5xx" in Asia Pacific (Tokyo)`。**P1 = 利用者影響あり・気づいたら即対応**、**P2 = 翌営業日でよい**。復旧時は `OK:` で始まる同名メール |
| 購読の有効化 | SNS の購読は受信者が「AWS Notification - Subscription Confirmation」のリンクを押すまで無効（3 日で失効）。新しい受信者を足したら必ず押してもらう |
| 通知先の変更 | 監視スタックを `AlertEmailPrimary` / `AlertEmailSecondary` を変えて再デプロイ（アドレスはリポジトリに書かない） |
| AWS Budget 通知 | 2026-09-30 の開発環境では設定を確認。現在の監視 SAM テンプレート管理外であり、通知到達・閾値は未確認。変更前に AWS Budgets 側を確認する |

## 2. アラーム一覧と最初に見る場所

> 最終検証: 2026-10-05 — 2026-09-30 の AWS 読み取り専用観測記録と develop の監視テンプレートを照合

| アラーム名（`EleKnowledge-dev-` 以下） | 意味 | 最初に見る場所 | 典型的な原因と対処 |
|---|---|---|---|
| **P1-rag-api-5xx** | RAG API が 5XX を返した | Logs Insights 保存クエリ `EleKnowledge/dev/rag-error-lines` | Bedrock スロットル / KB 障害 / DynamoDB 障害。ログの AWS エラーコードで切り分け。Bedrock 側なら [AWS Health](https://health.aws.amazon.com/) も確認 |
| **P1-chat-api-5xx** | 履歴・フィードバック API が 5XX | 保存クエリ `chat-error-lines` | DynamoDB 障害が主。チャット本文は RAG API なので、履歴一覧だけ壊れている状態 |
| **P1-auth-api-5xx** | ログイン系が 5XX | API Gateway 実行ログ `API-Gateway-Execution-Logs_mqsyka1v9j/dev` | Cognito 障害。利用者は全員ログインできない |
| **P1-app-api-5xx** / **P1-troubleshooting-api-5xx** | お知らせ・メトリクス / トラブルシューティング API が 5XX | 各 Lambda のログ | 業務影響は限定的（お知らせが出ない、管理画面が開かない） |
| **P1-rag-throttles** / **P1-chat-throttles** / **P1-login-throttles** | Lambda 同時実行の上限 | CloudWatch Lambda メトリクス `ConcurrentExecutions` | 同時利用が想定（20 人）を超えた。アカウントの同時実行上限を確認 |
| **P1-rag-duration-max** | 1 回の RAG が 25 秒超（API Gateway の 29 秒制限の手前） | 保存クエリ `rag-slow-requests` | Bedrock の遅延。利用者には 504 が出た可能性。連続するなら Bedrock 側の状況を確認し、代替モデル切替（§7）を検討 |
| **P1-rag-error-lines** / **P1-chat-error-lines** | Lambda ログにエラー行（500 を return する設計のため Lambda Errors には乗らない） | 同上の保存クエリ | 5XX アラームと同時に鳴るのが普通。単独で鳴ったらログ本文を読む |
| **P1-chat-archive-errors** / **archive failure notification** | 会話ログの S3 アーカイブが失敗し、再試行後の完全な呼出し記録がS3へ保存された | §5.5 の復旧手順 | S3 障害か権限。**24 時間以内に対処**（Stream の保持期限） |
| P2-rag-api-4xx-spike / chat / auth | 5 分に 4XX が 30 件超 | API Gateway 実行ログ | 許可リスト外 IP からの 403 か、トークン失効の 401 が大半。§5.1 |
| P2-rag-duration-p90 | 15 分間の p90 が 20 秒超 | Bedrock メトリクス `InvocationLatency`（ModelId = 使用中プロファイル） | Bedrock の遅延傾向。単発なら様子見 |
| P2-metrics-aggregator-errors / P2-metrics-schedule-failed | 日次・毎時集計の失敗 | `/aws/lambda/metrics-aggregator-dev` | 管理画面の数字が止まる。翌日 02:00 の再実行で埋まるか、手動再実行（`{"date": "YYYY-MM-DD"}` で invoke） |
| P2-announcements-publisher-errors | 予約公開の昇格失敗 | `/aws/lambda/announcements-publisher-dev` | 予約した告知が「予約」のまま。read 側は期限到来分を表示するので利用者影響は小さい |
| P2-chatlogs-read/write-throttle / P2-sessions-write-throttle | DynamoDB スロットル | DynamoDB コンソールのメトリクス | オンデマンドのため通常は起きない。起きたら急激な負荷 |
| **P1-cognito-email-errors** | Cognito のサインアップ・再送・再設定が上限 / 配信失敗 / スロットルで失敗（CloudTrail 経由） | SNS 本文（API 名・エラーコード・本文） | §5.6 |
| P2-cognito-signups-40 / **P1-cognito-signups-45・50** | その日のサインアップ数が 40 / 45 / 50 に到達（メール 50 通/日の接近） | Cognito ユーザー一覧（作成日） | §5.6。40 で受付停止の告知を検討 |
| 未設定（WAF Block / per-user rate limit） | Web ACL による遮断。2026-09-30 時点で EleKnowledge 用 CloudWatch アラーム・ログ配信・専用 SNS は未確認 | API Gateway の実行ログと WAF コンソールの Web ACL / メトリクス | 既存手順で S3 WAF ログや WAF 通知を探さない。過去の要求内容を WAF ログから追跡できる状態ではない |

「INSUFFICIENT_DATA」は「その 5 分間にデータが無かった」だけで異常ではない（データ欠損は正常扱いの設定）。

## 3. 見る場所

> 最終検証: 2026-10-05 — 2026-09-30 の AWS 読み取り専用観測記録と develop の管理画面・監視設定を照合

| 目的 | 場所 |
|---|---|
| アラーム状態の一覧 | CloudWatch → アラーム → 名前で `EleKnowledge-dev-` を検索 |
| エラーログ | CloudWatch Logs Insights → 保存クエリ `EleKnowledge/dev/rag-error-lines` / `chat-error-lines` / `rag-slow-requests` |
| 利用状況・いいね率・not_found | 管理画面 `/admin/dashboard`。現行 aggregator は前日 UTC の日次データを作る。AWS で毎時 EventBridge ルールは確認したが、時間別・当日 KPI の更新は確認していない。 |
| 失敗した回答・要望 | 管理画面 `/admin/failures` |
| Bedrock の呼び出し・トークン・遅延 | CloudWatch → メトリクス → `AWS/Bedrock` → ModelId = `global.anthropic.claude-sonnet-5` |
| 会話ログの長期分析 | Athena ワークグループ `eleknowledge-analytics-dev`、テーブル `eleknowledge_analytics.chatlogs_archive`（`dt=` で日付パーティション） |
| 処理リージョン（global プロファイル） | CloudTrail の `InvokeModel` イベント → `additionalEventData.inferenceRegion` |

## 4. 初週の日次点検（任意・朝 5 分）

1. アラーム一覧に ALARM が無い
2. `/admin/dashboard` の「今日 / 今週」に前日の利用件数・いいね率が出ている（0 のままなら集計の障害）
3. `/admin/failures` の新着（👎・not_found）を眺め、明らかな検索ミスがあれば issue #86 に一言残す
4. Bedrock メトリクスで前日の呼び出し数がチャット件数と合っている
5. アーカイブ失敗通知が届いていないこと（届いた場合は §5.5 を完了するまで障害として扱う）

## 5. 切り分け手順

### 5.1 「使えない」「開けない」と言われたら

> 最終検証: 2026-10-05 — develop の WAF 定義と 2026-09-30 AWS 読み取り専用観測記録を照合
1. 接続元が社内ネットワーク / VPN か確認。許可リスト外の IP からは **API が 403**（WAF の IP 許可リスト）。画面は開くが質問すると失敗する、が典型
2. **403 / 429** は WAF の IP 許可リストまたは利用者レート制限を確認する（閾値の正は [docs/api/common.md](./api/common.md)）。開発環境では EleKnowledge 向け WAF ログの S3 配信と WAF アラームは未確認のため、CloudWatch の専用通知や S3 ログを前提にしない。テンプレート定義は [security-waf-template.yaml](../infrastructure/sam/security-waf-template.yaml) にあるが、デプロイ済みとは扱わない。
3. ログインして長時間経過していれば **401（トークン失効）**。再ログインで直る
4. どちらでもなければ 5XX アラームの有無を確認

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
1. Lambda ログで原因（S3 権限 / 障害）を確認する。失敗通知は、再試行を使い切った後にS3へ失敗記録が作られたことを示す。
2. `s3://eleknowledge-chat-archive-dev-<account>/aws/lambda/` 配下の失敗記録を取得する。S3失敗宛先はメタデータに加え、元のDynamoDB Streamsイベント全体を JSON の `payload` に保存する。
3. `payload` を JSON として復元し、`Records` 配列の件数、`eventID`、`NewImage` / `OldImage`、重複の有無を確認する。保存JSONそのものや小文字の `records` をそのままLambdaに渡さない。
4. 原因解消後、復元した `payload` を `eleknowledge-chat-archive-dev` に手動 invoke する。`chatlogs/dt=.../` への出力後、同じ照合を行い、記録する。
5. 通知はSQSではなくS3オブジェクト作成に対するSNS通知であるため、削除対象のメッセージはない。復旧記録を残して障害をクローズする。

### 5.6 Cognito のメール送信上限（P1-cognito-email-errors / P1-cognito-signups-45・50 / P2-cognito-signups-40）
- 背景: サインアップ・確認コード再送・パスワード再設定の確認メールは Cognito 既定の送信で、**AWSアカウントあたり 1 日 50 通**。リセットは **09:00 UTC（18:00 JST）**。SES 未設定のため増やせない（issue #99）
- 検知: (a) サインアップ数が 40 / 45 / 50 に達した（`SignUpSuccesses`、再送・再設定は含まない）、(b) Cognito が `Exceeded daily email limit` 等のエラーを返した（CloudTrail → EventBridge。SNS 本文に API 名・エラーコード・本文が入る）
- 利用者側の表示: 画面が自動で「本日のメール送信数が上限に達したため…明日以降に」を出す。サインアップの場合はアカウントが未確認で作成済みのことがあるため「翌日、確認画面の『確認コードを再送信』から」と案内される（PR #102）
- 対応:
  1. 問い合わせには「18時以降に確認画面の再送から。『登録が完了していません』と出た人だけ新規登録をやり直す」と案内
  2. **上限に当たった人を個別に救う（推奨）**: `python scripts/ops/confirm_unconfirmed_users.py list` で未確認アカウントを一覧 → 正式な社内情報で対象メールと本人を照合し、確認者・日時・根拠・結果を社内記録へ残す → `confirm --emails <address> --verified-by <担当者> --evidence-ref <社内記録参照>` で確認済みにする。自己申告だけでは実行しない。
  3. 登録が集中する見込みなら **事前発行**（`scripts/ops/provision_users.py`、CSV から招待メールなしで作成し初期パスワードを配布。PR #101）
  4. 恒久対策は SES への切替（送信元ドメイン検証 + 本番アクセス申請 + Cognito の `DEVELOPER` 設定）。issue #99
- 初回に到達したときは、SNS 本文のエラーコードと本文を issue #99 に記録し、画面側の判定（`classifyAuthError`）と一致しているか確認する

## 6. データ保全と保持期間

> 最終検証: 2026-10-05 — develop の DynamoDB / ログ保持設定と 2026-09-30 AWS 読み取り専用観測記録を照合

| データ | 保持 | 場所 |
|---|---|---|
| 会話ログ（利用者に見える） | 60 日（TTL、不変条件） | DynamoDB `chatlogs-dev` |
| 会話ログの正本 | 無期限（60 日で IA、180 日で Glacier）。バージョニング有効 | S3 アーカイブ + Athena |
| 日次 KPI | TTL 無効（2026-09-30 の AWS 観測）。aggregator が書く `ttl` 属性だけでは DynamoDB 項目は削除されない | DynamoDB `metrics-dev` |
| Lambda ログ | 365 日 | CloudWatch Logs |
| API Gateway 実行ログ | 90 日 | CloudWatch Logs |
| 保持期間の再設定 | `python scripts/ops/set_log_retention.py --env dev`（対象は EleKnowledge の関数名・API 名に限定） | — |

## 7. 生成モデルと推論プロファイル

### 7.1 現在の構成
> 最終検証: 2026-09-29 — Phase 2 SAM の既定値と生成モデル設定を照合

- 生成モデル: **Sonnet 5**（`global.anthropic.claude-sonnet-5`、2026-09-09 23:02 JST 切替）。環境変数 `BEDROCK_MODEL_ID` で指定。採用条件・見直し条件の正本は PR #119
- `model_profile.py` の能力表に基づき、`temperature` / thinking / effort をモデル別に組み立てる。見出し生成・検索語書き換えでは thinking を無効化できない effort 対応モデルに `effort=low` を送る。能力表にも `MODEL_PROFILE_JSON` にもないモデルは、既定で最小リクエストを送りモデル既定に任せる。
- 本番の既定モデルは Sonnet 5 のまま。モデルを切り替える場合は次の手順で評価する。

### 7.2 推論プロファイルの仕組み（切替・費用分離のために知っておくこと）
- Bedrock のモデル呼び出し課金はモデルとトークン数で計上され、Lambda のようにリソース単位でタグを付けられない
- **システム定義プロファイル**（`jp.` / `global.` など）は AWS が用意した呼び出し口。`jp.` は国内リージョンで推論（+10%）、`global.` は世界分散（プレミアム無し）。Sonnet 5 は東京では `global.` のみ
- **アプリケーション推論プロファイル**は自分で作る呼び出し口で、タグを付けられる。これ経由の利用は請求にタグ付きで載り、CloudWatch のメトリクスも ModelId = プロファイル ARN で分離される
- ただし本アカウントでは **global を元にしたアプリケーションプロファイル経由の呼び出しが SCP で拒否される**（元モデル ARN がリージョン無しになるため）。`jp.` を元にしたものは通る。作成済みの `EleKnowledge-rag-dev-sonnet5-20260909` は SCP 見直し後に使う
- したがって当面は global を直接指定し、**推論コストはトークン数 × 単価で算出**する（P1 の検索トレースで実装）

### 7.3 モデルを切り替える手順
> 最終検証: 2026-10-01 — `MODEL_PROFILE_JSON` の API 指定を追記し実装と照合

1. 新モデルが出たら `lambda/rag/rag-function/model_profile.py` の既知能力表に追加するか、SAM の `ModelProfileJson`（環境変数 `MODEL_PROFILE_JSON`）で能力を指定する。JSON の形式は `{"sonnet-5-5":{"sampling":false,"thinking_disable":false,"adaptive":true,"effort":true},"gpt-6-luna":{"api":"converse"}}`。API は `invoke` / `converse`。モデル名を含まない application inference profile ARN の場合は、JSON キーに ARN 全体を指定する。
2. 互換用の SAM パラメータ `BedrockRequestStyle`（環境変数 `BEDROCK_REQUEST_STYLE`）は非推奨。既定 `auto` は能力表の判定どおりにし、判定できないモデルでは最小リクエストを送る。`new` は判定できないモデルを新世代扱い（sampling なし、thinking を disabled にできるとは仮定せず最小リクエスト）、`legacy` は判定できないモデルに `temperature` を送る。既知能力表または `MODEL_PROFILE_JSON` で判定できるモデルはこの設定より優先される。新モデルの能力指定には `MODEL_PROFILE_JSON` を推奨する。
3. `sam deploy`（phase2）で `BedrockModelId=<推論プロファイル ID>` を指定する。推論プロファイルと関連モデルの IAM 許可範囲は Phase 2 テンプレートで管理する（Global Cross-Region は Global foundation model ARN も認可対象）。詳細は [AWS の Global Cross-Region IAM 要件](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html) を参照。
4. 本番の既定モデルはこの手順では変更しない。評価環境で評価セットを実行し、回答品質・引用・レイテンシ・Bedrock 費用を比較して記録する。採用判断後にだけ運用モデルの切替を別途行う。

### 7.4 GPT-6 Luna を開発環境で試す
> 最終検証: 2026-10-01 — Luna モデルカード、Converse API / IAM 要件、濫用検知のデータ保持説明を照合

- デプロイ時に `BedrockModelId=global.openai.gpt-6-luna` を指定する。Phase 2 の既定値（Haiku 4.5）は変更しない。能力表で `api=converse` が選ばれ、本文・見出し・検索語書き換えが Converse 経由になる。
- Lambda 実行ロールには `bedrock:InvokeModel` が必要。Converse は同じアクションで認可される。Global inference の inference-profile ARN、呼出元リージョンの foundation-model ARN、リージョンなし foundation-model ARN を許可する。既存のリージョンワイルドカードがリージョンなし ARN にも一致する。Converse 呼び出しに project/default ARN は追加しない。
- Luna は画像入力に対応する。Converse で reasoning effort を設定するフィールド名はモデルカードで確認できなかったため、追加フィールドを送らずモデル既定値を使う。
- `global.` は世界中の対応商用リージョンへ推論を振り分ける。**国内処理は保証されない**。濫用検知では classifier がフラグした入力・出力を自動検知用に最大30日保持する場合があり、Global 推論では処理先リージョンに保持される。投入データを選ぶ前に [AWS の濫用検知とデータ保持](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html) を確認する。
- 比較時は [モデル比較手順](eval-2026-09-09-model-bakeoff.md#再実行手順2026-10-01) の `--save-retrieval` / `--load-retrieval` を使い、同じ Retrieve 結果を再利用する。

## 8. デプロイとロールバック

- **ルール**: develop へのマージ（＝Amplify が自動配信）と本番スタックの deploy は **定時後** に行う（AGENTS.md）
- 手順: 統合ブランチを作る → `sam build` → `sam deploy --no-execute-changeset` で changeset を作る → 内容（Add / Modify / Replace）を確認 → `execute-change-set`。Replace が出たら止まって確認
- **announcements-monitoring は必ず TTL 無効化を含むテンプレートから**（develop 単体から作ると TTL が再有効化される事故があった）
- 配信構成の記録は issue #86 のデプロイ記録に残す（Lambda の CodeSha256、環境変数、KB ID、モデル ID、フロントの commit）
- ロールバック: 旧コードだけでなく **モデル ID と環境変数の組合せ** を指定して phase2 を再デプロイする（例: `BedrockModelId=jp.anthropic.claude-haiku-4-5-20251001-v1:0` + 当時の commit）

### SAMのデプロイ用ローカル設定

> 最終検証: 2026-10-14 — SAM設定ファイルとAWS公式CLIの`--config-file`・`--resolve-s3`・`--kms-key-id`を照合。AWSバケット設定・組織SCPの再検証は含まない。

`infrastructure/sam/samconfig-monitoring.example.toml`と`samconfig-announcements-monitoring.example.toml`を、それぞれ同じディレクトリの`.local.toml`へコピーし、既存のデプロイ成果物バケット名を各自のローカル設定から記入する。`.local.toml`はGit追跡対象外とし、共有する例には実アカウントID・メール・認証情報を入れない。既存設定を移すときはスタック名・リージョン・パラメータを保持し、バケットを新しく作らない。

`infrastructure/sam`で、`sam deploy --config-file samconfig-monitoring.local.toml --profile <profile>`または`sam deploy --config-file samconfig-announcements-monitoring.local.toml --profile <profile>`を使う。旧ファイル名でのコマンドを使い続けない。`--parameter-overrides`は設定内の一覧全体を置き換えるため、追加値だけでなく維持する値もすべて渡す。

`resolve_s3 = true`はSAMがデプロイ成果物を置くS3バケットを用意する機能であり、設定値や認証情報を保管する機能ではない。既存の移行記録では組織SCPが`PutBucketPublicAccessBlock`を拒否しているため、今回は既存バケットを維持する。将来の自動作成への移行は組織制御と権限を別途確認する。

成果物の暗号化はS3の暗号化設定と、必要ならSAMの`--kms-key-id`で管理する。KMSキーは暗号化・復号の権限を制御する鍵であり設定ファイルの保管先ではない。将来AWS内に設定を集約する場合、通常の設定はSSM Parameter Store、秘匿情報はSecrets Managerを候補とし、実行ロール・CIの認証とともに別途設計する。今回KMSキー・バケット・Secrets ManagerのAWS変更は行わない。

- 根拠: [SAM設定ファイル](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-config.html)、[sam deploy](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html)、[既存のSCP確認記録](aws-migration-runbook.md)。

## 9. コストの追い方

- リソース費: Cost Explorer で `Project=EleKnowledge` タグ（**コスト配分タグの有効化は管理アカウント側の作業**。有効化前の利用には遡及しない）
- Bedrock 費: 検索トレースのトークン数 × 単価（SSM パラメータ）を日次集計し、管理画面に「今月の推定 Bedrock 費」（P1 で実装）。CloudWatch の ModelId 別トークンは他システム混在のため参考値
- 共有 KB（OpenSearch Serverless）は他システムと共有のため按分しない

## 10. 開発用依存のhigh脆弱性（#173）

> 最終検証: 2026-10-14 — npm auditとNext ESLintプラグインの依存・呼出し箇所を照合。後続PRでの変更であり、#179のcritical修正とは分離する。

`@next/eslint-plugin-next`がルートディレクトリ探索に使う`fast-glob`は、`micromatch`経由で未修正版の`braces`を取り込む（[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)）。この依存経路だけをnpmのscoped overrideで`glob@13.0.6`へ置き換える。Nextプラグインが使う`globSync`の絶対パス・配列・braceパターン・Windowsパスと、内部リンクのlint検出が維持されることを合成ディレクトリと実ESLintで検証する。lint規則は削除・無効化しない。

これはfast-glob全APIの互換置換ではない。`glob`は`onlyDirectories`を解釈せず一致ファイルも返すが、Nextの呼出し側は存在するpages/appディレクトリだけを利用する。ファイルが混在するrootDirパターンでも内部リンク違反を検出できることをテストする。Nextプラグイン更新時は`get-root-dirs`の呼出しAPIと利用側を再確認する。他の依存へこのoverrideを広げない。

受入条件は、`npm ci`後の全依存auditでhigh・criticalが0件、production audit成功、互換性テスト・lint・typecheck・既存テスト・build成功。修正版のない脆弱性を例外登録したり、audit対象から除外したりして解消扱いにしない。

> 最終検証: 2026-10-15 — 全依存監査の期限付き例外スキーマ・推移依存への適用・期限切れの拒否をテストで照合。台帳は空で、実際の例外は追加していない。

全依存の監査は`npm run audit:all`で行う。`scripts/dependency-audit-exceptions.json`にはアドバイザリID・理由・期限（JSTの日末）・追跡Issue・人の明示承認へのリンクを必須とする。未登録・期限切れ・形式不正・分類できないhigh/criticalは失敗させる。推移依存も根本のアドバイザリ単位で判定し、別のアドバイザリまで一括免除しない。npm取得失敗やJSON不正を脆弱性0件として扱わない。

今回の台帳は空。仕組みの追加自体は脆弱性の使用許可ではなく、将来の実例外の登録にはAGENTS.mdとの整合と人の明示承認を別途確認する。例外中は修正済みと表示せず、修正版採用後に台帳から削除する。本番依存の監査は別途従来どおり実行する。

## 11. 変更履歴

- 2026-09-10 初版（issue #86 の P0 反映後）

## 11. 法令チャットのdevelopプレリリース

> 最終検証: 2026-10-09 — #155 / #156、developコード、Amplify job 64、RAG有効化設定と実配信画面を照合。developカード表示と法令画面への遷移を確認。実費は今後確認。

法令チャットの反映・受入・計測・停止は[専用手順](legal-chat-prerelease.md)を参照する。フロントの公開フラグとバックエンドのdevゲートを別々に確認し、通常RAGのKB・モデル設定を保持する。追加同期・本番有効化・範囲拡大・削除は今回の試行反映に含めない。法令のe-Govリンクは`GET /rag/document`を通らないため、同APIのPDF閲覧数を法令原文の到達件数に流用しない。現在の集計で区別できない値は未計測として[確認記録](verification-2026-10-09-legal-chat-prerelease.md)へ残す。
