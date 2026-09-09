---
status: draft
last-verified: 2026-09-10
related-code: lambda/metrics/aggregator/app.py, lambda/metrics/read/app.py, infrastructure/sam/announcements-monitoring-template.yaml, frontend/src/app/admin/dashboard/page.tsx, frontend/src/lib/metrics.ts
---

# 設計: 日次 KPI（metrics）v2 — JST 境界・毎時集計・新指標・推定コスト

> **状態:** 設計（実装前）。決定の経緯は issue #86（コメント 3・4・16）。実装は初週。

## 1. 現状と課題（2026-09-09 実測）

| # | 課題 | 場所 |
|---|---|---|
| A | 日付境界が UTC。「9/9」の行に JST 9/9 09:00〜9/10 09:00 が入る | `aggregator/app.py:44,142`、`read/app.py:39` |
| A | 「今日」タブが翌日 02:00 JST まで常に 0 | 日次スケジュールのみ |
| B | 週・月のアクティブユーザーが日別の **最大値**（ユニーク数ではない） | `read/app.py:112` |
| B | 増分が常に「最終日 vs 前日」 | `read/app.py:115` |
| B | 健全性: `errorRate` は Lambda Errors 依存（500 を return するため常に 0）、`http5xx` は rag-api のみ、`latencyP90` は Lambda Duration | `aggregator/app.py:140-163` |
| C | 指標が少ない（not_found 率、聞き返し率、👎 理由、要望件数、機種別、コストが無い） | — |
| C | Scan ベース（現状 272 項目・平均 16 KB。想定上限 1,000 クエリ/日で約 30 MB/日） | `aggregator/app.py:47-64` |

## 2. 方針（決定済み）

- 日次確定（02:00 JST）+ **当日は毎時更新**（24 時間、月 1 USD 未満）
- 日次行に加えて **時間帯別の行** を保存し、後から時間帯の分析ができるようにする
- TTL は無効（PR #93 反映済み）。無期限保持
- リアルタイム性はアラーム（監視スタック）が担い、ダッシュボードは業務向け

## 3. 時刻

- **JST 固定オフセット** `timezone(timedelta(hours=9))` を使う（DST 無し。Lambda 実行環境の tz データベースに依存しない）
- `metricDate`（日次）= JST の日付 `YYYY-MM-DD`。chatlogs の `timestamp`（UTC ISO）を JST に変換して日付を決める
- Scan の FilterExpression は UTC に戻した境界 `[JST 00:00 → UTC 前日 15:00, 翌日 15:00)` で指定する（既存の `#ts BETWEEN` を流用）
- read 側の `today` も JST で決める

## 4. 行の種類（`metrics-dev`、PK `metricDate` / SK `scope`）

| scope | metricDate | 内容 | 書き込み |
|---|---|---|---|
| `overall` | `YYYY-MM-DD` | 日次 KPI（既存 + 新指標）。当日は `partial: true` | 毎時（当日を累計で上書き）+ 02:00 JST に前日を確定 |
| `hourly` | `YYYY-MM-DDTHH`（JST） | その 1 時間の件数系（queries, notFound, clarify, feedbackGood/Bad, activeUsers, inputTokens, outputTokens） | 毎時（直前 1 時間分）。02:00 JST に前日 24 行を再計算 |
| `eval` | `YYYY-MM-DD` | 週次のゴールデンセット評価（別設計） | — |

GSI `scope-metricDate-index` はそのまま使える。

## 5. 日次行（`overall`）の項目

| 項目 | 定義 | 出典 |
|---|---|---|
| `queries`, `sessions`, `activeUsers` | 既存どおり | chatlogs |
| `userIds` | 期間内に発話した Cognito sub の一覧（週・月のユニーク数を read 側で和集合するため。個人情報ではない） | chatlogs |
| `newUsers` | その日に初めて発話した sub の数（scan 対象の 60 日内で最古の日付がその日） | chatlogs |
| `notFound`, `clarify`, `pages` | assistant の `responseType` 件数 | chatlogs |
| `feedbackGood`, `feedbackBad`, `likeRate` | 既存 | chatlogs |
| `feedbackReasons` | `{wrong_doc, unresolved, bad_answer, other, none}` | chatlogs |
| `productWishes` | `role=product_wish` の件数 | chatlogs |
| `byModelType` | `{<modelType or "none">: {queries, bad, notFound}}` | `queryFilters.modelType` |
| `byCategory` | `{<category or "all">: {queries, bad}}`（複数選択はそれぞれに加算） | `queryFilters.category` |
| `topDocuments` | 既存（上位 10） | `sourceDocuments` |
| `inputTokens`, `outputTokens`, `estimatedBedrockCostUsd`, `tokenizedQueries` | `retrievalTrace.generation` の合計と、SSM 単価による推定 | chatlogs（トレース実装後。無い項目は 0） |
| `latency` | `{ragP50, ragP90}` を **API Gateway `Latency`**（rag-api）から取得（ms） | CloudWatch |
| `http5xx` | 4 API（rag / chat / auth / app）の `5XXError` 合計 | CloudWatch |
| `apiCount` | 4 API の `Count` 合計 | CloudWatch |
| `errorRate` | `http5xx / apiCount`（Lambda Errors は使わない） | 算出 |
| `incidents` | その日に **ALARM に遷移した P1 アラームの回数**（`DescribeAlarmHistory`、`EleKnowledge-{env}-P1-` プレフィックス） | CloudWatch |
| `partial`, `aggregatedAt`, `logicVersion` | 当日更新中か、集計時刻、集計ロジック版 | — |

