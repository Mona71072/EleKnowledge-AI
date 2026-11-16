---
status: development
last-verified: 2026-11-14
related-code:
  - lambda/rag/knowhow-rewrite/app.py
  - lambda/rag/knowhow-rewrite/rewrite_input.py
  - lambda/rag/knowhow-rewrite/rewrite_prompt.py
  - lambda/rag/knowhow-rewrite/rewrite_model.py
  - lambda/rag/knowhow-rewrite/rewrite_validate.py
  - lambda/rag/knowhow-rewrite/rewrite_tokens.py
  - infrastructure/sam/phase2-template.yaml
  - tests/unit/test_knowhow_rewrite.py
  - tests/fixtures/knowhow-rewrite/contract.json
  - frontend/src/lib/knowhow-card-check-text.mjs
---

# ノウハウカード本文の書き換え案 API 契約

> 最終検証: 2026-11-14 — 単体テスト（レビュー指摘の検証すり抜けを直した後の版を含む）（`tests/unit/test_knowhow_rewrite.py`）と SAM テンプレートの静的検査。Bedrock の実出力・AWS 実機は未確認

## 目的と方針

管理者が確認済みの根拠（KB の照合結果のうち、管理者が「確認して追記する」を選んだもの）だけを材料に、AI がカード本文の対象の節の書き換え案を作る。管理者は画面で差分を見て確認するだけにする。

* AI の結果をそのままカードに入れない。この API は案を返すだけで、保存しない
* モデルの出力は信用せず、サーバー側で検証してから返す
* 開発環境（`ENVIRONMENT=dev`）・管理者のみ・既定オフ。通常の書き換えは `KnowhowRewriteEnabled`、`field` レーンは追加で `KnowhowFieldMaterialEnabled`（既定 `false`）を必要とする

## エンドポイント

`POST /rag/knowhow/rewrite-proposal`（RagApi。オーソライザー・CORS・WAF は RagApi のものを継承）。

* SAM パラメータ `KnowhowRewriteEnabled`（既定 `'false'`）と Condition `KnowhowRewriteDevEnabled`（dev かつ true）で、関数・ロール・経路を条件付きで作る。`KnowhowFieldMaterialEnabled`（既定 `'false'`）は既存経路の `field` レーンだけを別途許可する。フロント設定 `NEXT_PUBLIC_ENABLE_KNOWHOW_FIELD_MATERIAL=true` と両方を有効にする
* 認可は JWT の claims のみ。`sub` と `cognito:groups`（文字列でも配列でも可）を使い、`ADMIN_GROUP_NAME` に入っている管理者だけ通す。ユーザー ID は本文から取らない

## 要求

正本は `tests/fixtures/knowhow-rewrite/contract.json`。未知のキーは 400。

| 項目 | 規則 |
| --- | --- |
| 本文全体 | 256 KiB（262,144 バイト）以下。超えたら 413 |
| `knowledgeId` | `^KH-[A-Z0-9-]{1,80}$` |
| `cardVersion` | 整数 1〜9999 |
| `targets` | 1〜3 件。`heading` は「統合した回答・ノウハウ」「調査・確認手順」「未確認事項」のみ・重複不可。`body` は各 2,000 字以下、合計 4,000 字以下 |
| `context`（省略可） | 0〜8 件。`heading`（非空・200 字以下）と `body`（各 4,000 字以下、合計 16,000 字以下） |
| `evidence` | 通常レーンは 1〜12 件。`question` 2,000 字以下・`lane`（`technical` か `law`）・`checkedOn`（実在する `YYYY-MM-DD`）・`answer` 2,000 字以下・`sources`（省略可、0〜8 件）。`field` レーンは下記の専用形のみ |
| `sources[]` | `title` 200 字以下、`page`（省略可）1〜9999 の整数 |

### 現場資料の限定レーン（`field`）

> 最終検証: 2026-11-14 — `tests/unit/test_knowhow_rewrite.py` の合成入力テストと SAM テンプレート静的検査。Bedrock 実出力・AWS 実機は未確認

管理者が確認し、利用を許可した現場資料の抜粋を、非公式な観察知として文章化するための任意レーン。`knowledgeId` と `cardVersion` は `KH-FIELD-MATERIAL` と `1` に固定した API エンベロープ互換値で、実在カードの ID・版ではない。既存カードの存在確認・本文取得は行わない。

サーバーは `field` リクエストを以下の形に限定し、他レーンとの混在や追加の入力を拒否する。

