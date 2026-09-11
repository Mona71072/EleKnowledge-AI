---
status: draft
last-verified: 2026-09-10
related-code: lambda/metrics/aggregator/app.py, lambda/metrics/read/app.py, frontend/src/app/admin/dashboard/page.tsx, frontend/src/lib/metrics.ts, frontend/src/components/dashboard/charts.tsx, infrastructure/sam/monitoring-template.yaml, infrastructure/sam/phase2-template.yaml, infrastructure/sam/announcements-monitoring-template.yaml, lambda/rag/rag-function/app.py
---

# 設計: 運用ダッシュボード v2 — 毎朝の判断・健全性・切り分け・コスト

> **状態:** 設計（実装前・共同確認用）。実装コードは含まない。
> **前提:** データ源は [telemetry-inventory-2026-09-10.md](./telemetry-inventory-2026-09-10.md) に列挙したものが上限。棚卸しに無いものは「足す提案」として作業量つきで書く。
> **上書き対象:** [design-2026-09-10-metrics-v2.md](./design-2026-09-10-metrics-v2.md) の §6（read API）・§7（UI）・§11（PR 分割）は本書で置き換える。§3〜§5（JST 境界・毎時集計・日次行）は本書の §6 の差分を足したうえで **そのまま生かす**。[design-2026-09-10-retrieval-trace.md](./design-2026-09-10-retrieval-trace.md) は変更しない（§5.1 でコスト算出の役割だけ変える）。
> **記法:** 外部仕様への言及は ◎ = 公式仕様・実測で確度が高い、△ = 記憶に頼っており実装時に一次情報で確認、の 2 段で書き分ける。
> **モック:** [design-2026-09-10-dashboard-v2-mock.html](./design-2026-09-10-dashboard-v2-mock.html)（「平穏な朝」「異常がある朝」の切替つき。数字は表示例。§8 の回答と別立て B2 / B3 / B5 を反映済み）

---

## 0. 結論

**載せるべきもの（朝の 1 画面）** は次の 5 つだけ。上から順に「いま」「昨日」「到達ファネル」「14 日の推移」「直近 7 日の出来事」。

1. **いま**: 現在 ALARM 状態のアラーム（P1 / P2 別）と、直近 60 分のリクエスト数・5xx・p90。ページを開いた瞬間に CloudWatch を直接読む
2. **昨日**: 障害（P1 遷移回数・5xx 件数）／応答時間（API Gateway `Latency` の p90 と最大）／到達できなかった質問（not_found + 👎 の**件数**）／利用（質問・ユニーク利用者・初めての利用者）／Bedrock 費（昨日の推定・今月の実額）
3. **到達ファネル**: ログイン → 質問 → 候補あり → 資料を開いた → 👍。製品の成功定義（資料到達）を数える唯一の場所
4. **推移（14 日）**: 質問数（到達できずを積み上げ）と rag 応答時間（p90・最大、20 s / 25 s の基準線）
5. **出来事（7 日）**: アラームの ALARM/OK 遷移と（後続で）デプロイ。各行から CloudWatch Logs Insights へ時間範囲つきで飛ぶ

**今の画面の何が間違っているか**

- 健全性 4 項目のデータ源が違う（Lambda `Errors`、Lambda `Duration`、rag-api だけの 5xx、`incidents: 0` 固定）。加えて **閾値がアラームと別物**（p90 3 s / 6 s / 10 s。Sonnet 5 の正常値 9〜12 s で常に「悪化」になる）
- 「いいね率」を主役に置いている。母数が 1 日数件のときの率は判断に使えないし、率そのものは製品目標ではない
- 期間タブ（今日／今週／今月）が画面の全数字を差し替えるため、毎朝同じ位置を同じ目で見る運用ができない。「今日」は翌日 02:00 まで 0
- 「いま正常か」を示すものが無い。アラームは鳴るが、画面には現在の ALARM 状態が出ない

**画面構成の判断**: 役割 1（毎朝）と 2（いま）は **1 画面（`/admin/dashboard`）** に統合する。役割 4（コスト）は **別画面（`/admin/cost`）** にする。役割 3（切り分け）は **画面を作らず、記録を足して CloudWatch に導線を引く**。理由は §1。既存の 2 画面は残し、**失敗・改善提案**には期間絞り込みと振り分けの記録（§9）、**お知らせ管理**には障害時のテンプレートとチャット画面での表示と導線（§10）を足す。各要素には推奨度（◎ 入れる前提 / ○ あると良い / △ 判断材料）を付けたので、取捨選択はそこで。

**コストの判断**: Bedrock の生成費は **Cost Explorer の「Claude Sonnet 5」行を実額として採用**する。先行決定していたトークン × SSM 単価の推定は廃止せず、役割を「1 質問あたりの単価」「見込み」「実額との整合チェック」に限定する。実額と推定の差が 20 % を超えたら「唯一の利用者」前提が崩れたサインとして画面に出す（§5.5）。

**予算アラート**: AWS Budgets を **Sonnet 5 の行に 1 本**（月 100 USD、実績 50 % / 100 %、予測 100 %）、通知は既存 SNS `eleknowledge-alerts-dev` へ。アカウント全体の予算は他システム支配のため置かない（§5.7）。

**チャートライブラリ**: 追加しない。必要なのは棒・積み上げ棒・折れ線・横棒・表だけで、`charts.tsx` の延長で足りる（§6.5）。

---

## 1. 4 つの役割と画面の対応

| 役割 | 朝の問い | 答える場所 | 更新 | 今日のデータで成立するか |
|---|---|---|---|---|
| 1 毎朝の判断 | 昨日うまくいったか。今日直すものは何か | `/admin/dashboard` 「昨日」「ファネル」「推移」「出来事」 | 02:00 JST 確定 + 当日は毎時 | ほぼ成立。「資料を開いた」だけ計測が無い（§4.3 I3 で足す） |
| 2 健全性 | いま正常か | 同画面の最上段「いま」 | ページを開くたび（CloudWatch を直接読む） | 成立（`DescribeAlarms` と `GetMetricData` は今すぐ呼べる） |
| 3 切り分け | どこで何が起きたか | ダッシュボードの「出来事」→ CloudWatch Logs Insights | 記録は常時、参照は都度 | **不成立**。アクセスログ未配線・エラー行にリクエスト ID が無い（§4） |
| 4 コスト | どこでいくら。利用量に見合うか | `/admin/cost` | 日次（Cost Explorer を 1 日 2 回） | Bedrock 生成費は成立。他は帰属未確認か按分不能（§5） |
| 1' 今日直すもの | 到達できなかった 1 件ずつをどう扱い、何を直したか | `/admin/failures`（§9） | 表示時 | 一覧は成立。期間の絞り込みと振り分けの記録先が無い |
| 3' 利用者への告知 | 障害中・受付停止を利用者にどう伝えるか | `/admin/announcements`（§10） | 表示時 | CRUD は成立。文面の型・導線・チャット画面での表示が無い |

**1 画面に統合しない理由（役割 4）**: コストは「月」の単位で読むもので、日付基準も UTC（Cost Explorer の仕様）で違う。朝の画面に混ぜると「昨日」の枠と噛み合わず、数字の意味を毎回読み替えることになる。朝の画面には Bedrock 費のタイル 1 枚だけ置き、そこからコスト画面へ飛ぶ。

**役割 3 の画面を作らない理由**: いま欠けているのは「見る画面」ではなく「見るべき記録」。アクセスログとリクエスト ID が揃えば、CloudWatch Logs Insights がそのまま切り分け画面になる。2 人で Next.js にログビューアを作る工数を、記録を足す側に回す。ダッシュボードの役割は「いつ・どのアラームか」を示して、時間範囲つきで Logs Insights へ飛ばすところまで。

**行き来**: 管理コンソールのサブナビ（`admin/layout.tsx`）に「コスト」を足して 4 タブ（ダッシュボード／失敗・改善提案／コスト／お知らせ）。ダッシュボードの「到達できず」タイルは `/admin/failures` の該当フィルタへ、「Bedrock 費」タイルは `/admin/cost` へ、「出来事」の各行は CloudWatch へリンクする。

---

## 2. 朝の画面 `/admin/dashboard`

### 2.1 並び

「異常がある朝」は最上段の帯が色つきで、「平穏な朝」は帯が 1 行の緑で終わる。それ以下は毎朝同じ位置に同じ数字が並ぶ。期間タブは廃止し、枠は「昨日」「直近 7 日」「直近 14 日」に固定する（推移チャートだけ 14 / 30 / 90 日の切替を持つ）。

```
┌ いま ──────────────────────────────────────────────────────────────┐
│ ● 正常  ALARM なし │ 直近60分: 質問 0 / 5xx 0 / p90 — │ 前日集計 02:03 済 │
└──────────────────────────────────────────────────────────────────────┘
┌ 昨日（9/9 火）──────────────────────────────────────────────────────┐
│ [障害]      [応答時間]     [到達できず]   [利用]          [Bedrock 費]   │
│ ● 0 / 0     ● p90 11.2s    3 件 →失敗     質問 6          推定 0.08 USD  │
│ P1 / 5xx    最大 18.4s     not_found 2    利用者 4        今月実額 1.5   │
│                            👎 1           初めて 1        (D-2 まで)     │
│ 今日ここまで（08:40）: 質問 1 / 到達できず 0 / 5xx 0                    │
└──────────────────────────────────────────────────────────────────────┘
┌ 到達ファネル ─────────────── 昨日 ───┬─── 直近 7 日 ─────────────────┐
│ ログイン 9 → 質問 6 → 候補あり 4 → 資料を開いた（未計測）→ 👍 1          │
└──────────────────────────────────────────────────────────────────────┘
┌ 質問数（到達できず を積み上げ）14 日 ┐ ┌ rag 応答時間 p90・最大 14 日 ┐
│ ▂▃▁▅▂▃▂▆▃▂▁▂▃▂                     │ │ ~~~~~~~~~ 25s ---- 20s ----   │
└──────────────────────────────────┘ └──────────────────────────────┘
┌ 出来事（直近 7 日）───────────────────────────────────────────────────┐
│ 9/9 23:02  デプロイ phase2（モデル切替 Sonnet 5）           → 記録     │
│ 9/8 14:11  ALARM P2-rag-api-4xx-spike 14:11–14:16 (5 分)   → ログ     │
└──────────────────────────────────────────────────────────────────────┘
（最下部・折りたたみ）参照文書 TOP10（30 日）／ 最終ゴールデン評価
```

### 2.2 いま（帯）

