---
status: draft
last-verified: 2026-09-24
related-code: lambda/rag/rag-function/app.py, infrastructure/sam/phase2-template.yaml, frontend/src/app/chat/page.tsx, lambda/chat/chat-management/app.py
---

# 設計: RAG の 2 モード化（通常モード＋じっくりモード）

> **状態:** 共同確認済み（2026-09-29、mona・itai）。実装はまだない。決定事項は [decisions-2026-09-24-rag-two-modes.md](./decisions-2026-09-24-rag-two-modes.md)、根拠となる調査は [survey-2026-09-24-agentic-rag.md](./survey-2026-09-24-agentic-rag.md)、KB 側への修正依頼は [kb-change-requests.md](./kb-change-requests.md) を正本とする。本書の数値のうち「1 人 1 日 10 回」以外はすべて **暫定値**（評価後に見直す。SAM パラメータで変更可能にする）。

## 1. 目的

利用者が質問の重さに応じて選べる 2 つのモードを持つ。

| | 通常モード | じっくりモード（新設） |
|---|---|---|
| 目的 | すぐに該当資料へ届く | 複数資料・複数機種を突き合わせて、根拠つきで整理する |
| 応答 | 10〜20 秒で 1 回答 | 1〜3 分。途中経過を表示 |
| 検索 | 1 回（条件付きで 2 回） | 質問を 2〜5 観点に分けて最大 8 回 |
| 生成 | 採用モデルを 1 回 | 計画・統合・照合で 3 回 |
| 回数 | 制限なし | **1 人 1 日 10 回（決定済み）** |
| 費用の概算 | 約 $0.01〜0.03 / 問 | 約 $0.2〜0.6 / 問（公表単価からの概算。実測で置き換える） |

採用モデルは運用上 Sonnet 5（[decisions-2026-09-17-global-sonnet5-user-verification.md](./decisions-2026-09-17-global-sonnet5-user-verification.md)）。SAM テンプレートの `BedrockModelId` 既定値は Haiku 4.5 のままなので、デプロイ時のパラメータが実際のモデルを決める。

## 2. なぜ 2 モードか（要点。詳細は survey）

- 単発 RAG は「比較」「複数資料の突合」「会話の続き」の質問に構造的に弱い。一方、1 資料で答えが出る質問では、反復検索は精度が変わらないか下がり、時間は 3〜9 倍になる（Adaptive-RAG、Search-o1、FlashRAG）。
- ChatGPT / Claude / Perplexity / M365 Copilot / Gemini / Glean は、いずれも速い既定の流れと、時間をかける深いモードを分けている。
- 思考（thinking）を有効にするだけでは忠実性は上がらず、無関係な情報に引きずられる報告がある。効くのは「思考の結果を追加の検索と照合に使う」場合。
- 既知の誤答（機種の異なる数値の混在、抜粋にない断定、少数カテゴリの資料が出ない）のうち、じっくりモードで直せるのは前の 2 つと「検索で届かない」の一部。KB 側の欠落（表・図の解析、索引漏れ、メタデータ）はモードでは直らないため、[kb-change-requests.md](./kb-change-requests.md) で所有部門へ依頼する。

`PRODUCT_INTENT.md` の「最初からマルチエージェントにしない」は維持する。じっくりモードは **1 つの AI が決まった手順で何度も調べる固定ワークフロー** であり、自律的に役割を分担するマルチエージェントではない。

## 3. 全体構成

```text
画面（chat/page.tsx）
 ├─ 通常    → POST /rag/query（既存。rag-{env}、同期）
 └─ じっくり → POST /rag/research（新設。rag-research-api-{env} が受付 → 202）
               │   └─ rag-research-worker-{env} を非同期起動（InvocationType=Event、jobId だけ渡す）
               ├─ GET /rag/research/{jobId}         進捗・結果（画面が 2〜10 秒間隔で問い合わせ。§4.11）
               ├─ GET /rag/research?sessionId=…     そのセッションの実行中ジョブ（画面復帰用）
               └─ GET /rag/research/quota           残り回数
```

- **受付 Lambda（`rag-research-api-{env}`）とワーカー Lambda（`rag-research-worker-{env}`）は別関数にする。** 同じ関数だと、予約同時実行の枠をワーカーが使い切ったときに受付・進捗確認まで止まる。コードは同じディレクトリ（`lambda/rag/rag-function/`）を共有し、Handler だけ分ける。
- 認証は既存の `RagApi` の Cognito Authorizer、WAF、スロットリングをそのまま使う。ワーカーは API から呼べない（Lambda の非同期起動のみ。起動権限は受付 Lambda の実行ロールだけに与える）。

### 3.1 部品（既存と新設）

| 部品 | 状態 | 内容 |
|---|---|---|
| `query_knowledge_base` / `build_kb_filter` / `in_service_scope` / `merge_retrieval_results` / `needs_clarify` | 既存 | 両モードで共通に使う |
| `answer_policy.py` / `retrieval_policy.py` / `query_policy.py` | 既存（`app.py` と二重管理の移行中） | 純粋ロジック。じっくりモードの実装前に、使う関数の正本をどちらかに寄せる |
| `kb_profile.py` | **新設（実装 PR 段 1）** | KB ごとの違い（メタデータキー、フィルタ演算子、検索方式）を 1 か所に集約 |
| リランク | **新設（段 1、既定 OFF）** | Retrieve の後に Rerank API を別呼び出し。並び順だけ変え、閾値判定と画面の relevance は元の score のまま。Rerank が失敗したら Retrieve の元の順に戻す |
| じっくりモードの受付・ワーカー・ジョブ管理 | **新設（段 2）** | 本書 §4 |