* `evidence` は1件のみ。`lane` は `field`、`question` は人が付けたトピック（空白のみ不可、2,000 字以下）、`answer` は利用許可済み抜粋そのもの（空白のみ不可、2,000 字以下）、`checkedOn` は実在する日付
* `sources` は1件のみで、`title` に非空の資料名を入れる。URL と `page` は受け付けない
* `targets` は `[{"heading":"統合した回答・ノウハウ","body":""}]` のみ。`context` は空配列のみ
* 見出し・本文・参考節など、上記以外のカード由来テキストを送らない

このレーンの提案は非公式な観察知として扱う。抜粋に書かれた条件と不確実性を維持し、公式要件・安全要件を追加したり、抜粋にない結論を推論したりしない。資料データに含まれる指示、URL、リンク、行動要求を提案へ転記・実行しない。従来の `technical` / `law` レーンの入力・画面・認可条件は変更しない。

値の裏付けは `answer` の抜粋だけから行う。`question`・`checkedOn`・`sources[].title` はトピックや出典の表示用で、数値・資料番号の根拠にはしない。単位のない2桁以上または小数の数字に `answer` 内の裏付けがない場合も、通常レーンの警告扱いではなく `unverified_number` で節を `rejected` にする。

根拠の番号は `evidence` 配列の 1 始まり。`knowledgeId` と `cardVersion` はそのまま応答に写すだけで、モデルには渡さない。

## 応答

```json
{
  "knowledgeId": "KH-...",
  "cardVersion": 1,
  "sections": [
    { "heading": "統合した回答・ノウハウ", "status": "unchanged" },
    { "heading": "未確認事項", "status": "changed", "body": "...", "reason": "...", "evidence": [1], "warnings": [] },
    { "heading": "調査・確認手順", "status": "rejected", "warnings": [{ "code": "unsupported_value", "tokens": ["700 mm"] }] }
  ],
  "conflicts": [{ "heading": "未確認事項", "summary": "...", "evidence": [1] }]
}
```

* `sections` は要求の `targets` と同じ順・同じ見出し。モデルが返さなかった節は `unchanged` で補う
* `unchanged` と `rejected` は `body` を返さない。`rejected` は `warnings` に理由を持つ
* `changed` は `body`（新しい本文の全体）・`reason`（300 字まで）・`evidence`（使った根拠の番号、昇順・重複なし）・`warnings` を持つ
* `warnings[]` は `{code, tokens?}`。`tokens` は新しい本文に出てきた該当の値（NFKC 正規化後の文字列、出現順・重複なし）
* `conflicts[]` は `{heading, summary, evidence}`。`heading` は対象の節に紐づかないとき `null`、`summary` は 200 字まで、最大 10 件。食い違いがある節の本文はモデルに変えさせない

| 警告コード | 意味 | status |
| --- | --- | --- |
| `unsupported_value` | 資料番号・法令番号・単位つき数量（数字＋単位らしきもの）が、元の節・他の対象・参考の節・根拠のどこにも無い（`tokens` あり） | rejected |
| `missing_evidence` | `changed` なのに有効な根拠番号が無い | rejected |
| `heading_in_body` | 本文にコードフェンス外の `## ` 見出し行、`---` / `===` だけの行（setext 見出し・区切り線）、先頭の `---` がある | rejected |
| `unclosed_fence` | コードフェンスが閉じていない（後続の節を飲み込む） | rejected |
| `suspicious_text` | 本文に書式文字（ゼロ幅・双方向制御・BOM）、孤立サロゲート、制御文字（改行・復帰・タブ以外）がある | rejected |
| `link_or_html` | 元の節に無い URL（`http(s)://`・`www.`）、Markdown のリンク・画像、HTML タグ、`javascript:` 等のスキームがある | rejected |
| `too_long` | 新しい本文が 4,000 字を超える | rejected |
| `empty_body` | `changed` なのに本文が空 | rejected |
| `unverified_number` | 単位の続かない 2 桁以上（または小数）の数字が、同じ範囲に無い（`tokens` あり） | 通常レーンは changed のまま警告。`field` レーンは rejected |

契約 JSON の `warningCodes` に無いコード（`suspicious_text`・`link_or_html`・`unclosed_fence`・`empty_body`）がある。フロントは未知のコードを汎用表示する。

## エラー

形式は `{error, message}`。

