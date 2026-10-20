---
status: draft
last-verified: 2026-10-20
related-code:
  - lambda/rag/rag-function/senpai_research_*.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/lib/knowledge-senpai-research.mjs
  - frontend/src/components/knowledge/KnowledgeSenpaiChat.tsx
---

# 工技先輩の調査ジョブ（試作）: API と段階イベントの契約

> 最終検証: 2026-10-20 — 実装前の契約。根拠は [調査](../../survey-2026-10-20-senpai-agentic-search.md) §2・§4・§6。dev・管理者限定、既定オフ。

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

- 同じ `clientRequestId` の再送は同じ `jobId` を返す。
- 1人1件まで同時実行（実行中は 409 `JobInProgress`）。1人1日の上限は SAM パラメータ `SenpaiResearchDailyLimit`（既定 20。超過は 429 `DailyLimitExceeded`）。
- `userId` は JWT の `sub` のみ。要求本文から受け取らない。

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
  "answerMarkdown": "統一回答（見出し: 結論の候補 / 技術資料から / 法令から / ノウハウ（未承認・参考） / 食い違い・不足 / 次に確認すること）。本文中の根拠は [T1] [L2] [K1] の形",
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
  "stopReason": "sufficient | budget | no_new_results | clarify"
}
```

- `used` は回答本文で実際に引用されたカード。`candidates` は渡したが引用されなかったカード。どれも引用されなければ `used` は空配列で、画面は「ノウハウは参照していません」と表示する。
- 回答本文の `[T*]` `[L*]` `[K*]` は、ワーカーが**取得結果に実在する参照だけを残す**（実在しない参照は本文から外し `unverifiedRefs` に記録）。

## 開発者向け（`debug`、admin のみ）

```json
{
  "understandingRaw": { /* 整理結果の全項目 */ },
  "queries": { "tech": ["…"], "law": ["…"], "knowhow": "…" },
  "tools": [{ "seq": 4, "tool": "tech_search", "query": "…", "filters": { "modelType": "…" }, "hits": 30, "selected": 6, "topScores": [0.61, 0.55], "ms": 1830 }],
  "budget": { "searchesUsed": 4, "searchesMax": 6, "modelCallsUsed": 3, "modelCallsMax": 4, "elapsedMs": 21500, "elapsedMaxMs": 60000 }
}
```

## ワーカーの手順と上限（初期値。SAM パラメータで変更可）

0. **質問の整理（LLM 1回、小さいモデル）**: 上記 `understanding` と、道具ごとの検索語（技術・法令・ノウハウ）、足りない情報を JSON で出させ、コードで検証する。失敗時は元の質問をそのまま使う。**元の質問は常に残し、検索は元の文と整理した検索語の両方で行う。** 機種は根拠なく補わない。画面で機種が選ばれていればそれを優先する。
1. **ノウハウ**: 既存の `knowhow_retrieval`（字句・LLM なし）。機種フィルタと `modelFit` は既存の規則。
2. **技術・法令を同時に**: 既存の RAG の検索・選別（`retrieve_for_normal_query`・`select_retrieval_results`・法令の検索と全文補強）を再利用する。生成はしない。カードの出典の資料番号は検索語の補助に使う。法令に関係しないと整理された質問では法令検索を `skipped` にする。
3. **十分性（LLM 1回）**: 十分なら 4 へ。不足なら、`retry_search`（言い換え・機種条件の変更）、`doc_page`（原資料ページ）、`clarify`（利用者へ質問して終了）から選ぶ。追加の検索は最大2回。同じ検索語・同じ結果は拒否。新しい資料が増えない往復が続いたら打ち切る。
4. **まとめ（LLM 1回）**: 主張に `[T*][L*][K*]` を付けさせ、5 で照合。
5. **照合（コード）**: 実在しない参照を除去。

上限: 検索系 合計6回、モデル呼び出し 合計4回、ジョブ全体 60 秒（超過は確認できた範囲で答えて `stopReason=budget`）、ワーカー Lambda のタイムアウトは余裕を見て 120 秒。

## 保存とログ

- ジョブ表 `senpai-research-jobs-<env>`（TTL 7日）。段階イベントはジョブ表に保存。
- 完了した回答は ChatLogs に `ragMode=senpai_research`、既存の先輩タグ（`senpaiConversationId`/`senpaiTurnId`）付きの assistant 行として保存（TTL 60日）。相談履歴から開き直すと回答・出典を復元する（段階イベントは復元しない）。通常の `/chat` 履歴には出さない。
- CloudWatch には段階名・件数・時間・終了理由・エラー種別だけを出す。質問・検索語・本文・回答は出さない。