### 3.2 実行方式の選定

| 方式 | 採否 | 理由 |
|---|---|---|
| 非同期ジョブ（受付 Lambda → ワーカー Lambda の非同期起動＋DynamoDB＋ポーリング） | **第 1 版で採用** | 既存の見出し生成と同じ考え方で作れる。API Gateway・Cognito Authorizer・WAF をそのまま使える。電波が切れても結果を取り戻せる |
| 同期＋REST API レスポンスストリーミング | 後続 | Python Lambda は Lambda Web Adapter かカスタムランタイムが必要。画面も一括受信からストリーム受信へ作り替えになる。正確さは上がらず、待ち時間の体感だけが良くなる |
| Step Functions | 後続（必要になったら） | 第 1 版の検索は最大 8 回で、1 つの Lambda 内の並列実行で足りる。段ごとの再試行や長時間処理が必要になったら移す |
| SQS の待ち行列で順番待ち | 後続（起動待ちの失敗 `DispatchTimeout` が多いとき） | 第 1 版は 1 人 1 日 5 回の想定で、同時実行の枠（ワーカー 5）が埋まることは少ない。頻発したら、受付とワーカーの間に SQS を入れて順番待ちにする |
| API Gateway のタイムアウト引き上げだけ | 不採用 | 進捗表示・再開・二重投入防止を解決しない |

## 4. じっくりモード

### 4.1 受付（POST /rag/research）

1. 利用者 ID は Cognito の `sub` から取る（body の userId は使わない）。
2. 入力検証: `query` は 1〜2,000 文字の文字列、`filters` は `/rag/query` と同じ形（`category` / `modelType`）、`clientRequestId`（画面が送信ごとに生成する UUID。再送時は同じ値）は必須。`sessionId` を指定したら所有者を確認（他人・不存在は 404）。
3. 聞き返し判定（既存の `needs_clarify`）。聞き返すなら **回数を消費せず** 同期で `clarify` を返す。
4. まず `REQ#<userId>#<clientRequestId>` を強整合性で読み、存在すればそこから既存 `jobId` を引いて 202 で返す。存在しない場合も、**回数・同時実行・二重送信防止・ジョブ作成を 1 つの DynamoDB トランザクション（`TransactWriteItems`）で行う。** どれか 1 つでも条件を満たさなければ、全部を反映しない。
   - `ACTIVE#<userId>` の取得: 存在しない、または有効期限切れのときだけ成功（同時実行 1 件）
   - `QUOTA#<userId>#<JST 日付>` の成功回数を 1 増やす: 10 未満のときだけ成功
   - `ATTEMPT#<userId>#<JST 日付>` の起動回数を 1 増やす: 20 未満のときだけ成功（失敗時の返金を悪用した無制限実行を防ぐ）
   - `REQ#<userId>#<clientRequestId>` を `attribute_not_exists(pk)` で作成し、`jobId` を記録（二重送信の防止）
   - `JOB#<jobId>` を `attribute_not_exists(pk)` で作成。`userMessageId`（利用者メッセージの ID）は受付が先に採番してジョブに書き、質問文そのものはジョブに持たない（§4.6）。`dispatchDeadline` は作成時刻から 120 秒後にする（同時実行の枠が埋まったとき、順番が来るまで待てる時間。§4.3）
5. トランザクションが `REQ` の条件で失敗したら、同じ `REQ#<userId>#<clientRequestId>` を強整合性で読み、そこから既存 `jobId` を引く。そのジョブを 202 で返し、回数・ロック・ジョブを追加作成しない。同じ `clientRequestId` の同時送信でもこの経路にする。その他の失敗の応答は、実行中 → 409、回数上限 → 429 `{ error: "DailyLimitExceeded", quota }`。
6. トランザクション後に利用者メッセージを chatlogs へ条件付きで保存（`messageId` はジョブの `userMessageId`、`researchJobId` を付ける）。保存に失敗したら、`queued` かつ未返金のジョブだけを条件付きで `failed` にし、回数を返して `ACTIVE#<userId>` を自分の `jobId` のときだけ解除し、503 を返す。途中停止時は `dispatchDeadline` による受付時・GET 時の回収に任せ、保存済みメッセージは削除しない。
7. 利用者メッセージ保存後にワーカーを非同期起動（ペイロードは `{ jobId }` だけ）。起動 API が失敗したら、`queued` の条件付きトランザクションで回数・ロックを戻し、ジョブを `failed` にして 503 を返す。受付 Lambda がその前に停止しても、期限超過時に同じ回収を行う。
8. `202 { jobId, sessionId, userMessageId, status: "queued", quota }` を返す。