| status | error | 条件 |
| --- | --- | --- |
| 400 | ValidationError | JSON 不正、未知のキー、上限・形式の違反、UTF-8 にできない文字（孤立サロゲート）や制御文字（改行・復帰・タブ以外）を含む文字列 |
| 401 | Unauthorized | `sub` が無い |
| 403 | FeatureUnavailable | dev 以外、通常機能フラグがオフ、管理者以外。`field` レーンは追加フラグ `KnowhowFieldMaterialEnabled` が `true` でない場合も拒否 |
| 405 | MethodNotAllowed | POST 以外（OPTIONS を除く） |
| 413 | PayloadTooLarge | 本文が 256 KiB を超える |
| 429 | RewriteThrottled | Bedrock のスロットリング |
| 502 | RewriteFailed | 応答が空、JSON として読めない、型やキーの違反、節の重複、`stop_reason` が `refusal` など正常終了（`end_turn`・`stop_sequence`・空）以外 |
| 502 | RewriteTruncated | `max_tokens` で打ち切られた |
| 504 | RewriteTimeout | Bedrock の読み取り待ち超過 |
| 500 | InternalError | その他。例外の本文は返さない |

## サーバー側の検証規則（モデル出力）

1. 打ち切り（`stop_reason` が `max_tokens` など）は、JSON として読めても 502 `RewriteTruncated`。空応答は 502 `RewriteFailed`
2. JSON の取り出しは、全体、または最初の `{` から最後の `}` まで。コードフェンスや前置きは許す。許可するキー以外は捨てる
3. `sections[].heading` は要求の `targets` と完全一致のものだけ使い、要求に無い節は捨てる。同じ見出しの重複は 502
4. `evidence` の番号は 1〜n の整数だけ残す（範囲外・非整数は除く）。`changed` で残りが空なら `rejected`（`missing_evidence`）
5. 新しい本文が元と同じ（空白の正規化後）なら `unchanged`
6. 本文の構造: 見出し行（行頭 0〜3 個の空白を許す `## `）、`---` / `===` だけの行、先頭の `---`、閉じていないコードフェンスは `rejected`。コードフェンス（` ``` ` / `~~~`。開いたときと同じ記号・同じ長さ以上で閉じる）の中は見出しとして扱わない。判定はフロントの `findRewriteBodyProblem`（`knowhow-rewrite-sections.mjs`）に揃えてある。4,000 字超と空も `rejected`
7. 文字: 新しい本文に書式文字（Unicode の Cf: ゼロ幅・双方向制御・BOM）、サロゲート、制御文字（改行・復帰・タブ以外）があれば `rejected`（`suspicious_text`）
8. リンク・HTML: 新しい本文の URL・Markdown リンク・画像・HTML タグ・スキームのうち、元の節に無い（文字列が一致しない）ものが 1 つでもあれば `rejected`（`link_or_html`）。元の節に同じものがあるときだけ通す。`reason` と `conflicts[].summary` は、リンク・HTML・書式文字を含むと空にする（conflict は除く）
9. 数量の裏付け: 新しい本文から資料番号（`SUE-3-17`、`S-EL-323.1`、`Q-3786`）・法令や条番号（`告示 1455`、`JIS3525`、`29 条`）・数量を拾う（`knowhow-card-check-text.mjs` の正規表現を土台に、より厳しくした）。数量は「数字＋単位らしきもの」で、単位の種類は問わない（英字 1〜4 字、`%`・`°C`・`Ω` など、`ミリ`・`センチ`・`秒`・`分`・`度`・`回`・`個`・`本`・`階` などの語、漢数字＋単位の `六百mm`・`三回`）。1 桁の数字も、単位が続けば数量として検査する。符号つき（`-50 mm`・`±5 mm`）は符号込みで拾う。英字が前に付く `H1200mm`・`ABC900mm` も数字と単位の部分を拾う
   * 照合の前に、NFKC 正規化、書式文字の除去、桁区切りのカンマの除去（`1,600 mm` と `1，600 mm` は `1600 mm`）、空白除去、大小文字統一を行う。Markdown の強調記号（`*` `_` `` ` `` `~~`）を除いた文字列でも検査する（`**600** cm` は `600 cm`）。`６００ｍｍ` と `600 mm` は同じ値
   * 通常レーンでは、元のその節・他の `targets`・`context`・根拠（`question`・`answer`・`sources[].title`）・確認日（`checkedOn`）のどこにも無い値が 1 つでもあれば `rejected`（`unsupported_value`）。契約の応答例が本文に確認日を書くため、通常レーンでは `checkedOn` を範囲に含める。`field` レーンは利用許可済み抜粋の `answer` だけを裏付け範囲とし、トピック・出典名・確認日・空の対象本文を根拠に使わない
   * 誤検出を避ける規則: 行頭の番号付き箇条書き（`1.` `2.` `10.`）は数字として扱わない。通常レーンでは日付 `2026-11-14` を確認日の数字で裏付けできる。`十分に` は数量にしない。単位の無い 1 桁の数字は検査しない。元の本文と同じ数量・同じ URL を保った書き換えは通る