| 表示 | 定義 | データ源 | 状態色 |
|---|---|---|---|
| ALARM 状態 | 現在 `ALARM` の EleKnowledge アラーム名（P1 / P2 で分ける） | `DescribeAlarms`（`AlarmNamePrefix=EleKnowledge-dev-`）を read API がページ表示のたびに 1 回 | P1 あり → 重大、P2 のみ → 注意、なし → 正常 |
| 直近 60 分 | 4 API（rag / chat / auth / app）の `Count` 合計、`5XXError` 合計、rag-api `Latency` p90 | `GetMetricData`（5 分粒度 × 60 分）を同じく 1 回 | 5xx ≥ 1 → 注意。件数 0 は「静か」として正常（色なし） |
| 鮮度 | 前日行の `aggregatedAt`、当日行の `partial` 時刻 | metrics-dev | 09:00 JST 時点で前日行が無い → 注意「集計未完了」（ランブック §5.4 に直結） |
| 告知（§10.3、◎） | P1 が ALARM 中なら「利用者へ告知 →」（障害テンプレートを開く）。表示中の告知があれば「告知中: タイトル（HH:MM から）」と「表示終了」 | announcements テーブル（公開中かつ未終了） | 色なし |

「いま」を metrics-dev の毎時行から作らない。毎時行は最大 1 時間遅れるし、「正常か」の判定はアラームが 5 分粒度で既にやっている。判定ロジックを画面側で二重に持たず、**アラームの状態をそのまま映す**。

### 2.3 昨日（タイル 5 枚）

| # | タイル | 主表示 | 副表示 | 状態色 | データ源 |
|---|---|---|---|---|---|
| Y1 | 障害 | P1 の ALARM 遷移回数 / 5xx 件数 | 5xx の内訳（API 別 + Amplify） | P1 ≥ 1 → 悪化以上。5xx: 0 正常 / 1–5 注意 / 6–20 悪化 / 21〜 重大 | `DescribeAlarmHistory`、API GW `5XXError`（4 API）、`AWS/AmplifyHosting 5xxErrors` |
| Y2 | 応答時間 | rag-api `Latency` p90（件数 ≥ 10 のとき）。件数 < 10 なら中央値 | 最大値 | p90: ≤ 20 s 正常 / ≤ 25 s 注意 / ≤ 29 s 悪化 / 超 重大。最大 > 25 s なら注意以上 | API GW `Latency`（ApiName=rag-api-dev） |
| Y3 | 到達できず | `not_found` + 👎 の件数（重複は 1 件） | not_found / 👎 の内訳・言い換え（別立て B2 採用時）・**未振り分け n**（§9.4）。`/admin/failures?since=昨日` へリンク | **色なし**（作業量であって健全性ではない） | chatlogs（`responseType`, `feedback`） |
| Y4 | 利用 | 質問数 | ユニーク利用者・初めての利用者・先週同曜日の質問数 | 色なし | chatlogs（`userIds`, `newUsers`） |
| Y5 | Bedrock 費 | 昨日の推定（トークン × 単価） | 今月の実額（Cost Explorer、D-2 まで）。`/admin/cost` へリンク | 昨日の推定が直近 7 日中央値の 3 倍超 **かつ** 1 USD 超 → 注意 | `AWS/Bedrock InputTokenCount / OutputTokenCount`（トレース実装後はトレース）、Cost Explorer |

タイル直下に「今日ここまで（HH:MM 時点）」を 1 行。当日の `partial` 行（毎時更新）から質問・到達できず・5xx の 3 つだけ出す。朝に起きた問題を昼まで待たずに拾うため。

**▲▼ の増減表示は廃止する**。3 件が 2 件に減って赤い ▼ が出る画面は、少件数の期間中ずっとノイズになる。比較は「先週同曜日: n」の灰色テキストだけ。

### 2.4 到達ファネル

製品の成功定義は「資料に到達し、疑問が解ける」（[decisions-2026-07-29-success-document-reach.md](./decisions-2026-07-29-success-document-reach.md)）。いまの画面にはこれを数える場所が無い。ファネルは「昨日」と「直近 7 日」の 2 行で同じ形を並べる（7 日行は少件数のぶれを均すため）。

| 段 | 定義 | データ源 | 今取れるか |
|---|---|---|---|
| ログイン | `SignInSuccesses` 合計 | `AWS/Cognito`（UserPool + UserPoolClient） | 取れる（G4、未配線） |
| 質問 | `role=user` 件数 | chatlogs | 取れている |
| 候補あり | `responseType=pages` 件数 | chatlogs | 取れる（運用開始日以降のみ。N2） |
| 資料を開いた | 引用リンクから文書を開いた **回答の数**（同じ回答の複数クリックは 1） | chatlogs の `documentOpens`（§4.3 I3 で追加） | 実装 PR（rag テレメトリ）適用後に取れる。行に無い日は「未計測」と灰色表示 |
| 👍 | `feedback=good` 件数 | chatlogs | 取れている |

段は入れ子ではない（👍 は資料を開かなくても押せる）。比率の線は引かず、**件数だけ**を並べる。

「資料を開いた」は到達の代理指標であって「疑問が解けた」ではない。それでも、資料到達を第一優先と決めた方針に対して **唯一の直接指標** なので、実装の優先度は §4.3 で P0 にする。

### 2.5 推移（14 日、切替 30 / 90 日）

| チャート | 形 | 軸 | 内容 |
|---|---|---|---|
| 質問数 | 積み上げ棒 | 件数 1 軸 | 下段: 到達できず（not_found + 👎）、上段: それ以外。色は状態パレットの「注意」と系列青 |
| rag 応答時間 | 折れ線 2 本 | ms 1 軸 | p90 と最大。基準線 20 s（SLO / P2 アラーム）と 25 s（P1 アラーム） |

いいね率の折れ線は外す（§2.9）。5xx の日別棒も置かない。5xx はタイル Y1 と「出来事」で足りる。

### 2.6 出来事（直近 7 日）

| 行の種類 | 内容 | データ源 | リンク先 |
|---|---|---|---|
| アラーム遷移 | 時刻、アラーム名、ALARM → OK の継続時間 | `DescribeAlarmHistory`（日次行に `alarmTransitions` として保存 + 当日分は表示時に直近 24 時間を取得） | Logs Insights の該当ロググループ・時間範囲（前後 15 分） |
| デプロイ・設定変更（後続 P2） | 時刻、スタック名、`UpdateFunctionConfiguration` なら環境変数変更（モデル切替） | CloudTrail `LookupEvents`（棚卸し §2.3。管理イベントは 90 日読める） | issue #86 のデプロイ記録 |

「いつ何が起きたか」が 1 列に並ぶことで、切り分けの最初の問い（変更の直後か、単発か、繰り返しか）に画面だけで答えられる。

Logs Insights への深いリンクはコンソール URL に時間範囲とクエリを埋め込める（△ エンコード形式はコンソール依存。実装時に実機で確認）。埋め込みが崩れる場合は保存クエリ名と時間範囲のテキストを表示してコピーさせる形に落とす。

### 2.7 少サンプルでの表示規則

当分は 1 日数件で、上限でも 1 日 1,000 件。以下を read API と UI の共通ルールにする。

1. **件数が先、率は後。** 率は分母が 30 以上のときだけ副表示に出し、分母を併記する（`3/40`）。分母 30 未満は率を出さない
2. **状態色はシステム信号にだけ付ける。** アラーム・5xx・応答時間・コスト急増は色あり。到達できず・利用・ファネルは色なし。少件数の品質指標に色を付けると、毎朝「悪化」が出て見なくなる
3. **p90 は件数 10 以上のときだけ。** 未満は中央値と最大を出す
4. **0 と「無い」を分ける。** 集計行が無い日は `—` と「未集計」、0 件は `0`。read API は `null` と `0` を区別して返す
5. **比較は先週同曜日。** 前日比は曜日の影響が大きく、少件数では常に大きな変化率になる
6. **閾値はアラームと同じ値にする。** 画面が「注意」でアラームは沈黙、あるいはその逆、という状態を作らない（§2.8）

### 2.8 状態色の閾値（アラームと一致させる）

| 指標 | 正常 | 注意 | 悪化 | 重大 | 根拠 |
|---|---|---|---|---|---|
| 現在の ALARM | なし | P2 のみ | — | P1 あり | ランブック §1 の P1 / P2 定義 |
| 5xx（昨日、4 API + Amplify） | 0 | 1–5 | 6–20 | 21〜 | 既存 `THRESHOLDS` を踏襲。1 件でも P1 が鳴る設計なので注意から始める |
| rag p90（昨日） | ≤ 20 s | ≤ 25 s | ≤ 29 s | > 29 s | SLO p90 20 s（Q1 決定）= P2 `rag-duration-p90`、P1 `rag-duration-max` 25 s、API GW 制限 29 s |
| rag 最大（昨日） | ≤ 25 s | ≤ 29 s | > 29 s | — | 25 s 超は 504 の可能性、29 s 超は 504 が確実に出ている |
| Bedrock 費（昨日推定） | — | 7 日中央値の 3 倍超かつ 1 USD 超 | — | — | 暴走呼び出しの検知。1 USD の下限で少額期のノイズを避ける |
| 集計鮮度 | 前日行あり | 09:00 JST に前日行なし | — | — | ランブック §5.4 |

SLO は **p90 20 s** と決めた（Q1、itai 2026-09-10）。`AGENTS.md` の「RAG 応答 p95 < 3 s」は Sonnet 5 の実測（平均 9〜12 s）と両立しないため、別 PR（AI ルール同期の手順）で「RAG 応答 p90 < 20 s」に改定する。画面の「正常」は SLO 内、「注意」は SLO 超過（= P2 アラームが鳴る水準）と読める。

### 2.9 載せないもの

| 外すもの | 理由 | 代わり |
|---|---|---|
| いいね率（KPI タイル・推移） | 母数が数件〜数十件の期間に率は判断に使えない。率そのものは製品目標ではない | ファネルの「👍」件数。分母 30 以上になったら副表示で率 |
| errorRate | 5xx **件数** で行動が決まる。分母 3 の率に意味は無い | Y1 |
| Lambda `Duration` p90 | 利用者の体感ではない | API GW `Latency` |
| 期間タブ（今日／今週／今月） | 全数字が差し替わり、朝の目視が毎回リセットされる | 「昨日」「7 日」「14 日」の固定枠 + 推移チャートの日数切替 |
| 機種別・カテゴリ別の内訳（metrics-v2 §7） | `queryFilters` が全項目の 11 % にしか無く、当分は 1 セル 0〜2 件。朝の判断を変えない | 日次行には保存する。`/admin/failures` のフィルタで個別に見る。質問が 2 週間連続で 1 日 30 件を超えたら再検討 |
| 👎 理由の内訳（metrics-v2 §7） | `/admin/failures` の理由チップと同じもの。二重表示になる | Y3 から failures へリンク |
| 時間帯別バー（metrics-v2 §7「今日」タブ） | 毎時行は「今日ここまで」の 1 行と「いま」の帯で使い切る。時間帯の分析は月次で Athena | 日次行・毎時行は保存する |
| 部門別・役職別 | 収集していない・今後もしない（N4） | — |
| 参照文書 TOP5（現在の位置） | 朝の行動を変えない。KB 整備の月次材料 | 最下部に折りたたみで TOP10（30 日）を残す |
| Bedrock の `InvocationLatency` / `TimeToFirstToken` | 応答時間は API GW `Latency` で足りる。段階の切り分けはトレースの `latencyMs` が担う | 切り分け時に CloudWatch で直接見る（§4.2） |