JST 日付は `zoneinfo.ZoneInfo("Asia/Tokyo")` で算出する（Lambda の既定は UTC）。`quota.resetsAt` も同じ基準。

### 4.2 ワーカー（固定ワークフロー）

**開始時:** イベントの `jobId` だけを信用し、DynamoDB からジョブを読む。`userId` / `sessionId` / `userMessageId` / `filters` はジョブ項目の値を使い、質問文は chatlogs の利用者メッセージ（`sessionId` と `userMessageId`）から読む。メッセージが無い、または削除済み（`deleted`）なら開始せず、`failed`（`errorCode: "QuestionUnavailable"`）にして回数を返す。`dispatchDeadline` を過ぎていれば開始しない。ワーカー自身が一意な `leaseToken` を発行し、`status=queued AND dispatchDeadline>=now` の条件付き更新で `queued → running`、`leaseToken`、`runningUntil` を同時に書き、同じトランザクションの `ConditionCheck` で `ACTIVE#<userId>` の `jobId=<jobId>` を確認する。失敗したら（すでに running・完了、期限超過、または自分のロックでない）何もせず終わる。以後のジョブ更新・進捗・chatlogs 保存・完了更新・ロック解除・返金は、すべて `status=running AND leaseToken=<自分のトークン>` の条件を満たす場合だけ行う。

| 段 | 処理 | 設定（暫定） | 失敗時 |
|---|---|---|---|
| 1. 計画 | 質問から、検索の観点（2〜5 個の検索語と目的）、質問の種類（単一 / 比較 / 手順 / 複数資料）、言及された機種、リスク分類を JSON で出す | 採用モデル、`thinking: disabled`、出力 1,000 トークン | 元の質問と略語展開した検索語の 2 本で続行 |
| 2. 検索 | 元の質問＋観点ごとの検索語で Retrieve を並列実行 | 最大 8 回、各 30 件 | 失敗した検索だけ除外して続行。全滅なら失敗 |
| 3. 絞り込み | 重複排除（`merge_retrieval_results`）→ リランク（設定時）→ 根拠の選定。根拠に `E1…En` の ID を振る | score 0.3 以上、1 資料 3 件まで、合計 20 件、各 2,000 文字まで | 根拠 0 件なら「見つからない」結果を返す（作文しない） |
| 4. 統合 | 根拠を `<evidence id="E1" doc="…" model_type="…" page="…">` で渡し、主張ごとに根拠 ID を付けた JSON を出させる | `thinking: adaptive`、`output_config.effort: medium`、出力 16,000 トークン | 1 回だけ再試行。だめなら失敗 |
| 5. 照合 | ①機械的な検査: 主張が引用した ID が段 3 の根拠に実在するか、主張の機種と根拠の `model_type` が食い違わないか。②意味の検査: 引用した根拠の本文で主張が裏付けられるか。裏付けがない主張は削除して「確認できなかった点」へ移す | ②は `thinking: adaptive`、`effort: low`、出力 4,000 トークン | ②ができなければ、全主張に「未照合」の印を付けて返す |
| 6. 保存 | 回答を chatlogs に assistant メッセージとして保存し、ジョブを `completed` にする | — | 失敗 |

- **thinking の設定は段ごとに明示する。** 通常モードの設定（`GENERATION_THINKING`、既定 disabled）とは別の設定値を使い、共通の `build_generation_request` に段ごとの値を渡す。通常モードの挙動が変わらないことをテストで固定する。
- **フィルタの扱い:** 計画段が見つけた機種は「回答をまとめる単位」にだけ使い、検索フィルタには使わない。検索フィルタは利用者が画面で指定したものだけ（`build_kb_filter` と `in_service_scope` が最終判断）。
- **安全ゲート:** 既存の聞き返し・弱検索ゲート・取扱機種スコープに加え、根拠 0 件なら作文しない。照合で全主張が落ちたら結論を出さず、「確認できなかった点」だけを返す。安全・法令・作業可否の判断を含む高リスク質問は、結論で可否を断定せず、根拠と確認先を示す。
- **PRODUCT_INTENT との対応:** 計画段の出力にリスク分類を含め、`リスク分類 → 検索 → 版・権限・関連性確認 → 根拠パック → 統合 → 照合 → 安全ゲート → 表示` の順で処理する。安全ゲートは上記の保留・非断定条件を機械的に適用する。
- **LLM 出力の検証:** 計画・統合・照合の JSON は、必須キー・型・最大件数・文字数をスキーマで検証する。根拠 ID は `E1`〜`En` 以外を拒否する。不正時は、計画は既定の 2 本で続行、統合は 1 回だけ再試行、照合は「未照合」扱いにする。具体的なスキーマ（必須キー・型・件数・文字数）は実装 PR で `docs/api/rag-research.md` とテストに定義する。
- **資料内の指示に従わない:** 根拠・会話履歴は「データ」として区切って渡し、中の指示・URL・コードには従わないとシステムプロンプトに書く。ツール実行や外部アクセスは持たせない。

### 4.3 二重実行・取り残しを防ぐ

