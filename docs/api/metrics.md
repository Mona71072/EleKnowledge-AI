---
status: draft
phase: 2
last-verified: 2026-09-11
related-code: lambda/metrics/read/, lambda/metrics/aggregator/, frontend/src/lib/metrics.ts, frontend/src/app/admin/dashboard/, frontend/src/app/admin/cost/
---

# 運用ダッシュボード API（metrics）

> 実装 PR #110（announcements-monitoring スタック）。実環境での検証は未実施のため `draft`。設計: [design-2026-09-10-dashboard-v2.md](../design-2026-09-10-dashboard-v2.md) §2 / §5 / §6.3

**Base URL:** announcements-monitoring `AppApiUrl` output（`NEXT_PUBLIC_APP_API_URL`）

認可: Cognito Authorizer + **admin グループ**（サーバー側で 403）。

## GET /admin/metrics/dashboard

> 最終検証: 2026-09-25 — now.status / now.cloudwatchAvailable の仕様を PR #135 と照合

朝の画面を、画面の並びと同じ形で返す。日付は JST。`?trend=14|30|90`（推移の日数、既定 14）。

| キー | 内容 | 出典 | 更新 |
|---|---|---|---|
| `now.alarms[]` | 現在 `ALARM` の EleKnowledge アラーム（`name`, `severity` P1/P2, `since`） | `DescribeAlarms` | 表示時 |
| `now.status` | CloudWatch 取得失敗 → `unknown`、P1 あり → `critical`、P2 のみ → `warning`、なし → `good` | 算出 | 表示時 |
| `now.cloudwatchAvailable` | CloudWatch を取得できたか（失敗時は `false`） | CloudWatch 呼び出し | 表示時 |
| `now.last60min` | `requests` / `http5xx`（4 API 合計）、rag-api `ragP90Ms` / `ragMaxMs` / `ragCount` | `GetMetricData`（5 分粒度 × 60 分） | 表示時 |
| `now.freshness` | 前日行の `aggregatedAt`、当日 partial 行の `aggregatedAt`、`status`（09:00 JST に前日行が無ければ `warning`） | metrics テーブル | 表示時 |
| `now.activeNotices[]` | 公開中かつ未終了の告知（`id`, `title`, `severity`, `since`, `showInChat`） | announcements テーブル | 表示時 |
| `yesterday` | `incidents`（P1 遷移回数・5xx 件数・API 別）、`latency`（p50 / p90 / 最大 / 件数。件数 10 未満は `showP90=false`）、`unreached`（合計・not_found・👎・言い換え・未振り分け）、`usage`（質問・ユニーク利用者・初めて・先週同曜日）、`bedrockCost`（昨日の推定・今月の実額・確定日） | 日次行（`scope=overall`）+ `scope=cost` | 02:00 JST |
| `todaySoFar` | 当日 partial 行の `asOf`（JST HH:MM）・質問・到達できず・5xx。無ければ `null` | 当日行 | 毎時 |
| `funnel` | `yesterday` / `last7d`: `signIns` → `queries` → `pages` → `opened`（無ければ `"unmeasured"`）→ `good`。`showRates` は 7 日の分母が 30 以上のとき | 日次行 | 02:00 JST |
| `trend` | `queriesByDay[{date,total,unreached}]`、`latencyByDay[{date,p90Ms,maxMs}]`、`hourlyToday` | 日次行・時間帯別の行 | 02:00 JST / 毎時 |
| `events[]` | アラーム遷移（ALARM → 同名の OK を `durationSec` に畳む）。`logGroup` / `queryName` / `from` / `to`（前後 15 分） | 日次行の `alarmTransitions` + 直近 24 時間の `DescribeAlarmHistory` | 表示時 |
| `reference` | `topDocuments`（30 日 TOP10）、`lastEval`（`scope=eval` の最新。無ければ `null`） | 日次行 | 02:00 JST |
| `thresholds` | `sloP90Ms` 20000 / `p1MaxMs` 25000 / `timeoutMs` 29000 / `rateDenominatorMin` 30 | 定数 | — |

状態色は 4 段階（`good` / `warning` / `serious` / `critical`）。閾値はアラームと同じ値（設計 §2.8）。件数の `null` は「集計行が無い」で、`0` と区別する。

## GET /admin/metrics/cost

コスト画面。`?month=YYYY-MM`（既定は当月、**UTC 日**基準）。

| キー | 内容 |
|---|---|
| `settledThrough` | 確定扱い（D-2 以前）の最終日 |
| `confirmed` | 実額・確定: Bedrock のモデル行（入力 / 出力 / キャッシュ）と Amplify、`budgetUsd` / `budgetPct` / `forecastUsd` |
| `unattributed` | 実額・帰属未確認（CloudWatch / Lambda / DynamoDB / API Gateway / S3 / WAF …のアカウント合計。タグ有効化まで） |
| `shared` | 共有・按分不能（OpenSearch Serverless、埋め込みモデル） |
| `otherSystems` | 他モデルの Bedrock 行など、EleKnowledge と無関係なもの（参考） |
| `checks` | `soleUser`（Bedrock 呼び出し数 ≒ 候補あり回答数）、`actualVsEstimate`（±20 % 超で `warning`）、`modelIds` |
| `daily[]` / `queriesDaily[]` | Bedrock 実額（UTC 日）と質問数（JST 日）。日付基準が違うので別系列 |
| `perQuery` / `projection` | 実額 ÷ 質問・回答、100 / 300 / 1,000 質問/日の月額見込み（推定） |

Cost Explorer は日次バッチが 1 日 2 回だけ呼ぶ（0.02 USD/日）。画面表示では呼ばない。

## GET /admin/metrics（旧）

`?period=today|week|month|custom`。旧ダッシュボードの形（`kpi` / `series` / `topDocuments` / `health`）。UI 切替後に削除する。

## エラー

| status | error | 条件 |
|---|---|---|
| 403 | `Forbidden` | admin グループでない |
| 500 | `InternalServerError` | DynamoDB / CloudWatch の失敗（本文は一般化） |