---

## 3. 指標の定義一覧

更新の列は「日次」= 02:00 JST に前日分を確定、「毎時」= 当日を累計で上書き（metrics-v2 §2）、「表示時」= read API が CloudWatch を直接呼ぶ。

| ID | 表示名 | 定義 | データ源（棚卸し番号） | 更新 | 状態色 |
|---|---|---|---|---|---|
| N1 | 現在の ALARM | `StateValue=ALARM` のアラーム名一覧 | `DescribeAlarms`（§2.2 で既に使用中の名前空間） | 表示時 | あり |
| N2 | 直近 60 分 | 4 API の `Count` / `5XXError` 合計、rag-api `Latency` p90 | `AWS/ApiGateway` | 表示時 | 5xx のみ |
| N3 | 鮮度 | 前日行 `aggregatedAt`、当日行 `partial` と時刻 | metrics-dev | 表示時 | あり |
| Y1 | 障害 | P1 の ALARM 遷移回数、5xx 合計（4 API + Amplify） | `DescribeAlarmHistory`（G6）、`AWS/ApiGateway 5XXError`、`AWS/AmplifyHosting 5xxErrors`（G3） | 日次・毎時 | あり |
| Y2 | 応答時間 | rag-api `Latency` の p90・p50・最大（ms） | `AWS/ApiGateway Latency` | 日次・毎時 | あり |
| Y3 | 到達できず | assistant 行のうち `responseType=not_found` または `feedback=bad`（重複は 1） | chatlogs | 日次・毎時 | なし |
| Y4 | 利用 | `queries`、`userIds` のユニーク数、`newUsers`、先週同曜日の `queries` | chatlogs（metrics-v2 §5） | 日次・毎時 | なし |
| Y5 | Bedrock 費 | 昨日: トークン × SSM 単価。今月: Cost Explorer Sonnet 5 行の D-2 までの合計 | `AWS/Bedrock InputTokenCount / OutputTokenCount`（G2）→ トレース実装後は `retrievalTrace.generation`。Cost Explorer（§5） | 日次 | あり |
| F1〜F5 | ファネル | ログイン / 質問 / 候補あり / 資料を開いた / 👍 | `AWS/Cognito SignInSuccesses`（G4）、chatlogs、chatlogs の `documentOpens`（§4.3 I3）、chatlogs | 日次・毎時 | なし |
| T1 | 質問数の推移 | 日別 `queries` と `notFound + bad` | metrics-dev | 日次 | — |
| T2 | 応答時間の推移 | 日別 p90 と最大 | metrics-dev | 日次 | 基準線のみ |
| E1 | 出来事 | アラーム遷移（名前・開始・終了・継続）、デプロイ（後続） | `alarmTransitions`（日次行）+ 表示時に直近 24 時間、CloudTrail（P2） | 日次 + 表示時 | — |
| R1 | 参照文書 TOP10 | 30 日の `topDocuments` 合算 | metrics-dev | 日次 | — |
| R2 | 最終ゴールデン評価 | 最新の `scope=eval` 行の日付と `hit_in_candidates` n/N | metrics-dev（metrics-v2 §4、別設計） | 週次 | — |

コスト画面の指標は §5.3。

---

## 4. 切り分け（役割 3）— 何を記録し始めるか

### 4.1 昨夜の 4xx 5 件が追えなかった理由

4xx の一次情報になるはずのものが 3 つとも欠けている。

1. **アクセスログが無い**（G1）。5 ステージすべて未設定で、受け皿のロググループは 0 バイト。誰が・どのパスを・どの結果で叩いたかの 1 行が存在しない
2. **実行ログには内訳が出ない**。`loggingLevel=INFO` の実行ログは「Method completed with status: 403」は残すが、送信元 IP と失敗種別（WAF ブロック／認可拒否／トークン失効）を 1 行で読めない。△ WAF がブロックした要求は実行ログ自体に残らず、アクセスログにだけ `wafResponseCode` 付きで残る
3. **Lambda のエラー行にリクエスト ID が無い**。`rag-function` の 500 経路は `ClientError` を握って 500 を返すだけで、API Gateway のリクエスト ID・失敗した段階（retrieve / generate / save）・`messageId` を出さない。アクセスログがあっても Lambda ログと突き合わせられない

4xx アラームの閾値は 5 分 30 件なので 5 件は鳴っていない。それでも「後から追える」状態にしておくのが役割 3 の要件で、それにはまず記録が要る。

### 4.2 経路ごとの信号（どこで何が起きているか）

利用者の 1 回の質問が通る経路と、各段で「壊れた」ときに見える信号。太字は本設計で足すもの。

| 段 | 典型症状 | 今ある信号 | 見る場所 | 足すもの |
|---|---|---|---|---|
| Amplify（画面配信） | 画面が開かない | `AWS/AmplifyHosting 5xxErrors / Requests`（G3、未参照。**アラームも無い**） | Amplify コンソール | **Amplify 5xx アラーム**（P1）、日次行に `amplifyRequests / amplify5xx` |
| WAF（IP 許可リスト） | 403 | `AWS/WAFV2 BlockedRequests` | — | **アクセスログ `wafResponseCode`** |
| API Gateway 認可 | 401 / 403 | `4XXError`（内訳なし） | 実行ログ | **アクセスログ `error.responseType`** |
| Lambda rag / chat | 500 | `5XXError`、メトリクスフィルタのエラー行 | 保存クエリ `rag-error-lines` | **構造化エラー行（`apiRequestId`・段階・エラーコード）** |
| Knowledge Base / OpenSearch | retrieve 失敗・遅延 | `print("Knowledge Base query error")` のみ | 同上 | トレースの `latencyMs.retrieve`（別設計） |
| Bedrock | スロットル・遅延・5xx | `AWS/Bedrock InvocationThrottles / InvocationServerErrors / InvocationLatency`（G2、未参照） | CloudWatch メトリクス（ModelId） | 日次行に `bedrockThrottles / bedrockServerErrors`。切り分け時は直接見る |
| DynamoDB | スロットル | `ReadThrottleEvents / WriteThrottleEvents` アラーム | DynamoDB コンソール | — |
| Cognito | ログイン失敗・メール上限 | CloudTrail → EventBridge の P1 通知（本文に API 名・エラーコード） | SNS 本文 | — |

### 4.3 追加する記録

| # | 何を | どこに | 何が分かるようになるか | 作業量 | 優先 |
|---|---|---|---|---|---|
| I1 | **API Gateway アクセスログ**（JSON 1 行/リクエスト）を 4 ステージ（rag / chat / auth / app）に設定。項目: リクエスト ID、時刻、メソッド、パス、ステータス、応答時間、統合時間、送信元 IP、UA、`error.responseType`、`error.message`、`wafResponseCode`、`authorizer.claims.sub`（△ 変数名は公式の `$context` 一覧で確認） | 既存の `/aws/apigateway/*-api-dev`（保持 90 日） | 4xx の内訳（WAF / 認可 / 失効 / スロットル）、利用者体感レイテンシ、利用者別の利用、**引用文書を開いた回数**（`GET /rag/document` の件数） | 小（`AccessLogSetting` を Stage に足すだけ。既存ログ群へ流す） | **P0** |
| I2 | **rag / chat の 1 リクエスト 1 行の構造化ログ**（トレース設計 §4-5 の行に `apiRequestId` = `event.requestContext.requestId` を追加）と、**500 経路の構造化エラー行**（`apiRequestId`, `stage: retrieve / generate / save`, `errorCode`, `messageId`）。あわせて 500 応答本文から AWS のエラーメッセージを外す（現在は `ClientError` の本文をそのまま返している） | Lambda ログ | アクセスログ ↔ Lambda ログ ↔ chatlogs を ID で結べる。アラーム本文だけで「どの段階で何のエラーか」が読める | 小 | **P0** |
| I3 | **引用文書を開いた回数を回答の行に加算**。フロントは `/doc?uri=…` に `&s=<sessionId>&m=<messageId>` を足し、`GET /rag/document?uri=&s=&m=` が所有者を確認したうえで該当の assistant 行に `documentOpens` を加算し `lastOpenedAt` を記録する。あわせて `document_open` の構造化行（本文なし）を出す | chatlogs（`documentOpens` 属性）+ Lambda ログ | ファネル F4「資料を開いた」。日次集計は chatlogs の走査で数えるので EMF は要らない（実装時に EMF 案から変更。後付けのクリックも D-1〜D-3 の再集計で回答日の行に乗る） | 小（Lambda に 1 関数、フロントのリンク生成 1 か所、aggregator に集計 1 項目） | **P0** |
| I4 | **アラーム遷移の保存**（`alarmTransitions: [{alarm, state, at}]`）と **P1 遷移回数**（metrics-v2 §5 の `incidents` を拡張） | 日次行 | 「出来事」の一覧 | 小（metrics-v2 PR-2 に含める） | P1 |
| I5 | **AlarmDescription にランブック節と保存クエリ名を入れる**（Cognito ルールは既にやっている。28 本に揃える） | monitoring-template | 通知メールだけで「最初に見る場所」に着ける | 小 | P1 |
| I6 | **アクセスログ用の保存クエリ**を監視スタックに追加: `api-4xx-breakdown`（`stats count() by error.responseType, status, resourcePath`）、`request-by-id`（ID で 3 ロググループ横断）、`slow-requests`（`responseLatency` 降順） | monitoring-template | 切り分けの手順がクエリ名で固定される | 小 | P1 |
| I7 | **デプロイ・設定変更のマーカー**（CloudTrail `LookupEvents` で `UpdateStack` / `UpdateFunctionCode*` / `UpdateFunctionConfiguration*` を EleKnowledge のリソース名で絞る） | 日次行 `changes` | 「出来事」に変更が並び、障害と変更の前後関係が画面で分かる | 中（IAM `cloudtrail:LookupEvents`、名前での絞り込み、2 TPS 制限） | P2 |

I1 の送信元 IP と `sub` は AGENTS.md「ログと秘匿」の禁止対象（トークン・個人情報・引用全文）には当たらないと判断したが、確認事項として §8 Q4 に残す。

### 4.4 ダッシュボードからの導線

1. アラームのメールが来る → 件名でアラーム名と P1/P2 が分かる（現状どおり）
2. `/admin/dashboard` を開く → 「いま」に現在の ALARM、「出来事」に遷移時刻が並ぶ
3. 行の「→ ログ」で Logs Insights を該当ロググループ・前後 15 分で開く。4xx なら `api-4xx-breakdown`、5xx なら `rag-error-lines`、遅延なら `slow-requests`
4. `apiRequestId` を `request-by-id` に貼れば、アクセスログ・Lambda ログ・（トレース実装後は）`messageId` 経由で chatlogs まで辿れる