| 事象 | 対策 |
|---|---|
| Lambda の非同期起動の自動再試行（既定で最大 2 回） | ワーカーの非同期起動設定で `MaximumRetryAttempts=0`（関数エラーでは再試行しない）、`MaximumEventAgeInSeconds=120`（`dispatchDeadline` と同じ長さ。同時実行の枠が埋まって起動できないイベントは、Lambda がこの時間まで再試行して起動を待つ）。失敗イベントは OnFailure 先（SQS）へ送る |
| それでも二重に動いた場合 | 状態遷移（`queued → running → completed / failed`）はすべて条件付き更新。assistant メッセージの `messageId` はジョブから決定的に作り（例 `research-<jobId>`）、存在しないときだけ保存する。chatlogs 保存は同じ `leaseToken` 条件の `ConditionCheck` と一緒に行う |
| `queued` のまま起動されない（受付 Lambda の停止、起動 API の未受理、同時実行の枠が埋まったままの順番待ち） | ジョブの `dispatchDeadline`（120 秒）を過ぎたものを受付時または GET 時に、`status=queued AND dispatchDeadline<now AND refunded=false` の条件付きトランザクションで `failed`（`errorCode: "DispatchTimeout"`）化・返金・ロック解除を行う。`ACTIVE#<userId>` は jobId が自分のときだけ解除する。第 1 版は OnFailure SQS を運用アラームの対象とするだけで消費処理を持たず、GET 時回収で整合させる。EventBridge 定期回収は後続とする |
| ワーカーのタイムアウト・異常終了で `running` のまま残る | `running` に期限（開始＋ジョブ上限時間＋余裕）を持たせる。GET 時の期限切れ処理は、取得した `leaseToken` と `status=running` を条件に `failed`（`errorCode: "Timeout"`）へ更新し、同じ条件付き処理でロックを外し、回数を返す。条件が外れた元ワーカーの後続書き込みはすべて無効になる |
| 回数の返却 | 返すのは利用者の入力に起因しない失敗（Bedrock の 5xx・タイムアウト・スロットリング、起動失敗、タイムアウト）だけ。ジョブの `refunded` 属性で 1 回だけ返す。起動回数（ATTEMPT）は返さない |
| ロック | `ACTIVE#<userId>` の有効期限は 360 秒（起動待ち 120 秒＋ジョブ上限 180 秒＋余裕 60 秒。起動待ちの間にロックが切れて、同じ利用者の 2 本目が動かないようにする）。完了・失敗時に、`ACTIVE#<userId>` の jobId が自分のときだけ明示的に外す |

assistant 保存から完了処理までは、**assistant メッセージを条件付きで保存（存在しないときだけ）→ ジョブを `completed`（`leaseToken` 一致かつ `status=running` のときだけ）→ ロック解除**の順にする。途中で落ちた場合は、failed 化（GET 回収を含む）の前に決定的な `messageId`（`research-<jobId>`）の assistant メッセージが存在するか確認し、存在すれば同じトークン条件で `completed` に補正してからロックを解除する。回答が保存済みなら `completed` を優先する。

GET の期限切れ処理は、`running` ならジョブの `status`、期限、取得時の `leaseToken`、`refunded=false` を条件に、`queued` なら `status=queued AND dispatchDeadline<now AND refunded=false` を条件にしたトランザクションで `failed` 化・ロック解除・返金を行う。ジョブ更新・回数返却・ロック解除のいずれかの条件が外れたら何も反映せず再読込する。

### 4.4 回答の形

```text
[じっくり調査] 検索 6 回・根拠 14 件・所要 84 秒

■ 結論（2〜5 行）
■ 機種ごとの整理（表: 機種 / 値・手順 / 根拠）
■ 資料間で違いがある点（表: 項目 / 機種・版 / 値 / 根拠）
■ 確認できなかった点（照合で裏付けが取れなかった主張、資料に無かった情報）
■ 確認先・エスカレーション（高リスクのとき）
■ 根拠資料（資料名・ページ）
```

同じ項目で機種や版によって値が違うときは、**1 つの値にまとめず** 「資料間で違いがある点」に並べる。

### 4.5 上限（「1 日 10 回」以外は暫定。すべて SAM パラメータで変更可能）

| 項目 | 初期値 | 備考 |
|---|---|---|
| 1 人 1 日の成功回数 | **10（決定済み）** | mona 2026-09-24 |
| 1 人 1 日の起動回数 | 20 | 失敗による返金を含めた上限 |
| 1 人の同時実行 | 1 | |
| 検索の観点 | 最大 5 | |
| Retrieve の回数 | 最大 8 | |
| 根拠の件数 | 最大 20 件（1 資料 3 件まで、各 2,000 文字） | 長い文脈は 32k〜64k トークン超で劣化の報告 |
| 起動待ち（順番待ち）の上限 | 120 秒 | ワーカーの同時実行の枠が埋まっているとき、この時間まで待つ。超えたら失敗（`DispatchTimeout`）にして回数を返す。`dispatchDeadline` と `MaximumEventAgeInSeconds` を同じ値にする |
| ジョブの時間 | 180 秒で打ち切り | ワーカー Lambda のタイムアウト設定は 300 秒（AWS の上限は 900 秒） |
| 1 ジョブの推定費用 | $0.60 を超えたら以降の段を打ち切る | トークン数×単価で逐次計算 |
| ワーカーの予約同時実行 | 5 | 組織全体の費用・負荷の上限。受付 Lambda には予約を付けない |

