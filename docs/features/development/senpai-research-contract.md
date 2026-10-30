---
status: draft
last-verified: 2026-10-21
related-code:
  - lambda/rag/rag-function/senpai_research_*.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/lib/knowledge-senpai-research.mjs
  - frontend/src/components/knowledge/KnowledgeSenpaiChat.tsx
---

# 工技先輩の調査ジョブ（試作）: API と段階イベントの契約

> 最終検証: 2026-10-21 — 実装済み。バックエンドは単体テスト（moto・偽の Bedrock/KB）と cfn-lint まで確認し、監査 F1〜F13（時間予算・リース・日次枠の返却・引用の強制など）を反映済み。dev への実機デプロイと実モデルでの所要時間は未確認。根拠は [調査](../../survey-2026-10-20-senpai-agentic-search.md) §2・§4・§6。dev・管理者限定、既定オフ。

## 目的

利用者の質問を、裏で動く1つの係（ワーカー）が「質問の整理 → ノウハウを読む → 技術資料と法令を同時に検索 → 足りなければ上限内で再検索 → 1つの回答にまとめる」順に処理し、画面は数秒ごとに進捗を取りに行く。骨組みはコードが決め、AI が選ぶのは「足りないときの調べ直し方」だけ（型 B）。

## 有効化の条件

- サーバー: `Environment=dev` かつ SAM パラメータ `SenpaiResearchEnabled=true` のときだけ、テーブル・関数・API 経路を作る。呼び出し者は Cognito の `admin` グループに属すること（それ以外は 403 `FeatureUnavailable`）。
- 画面: `NEXT_PUBLIC_ENABLE_SENPAI_RESEARCH=true` のときだけ、先輩チャットの送信をこのジョブ経由にする。オフなら従来の2レーン表示のまま。

## API（RagApi、Cognito 認可）

### `POST /rag/senpai/research`

要求:

```json
{
  "question": "1〜2000文字",
  "modelType": "AXIEZ | AXIEZ-LINKs | NEXCUBE | メルシティ | メルワイド | エスカレーター（任意）",
  "senpaiConversationId": "UUID",
  "senpaiTurnId": "UUID",
  "clientRequestId": "UUID（二重送信防止）"
}
```

応答 `202`: `{ "jobId": "UUID", "status": "queued", "pollAfterMs": 1500 }`

- 同じ `clientRequestId` の再送は同じ `jobId` を返す（`status` は現在の状態）。先行受付の要求予約だけがありジョブ行がまだ無い間は、予約を消さず409 `RequestInProgress` を返す。予約の60秒リースを過ぎてもジョブ行が無い場合だけ、条件付きで新しい受付へ引き継ぐ。並行する受付が互いの予約を削除して二重起動しないようにする。
- 1人1件まで同時実行（実行中は 409 `JobInProgress`）。1人1日の上限は SAM パラメータ `SenpaiResearchDailyLimit`（既定 20。超過は 429 `DailyLimitExceeded`）。
- `userId` は JWT の `sub` のみ。要求本文から受け取らない。

#### 日次枠の扱い（返却ポリシー）

- 受付で 1 回分を消費する。**システム起因で `failed` になったジョブは、1 回だけ返す**（`Timeout`・`BudgetExceeded`・`Internal`・`QuestionUnavailable`、起動失敗 `StartFailed`）。返す先は枠を取った日（JST）の枠で、日付を跨いでも翌日の枠は減らない。
- `completed` は `kind` が `answer` / `clarify` / `not_found` のどれでも消費したままにする（調査は実行されたため）。
- 期限切れ（リース切れ）でポーリングが `Timeout` にしたジョブも同じ規則で 1 回だけ返す。

#### エラー応答（統一形式 `{ "error": "<code>", "message": "日本語" }`）

| HTTP | `error` | 条件 |
| --- | --- | --- |
| 400 | `ValidationError` | 本文・`afterSeq` が不正（未知のキー、UUID でない ID、質問が空または 2000 文字超、未知の機種キー） |
| 401 | `Unauthorized` | JWT に `sub` が無い |
| 403 | `FeatureUnavailable` | 本番・無効時・`admin` グループ外（DB・ワーカーに触れる前に返す） |
| 404 | `JobNotFound` | 他人のジョブ・存在しないジョブ・UUID でない `jobId`（区別しない） |
| 405 | `MethodNotAllowed` | POST / GET 以外 |
| 409 | `JobInProgress` | 同じ人の調査が実行中 |
| 409 | `RequestInProgress` | 同じ要求の受付が進行中でジョブ行の作成を待っている |
| 429 | `DailyLimitExceeded` | 1 日の上限 |
| 500 | `InternalError` | 想定外の失敗（必須の環境変数の欠落を含む。スタックトレースは返さない） |
| 502 | `StartFailed` | ワーカーを起動できなかった（枠・ロックは戻す） |