**○ 任意の拡張「行内の内訳」**: 出来事の行を開くと、read API がその時間帯（前後 15 分）について Logs Insights の `StartQuery` を 1 本流し（5〜10 秒）、結果の**集計だけ**を行内に出す。4xx なら `error.responseType × status × path`、5xx なら `stage × errorCode`、いずれも影響した `sub` の数と `apiRequestId` の上位 5 件。ログ本文は出さず、本文が要るときは同じ条件で Logs Insights を開く。アプリ内ログビューアを作らずに「どこで何が」の 8 割を画面で済ませられる。費用は走査量課金（△ 1 GB あたり数セント）で、この規模では無視できる。I1・I2 が入った後に足す。

ランブック §2「最初に見る場所」は、I1〜I6 が入った時点で上記に書き換える。

### 4.5 やらないこと

| やらない | 理由 |
|---|---|
| X-Ray（G10） | 「retrieve が遅いか generate が遅いか」はトレースの `latencyMs` で足りる。サンプリングと費用の管理が増える |
| WAF ログ（G7） | アクセスログの `wafResponseCode` で「WAF がブロックした」までは分かる。どのルールかまで必要になった時点で入れる |
| Cognito ログ配信（G8） | メール失敗は CloudTrail 経由の通知が既にある。プールが ESSENTIALS で認証イベントは取れない |
| アプリ内ログビューア | Logs Insights で足りる。2 人の工数は記録を足す側に使う |
| リアルタイム集計基盤 | 制約どおり。「いま」は CloudWatch を表示時に読むことで賄う |

---

## 5. コスト（役割 4）`/admin/cost`

### 5.1 判断: Cost Explorer の実額を採用し、トークン推定は役割を限定して残す

| | Cost Explorer「Claude Sonnet 5」行 | トークン × SSM 単価（先行決定） |
|---|---|---|
| 正確さ | 請求の真値。キャッシュ・プロファイル差など単価の細部を自動で含む | 単価表の保守が要る。実額とのずれが出る |
| 帰属 | 「Sonnet 5 の唯一の利用者」の間だけ EleKnowledge 分。**他システムが Sonnet 5 を使い始めた瞬間、または EleKnowledge が代替モデル（ランブック §7.3）へ切り替えた瞬間に崩れる** | トレース由来なら常に EleKnowledge 分（CloudWatch 由来ならモデル単位で同じ弱点） |
| 粒度 | 日（UTC）・使用タイプ（入力／出力） | 1 回答ごと |
| 遅延 | D-1 は暫定、D-2 で確定扱い（△ Cost Explorer の反映は通常 24 時間以内） | 即日 |
| 費用 | 0.01 USD / 呼び出し | なし |

**採用**: 月の実額は Cost Explorer。推定は (a) 1 質問あたりの単価、(b) 利用が伸びたときの見込み、(c) 実額との整合チェック（前提崩れの検知）、の 3 つに限定する。どちらか一方にしなかったのは、実額は帰属が前提依存で、推定は単価が前提依存だから。両方を並べて差を見ることで、どちらの前提が崩れたかを画面で検知できる。

トークンの取り方は 2 段階にする。**今すぐ**は `AWS/Bedrock` の `InputTokenCount / OutputTokenCount`（ModelId 別、G2）で日次行に入れる。コード変更なしで動く。**トレース実装後**は `retrievalTrace.generation` の合計に切り替え（`estimateSource: "trace"`）、CloudWatch 側は整合チェック用に残す。トレース由来だけがアカウント共有の影響を受けない。

### 5.2 数字の 4 分類（混ぜない）

画面のすべての金額に次のバッジを付ける。分類はデータの出所で機械的に決まり、読み手の解釈に任せない。

| バッジ | 意味 | 該当 | 今後の移動 |
|---|---|---|---|
| **実額・確定** | 請求額で、EleKnowledge 分と言い切れる | Cost Explorer「Claude Sonnet 5」行（唯一利用者フラグが真のとき）、**Amplify**（Q2: アカウント内で EleKnowledge 専用と確認済み） | 他システムの Sonnet 5 利用が検知されたら Bedrock 行を「実額・帰属未確認」へ自動降格 |
| **実額・帰属未確認** | 請求額だが、アカウント内の他システム分を含む可能性がある | CloudWatch、Lambda / DynamoDB / API Gateway / S3 のアカウント合計 | コスト配分タグ有効化後、`Project=EleKnowledge` フィルタで「実額・確定」へ |
| **共有・按分不能** | 請求額だが、原理的に切り出せない | OpenSearch Serverless（OCU 課金）、KB の検索時埋め込みモデルの行（少額。上位 5 行に出ていない） | 移動しない。EleKnowledge の増分コストは 0 とみなす（OCU が増えない限り） |
| **推定** | 計測値 × 単価、按分、または外挿 | 昨日の Bedrock 費、1 質問あたり、見込み、**WAF の EleKnowledge 分**（Q2: 他システムも WAF を使うが Web ACL は別。Cost Explorer の使用タイプは Web ACL 単位に分かれないため、タグ有効化までは構成 × 料金表で置く）、**OpenSearch のリクエスト按分**（§5.9） | WAF はタグ有効化後に「実額・確定」へ。他は推定のまま |

「共有・按分不能」は月額のいちばん大きい箱（9 日で 179 USD ≒ 月 600 USD 規模）になる。隠さずに出すが、**EleKnowledge の費用対効果の分母には入れない**。理由: EleKnowledge があってもなくても発生している固定費で、増分がゼロだから。増分がゼロでなくなる条件（OCU が増える）は §8 Q3 に確認事項として残す。

### 5.3 画面構成

```
┌ 今月（UTC 日基準・D-2 まで確定）─────────────────────────────────────┐
│ [実額・確定]           [実額・帰属未確認]     [共有・按分不能]        │
│ Bedrock Sonnet 5       WAF / Amplify /       OpenSearch Serverless   │
│ 3.2 USD                CloudWatch ほか        61 USD                 │
│ 入力 1.9 / 出力 1.3    5.8 USD（タグ待ち）    増分 0 とみなす          │
│ 予算 100 USD の 3 %                                                   │
├ 前提チェック ────────────────────────────────────────────────────────┤
│ ● Sonnet 5 の唯一の利用者: 成立（呼び出し 41 = 回答 41）              │
│ ● 実額 vs 推定: 3.2 / 3.0 USD（+7 %）                                  │
├ 日次推移（30 日）───────────────────────────────────────────────────┤
│ Sonnet 5 実額（UTC 日） ▂▁▃▂▂▅▂   │  質問数（JST 日） ▂▃▁▅▂▃▂         │
├ 1 質問あたり（推定）─────────────────────────────────────────────────┤
│ 実額 ÷ 質問（今月）: 0.014 USD │ トレース中央値: —（実装待ち） p90: — │
├ 見込み（推定、いまの単価で）───────────────────────────────────────┤
│ 100 質問/日 → 42 USD/月   300 → 126 USD/月   1,000 → 420 USD/月       │
│ 効くのは Bedrock だけ。Lambda / DynamoDB / API GW は 1,000/日でも 1 USD 未満│
└──────────────────────────────────────────────────────────────────────┘
```

（金額は表示例。実装時は Cost Explorer の値がそのまま入る。）

| ID | 表示名 | 定義 | バッジ |
|---|---|---|---|
| C1 | 今月 Bedrock 実額 | Cost Explorer、Service = Sonnet 5 行、当月 1 日〜D-2 の合計。使用タイプで入力／出力（あればキャッシュ）に分ける | 実額・確定 |
| C1b | 今月 Amplify 実額 | Cost Explorer、Service = AWS Amplify、当月合計（Q2: 専用と確認済み） | 実額・確定 |
| C2 | 今月 帰属未確認 | CloudWatch、Lambda、DynamoDB、API Gateway、S3 のアカウント合計。サービス別の内訳を表で | 実額・帰属未確認 |
| C10 | WAF の EleKnowledge 分 | **実装では当面「実額・帰属未確認」の箱に置く**（構成 × 料金表の推定は入れていない。料金表の値を持ち込むより、タグ有効化で実額に切り替える方が確実）。タグ有効化後は Cost Explorer のタグフィルタで「実額・確定」へ | 実額・帰属未確認 → 実額・確定 |
| C11 | OpenSearch リクエスト按分（**未実装**） | §5.9 | 推定 |
| C12 | 他システム | Cost Explorer の行のうち、他モデルの Bedrock 行など EleKnowledge と無関係なもの。参考として別枠に出す（4 分類に収まらないため実装で追加） | 他システム |
| C3 | 今月 共有 | OpenSearch Serverless の合計 | 共有・按分不能 |
| C4 | 予算消化 | C1 ÷ SSM の予算額（Budgets と同じ値を置く） | 実額・確定 |
| C5 | 唯一利用者チェック | 日ごとに `AWS/Bedrock Invocations`（ModelId）と chatlogs の `pages` 件数（= `invoke_model` 呼び出し数。1 回答 1 呼び出し）を比較。`Invocations > pages × 1.05 + 2` の日があれば「不成立」 | — |
| C6 | 実額 vs 推定 | 同じ UTC 日範囲で C1 と推定合計を比較。差が ±20 % 超で注意 | — |
| C7 | 日次推移 | Sonnet 5 実額（UTC 日、30 日）と質問数（JST 日、30 日）を **別チャート** で並べる。日付基準が違うことを副題に明記 | 実額・確定 / — |
| C8 | 1 質問あたり | 実額ベース: C1 ÷ 当月 `queries`。推定ベース: トレースの 1 回答コストの中央値と p90（実装まで `—`）。生成が走るのは `pages` 応答だけなので「1 回答あたり」も併記 | 推定 |
| C9 | 見込み | 100 / 300 / 1,000 質問/日 × C8（実額ベース）× 30 日 | 推定 |

### 5.4 データ取得と保存