想定利用は 1 人 1 日 5 回（itai、2026-09-29）で、10 回は上限。1 回 約 $0.2〜0.6 の概算だと、毎日使う人 1 人で月 $20〜60。Bedrock の予算アラートは、利用が少ない間の暫定値として月 $100（#106）。本番を `beta` にするとき、想定回数×人数で見直す。

### 4.6 保存するデータ

新規テーブル `research-jobs`（PK `pk`、TTL 属性 `ttl`。Scan は使わない）。

| 項目 | キー | 主な属性 | TTL |
|---|---|---|---|
| ジョブ | `JOB#<jobId>` | `userId`、`sessionId`、`userMessageId`、`clientRequestId`、`filters`、`status`、`stage`、`progress`、`createdAt` / `updatedAt` / `dispatchDeadline` / `runningUntil`、`leaseToken`、`errorCode`、`refunded`、`resultMessageId`、`researchTrace` | 60 日 |
| 二重送信の防止 | `REQ#<userId>#<clientRequestId>` | `jobId` | 1 日 |
| 成功回数 | `QUOTA#<userId>#<JST 日付>` | `count` | 3 日 |
| 起動回数 | `ATTEMPT#<userId>#<JST 日付>` | `count` | 3 日 |
| 同時実行ロック | `ACTIVE#<userId>` | `jobId`、`expiresAt` | 1 日 |
| セッションの実行中ジョブ | GSI（パーティションキー `userId`、ソートキー `createdAt`） | userId で Query して sessionId で絞る画面復帰用 | 60 日 |

- **質問文はジョブに持たない。** 利用者メッセージ（chatlogs）を `sessionId` と `userMessageId` で参照する。質問文の保存場所・削除・保持期間を chatlogs の 1 か所に保つため（検索トレース #146 の「質問本文はコピーせず、user メッセージを参照する」と同じ方針）。利用者がセッションを削除すると（`deleted`）、順番待ちのジョブは開始されない（§4.2）。
- `researchTrace` は検索語、選んだ根拠の URI・ページ・score だけを持ち、**根拠の本文は持たない**。
- 回答は既存の chatlogs に assistant メッセージとして保存する（`responseType: "research"`、`sourceDocuments`、`pageCandidates`、`research`（主張と根拠 ID、資料間の違い、確認できなかった点、統計））。既存の 60 日 TTL と Stream→S3 保全にそのまま乗る。

### 4.7 利用者への露出

| データ | 利用者向け API で返すか |
|---|---|
| 回答（結論・表・違い・確認できなかった点・根拠資料） | 返す（`GET /rag/research/{jobId}` の完了時、チャット履歴） |
| 進捗（段・件数） | 返す |
| `researchTrace`（検索語・根拠の URI・score） | **返さない**。将来、管理者向けに見せる場合は Cognito admin グループと IP 許可リストの内側に限る（[design-2026-09-10-retrieval-trace.md](./design-2026-09-10-retrieval-trace.md) と同じ） |
| 他人のジョブ | 返さない（存在有無も区別せず 404）。所有者の判定は、ジョブ項目の `userId` と Cognito の `sub` の比較だけで行う |

### 4.8 ログ（#133 の RAG 運用ログ契約に合わせる）

- CloudWatch には、段ごとの所要ミリ秒、件数（検索回数・候補数・根拠数・削除した主張数）、トークン数、モデル ID、終了理由だけを JSON 1 行で出す。
- **出さないもの:** 質問・検索語・回答・根拠の本文、`sub`、`sessionId` / `messageId` / `jobId`、IP、例外の本文（型名とエラーコードだけ）。相関は受付時の API Gateway `requestId` をジョブ項目に保存し、ワーカーのログに出して行う。

### 4.9 API（案。実装 PR で `docs/api/rag-research.md` として正本化する）

| メソッド・パス | 要点 |
|---|---|
| `POST /rag/research` | body `{ query, clientRequestId, sessionId?, filters? }`。`202 { jobId, sessionId, userMessageId, status, quota }`。聞き返し時は `200 { responseType: "clarify", … }`（回数を消費しない）。実行中 409、上限 429、起動失敗 503 |
| `GET /rag/research/{jobId}` | `{ jobId, status, stage, progress: { step, totalSteps, searchesDone, searchesTotal }, pollAfterMs?, message?, error? }`。完了時の `message` はチャット履歴と同じ形。`pollAfterMs` は次の確認までの目安（ミリ秒）で、開始待ち（`queued`）は 5000、最後の段（照合中）は 3000、それ以外は省略する（省略時は画面の規則で決める。§4.11） |
| `GET /rag/research?sessionId=…` | Cognito の userId で `userId-createdAt` GSI を Query し、`sessionId` で絞った実行中ジョブ（画面復帰用）。他人のセッションは結果に出さず 404 |
| `GET /rag/research/quota` | `{ limit, used, remaining, resetsAt }` |

### 4.10 SAM / IAM（実装 PR で追加するもの）

