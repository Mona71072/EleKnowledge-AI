---
status: draft
last-verified: 2026-10-20
related-code:
  - lambda/rag/senpai-field-report/app.py
  - lambda/rag/senpai-field-report/field_report_store.py
  - lambda/rag/senpai-field-report/field_report_vocab.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/lib/knowledge-senpai-field-report.mjs
  - frontend/src/components/knowledge/SenpaiFieldReportForm.tsx
  - frontend/src/components/knowledge/KnowledgeSenpaiChat.tsx
  - scripts/knowledge/build_scope_review_queue.py
---

# 先輩チャット「結果を残す」（現場の報告候補）— 開発メモ

> 開発中・dev 管理者限定。SAM パラメーター `SenpaiFieldReportsEnabled` は既定 `false`。
> 構想は [工技先輩の知識循環](../../concept-2026-10-19-kougi-senpai-knowledge-cycle.md) §5.2・§6・§10「先に試す」。
> 本メモは実装の記録であり、業務スコープ・保存期間の決定記録ではない（§7 の共同確認事項を参照）。

## 1. 目的

改善ループで欠けていた「実際に使った結果」を集め、どのノウハウカードを先に確認・訂正するかを決める材料にする。
集めたものは **観測・報告（未確認の候補）** であり、確認済みノウハウではない。工技先輩の回答・検索には使わない。

## 2. 利用者の操作（フロントエンド）

先輩チャットの各相談（turn）の回答の下に「結果を残す」を置く。押すまでは何も送らない。
表示は `NEXT_PUBLIC_ENABLE_SENPAI_FIELD_REPORTS=true` のときだけ（既定オフ。SAM の `SenpaiFieldReportsEnabled` と合わせて有効化する）。
両方の検索が終わり、少なくとも一方が回答できた相談にだけ表示する。

| 入力 | 必須 | 初期値・制約 |
| --- | --- | --- |
| 何が分かったか | 必須 | 空。最大 500 文字。会話本文は自動で入れない |
| どの条件か | 任意 | 空。最大 300 文字 |
| 機種 | 任意 | その相談で選んだ機種（`turn.modelType`）。UI の 6 機種または「指定しない」 |
| 参照したカードごとの反応 | 任意 | 「この条件で当てはまった／当てはまらなかった／分からない」。未選択はそのカードを送らない |

「内容を確認する」で送信内容を一覧表示し、本人が「この内容で送る」を押したときだけ送信する。
顧客名・個人名・物件名を書かない注意を入力欄の近くに表示する。送信後は「送信済み（未確認）」を表示する。

## 3. サーバー（`POST /rag/senpai/field-reports`）

> 最終検証: 2026-10-21 — エラーコード・保存先テーブル名を lambda/rag/senpai-field-report/app.py・field_report_store.py と infrastructure/sam/phase2-template.yaml に照合（§3 のみ）。

1関数1責任のため、新しい Lambda `senpai-field-report-${Environment}` を置く（既存 chat-management・まとめ Lambda には混ぜない）。

- 利用条件: `ENVIRONMENT=dev` かつ `SENPAI_FIELD_REPORTS_ENABLED=true` かつ Cognito `admin` グループ。それ以外は 403 `FeatureUnavailable`。JWT が無いときは 401 `Unauthorized`。
- `userId` は JWT の `sub` だけを使う。リクエストに `userId` を含めると 400 `ValidationError`。
- 相談の実在と所有の確認: ChatLogs のユーザー GSI（`userId-timestamp-index`、Scan なし）で、その利用者の
  `senpaiConversationId`＋`senpaiTurnId` の行を読む。無ければ 404 `TurnNotFound`。
- カード ID と版は **保存済みの技術KB回答行の `knowhow.matches`** と照合する。回答で参照していないカードは 400 `UnknownCard`、
  版違いは 400 `UnknownCard`。カードの適用範囲の確認状態（`scope_status`）と機種の値は、クライアントではなく保存行から写す。
- 1 相談につき 1 件（`reportId = field-report-<senpaiTurnId>`、条件付き Put）。同じ相談に再送すると既存を返す（冪等）。
  別所有者の行と衝突したら 409 `ReportConflict` で何も返さない。
- 本文は制御文字を除いて保存し、長さ超過は 400 `ValidationError`。保存・読み込みの失敗は 500 `InternalError`。未対応のメソッドは 405 `MethodNotAllowed`。CloudWatch には段階・状態・例外クラスだけを出す（本文・ID・トークンを出さない）。

`GET /rag/senpai/field-reports?senpaiConversationId=<uuid>` は、本人のその相談の報告だけを返す（GSI `userId-createdAt-index`）。
履歴から相談を開き直したときに「送信済み」を表示するために使う。

### 3.1 保存項目（DynamoDB `senpai-field-reports-${Environment}`）

| 項目 | 内容 |
| --- | --- |
| `reportId` (PK) | `field-report-<senpaiTurnId>` |
| `userId` | JWT `sub` |
| `senpaiConversationId` / `senpaiTurnId` | 相談との紐付け |
| `createdAt` | ISO-8601 UTC |
| `finding` / `condition` | 本人が確認した入力 |
| `modelType` | 本人が選んだ機種（UI キー）。未指定は項目なし |
| `turnModelType` | 相談時に選ばれていた機種（保存行の `queryFilters` から） |
| `cardReactions[]` | `knowledgeId`, `cardVersion`, `reaction`, `cardScopeStatus`, `cardProductScope`（保存行から） |
| `reviewState` | `unconfirmed`（未確認）で作成 |
| `ttl` | §4 |