10. 単位の続かない 2 桁以上（または小数）の数字が同じ範囲に無ければ、通常レーンでは `changed` のまま警告（`unverified_number`）、`field` レーンでは `rejected`（同コード）
11. 正規表現は 2,000 字ごとの区切り（行内）に当て、入れ子の量指定を避ける。病的な入力（長い数字列・記号・カンマ・括弧の連続）で 1 秒以内に終わることをテストで確認している

## モデル呼び出し

* 命令は system だけ。カード（`targets`・`context`）と根拠は user メッセージ内の JSON ブロックに入れ、`<` `>` `&` を `<` `>` `&` にエスケープする（`rag-function/knowhow_answer.py` の `_cards_block` と同じ流儀）
* モデル ID は環境変数 `BEDROCK_MODEL_ID`（SAM の `BedrockModelId`）。ハードコードしない
* 1 リクエストで Bedrock は 1 回だけ。読み取り待ち `BEDROCK_READ_TIMEOUT` 既定 24 秒（上限 27 秒）、接続 3 秒、再試行なし。`max_tokens` は `KNOWHOW_REWRITE_MAX_TOKENS` 既定 4,096
* Lambda ごとに別々に配備するため、`rag-function` や `senpai-synthesis` を import せず、`synthesis_model.py` と同じ方針の実装を持つ

## ログに出すもの・出さないもの

構造化 JSON（`event: knowhow_rewrite`）。出すのは `stage`・`status`・`errorClass`（型名）・`durationMs`・`modelId`・`inputTokens`・`outputTokens`・`targetCount`・`evidenceCount`・`changedCount`・`rejectedCount`・`conflictCount` だけ。

本文・質問・回答・`knowledgeId`・`sub`・警告の `tokens`・例外の本文は出さない（テストで確認）。

## 保存しないこと

DynamoDB・S3 に一切書かない。IAM ロールにも付けない（`bedrock:InvokeModel` だけ）。結果は呼び出した管理者の編集欄に戻るだけで、管理者が確認して採用したときの保存は既存のカード編集の経路が担う。

## 限界

* 根拠はブラウザーが送る。サーバーは、その根拠が KB 由来かどうかを検証できない。管理者が改ざんした根拠でも通る。この API は管理者のみ・dev のみで、結果は本人の編集欄に戻るだけなので、この範囲で許容している
* `field` の資料名・抜粋が利用許可済み原文かどうかもサーバーでは検証できない。送信側が許可された抜粋をそのまま `answer` に入れる前提であり、サーバーが保証するのは入力形状と上限、結果の表示安全性まで
* 数値の裏付けは文字の一致で、意味の正しさは保証しない。根拠に出てくる数値を別の文脈で使っても通る。管理者の差分確認に依る
* 引用した根拠の番号（`evidence`）が実際にその値を含むかは見ない。裏付けは、全根拠・元の本文・他の節・参考の節の和集合で照合する。別の根拠にある値を、別の根拠の番号で引用しても通る
* 検査の範囲外: 英数字の単位を伴わない裸の 1 桁の数字、`example.com` のような scheme の無いドメイン名、仮名で書いた数（`ろくひゃくミリ`）、漢数字だけで単位が続かない数。単位らしきものの判定は広めで、新しく書いた `5 SW` のような英字の続く数字は落とす（案が出ないだけで害は小さい、という判断）
* 検証できるのは、資料番号・法令番号・単位つき数値・裸の数字だけ。言い回しの変化による意味の変更（「以上」と「以下」の取り違えなど）は検出できない
* 単体テストはモデルをモックしている。モデルの実出力での挙動（JSON 形式の遵守率、`rejected` になる頻度、打ち切りの発生）は未検証
* 正規表現の移植元はフロントの `knowhow-card-check-text.mjs`。フロント側の変更は自動では追従しないので、変更時は両方を見直す