- `research-jobs` テーブル（オンデマンド、TTL、ポイントインタイムリカバリは既存テーブルに合わせる）
- 受付 Lambda・ワーカー Lambda（同じ `CodeUri`、Handler を分ける）、ワーカーの非同期起動設定（`MaximumRetryAttempts=0`、OnFailure の SQS）、ワーカーの予約同時実行
- `RagApi` に 4 つの経路（Cognito Authorizer）
- IAM（最小権限）
  - 受付 Lambda とワーカー Lambda は別の実行ロールにする。受付ロールにはワーカー処理用の Bedrock 権限を与えない
  - 受付: `research-jobs` への `GetItem` / `PutItem` / `UpdateItem` / `Query` / `TransactWriteItems`（テーブルと GSI の ARN 限定）、chatlogs への保存、ワーカー ARN に限った `lambda:InvokeFunction`
  - ワーカー: `research-jobs` と chatlogs への読み書き（ARN 限定）、`bedrock:Retrieve`（KB ARN 限定）、`bedrock:InvokeModel`（採用モデル）、リランクを使うときは `bedrock:Rerank`
  - OnFailure の SQS への `sqs:SendMessage` はワーカー側の非同期起動設定（Lambda サービス）が必要とする権限として付与する。受付ロールには付けない
  - Scan 権限は付けない

#### 提供範囲の切り替え

画面と API は同じ値の機能フラグで切り替える。

| 値 | 画面 | API（`/rag/research`） |
|---|---|---|
| `off`（既定） | じっくりモードを表示しない | 404 を返す |
| `beta` | 「開発中」表示つきで表示 | 利用可能 |
| `on` | 正式提供として表示（「開発中」表示なし） | 利用可能 |

- `beta` にした環境では、開発中も利用者を限定せず全員が使える。
- フロントエンドは `NEXT_PUBLIC_RESEARCH_MODE=off|beta|on`、API 側は `RESEARCH_MODE_ENABLED=off|beta|on` とする。
- API 側で `off` のときは、画面で隠すだけでなく `POST /rag/research` と関連する GET を 404 にする。
- 第 1 版は dev 環境を `beta`、本番を `off` から始める。本番を `beta` にする時期は別途合意する。

### 4.11 画面

> 最終検証: 2026-09-25 — `frontend/src/app/chat/page.tsx` と `frontend/src/components/` の表示実装確認

- 入力欄の上に切り替え: 「通常」「じっくり調べる（残り n 回）」。既定は通常。
- じっくりを選ぶと説明を表示:「複数の観点で検索し、資料間の違いを確認します。1〜3 分かかります。1 日 10 回まで」。
- 通常モードの回答で **根拠が弱い・見つからない・👎 のあと** に「じっくり調べる」ボタンを出す（同じ質問で起動）。自動では切り替えない。
- 実行中は進捗カード:「観点を整理中 → 検索中 3/6 → 根拠を選定中 → まとめ中 → 照合中」。
- 開始待ち（`queued`）の間は「受付済みです。混み合っているときは、順番が来るまで最大 2 分お待ちください」と表示する（20 秒を過ぎたら混雑の説明を足す）。120 秒で開始できず失敗（`DispatchTimeout`）したときは「混み合っていて開始できませんでした。回数は消費していません。しばらくしてからもう一度お試しください」と表示し、「通常モードで質問する」ボタンを出す。
- ページを離れて戻ったときは、`GET /rag/research?sessionId=…` で実行中ジョブを見つけて進捗表示を再開する。完了していればチャット履歴に回答が入っている。
- 送信ボタンは実行中は無効。`clientRequestId` は送信ごとに作り、通信エラーで再送するときは同じ値を使う。
- 結果は「じっくり調査」の印つきカードで §4.4 の形に表示。既存の 👍👎 と理由を使う。

#### 進捗の確認間隔

> 最終検証: 2026-09-29 — WAF の利用者レート制限（`security-waf-template.yaml`）、API Gateway のステージ上限（`phase2-template.yaml`）、既存の画面に定期確認の処理がないこと（`frontend/src`）を確認

2 秒ごとに確認し続けると、1 回のジョブ（3 分）で約 90 回、2 つのタブで 180 回になる。次の 2 つの上限に近づくため、間隔を延ばす。

- WAF の利用者レート制限: 同じトークンで 5 分 300 回まで。rag・chat・auth などの API の合計で数え、超えると質問や履歴の表示も 429 で止まる。
- RAG API のステージ上限: 既定で 1 秒 5 回（バースト 20）で、全利用者の合計。2 秒間隔だと 10 人が同時に待つだけで使い切る。

確認の規則（第 1 版。実装は `frontend/src/lib/research-polling.mjs`。画面・API への接続は、じっくりモードの実装 PR で行う）:

- 間隔は、開始から 30 秒は 2 秒、90 秒までは 5 秒、以降は 10 秒（3 分で 36 回）。応答の `pollAfterMs` があれば、それを 1〜30 秒に丸めて優先する。
- タブが非表示の間は確認を止め、表示に戻ったらすぐ 1 回確認して再開する（`document.visibilityState`）。
- 429 やネットワークエラーのときは、連続した回数ぶん間隔を倍にし（上限 30 秒、成功すれば元に戻す）、429 のときは「アクセスが多いため、しばらくお待ちください」と表示する。
- 確認のタイマーはジョブごとに 1 本だけ持つ（画面の再描画で二重に動かさない）。
- 送信から 6 分（起動待ち 120 秒＋実行 180 秒＋余裕。同時実行ロックの 360 秒と同じ）で確認を打ち切り、「結果を確認できませんでした。画面を再読み込みしてください。回答はチャット履歴に保存されている場合があります」と表示する。
- 複数のタブで確認を 1 本にまとめることはしない。2 つのタブでも 5 分あたり約 96 回で、WAF の 300 回に収まる。実測で問題が出たら見直す。

実装のテストで確認する項目: 3 分で 36 回、6 分で打ち切り（53 回で停止）、`pollAfterMs` の優先と丸め、429・通信エラーでの倍化と回復、非表示で停止・復帰で即時確認、同じジョブは 1 本、完了・失敗で停止、確認中の停止・非表示で次を予約しない。

#### 開発中の表示（`beta` のとき）

- モード切り替えの「じっくり調べる」にだけ「開発中」バッジを付ける。通常モードには付けない。
- じっくりを選んだときは、次の説明を表示する。**「開発中の機能です。回答の正確さを検証しています。重要な判断は根拠資料で確認してください」**
- 進捗カードと結果カードの見出しを **「じっくり調査（開発中）」** とし、通常回答とは異なる violet 系の枠・背景色にする。警告色の赤は使わない。通常モードの回答の見た目は変更しない。
- 結果カードの末尾に **「気づいた点を 👍👎 で教えてください」** を表示する。
- 表示文言はフロントエンドの定数 1 か所にまとめ、`on` では「開発中」の表示を外せるようにする。既存の低信頼候補の amber 表示（`frontend/src/app/chat/page.tsx:975-1009`）と not_found 案内（`frontend/src/app/chat/page.tsx:1037-1049`）の配色・注意表示を踏まえるが、通常回答の表示は変えない。

## 5. 通常モードの改善（継続）

通常モードはこれまでどおり改善を続ける。新しい仕組みは **既定 OFF で入れ、評価してから ON にする**。

| 改善 | 状態 | ON にする条件 |
|---|---|---|
| KB プロファイル（KB の差し替えを設定で行う） | 実装 PR 段 1 で導入（既定は現行と完全一致） | — |
| リランク（Rerank API を別呼び出し。並び順だけ変更し、閾値判定・画面の relevance は元の score） | 段 1 で導入（既定 OFF） | 評価セットで到達率が悪化せず、候補上位の到達が改善 |
| 会話を踏まえた検索語の書き換え | 段 1 で導入（既定 OFF） | 会話の続きの質問で到達率が改善し、p95 の悪化が 2 秒以内 |
| thinking（adaptive＋effort low） | 段 1 で導入（既定は現行の disabled） | 機種誤帰属率が下がり、p95 が 20 秒以内 |
| ヒットした資料の前後の取り直し | 後続 | じっくりモードで効果を確認してから |
| 弱い検索・👎 のあとの「じっくり調べる」ボタン | じっくりモードと同時 | — |

書き換えに使う小型モデルは設定で選ぶ。Haiku 4.5 は Bedrock のモデルカードに「EOL は 2026-10-01 より前にはならない」とあるため、採用時に後継モデルを確認する。

## 6. KB を差し替えやすくする

どの KB を使うかは今後変わる可能性がある（共有 KB の改善、自前 KB、Managed Knowledge Base など）。KB ごとに違う前提をコードに散らさず、`kb_profile.py` に集める（実装 PR 段 1。現行はコード内の定数と環境変数に分散している）。

| KB ごとに違うもの | 置き場所 |
|---|---|
| KB ID | 既存の SAM パラメータ `KnowledgeBaseId` |
| メタデータのキー名（URI、チャンク ID、ページ番号、機種、カテゴリ） | `KbProfile`（`KB_PROFILE_JSON` で上書き） |
| 機種フィルタの演算子（現行 `listContains`） | 同上 |
| 検索方式（HYBRID / SEMANTIC） | 同上（既存の `RAG_SEARCH_TYPE`） |

**Managed Knowledge Base へ移る場合の注意（調査で判明）:** 既存 KB の変換はできず、新規作成・再投入・KB ID の変更になる。直接 API のフィルタ（`managedSearchConfiguration`）の演算子一覧には `listContains` が載っていない（AgentCore のコネクタ文書には載っている）ため、機種の配列を `in` などで表せる形に直す必要がありうる。ページ番号・引用の形式も変わり、IAM も増える（`bedrock:AgenticRetrieveStream` 等）。移るときは `KbProfile` の追加と、結果の形を揃える変換だけで済むようにしておく。本番とは切り離して試す。

## 7. 評価