- **保存先**: metrics-dev に `scope=cost`、`metricDate=YYYY-MM-DD`（**UTC 日**。Cost Explorer の日付をそのまま使う）。内容: `byService: {service: usd}`、`sonnet5: {input, output, cacheRead, cacheWrite, total}`、`settled: bool`、`fetchedAt`。既存 GSI `scope-metricDate-index` で月範囲を Query できる
- **取得**: 日次バッチ（02:00 JST）で Cost Explorer を **1 日 2 回**呼ぶ。(1) 直近 3 日・日次・`GroupBy=SERVICE`、(2) 直近 3 日・日次・Sonnet 5 行に絞って `GroupBy=USAGE_TYPE`。直近 3 日を毎日上書きするのは、Cost Explorer の当日・前日分が後から更新されるため。`settled` は D-2 以前で真
- **費用**: 2 回 × 0.01 USD × 30 日 = 0.6 USD/月。タグ有効化後は `Tag=Project` フィルタの 1 回を足して 0.9 USD/月
- **IAM**: aggregator に `ce:GetCostAndUsage`。SCP で Lambda ロールから拒否されないかはデプロイ時に 1 回試す（§8 Q5）
- **UTC と JST のずれ**: コストは UTC 日、利用は JST 日。月合計での比較（C8）はずれが 9 時間分で無視できる。日単位の突き合わせ（C5・C6）は UTC 日で揃えるため、aggregator は Bedrock の CloudWatch メトリクスを UTC 日でも取る（`GetMetricStatistics` の期間指定を変えるだけ）

### 5.5 「唯一の利用者」前提の監視

Cost Explorer の実額が EleKnowledge 分である保証は、他システムが Sonnet 5 を使っていないことに依存する。これは人の申し送りに頼らず、画面で自動検知する。

| チェック | 方法 | 崩れたときの表示 |
|---|---|---|
| 呼び出し数 = 回答数 | C5。Sonnet 5 の `Invocations` と `pages` 件数を日ごとに比較 | C1 のバッジを「実額・帰属未確認」に降格し、理由を表示 |
| 実額 ≈ 推定 | C6。差 ±20 % 超 | 注意色。単価改定か、キャッシュ課金か、他利用者かを人が確認 |
| モデル ID の変化 | 日次行に `modelId`（環境変数 `BEDROCK_MODEL_ID`）を記録し、前日と違えば「出来事」に出す | 代替モデルへ切り替えた月は、その行を Cost Explorer から切り出せない旨を C1 に表示 |

ランブック §4 の手作業「Bedrock 呼び出し数がチャット件数と合っている」は、C5 で自動化される。

### 5.6 1 質問あたりと見込み

実測に基づく単価が出るまで、トレース設計 §7 の SSM 単価（入力 2.0 / 出力 10.0 USD per MTok。**この値の妥当性は C6 の整合で検証する**）と、同設計 §2 の 1 回答例（入力 3,748 / 出力 578 トークン）から仮置きすると、1 回答 ≒ 0.013 USD。

| 質問/日 | 月の Bedrock（推定） | 備考 |
|---|---|---|
| 10（いま） | 4 USD | |
| 100 | 40 USD | |
| 300 | 120 USD | 予算 100 USD を超える水準 |
| 1,000（設計上限） | 400 USD | Lambda / DynamoDB / API GW はこの規模でも 1 USD 未満 |

利用が伸びたときに効くのは Bedrock だけ。次に効くのは CloudWatch Logs（アクセスログ・トレースの構造化行）だが、1,000 件/日でも取り込み量は月 1 GB に届かない。OpenSearch Serverless は OCU が増えない限り増分ゼロ。

### 5.7 予算アラート

| 項目 | 内容 |
|---|---|
| 入れるか | **入れる**。1 本だけ |
| 対象 | AWS Budgets、コスト予算、月次、フィルタ `Service = Claude Sonnet 5 (Amazon Bedrock Edition)`（◎ Budgets に Service 次元フィルタはある。△ Bedrock のモデル行が Budgets 側でも同じ名前で選べるかは作成時に確認。Cost Explorer と同じ次元なので選べる見込み） |
| 額 | **100 USD/月**。根拠: 1 質問 0.013 USD なら約 7,700 質問/月（≒ 250/日）。設計上限の 1/4 で、初月にここを超えるのは「普及が想定より速い」か「暴走」のどちらかで、どちらも知りたい。月初に「前月実績の 2 倍と 100 USD の大きい方」へ見直す |
| 通知 | 実績 50 %、実績 100 %、予測 100 % の 3 段。送信先は既存 SNS `eleknowledge-alerts-dev`（◎ Budgets は SNS トピックへ通知できる。トピックポリシーに `budgets.amazonaws.com` の `sns:Publish` 許可を足す）。件名の慣習に合わせて予算名を `EleKnowledge-dev-P2-budget-bedrock-sonnet5` にする |
| 置かないもの | アカウント全体の予算（他システムの Sonnet 4.6 と OpenSearch が支配的で、この 2 人が動ける情報にならない）。タグ別予算（タグ有効化まで作れない。有効化後に `Project=EleKnowledge` で 2 本目を足す） |
| 任意 | AWS Cost Anomaly Detection（サービス単位・無料）。この連結アカウントで作成権限があるかは未確認（△）。あれば Sonnet 5 行に 1 つ |

### 5.8 コスト配分タグが有効になったら

- aggregator に Cost Explorer の 3 回目（`Filter: Tag Project=EleKnowledge`, `GroupBy=SERVICE`）を足す
- C2 の各サービスがタグ付き分だけ「実額・確定」へ移る。**有効化前には遡及しない**ので、有効化日を SSM に置いて画面に「YYYY-MM-DD 以降」と表示する
- 依頼は管理アカウント側の作業。いつ有効になるか未定のため、本設計はタグ無しで完結するように組んである

### 5.9 OpenSearch Serverless の OCU と EleKnowledge の使用割合（Q3）

> 実装状況（2026-09-11）: **未実装**。`AWS/AOSS` のディメンション（OCU はアカウント単位か、コレクション別の検索リクエスト数の有無）を実環境で確かめてから、aggregator に `aoss` と `retrieveCalls` を足す後続 PR で入れる。

請求は按分できないが、**OCU が増えたか**と **EleKnowledge がどれだけ検索しているか**は取れる。前者は「増分ゼロ」の前提を毎月確かめる材料、後者は按分の推定に使う。

| 取るもの | 出典 | 粒度 | 備考 |
|---|---|---|---|
| 検索 OCU・インデックス OCU（平均・最大） | `AWS/AOSS` `SearchOCU` / `IndexingOCU` | 日次 | △ OCU の系列はアカウント単位（コレクション横断で共有されるため）。ディメンションは実装時に `list-metrics --namespace AWS/AOSS` で確認 |
| コレクションの検索リクエスト数 | `AWS/AOSS` `SearchRequestCount`（CollectionId 別） | 日次 | 棚卸しに無いため **要実測**（1 分で確認できる）。同一アカウント内なので読める見込み |
| EleKnowledge の retrieve 回数 | I2 の構造化行（`retrieveCalls`） | 日次 | 由来を区別できるのはこれだけ。AOSS 側に呼び出し元のディメンションは無い |

表示（コスト画面）:

- 「前提チェック」に **検索 OCU の平均・最大（30 日）** を出し、増えていなければ「EleKnowledge の増分は 0」を維持する。増えた月は所有側に確認する（Q6 の打ち合わせと同じ場）
- 「推定」の箱に **リクエスト按分** = OpenSearch 実額 × （EleKnowledge retrieve 回数 ÷ コレクションの `SearchRequestCount`）を出す。使用割合であって請求の真値ではないので、必ず「推定」バッジ付き。費用対効果の分母には入れない
- 日次推移に検索 OCU（最大）の折れ線を 1 本置く（増減が一目で分かればよいので 1 系列）

インデックス OCU は KB の同期（EleKnowledge の 3 データソース）でも動くが、同期のたびに按分するほどの金額差は出ないため、共有のまま扱う。

---

## 6. データと API の変更点（metrics-v2 との差分）

### 6.1 日次行 `overall` に足す項目

metrics-v2 §5 の項目に加えて:

| 項目 | 定義 | 出典 |
|---|---|---|
| `alarmTransitions` | `[{alarm, state: "ALARM" \| "OK", at}]`（P1 / P2 とも） | `DescribeAlarmHistory` |
| `apiLatency` | `{rag: {p50, p90, max, count}}`（ms）。metrics-v2 の `latency` を置き換え | API GW `Latency`, `Count` |
| `http5xxByApi` | `{rag, chat, auth, app, amplify}` | API GW `5XXError`, Amplify `5xxErrors` |
| `signIns` | `SignInSuccesses` 合計 | `AWS/Cognito` |
| `amplifyRequests` | `Requests` 合計 | `AWS/AmplifyHosting` |
| `documentOpens`, `messagesWithOpen` | assistant 行の `documentOpens` の合計と、1 回以上開かれた回答の数 | chatlogs（§4.3 I3） |
| `bedrock` | `{invocations, inputTokens, outputTokens, throttles, serverErrors, modelId}`（JST 日と UTC 日の 2 組） | `AWS/Bedrock`（ModelId） |
| `estimatedBedrockCostUsd`, `estimateSource` | トークン × SSM 単価。`"cloudwatch"` または `"trace"` | 算出 |
| `soleUserOk` | C5 の判定 | 算出 |
| `changes`（P2） | `[{at, eventName, resource}]` | CloudTrail |
| `retrieveCalls`（**未実装**） | KB `Retrieve` の呼び出し回数（I2 の構造化行から。略語展開で 2 回のときは 2） | Lambda ログ（メトリクスフィルタ）。§5.9 と同時に |
| `aoss`（**未実装**） | `{searchOcuAvg, searchOcuMax, indexingOcuMax, searchRequests}`（§5.9） | `AWS/AOSS`（要実測） |
| `reformulated` | 同一セッションで、`pages` 応答の 10 分以内に次の質問があり、その応答に 👍 も資料クリックも無い件数。印（`reformulatedAt`）は rag Lambda が次の質問を受けた瞬間に直前の回答へ付け、集計時に 👍・資料クリックの有無で確定する | chatlogs |
| `triageOpen` | 到達できなかった回答のうち `triage` が無いか `open` のもの（§9.4） | chatlogs |

`errorRate` は保存するが表示しない。`incidents` は `alarmTransitions` から P1 の ALARM 遷移を数えた値として残す。

### 6.2 新 scope `cost`

§5.4 のとおり。`metricDate` は UTC 日。

### 6.3 read API

画面の並びと同じ形を返す **`GET /admin/metrics/dashboard`**（`?trend=14|30|90`）と **`GET /admin/metrics/cost`**（`?month=YYYY-MM`）を新設する。旧 `GET /admin/metrics` は UI 切替までの間だけ残し、UI PR のマージ後に削除する（実装では新旧を同居させ、デプロイ順に依存しないようにした）。