#### リース（ジョブとロックの有効期限）

進行中ジョブとロックの有効秒数は 300 秒（`SENPAI_RESEARCH_JOB_TTL_SECONDS`）。非同期起動の最大待ち 120 秒 + ワーカーの Timeout 120 秒以上にする。期限を過ぎたジョブは開始も完了もできず（ワーカーは `lost_lease` をログに出して止まり、履歴にも保存しない）、次のポーリングで `Timeout` になる。

要求予約には60秒の回復リースを付ける（受付 Lambda のタイムアウト15秒より長い）。ジョブ行が無い状態で重複要求を受けても新しい予約を作らず、リース満了後に限り前の `jobId` を条件に予約を置き換える。完了結果はジョブの7日TTLが過ぎた時点で、DynamoDBの物理削除を待たずAPIから返さない。

### `GET /rag/senpai/research/{jobId}?afterSeq=<int>`

本人のジョブだけ返す（他人・存在しないものは 404）。

```json
{
  "jobId": "UUID",
  "status": "queued | running | completed | failed",
  "steps": [ /* afterSeq より大きい seq の段階イベント（下記） */ ],
  "pollAfterMs": 1500,
  "result": { /* status=completed のときだけ（下記） */ },
  "error": { "code": "Timeout | BudgetExceeded | Internal | QuestionUnavailable", "message": "日本語" },
  "debug": { /* admin のときだけ（下記） */ }
}
```

## 段階イベント（`steps[]`）

ワーカーが各段階の**実行前後にコードで**追記する（モデルの文章から作らない）。追記専用、`seq` は 1 から単調増加。

```json
{
  "seq": 3,
  "step": "understand | knowhow | tech_search | law_search | sufficiency | retry_search | doc_page | clarify | synthesize | verify",
  "labelJa": "質問を整理中 | ノウハウを確認中 | 技術資料を検索中 | 法令を確認中 | 足りない点を確認中 | 言い換えて再検索中 | 資料のページを確認中 | 確認が必要な点を整理中 | 回答をまとめています | 根拠を照合中",
  "detailJa": "任意。例: 「『LINKs ドア 開閉 異音』で検索」（120文字まで、本人にだけ返す）",
  "status": "running | done | skipped | failed",
  "counts": { "hits": 8, "selected": 4, "documents": 3 },
  "startedAt": "ISO8601",
  "endedAt": "ISO8601 | null"
}
```

画面は `labelJa` と `detailJa` だけを表示し、生の思考は表示しない。

## 結果（`result`）

```json
{
  "kind": "answer | clarify | not_found",
  "answerMarkdown": "結論先行の回答（Markdown の文字列。見出しは ## 結論 / ## 根拠と手順 / ## 確認が必要な点（無ければ省く））。本文中の根拠は [T1] [L2] [K1] の形",
  "clarifyQuestions": ["kind=clarify のときの聞き返し"],
  "sources": {
    "tech": [{ "ref": "T1", "title": "資料名", "documentName": "…", "pageNumber": 12, "sourceUri": "s3://…（既存の /rag/document で開く）" }],
    "law": [{ "ref": "L1", "lawTitle": "…", "provision": "第◯条", "effectiveDate": "…", "sourceUrl": "e-Gov URL（既存の法令出典と同じ扱い）" }],
    "knowhow": {
      "used": [{ "ref": "K1", "knowledgeId": "KH-…", "cardVersion": 2, "title": "…", "status": "draft", "modelFit": "matched | general | other_product | unknown" }],
      "candidates": [{ "knowledgeId": "KH-…", "cardVersion": 1, "title": "…" }]
    }
  },
  "understanding": {
    "modelType": "UIキー | null（質問から根拠をもって読めた場合だけ）",
    "controlMethod": "VFGLF 等 | null",
    "part": "…|null", "symptom": "…|null", "situation": "…|null",
    "intent": "procedure | cause | spec_value | legal | other",
    "lawRelevant": true
  },
  "unverifiedRefs": ["回答に現れたが取得結果に無かった参照（照合で除去したもの）"],
  "stopReason": "sufficient | budget | no_new_results | clarify",
  "warnings": ["任意。検索に失敗した道具があるときだけ付く日本語の注意。例: 法令の検索に失敗したため、法令の根拠は含まれていません。"]
}
```