## 6. read API（`GET /admin/metrics`）の変更

- `period=today|week|month|custom` はそのまま。`today` は当日の `overall`（partial）+ `hourly` の当日分を `series.queriesByHour` などで返す
- `kpi.activeUsers.value` = 期間内の `userIds` の和集合の数（`userIds` 自体は返さない）
- `delta` = 「当期間 vs 直前の同じ長さの期間」（today は前日、week は前週、month は前月）
- 追加: `kpi.notFoundRate`, `kpi.clarifyRate`, `kpi.estimatedBedrockCostUsd`（月累計）, `breakdown.feedbackReasons`, `breakdown.byModelType`, `breakdown.byCategory`, `series.notFoundByDay`
- `health` の出典を §5 に合わせる。`openIncidents` は **現在 ALARM 状態の P1 アラーム数**（`DescribeAlarms` をリアルタイムに 1 回）

## 7. UI（`/admin/dashboard`）

- 「今日」タブ: 時間帯別バー（クエリ数 / not_found / 👎）と `partial` 表示（「HH:MM 時点」）
- KPI タイル追加: not_found 率、聞き返し率、推定 Bedrock 費（今月）
- 内訳: 👎 理由、機種別（クエリ数と 👎 率）、カテゴリ別
- 既存の「表で見る」フォールバックを新チャートにも付ける

## 8. スケジュールと IAM

- EventBridge: 既存 `cron(0 17 * * ? *)`（02:00 JST、前日確定）に加えて `rate(1 hour)`（当日更新）。ハンドラは event の `mode`（`daily` / `hourly`）で分岐。手動: `{"date": "YYYY-MM-DD"}`（JST 日付）
- IAM 追加: `cloudwatch:DescribeAlarmHistory`, `cloudwatch:DescribeAlarms`, `ssm:GetParameter`（単価）
- 環境変数追加: `API_NAMES`（4 API 名、カンマ区切り）、`ALARM_PREFIX`（`EleKnowledge-dev-P1-`）、`UNIT_PRICE_PARAM`

## 9. Scan の上限と切替条件

- 毎時 Scan は「当日分のみ」の FilterExpression だが、Scan 自体はテーブル全体を読む。現状 4 MB、想定上限で 60 日 ≈ 2 GB → 毎時 2 GB 読みは非現実的
- **切替条件: テーブルサイズ 200 MB 超**（`describe-table` の TableSizeBytes）で、(a) `dateKey`（JST 日付）属性 + GSI `dateKey-timestamp-index` を追加して当日分だけ Query、または (b) Athena 集計に移行。試行期間は不要

## 10. テスト

- JST 境界: UTC 14:59 / 15:00 の timestamp が前日 / 当日に振り分けられる
- hourly 行のキーと集計対象時間
- unique users の和集合、delta の期間比
- health: 4 API 合算、Latency、alarm history の件数（CloudWatch 呼び出しはモック）
- コスト: SSM 単価 × トークン。単価が無いモデルは 0 と `unpricedQueries` を記録

## 11. 実装分割（PR）

| 順 | PR | 内容 |
|---|---|---|
| 1 | `fix(metrics)` | JST 境界 + 毎時更新（`partial`）+ hourly 行 + EventBridge/IAM。**UI 変更なし**（既存表示はそのまま動く） |
| 2 | `feat(metrics)` | 新指標・ユニークユーザー・期間比・health の出典変更・単価 SSM とコスト（read API 拡張） |
| 3 | `feat(dashboard)` | UI（時間帯別バー、KPI タイル、内訳）。develop マージで Amplify 公開（定時後） |
| 4 | `docs` | `docs/api/`（metrics API の正本を新設）、`docs/data-model.md`（production、事前確認要） |

## 12. 決めておくこと（実装前）

- `incidents` を P1 のみにするか P1+P2 にするか → **P1 のみで決定**（itai 2026-09-10）。P1 / P2 は監視スタックのアラーム名に付けた重要度で、定義は `docs/ops-runbook.md` §1（P1 = 利用者影響あり・即対応、P2 = 翌営業日）と §2（各アラームの分類）にある
- `userIds` を日次行に持つことの可否（sub のリスト。最大 100 人 × 36 文字 = 4 KB） → **可で決定**（itai 2026-09-10）
- 推定コストの表示単位（USD のみか、円換算も出すか） → **USD のみで決定**（itai 2026-09-10。為替は扱わない）