```ts
// frontend/src/lib/metrics.ts（差し替えの骨子）
export type HealthStatus = 'good' | 'warning' | 'serious' | 'critical';
type Count = number | null;                       // null = 未集計（0 と区別する）

export interface DashboardResponse {
  generatedAt: string;                            // ISO、JST 表示はフロントで
  now: {
    alarms: { name: string; severity: 'P1' | 'P2'; since: string }[];
    status: HealthStatus;                         // P1→critical, P2→warning, なし→good
    last60min: { requests: Count; http5xx: Count; ragP90Ms: Count };
    freshness: { yesterdayAggregatedAt: string | null; todayPartialAt: string | null; status: HealthStatus };
  };
  yesterday: {
    date: string;                                 // JST
    incidents: { p1Transitions: Count; http5xx: Count; byApi: Record<string, Count>; status: HealthStatus };
    latency: { p90Ms: Count; p50Ms: Count; maxMs: Count; count: Count; status: HealthStatus };
    unreached: { total: Count; notFound: Count; bad: Count };        // 色なし
    usage: { queries: Count; uniqueUsers: Count; newUsers: Count; queriesSameWeekdayLastWeek: Count };
    bedrockCost: { estimatedUsd: number | null; estimateSource: 'cloudwatch' | 'trace' | null;
                   monthActualUsd: number | null; actualThrough: string | null; status: HealthStatus };
  };
  todaySoFar: { asOf: string; queries: Count; unreached: Count; http5xx: Count } | null;
  funnel: { yesterday: FunnelRow; last7d: FunnelRow };
  trend: { days: number; queriesByDay: { date: string; total: number; unreached: number }[];
           latencyByDay: { date: string; p90Ms: number | null; maxMs: number | null }[] };
  events: { at: string; kind: 'alarm' | 'deploy'; title: string; durationSec?: number;
            logGroup?: string; from?: string; to?: string; queryName?: string }[];
  reference: { topDocuments: { name: string; count: number }[]; lastEval: { date: string; hit: number; n: number } | null };
}
interface FunnelRow { signIns: Count; queries: Count; pages: Count; opened: Count | 'unmeasured'; good: Count }

export interface CostResponse {
  month: string; settledThrough: string;          // UTC
  confirmed: { bedrockSonnet5: { total: number; input: number; output: number; cache: number }; budgetUsd: number };
  unattributed: { total: number; byService: Record<string, number>; note: 'tag_pending' };
  shared: { total: number; byService: Record<string, number> };
  checks: { soleUser: { ok: boolean; detail: string }; actualVsEstimate: { actual: number; estimate: number; diffPct: number; status: HealthStatus } };
  daily: { date: string; sonnet5Usd: number; settled: boolean }[];    // UTC 日
  queriesDaily: { date: string; queries: number }[];                  // JST 日（別チャート）
  perQuery: { actualUsd: number | null; traceMedianUsd: number | null; traceP90Usd: number | null; perAnswerUsd: number | null };
  projection: { queriesPerDay: number; monthlyUsd: number }[];
}
```

`now` は表示のたびに `DescribeAlarms` 1 回 + `GetMetricData` 1 回 + `DescribeAlarmHistory`（直近 24 時間）1 回。2 人が 1 日数回開く前提なので、キャッシュは要らない。

§9 / §10 で追加・変更する API:

| API | 変更 |
|---|---|
| `GET /chat/admin/failures` | `since` / `until`（JST 日付）、`triage=open\|in_progress\|done\|all`、`kind` に `reformulated` を追加。各項目に `traceSummary`・`opened`・`reformulated`・`triage`・`hints` |
| `PUT /chat/admin/messages/{sessionId}/{messageId}/triage` | 新設（admin）。`{status, cause?, note?, ref?}` |
| `GET /chat/admin/messages/{sessionId}/{messageId}/trace` | トレース設計 §5 のまま。一覧のドロワーで使う |
| `GET /admin/metrics` | `now.activeNotices: [{id, title, severity, since, showInChat}]` を追加 |
| `POST` / `PUT /admin/announcements` | `showInChat` を受ける。`endAt` は全種別で既に保存されている（UI 側の変更のみ） |
| `GET /announcements` | 変更なし（`showInChat` が項目に増えるだけ） |

### 6.4 IAM・スケジュール・費用

| 対象 | 追加 |
|---|---|
| aggregator ロール | `cloudwatch:DescribeAlarmHistory`, `ce:GetCostAndUsage`, `ssm:GetParameter`（単価・予算額）、（P2）`cloudtrail:LookupEvents` |
| read ロール | `cloudwatch:DescribeAlarms`, `cloudwatch:DescribeAlarmHistory`, `cloudwatch:GetMetricData` |
| スケジュール | metrics-v2 §8 のまま（日次 + 毎時）。日次は **D-1〜D-3 を再集計**する（後付けの 👍👎 を回答日の行へ。§8.2）。Cost Explorer は日次側だけ |
| 月額 | Cost Explorer 0.6 USD、CloudWatch API はほぼ 0、メトリクス取り込み（EMF 1 本）ほぼ 0。合計 1 USD 未満 |

### 6.5 チャートライブラリは追加しない

必要な形は、棒（あり）、積み上げ棒（`TimeBars` に 2 系列を足す）、ms 軸の折れ線と基準線（`RateLine` の軸を %固定から数値へ一般化）、横棒（`DocRanking` の流用）、ファネル（div）、状態帯（div）。いずれも 100 行未満の差分で、既存の「表で見る」フォールバックも引き継げる。Recharts 級を足すと 100 KB 超のバンドルと二軸誘惑が増える一方、得られるのはツールチップの見た目だけ。ズームやブラシが要る画面は無い。

---

## 7. 実装順（metrics-v2 §11 を置き換える）

| 順 | PR | 内容 | デプロイ | 依存 |
|---|---|---|---|---|
| 1 | `feat(infra)` 配線 | I1 アクセスログ（4 ステージ）、Amplify 5xx アラーム、I5 AlarmDescription、I6 保存クエリ、Budgets + SNS トピックポリシー | phase1 / phase2 / monitoring | なし。**単独で役割 3 の大半が成立する** |
| 2 | `fix(metrics)` | metrics-v2 PR-1 のまま（JST 境界・毎時・`partial`）。UI 変更なし | announcements-monitoring | なし |
| 3 | `feat(rag)` 記録 | I2 構造化ログ + 500 本文の整理、I3 `DocumentOpen` EMF、フロントの `&m=` | phase2 + Amplify | なし（トレース PR と並行可） |
| 4 | `feat(metrics)` 集計 | §6.1 の項目、`scope=cost`、C5 / C6 の判定 | announcements-monitoring | 2 |
| 5 | `feat(metrics)` read | §6.3 の 2 エンドポイント | announcements-monitoring | 4 |
| 6 | `feat(dashboard)` UI | `/admin/dashboard` v2、`/admin/cost`、サブナビ | Amplify | 5 |
| 6b | `feat(announcements)` | §10.4（`showInChat`、表示終了 UI、テンプレート、チャット画面バナー、ダッシュボードの告知導線） | announcements-monitoring + Amplify | なし。**単独で入れられ、今週から障害告知を型にできる** |
| 6c | `feat(chat)` failures v2 API | §9.5（期間・振り分け・ヒント・トレース要約） | phase2 | 3（構造化ログ）。トレース要約はトレース PR 後 |
| 6d | `feat(admin)` failures v2 UI | §9.2 | Amplify | 6c |
| 7 | トレース PR 群 | 別設計のまま。完了後に `estimateSource` を `trace` へ | phase2 ほか | 独立 |
| 8 | `docs` | `docs/api/`（metrics API 正本）、`docs/data-model.md`（production・事前確認要）、ランブック §2 / §3 / §4 / §9 の書き換え | — | 6 |
| 後 | P2 | I7 デプロイマーカー、Athena フラット化 VIEW、タグ有効化後の Cost Explorer 3 回目 | — | — |

順 1 と 3 は運用初週に入れる価値がある。順 1 は IaC だけで、順 3 は Lambda の追記だけで、どちらも既存表示を壊さない。

### 7.1 実装状況（2026-09-11）

§7 の順 1〜6d を 10 本のブランチで実装した。トレース（順 7）と P2 は未着手。

| 順 | ブランチ | base | 内容 | テスト |
|---|---|---|---|---|
| 1a | `feat/apigw-access-logs` | develop | I1 アクセスログ（auth / rag / chat / app） | cfn-lint |
| 1b | `feat/monitoring-runbook-hints-budget` | `feature/monitoring-stack`（PR #92） | I5 AlarmDescription、Amplify 5xx、I6 保存クエリ、Budgets | cfn-lint |
| 2 | `feat/metrics-v2-jst-hourly` | develop | JST 境界・毎時 partial・時間帯別の行・D-1〜D-3 再集計・TTL 書き込み削除 | pytest |
| 3 | `feat/rag-request-telemetry` | develop | I2 構造化ログ・500 経路の一般化、I3 `documentOpens`、言い換えの印 | pytest |
| 4 | `feat/metrics-v2-aggregator` | 2 の上 | §6.1（CloudWatch・アラーム履歴・単価推定・`triageOpen`）と `scope=cost` | pytest |
| 5 | `feat/metrics-v2-read` | 4 の上 | `/admin/metrics/dashboard`・`/admin/metrics/cost` | pytest |
| 6 | `feat/dashboard-v2-ui` | 5 の上 | ダッシュボード v2・コスト画面・サブナビ | tsc・node:test・next build |
| 6b | `feat/announcements-v2` | `fix/announcements-inspection`（PR #95） | §10（showInChat・表示終了・テンプレート・チャット画面の帯・導線） | pytest・tsc・node:test |
| 6c | `feat/failures-v2-api` | develop | §9.5 API と PUT triage | pytest・cfn-lint |
| 6d | `feat/failures-v2-ui` | 6c の上 | §9.2 画面 | tsc・node:test |

デプロイ順の依存: 6 は 5 と同じ announcements-monitoring スタックのデプロイ後に Amplify へ。6d は 6c の phase2 デプロイ後。3 は phase2。1b は監視スタック。

ドキュメント側の残り（production のため事前確認が要る）: `docs/data-model.md` に chatlogs の `documentOpens` / `lastOpenedAt` / `reformulatedAt` / `triage`、announcements の `showInChat`、metrics の `scope=hourly` / `scope=cost`。`docs/api/chat.md` に failures のパラメータと PUT triage。`docs/api/` に metrics API（新設）。ランブック §2 / §3 / §4 / §9 の書き換え。`AGENTS.md` の SLO 改定（Q1）。

---

## 8. 決定事項（2026-09-10 itai 回答）と設計への反映