- **回答の形（`answerMarkdown`。型は文字列のまま、見出しは固定）**: 経験のある先輩技術者が同僚に答える自然な です・ます 調で、出典を順に並べずに 1 つの筋道へ統合する。質問の整理結果（機種・制御方式・部位・症状・状況・意図）をまとめに渡し、その状況に合わせて書く。意図ごとの形は、原因＝可能性の高い順（見分け方と対処つき）、手順＝全体像のあと番号付き手順、数値＝値と適用条件、法令＝要件・条文・実務の判断点。
  - `## 結論`: 質問への答えを 2〜4 文で直接。確実でないときは有力な答えと確定のための確認を言い切る。
  - `## 根拠と手順`: 短い段落 1〜3 つ、または番号付きの手順 2〜8 項目。1 項目 1 事実の箇条書きにはしない。ノウハウは「現場の事例では…」と自然に書いて `[K#]` を付ける（文ごとの「未承認」表記はしない。画面が `[K#]` を未承認として示す）。
  - `## 確認が必要な点`: 資料に無い点・食い違い・答えが変わる条件だけを箇条書き。無ければ見出しごと省く。
  - 参照は、支える文の文末に `[T1][L1]` の形でまとめる。事実を述べる文には必ず参照を付ける。
  - 時間切れの代替回答も同じ見出しで、`## 結論` は「時間の上限に達したため、確認できた資料を示します。」、`## 根拠と手順` は資料の一覧（参照つき）。聞き返し（`kind=clarify`）と見つからない（`kind=not_found`）は従来の定型文で、この見出しは使わない。
- `used` は回答本文で実際に引用されたカード。`candidates` は渡したが引用されなかったカード。どれも引用されなければ `used` は空配列で、画面はノウハウの行を出さない（`candidates` は開発者表示だけ）。
- **画面の出し方**: 回答は技術資料・法令・ノウハウを1本にまとめたもの。「結論」「根拠と手順」「確認が必要な点」を含む回答本文は表示し、出典一覧（技術資料・法令・使ったノウハウ）だけを回答の下の閉じた開閉「根拠と出典（技術資料 n・法令 n・ノウハウ n）」に入れる。本文の番号（技1・法1・ノ1）を押すと開閉が開き、該当の出典の行へ移動する。「## 結論」などの見出しが無い回答は本文をそのまま出し、開閉は「出典（…）」になる。聞き返しの本文は畳まない。
- 回答本文の `[T*]` `[L*]` `[K*]` は、ワーカーが**取得結果に実在する参照だけを残す**（実在しない参照は本文から外し `unverifiedRefs` に記録）。`[T1, T2]`・全角・隅付き括弧（`［Ｔ１］` `【T1】`）は個別に検証し、`[T1][T2]` の標準形に直す。`T01` のような先頭ゼロは別物（未検証）。
- **検証できた参照が 1 つも無い回答は出さない**。まとめが参照を付けなかった、または付けた参照がすべて実在しなかったときは、再生成せずに `kind=not_found` とし、`answerMarkdown` に「回答に根拠となる資料の参照を付けられなかったため、回答を表示しません」の定型文を入れる（`unverifiedRefs` は記録。`stopReason` は元の理由のまま）。
- **法令関連質問は法令根拠を必須にする**。整理結果の `lawRelevant=true` で、検索・再検索の後も法令資料が1件も無い場合は、技術資料・ノウハウだけで回答を生成せず、まとめ・照合を省略して `kind=not_found` とする。法令検索の失敗と根拠なしを区別せず、法令を確認できなかった旨を返す。
- 回答本文から**リンク・画像・生の URL は除く**（Markdown のリンクは文字だけ残し、`[T1](…)` は `[T1]` にする）。出典は `sources` の参照でだけ示す。
- **時間切れ**: まとめを呼ぶ残り時間（8 秒）が無いとき、または残り時間が足りずモデルを呼べなかったときは、まとめを省略（段階 `synthesize` は `skipped` または `failed`）し、見つかった資料の一覧（参照つき・推測なし）を `kind=answer`・`stopReason=budget` で返す。
- **`warnings`（任意項目）**: 技術資料・法令のどちらかの検索が失敗したときだけ付く（無いときはキーごと無い）。法令根拠を得られない法令関連質問は回答を保留し、警告も結果に付ける。画面の検証は、このキーが無くても有っても通ること。

## 開発者向け（`debug`、admin のみ）