- **評価セット:** まず 20〜50 問。実際の質問と既存のモデル比較（GOLD / BAD / REAL）から、単一資料 / 機種横断の比較 / 複数資料の突合 / 会話の続き / 図表 / 対象外 / 見つからない、に分けてタグを付ける。評価と実験は並行で進め、問を増やしていく。
- **比べ方:** Bedrock RAG Evaluations の retrieve-and-generate BYOI に、自前の Retrieve 結果と回答を S3 の JSONL で渡す（1 ジョブ最大 1,000 件）。通常 / 通常の改善 ON / じっくり / 設定変更前後は別ジョブにし、同じ設問 ID・指標で比較する。取得失敗の切り分けには retrieve-only も使う（[BYOI 入力形式](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-prompt-retrieve-generate.html)）。
- **指標:** 期待資料への到達率、根拠のない主張の割合、機種の誤帰属率、資料間の違いの検出率、「分からない」と言うべき場面での保留率、p50 / p95 の時間、1 問あたり費用に加え、Correctness / Completeness / Faithfulness / CitationPrecision / CitationCoverage / ContextRelevance を使う。必要なら「機種の誤帰属」などをカスタム指標にする（[指標一覧](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-metrics.html)）。
- **judge:** 評価モデルは対応表にあるものを使う。2026-09-25 時点では Claude Sonnet 4.6 が候補で、Sonnet 5 は一覧にない（[対応モデル](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html)）。日本語品質は保証されていないため、初期は人の評価と照合する。
- **費用:** 評価ジョブ自体の追加料金はなく、judge のトークン代のみ。50 問 × 6 指標で数ドル規模を見込む。
- **判定・記録:** 自動評価は比較材料とし、採用判断は根拠確認を含む人のレビューで行う。設定版・モデル ID・プロンプト版・検索結果・回答・引用・trace ID を記録する。
- **週次の失敗振り分け:** 1 件ずつの原因分類と人の承認は Bedrock Evaluations ではなく、#104 §9.5 の提案どおり Lambda から直接モデルを呼ぶ。
- **判定:** じっくりモードは「比較・複数資料の質問で、根拠のない主張と機種誤帰属が減る」ことを確認する。単一資料の質問で通常モードより悪くならないことも見る。採点は LLM と人（現場代理人・品質担当）の両方。

## 8. 段階導入

| 段 | 内容 | PR の種類 |
|---|---|---|
| 0 | 本設計・決定記録・KB 修正依頼台帳の共同確認 | 共同確認 Markdown |
| 1 | KB プロファイル、リランク・書き換え・thinking の設定（すべて既定 OFF） | デプロイ |
| 2 | じっくりモード第 1 版（受付・ワーカー・ジョブ管理・画面・API 文書）を、開発中表示つき（`beta`）で dev から提供 | デプロイ（段 1 に積む） |
| 3 | 評価セットで通常 / じっくりを比較し、問題がなければ `on`（開発中表示を外す）にする。通常モードの ON 項目とじっくりモードの暫定値も見直す | 記録＋設定変更 |
| 4 | 必要なら: ストリーミング、前後ページの取り直し、Managed KB の比較、切り替えの自動提案 | 都度 |

### 当面の優先順位（mona 決定 2026-09-25。3・5 は 2026-09-29 に mona・itai 合意で更新）

1. 初期評価セット 20〜30 問を作る（AI が候補を出し、mona・itai が正解を確認）。
2. 検索トレースを最小限実装する。
3. KB 台帳（[kb-change-requests.md](./kb-change-requests.md)）に、失敗一覧や評価セットで見つけた実例の記録を始める（KB-01・02・12 は先に現況を再確認）。所有部門へは、実例を貯めてからまとめて一度に伝える（D4）。
4. dev 環境で比較し、その結果を見て通常モードの改善を ON にするか判断する。
5. じっくりモードは、評価を待たず dev の `beta` で試行実装する（D8）。効果が見られなければ `off` にして止める。

理由: 利用者の資料到達・疑問解決の改善を測れる状態を先に作るため。

試行の進め方（mona・itai 合意 2026-09-29）: じっくりモードは使ってみないと分からない点（待ち時間、回答の質、費用）が多く、機能フラグ（D7）で戻せるため、評価と並行して dev の `beta` で試す。有用でなければ `off` にし、必要なら削除する（`research-jobs` テーブル、Lambda 2 本、API の経路 4 本、画面の切り替え）。本番は `off` のままにする。

## 9. 実装で production 文書を変える予定（各実装 PR で事前確認する）

- `docs/data-model.md`: chatlogs の `responseType` に `research` と `research` / `researchJobId` 属性を追加、`research-jobs` テーブルを追加
- `docs/api/chat.md`: 履歴取得でじっくり調査の回答を返すこと
- 新規 `docs/api/rag-research.md`（status: development）: じっくりモードの API

## 10. この文書で決まること / 決まらないこと

**決まること（共同確認の対象）**
- 2 モード構成、じっくりモードの処理・画面の方針、非同期ジョブ方式（受付とワーカーの分離、二重実行・取り残し対策を含む）、通常モードの改善を既定 OFF で入れる方針、KB プロファイルで KB を差し替えやすくする方針、開発中（`beta`）も利用者を限定せず全員が使える方針、評価を待たずに dev の `beta` で試行し、効果がなければ止める進め方（D8）

**決まらないこと（後で決める）**
- 回数以外の上限の最終値（評価後）、通常モードで ON にする項目（評価後）、本番を `beta` にする時期、KB を自前にするか・Managed KB に移るか（所有部門との調整と比較試験の後）、ストリーミング化の時期