| # | 質問 | 回答 | 設計への反映 |
|---|---|---|---|
| Q1 | SLO「p95 < 3 s」と Sonnet 5 の実測が両立しない | **p90 20 s を妥協ライン（SLO）とする** | §2.8 の閾値を 20 / 25 / 29 s に改めた。`AGENTS.md` の SLO は別 PR（AI ルール同期の手順）で「RAG 応答 p90 < 20 s」に改定する |
| Q2 | WAF・Amplify は EleKnowledge 専用か | **Amplify は専用。WAF は他システムも使うが Web ACL は別（共用ではない）** | Amplify は「実額・確定」へ。WAF は Cost Explorer の使用タイプが Web ACL 単位に分かれないため、タグ有効化までは「推定（構成 × 料金表）」、有効化後に「実額・確定」（§5.2 / §5.3 C10） |
| Q3 | OpenSearch の OCU を追えるか。EleKnowledge 由来か区別できるか | **取れるなら取りたい。由来の区別ができれば最高** | §5.9 を追加。`AWS/AOSS` の OCU と検索リクエスト数を日次行に取り、EleKnowledge 自身の retrieve 回数（I2）との比で「リクエスト按分」を推定として出す。由来の区別は EleKnowledge 側の回数でしかできない |
| Q4 | アクセスログに IP と `sub` を残してよいか | **残してよい** | I1 のまま |
| Q5 | `ce:GetCostAndUsage` を Lambda から呼べるかの確認方法 | （質問） | §8.1 |
| Q6 | 他システムの Sonnet 5 利用の事前連絡 | **打ち合わせで聞く** | C5 の自動検知は前提どおり残す。連絡が取れれば降格時の説明に使う |
| Q7 | metrics-dev の TTL | **無効化する（またはアーカイブ）** | **TTL 無効化で確定**。**訂正（2026-09-11）**: `origin/develop` のテンプレートは PR #93 で既に `Enabled: false` になっていた。有効に見えたのは設計時の作業ブランチが develop より古かったため。実環境で有効のままなのは未デプロイだから。実装 PR-1 で `METRIC_TTL_DAYS` と `ttl` 属性の書き込みを削除した。テーブルは KB 規模で PITR 有効のため、別途アーカイブは要らない（別立て A5） |
| Q8 | 👍👎 の正本をどちらにするか | （解説の依頼） | §8.2。**chatlogs を正本**とし、日次バッチは D-1〜D-3 を再集計する（§6.4） |

### 8.1 Q5: `ce:GetCostAndUsage` が Lambda ロールで通るかの確認手順

SCP は原則アクション単位で**アカウント内の全プリンシパルに同じように**掛かる。CLI プロファイル（IAM ユーザーか SSO ロール）で `GetCostAndUsage` が通った以上、Lambda ロールだけ拒否されるとすれば `aws:PrincipalArn` 等の条件付き SCP に限られる。確認は 2 段。

1. **デプロイ前（無料・IAM 側だけ）**: `aws iam simulate-principal-policy --policy-source-arn <aggregator ロールの ARN> --action-names ce:GetCostAndUsage` で `allowed` を確認する。△ シミュレータが SCP まで評価するかは実装時に公式で確認する（コンソール版には Organizations の SCP を含めるオプションがあった記憶）
2. **デプロイ後（確実・0.01 USD）**: aggregator に `ce:GetCostAndUsage` を付けてデプロイし、`{"mode": "cost-probe"}` で 1 回手動 invoke する。ハンドラは直近 1 日・`GroupBy=SERVICE` を 1 回呼び、成功ならサービス数、失敗なら `AccessDeniedException` の本文をログに出す。SCP による拒否は本文に `explicit deny in a service control policy` と出る

2 で拒否された場合の逃げ道は、Cost Explorer の取得だけをローカルの `scripts/ops/` に落として日次で実行し、結果を metrics-dev に書くこと。

### 8.2 Q8: 👍👎 の正本は chatlogs

| 観点 | chatlogs（`feedback` 属性） | EMF `FeedbackGood/Bad` |
|---|---|---|
| 何を表すか | **状態**（その回答の最終評価） | **イベント**（押した回数。👍→👎 の変更や再送は 2 回数える） |
| 結合 | `messageId` / `sessionId` / `responseType` / `feedbackReason` と同じ項目 | 何とも結べない（値 1 の系列だけ） |
| 訂正 | 属性を直せば直る | 出た後は直せない |
| 保持 | 60 日 + S3 アーカイブ（無期限、Athena） | CloudWatch メトリクスの保持期間（△ 標準で 15 か月） |
| 鮮度 | 日次・毎時のバッチ | 数秒 |

ダッシュボードや報告に載せる数字は **chatlogs を正本**にする。EMF は「準リアルタイムの信号」用途にだけ残す（例: 1 時間に 👎 3 件でアラーム、が欲しくなったとき）。二つの値が食い違ったら chatlogs が正しく、EMF の方が大きいのが正常（再送の分）。

正本を chatlogs にすると、いまの集計に **1 つ穴がある**。日次行は 02:00 JST に確定するが、👍👎 は回答の翌日以降にも押される（朝に昨日の回答を見返して 👎 を押す）。確定後の投票は昨日の行に一度も反映されない。対策は日次バッチで **D-1 だけでなく D-1〜D-3 を再集計**すること（§6.4）。3 日を超えて遅れた投票は Athena でだけ見える。Cost Explorer の「直近 3 日を毎日上書き」と同じ考え方で、実装も同じループに乗る。

---

## 9. 失敗・改善提案 v2（`/admin/failures`）

役割は「今日直すもの」の作業場。ダッシュボードは件数と入口だけを持ち、1 件ずつの判断と記録はこの画面で行う。既存の骨格（信号チップ・理由フィルタ・改善提案カード・ゴールデン候補コピー・要望一覧）は残す。推奨度: ◎ 入れる前提 / ○ あると良い / △ 判断材料。

### 9.1 いま足りないもの

| 欠け | 何が困るか |
|---|---|
| 期間で絞れない | ダッシュボードの「昨日 5 件」から飛んでも、同じ 50 件が出る。週次レビューで「今週の分」が切り出せない |
| 振り分けの記録先が無い | 「unresolved は件ごとに人手で振り分け」が方針だが、結果は issue コメント頼み。先週の 7 件がどうなったかが画面で分からず、同じ件を二度読む |
| 検索の中身が見えない | 候補資料名 5 件だけ。何件取れて何が除外され、上位スコアがいくつだったかが無いので、検索ミスか作文かの当たりが付かない |
| 暗黙の失敗が見えない | 👎 を押す人は少数。資料が開かれたか、言い換えが起きたかが無い |
| 改善提案が「取得した 50 件」の集計 | 期間も対応済みも区別しないので、直した件がいつまでもカードに残る |

### 9.2 画面構成（上から）

| # | 要素 | 内容 | 推奨度 |
|---|---|---|---|
| 1 | 絞り込み | 期間（昨日 / 7 日 / 30 日 / 指定）・状態（未振り分け / 対応中 / 対応済み / すべて）・種類（👎 / not_found / 言い換え）・理由。ダッシュボードからは `?since=` 付きで飛ぶ | ◎ |
| 2 | 作業量の帯 | 未振り分け n / 対応中 n / 今週対応済み n / 要望（未読）n。**週次レビューのゴールは「未振り分けを 0 にする」** | ◎ |
| 3 | 改善提案カード | 期間内・未対応の信号だけを集計。しきい値 3 は据え置き。「該当を見る」で一覧を絞る（既存） | ○ |
| 4 | 一覧 | 1 件 = 信号・理由・時刻・質問・回答冒頭・フィルタ（既存）+ **ヒント**（§9.3）+ **検索の要約**（トレース設計 §5 の `traceSummary`）+ **振り分け**（§9.4）+ 操作（チャットで開く / ゴールデン候補 / トレース全文） | ◎（ヒント ○、トレース要約はトレース実装後） |
| 5 | トレース全文のドロワー | 候補 30 件の順位・文書・頁・スコア・機種・選択／除外理由の表。初月は Athena で代替 | △ |
| 6 | 要望 | 既存の一覧に既読／対応済みの振り分けを付ける | △ |

### 9.3 ヒント（機械的な手がかり。判断ではない）

| 条件 | ヒント | 疑う場所 |
|---|---|---|
| `excludedByModelScope ≥ 3` かつ 理由 = 資料が違う | 機種スコープで n 件除外 | 取扱機種スコープ表 |
| `topScore` が弱い（閾値はトレース実装後に実測で決める。仮 0.45）かつ not_found / 資料が違う | 上位スコアが弱い | 検索語・略語展開・正規化 |
| `opened = true` かつ 理由 = 疑問が解けない / 回答がおかしい | 資料は開かれた | snippet か作文（検索は当たっている） |
| 言い換えあり かつ 👍 なし | 言い換え後に評価なし | 暗黙の失敗として扱う |
| カテゴリ複数選択 かつ `mergedCount < 5` | カテゴリ過絞り | フィルタの組み合わせ |
| 直前が clarify | 聞き返し後の結合検索 | `compose_search_query` |

ヒントは read 側で付けて `hints: string[]` として返す。ルールはコードに置き、しきい値は SSM に置かない（変えるときはコード変更として記録に残す）。

### 9.4 振り分け（triage）

chatlogs の assistant 行と `product_wish` 行に属性を足す。未設定 = 未振り分け。

```jsonc
"triage": {
  "status": "open" | "in_progress" | "done" | "wontfix",
  "cause":  "search" | "snippet" | "writing" | "clarify" | "kb_missing" | "scope" | "user" | "other",
  "note":   "…（200 字まで）",
  "ref":    "#112 / G017 / e4f5a6b",     // issue・ゴールデン ID・commit のどれか
  "by":     "<sub>", "at": "2026-09-23T02:11:00Z"
}
```

- 更新は admin のみ（`PUT /chat/admin/messages/{sessionId}/{messageId}/triage`）。利用者向けの履歴 API には返さない（`retrievalTrace` と同じ除外）
- Stream → S3 アーカイブには MODIFY として流れるので、Athena で「原因別の件数」「対応までの日数」が後から出せる
- ダッシュボード Y3 の「未振り分け n」はこの属性から数える（`status` が無いか `open`）
- `docs/data-model.md` は production。追加前に事前確認

### 9.5 API

`GET /chat/admin/failures` に `since` / `until` / `triage` を足し、各項目に `traceSummary`・`opened`（`DocumentOpen` の `messageId` と突合）・`reformulated`・`triage`・`hints` を付ける。Scan は今のままで、`since` は FilterExpression に入るだけ（読み取り量は減らない）。25 ページ打ち切りは据え置き、1 日 1,000 件に近づいたら GSI か Athena（別立て A14）。改善提案の集計はクライアントのまま（期間と `triage` で絞った結果を集計）。

---

## 10. お知らせ管理 v2（`/admin/announcements`）

役割は切り分けの最後の一手「利用者へ知らせる」。監視が検知し、切り分けが進む間、利用者はチャット画面で失敗を見続けている。既存の CRUD（種別・重要度・固定・予約公開・Markdown）は残す。

### 10.1 いま足りないもの

| 欠け | 何が困るか |
|---|---|
| 文面の型が無い | 障害の朝にゼロから書く。書く人によって内容が揺れる |
| ダッシュボードとの導線が無い | 告知を出しに行く動線が無く、出した告知が表示中であることも見えない（戻し忘れ） |
| **チャット画面に告知が出ない** | バナーはホームだけ、しかもメンテナンス種別だけ。RAG が失敗しているとき利用者はチャット画面にいる |
| 表示終了がメンテナンスにしか設定できない | API は全種別で `endAt` を保存するが、フォームが出さない。障害告知の終了は削除するしかない |