### 3.2 語彙（3 か所で同じ値。`tests/unit/test_senpai_field_report_sync.py` で検査）

- 反応: `matched`（当てはまった）/ `not_matched`（当てはまらなかった）/ `unsure`（分からない）
- 状態: `unconfirmed`（未確認）/ `awaiting_review`（確認待ち）/ `reflected`（反映済み）/ `held_or_rejected`（保留・不採用）
- 機種: `ALL_MODEL_TYPES`（`frontend/src/data/kbModelTypes.ts`）＝ `UI_MODEL_FILTERS` ＝ `MODEL_ALIASES` のキー

## 4. 保存期間（暫定）

構想 §6 は「未確認」の候補を担当者が振り分けることを前提にし、期間は定めていない。暫定で次とする。

| 状態 | TTL |
| --- | --- |
| 未確認（この Lambda が作る唯一の状態） | 作成から `FIELD_REPORT_TTL_DAYS`（既定 180 日）で自動削除 |
| 確認待ち・反映済み・保留/不採用 | 担当者の画面（未実装）で状態を変えるときに TTL を外す／付け直す。採否の理由を残すため |

相談履歴（ChatLogs, 60 日）より長くするのは、現場で試してから結果を残すまでと、担当者の振り分けに時間がかかるため。
報告は会話全文を持たないので、相談履歴が消えても報告だけで意味が分かる最小項目を本人が入力する。

## 5. 改善ループへの接続（キュー）

> 最終検証: 2026-11-14 — 合成報告で、カードの版別集計、現行版の優先、旧集計からの読み込み、識別子・機種・報告内容の扱いを単体テストで確認。

`scripts/knowledge/build_scope_review_queue.py --field-reports <export.json>` で、書き出した報告 JSON（AWS は呼ばない）を
集計し、`knowledge/queues/scope-review/field-reports.json`（カード ID・版ごとの機種別反応件数・最新日付だけ。
本文・利用者 ID・相談 ID は含めない）へ保存してから `QUEUE.md` を作る。CI の鮮度テストはこの集計ファイルから再生成する。

集計は `knowledgeId` と `cardVersion` ごとに反応数・最新日を分ける。現行の `card_version` に一致する版を P0 内で先に表示し、旧版・現行版不明・カードが見つからない報告も版を明記して残す。カードとの機種食い違いは現行版のカード範囲だけで判定し、版を比較できない行は食い違い件数を `—` として示す。旧版・カード欠落などは、記録されたカード版の確認を先に促す。報告版がカードの現行版より大きい場合は「現行より新しい版」と表示する。旧形式の集計は版ごとの内訳を復元できないため、混在合計を「版不明」として一行で残し、旧集計に記録されていた版一覧も参考表示する。報告の機種ラベルは既知の機種語彙だけを集計ファイルに保存する。

`QUEUE.md` の先頭に **P0 現場の報告で確認が必要** を置く。対象は「当てはまらなかった」が 1 件以上、または
報告者の機種がカードの機種と食い違う（カードの機種名がすべて他機種）カード。検証済みカードも対象にする
（現場の報告は確認済みの適用範囲を見直す理由になるため）。現行版の報告は旧版・版不明より先に表示し、その内側は「当てはまらなかった」件数、現行版だけで判定した機種の食い違い件数、
報告総数、ID の順。旧版・版不明・カード欠落も見落とさないように表示する。状態が `unconfirmed` / `awaiting_review` の報告だけを数える。

書き出し JSON は、配列または `{"items": [...]}`。各要素は §3.1 の項目（DynamoDB JSON ではなく通常の JSON）。

## 6. テスト

- `tests/unit/test_senpai_field_report.py`: 利用条件、JWT 由来の userId、他人の相談、参照外カード、版違い、冪等、衝突、TTL、ログに本文が出ないこと、GET の所有者限定。
- `tests/unit/test_senpai_field_report_sync.py`: 反応・状態・機種の語彙が Lambda／フロント／キュー生成で一致。
- `tests/unit/test_scope_review_queue.py`: 書き出し JSON → 版別集計 → P0 の並び、旧集計の版不明表示、検証済みカードの扱い、集計に本文や任意ラベルが残らないこと、実カードでの鮮度。
- `frontend/tests/knowledge-senpai-field-report.test.mjs`: 送信内容の組立（会話本文を含めない、未選択カードは送らない、機種初期値）、HTTP クライアントの検証とエラー文言。

## 7. 共同確認が必要な事項（mona・itai）

実装は既定オフ。dev で有効化する前に次を決め、決定は別の docs PR に記録する。

1. 保存期間（未確認 180 日の暫定）と、確認後の保持方針。
2. 集計 `field-reports.json` をリポジトリへコミットしてよいか（本文・利用者は含まない、カード ID と件数のみ）。
3. 報告の書き出しを誰が・どの手段で行うか（Query のみ。担当者画面での書き出しは未実装）。
4. 試行の利用者範囲（dev 管理者のみで始める）。

## 8. 未実装

担当者の振り分け画面（状態変更・TTL の付け外し・採否理由）、書き出し API、投稿者への反映先表示、OneNote 追記案との接続。