```json
{
  "understandingRaw": { /* 整理結果の全項目 */ },
  "queries": { "tech": ["…"], "law": ["…"], "knowhow": "…" },
  "tools": [{ "seq": 4, "tool": "tech_search", "query": "…", "filters": { "modelType": "…" }, "hits": 30, "selected": 6, "topScores": [0.61, 0.55], "ms": 1830 }],
  "budget": { "searchesUsed": 4, "searchesMax": 6, "modelCallsUsed": 3, "modelCallsMax": 4, "elapsedMs": 21500, "elapsedMaxMs": 60000 }
}
```

`queries` には元の質問の文そのもの（元の文での検索）とモデルが整理した言い換えが入る。管理者にだけ返し、ジョブ行の TTL（7 日）で消える。CloudWatch には出さない。

## ワーカーの手順と上限（初期値。SAM パラメータで変更可）

0. **質問の整理（LLM 1回、小さいモデル）**: 上記 `understanding` と、道具ごとの検索語（技術・法令・ノウハウ）、足りない情報を JSON で出させ、コードで検証する。失敗時は元の質問をそのまま使う。**元の質問は常に残し、検索は元の文と整理した検索語の両方で行う。** 機種は根拠なく補わない。画面で機種が選ばれていればそれを優先する。
1. **ノウハウ**: 既存の `knowhow_retrieval`（字句・LLM なし）。機種フィルタと `modelFit` は既存の規則。
2. **技術・法令を同時に**: 既存の RAG の検索・選別（`retrieve_for_normal_query`・`select_retrieval_results`・法令の検索と全文補強）を再利用する。生成はしない。カードの出典の資料番号は検索語の補助に使う。法令に関係しないと整理された質問では法令検索を `skipped` にする。
3. **十分性（LLM 1回）**: 十分なら 4 へ。不足なら、`retry_search`（言い換え・機種条件の変更）、`doc_page`（原資料ページ）、`clarify`（利用者へ質問して終了）から選ぶ。追加の検索は最大2回。同じ検索語・同じ結果は拒否。新しい資料が増えない往復が続いたら打ち切る。
4. **まとめ（LLM 1回）**: 主張に `[T*][L*][K*]` を付けさせ、5 で照合。
5. **照合（コード）**: 実在しない参照を除去。

上限: 検索系 合計6回、モデル呼び出し 合計4回、ジョブ全体 60 秒（超過は確認できた範囲で答えて `stopReason=budget`）、ワーカー Lambda のタイムアウトは余裕を見て 120 秒。

**時間予算は待ち時間そのものを縛る**。柔らかい上限（60 秒）を過ぎたら追加の検索・判断は始めない。さらに、すべての KB 検索とモデル呼び出しは「硬い上限 = 予算 60 秒 + まとめ用 20 秒（Lambda の残り時間 - 10 秒を超えない）」までの残りに収まる読み取り待ちで呼ぶ（KB 検索 1 回は最大 12 秒・再試行 1 回、モデル 1 呼び出しは最大 40 秒で、余裕が 20 秒以上のときだけ半分にして 1 回再試行）。残りが足りない検索・モデル呼び出しは呼ばずに失敗として扱い、まとめの前に残りが 8 秒を切っていれば資料の一覧で返す。

## 保存とログ

- ジョブ表 `senpai-research-jobs-<env>`（TTL 7日）。段階イベントはジョブ表に保存。
- 完了した回答は ChatLogs に `ragMode=senpai_research`、既存の先輩タグ（`senpaiConversationId`/`senpaiTurnId`）付きの assistant 行として保存（TTL 60日）。相談履歴から開き直すと回答・出典を復元する（段階イベントは復元しない）。通常の `/chat` 履歴には出さない。
- 完了した回答の保存は、ジョブ行を `completed` にできた**後**にだけ行う（期限切れで失敗にされたジョブの回答は履歴に残さない）。
- CloudWatch には `jobId`（UUID）・段階名・件数・時間・終了理由・エラー種別だけを出す。質問・検索語・本文・回答・`userId` は出さない。ワーカーは `job_started` と `job_finished`（`status` は `completed` / `failed` / `lost_lease`）を対で出し、片方だけの `jobId` は異常（強制終了など）として検知できる。

## 2026-10-23のクラウド技術確認

> 最終検証: 2026-10-23 — 本節の検証記録リンクだけを追加。既存契約全体の検証日は据え置き。

[関連280テスト・SAM静的検証と未統合差分](verification-2026-10-23-senpai-cloud-review.md)を参照。itaiの未push修正と二段階承認は未統合で、実モデル・AWS・Windowsの受入ではない。