### 10.2 画面構成（上から）

| # | 要素 | 内容 | 推奨度 |
|---|---|---|---|
| 1 | いま表示中 | 公開中かつ未終了の告知。各行に「表示終了」（`endAt = now`）。チャット表示中なら印 | ◎ |
| 2 | テンプレート | 6 種（§10.3）。種別・重要度・固定・チャット表示のプリセットと、`{{時刻}}` `{{復旧見込み}}` の穴。押すとフォームに流し込む | ◎ |
| 3 | 一覧 | 既存 + 作成者 + 表示終了日時 | ○ |
| 4 | 編集フォーム | 既存 + **表示終了（全種別）** + **チャット画面にも表示** | ◎ |

### 10.3 テンプレートと導線

| テンプレート | 種別 / 重要度 / 固定 / チャット | 開く契機 |
|---|---|---|
| 障害中（回答が返らない） | notice / critical / 固定 / チャット | ダッシュボード「いま」が P1 のとき「利用者へ告知 →」 |
| 復旧 | notice / info / 固定なし / チャット | OK メールを見たら。障害告知を同時に表示終了 |
| 新規登録の受付を一時停止 | notice / warning / 固定 / ホーム | `P2-cognito-signups-40`（ランブック §5.6） |
| メール上限に達した方へ | notice / warning / 固定なし / ホーム | `P1-cognito-email-errors` |
| メンテナンス予告 | maintenance / warning / 固定 / チャット | 定時後デプロイの前日 |
| 生成モデルの切替 | update / info / 固定なし / ホーム | ランブック §7.3 |

テンプレートはフロントの定数（API 不要）。文面はランブックの案内文（§5.6 の翌日手順など）と同じ言い回しにし、二重管理にならないようランブック側からテンプレートを参照する。

### 10.4 データ・API・利用者画面

- announcements 行に `showInChat: boolean` を追加（既定: `severity = critical` なら真）。write Lambda の validate / create / update に 1 項目
- チャット画面に `NoticeBanner` を置く（`MaintenanceBanner` の一般化: 種別を問わず `showInChat` かつ表示中のもの。critical は閉じられない、の既存ルールを踏襲）
- ダッシュボード read API に `now.activeNotices`（同じスタックの announcements テーブルを Query。IAM 追加 1 行）
- 表示終了は `endAt` を今にする更新。削除ではないので履歴が残る

### 10.5 推奨度のまとめ

テンプレート ◎ / ダッシュボード導線 ◎ / チャット画面バナー ◎（利用者影響が最も大きい）/ 表示終了 UI ◎ / 作成者列 ○ / 要望の既読 △。

---

## 別立て A. いま手を付けていないが着手したほうがよいこと

優先度は「今週の 300 人試行で顕在化する順」。既知のもの（issue 番号あり）も、順位を示すために載せる。

| 優先 | 項目 | なぜ効くか | 作業量 |
|---|---|---|---|
| **P0** | A1 アクセスログ配線（I1） | 役割 3 が「記録が無い」で止まっている唯一の原因。IaC の追記だけで、昨夜の 4xx と同じ事象が次に起きたら追える | 小 |
| **P0** | A2 `DocumentOpen` 計測（I3） | 製品目標「資料到達」の唯一の直接指標。試行運用の成否を測る数字が、これが無いと最後まで出ない。`/doc` 中継ページを既に全クリックが通るので、Lambda 1 行 + リンク 1 か所で足りる | 小 |
| **P0** | A3 500 経路の構造化ログと本文整理（I2） | `rag-function` の `ClientError` 経路は AWS のエラーメッセージをそのまま利用者へ返し、ログにはリクエスト ID を残さない。切り分けと秘匿の両方に効く | 小 |
| **P0** | A4 Cognito メール 50 通/日の上限（issue #99、SES 切替） | 300 人が同じ週に登録すると 1 日目に当たる。検知と個別救済は整っているが、恒久対策が無いまま試行が始まった。初週に最も起きやすい「利用者影響あり」 | 中（ドメイン検証・本番申請の待ち時間） |
| **P0** | A5 metrics-dev の TTL 無効化（Q7 で決定） | 400 日で日次 KPI とコスト履歴が消える。テンプレートの `Enabled: false` と `ttl` 属性の書き込み削除。PITR 有効・KB 規模のためアーカイブは不要 | 小 |
| P1 | A6 Amplify 5xx アラーム | 「画面が開かない」を検知するアラームが 28 本の中に無い。API 側が全部正常でも利用者はゼロになる盲点 | 小 |
| P1 | A7 Budgets（§5.7） | 暴走と普及の両方を月内に知る。コード不要 | 小 |
| P1 | A8 コスト配分タグ有効化の依頼を出す | 遡及しないので、依頼が遅れた分だけ帰属できない月が増える | 依頼のみ |
| P1 | A9 合成監視（別立て B3） | 1 日数件の期間は「エラーが無い」と「使われていない」を区別できない。定期の既知クエリが唯一の「いま正常」の根拠になる | 中 |
| P1 | A10 ランブック §2 の書き換え（I5 / I6 と同時） | 通知メール → 最初に見る場所、を人の記憶に頼らない | 小 |
| P2 | A11 デプロイマーカー（I7） | 障害の切り分けで最初に聞く「直前に何を変えたか」を画面で答える | 中 |
| P2 | A12 Athena のフラット化 VIEW（G9） | 60 日を超える比較（月次・前年同月）が SQL 1 本で書ける状態にしておく。列が Stream 生形のままだと誰も使わない | 中 |
| P2 | A13 片付け: `sessions-dev` の監視、`/aws/apigateway/welcome`、EMF フィードバックの扱い決定（Q8） | 実体の無い監視は「アラーム 28 本」の信頼を削る | 小 |
| P2 | A14 `/admin/failures` の Scan | 25 ページ打ち切りで欠ける設計。1 日 1,000 件に近づいたら GSI か Athena へ。いまは不要 | — |

---

## 別立て B. 同種プロダクトの一般的なやり方と、うちでの見立て

社内向け RAG・小規模チーム運用で見かける計測・運用のうち、うちがやっていなくて効果が見込めるものだけ。◎ / △ は本書冒頭の記法。

| # | やり方 | 確度 | うちでの見立て |
|---|---|---|---|
| B1 | **ゼロ件率とクリック率を検索品質の主指標にする**（企業内検索の分析画面で定番の 2 指標） | ◎ 概念として定着。具体的な閾値は製品次第 | ゼロ件率 = not_found 率、クリック率 = 資料を開いた ÷ 候補あり。A1 + A2 で成立。**採用**（§2.4 のファネルがこれ） |
| B2 | **言い換え（reformulation）を暗黙の失敗信号にする**。同じセッションで、回答直後（例: 10 分以内）に利用者が続けて質問し、直前の回答に 👍 も資料クリックも無い場合を「言い換え」と数える | ◎ 検索分野で古くからある概念。閾値（10 分）は判断 | 👍👎 を押す人は少数で、300 人規模では暗黙信号の方が量が出る。chatlogs だけで計算でき、aggregator に 1 項目足すだけ。**採用を推奨**（日次行 `reformulated`。画面には「到達できず」の副表示として件数） |
| B3 | **合成監視（既知クエリの定期実行）**。CloudWatch Synthetics のカナリアや、スケジュール Lambda で本経路を叩く | ◎ 手法として定着 | 制約: API Gateway のリソースポリシーと WAF が IP 許可制で、VPC 外の Lambda は通れない。**Lambda 直接 invoke** に落とせば KB・Bedrock・DynamoDB は検証できる（WAF・API GW・Cognito は検証外）。2 時間おきなら 1 日 12 回 ≒ 月 5 USD（§5.6 の単価前提）。カナリア用ユーザーを aggregator で除外する。**採用を推奨（P1）** |
| B4 | **LLM による回答評価（faithfulness 等）を 👎 と無作為抽出に週次で掛ける** | 概念は ◎（RAGAS 等の指標定義）。小規模チームでの採用実態は △ | 1 日数件なら全件でも安い。Bedrock 内で完結し、データは外に出ない。ただし判断を変えるのは「👎 の内訳が人手で追い切れなくなってから」。**いまは見送り**、週次レビューが 30 分で終わらなくなったら着手 |
| B5 | **ゴールデンセット評価を定期実行し、結果を時系列で保存する** | ◎ | スクリプトは既にある（`run_retrieve_eval.py`）。欠けているのは定期実行と保存（`scope=eval`）。ラベル済み N < 10 では率を見ない、という既存ルールを守ったうえで、ダッシュボード最下部に「最終評価: 日付・n/N」の 1 行。**採用（小）** |
| B6 | **デプロイをダッシュボードに注記する** | ◎（監視ツールのアノテーション機能として一般的） | I7 / A11 で対応 |
| B7 | **LLM 可観測性 SaaS**（トレース・トークン・コストの専用画面） | ◎ 存在と機能。導入判断は製品次第 | 会話本文が社外に出る。`retrievalTrace` + Athena で同じものが手に入る規模。**採用しない** |
| B8 | **SLO とエラーバジェット** | ◎ | 2 人・当番なしでバジェット管理は回らない。アラーム閾値を SLO の代わりに使う（Q1）。**採用しない** |
| B9 | **週次の運用レビューを固定の議題で回す**（失敗 → ゴールデン追加 → 評価 → issue） | ◎ 手法として一般的 | 形は既にある。議題を「ダッシュボードの出来事 7 日分」「コスト画面の前提チェック」「failures の新着」の 3 つに固定すると、画面がそのまま議事録になる。**採用（運用のみ）** |
| B10 | **1 会話あたりコストを追い、サービス単位の予算を置く** | ◎（FinOps の単位経済の考え方） | §5 で対応 |

---

## 変更履歴

- 2026-09-10 初版（棚卸し・metrics-v2・retrieval-trace・ランブックを読んだうえでの設計。実装前）
- 2026-09-10 §8 の回答を反映（SLO p90 20 s、Amplify 確定・WAF 推定、OpenSearch §5.9、TTL 無効化、👍👎 の正本 = chatlogs と D-1〜D-3 再集計）。HTML モックを追加
- 2026-09-10 §9（失敗・改善提案 v2）と §10（お知らせ管理 v2）を追加。§2.2 に告知導線、§4.4 に行内の内訳（任意）、§6.3 に API 一覧、§7 に PR 6b〜6d。モックを 4 画面に拡張し、各要素に推奨度を付けた
- 2026-09-11 実装に合わせて更新。I3 は EMF ではなく回答の行の `documentOpens` に変更、read API は新パスを新設して旧パスを一時併存、WAF は当面「帰属未確認」、§5.9 は未実装、Q7 の訂正（develop は既に TTL 無効）。§7.1 に実装状況を追加
