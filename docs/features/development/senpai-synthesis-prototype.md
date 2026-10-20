---
status: draft
last-verified: 2026-10-20
related-code:
  - lambda/rag/senpai-synthesis/app.py
  - lambda/rag/senpai-synthesis/synthesis_prompt.py
  - lambda/rag/senpai-synthesis/synthesis_model.py
  - lambda/rag/senpai-synthesis/synthesis_store.py
  - lambda/chat/chat-management/app.py
  - infrastructure/sam/phase2-template.yaml
  - frontend/src/lib/knowledge-senpai-synthesis.mjs
  - frontend/src/lib/knowledge-senpai-chat.mjs
  - frontend/src/lib/knowledge-senpai-history.mjs
  - frontend/src/components/knowledge/KnowledgeSenpaiChat.tsx
  - tests/unit/test_senpai_synthesis.py
  - tests/unit/test_senpai_history.py
---

# 工技先輩のまとめ（試作）

dev の先輩チャット（管理者限定）で、同じ質問に対する技術KBの回答と法令KBの回答を、1つの文章に整理する試作。mona 上で動かして感触を確かめるための実装メモであり、仕様の確定ではない。

## 目的と範囲

- 技術KBと法令KBの回答は、これまで画面上で別々に並ぶだけだった。両方を読み比べる手間を減らす。
- まとめは「2つの回答を組み合わせた文章」であり、新しい事実を作らない。確認は各回答の出典で行う。
- 今回やらない: 非同期ジョブ化と利用回数の上限（`docs/design-2026-09-24-rag-two-modes.md` の「じっくりモード」）、まとめ品質の評価、本番や一般利用者への公開。

## 流れ

1. 利用者が先輩チャットで質問する。技術KB・法令KBの回答が保存される（各行に `senpaiConversationId` と `senpaiTurnId` が付く）。
2. 両方の検索が終わり、少なくとも一方が成功したターンに「工技先輩のまとめを作る」ボタンが出る（手動。費用を抑えるため自動では呼ばない）。
3. ブラウザは `POST /rag/senpai/synthesis` へ `{senpaiConversationId, senpaiTurnId}` だけを送る。回答本文はクライアントから受け取らない。
4. Lambda `senpai-synthesis` が、呼び出した本人（JWT の `sub`）の保存済み行だけをユーザー GSI（`userId-timestamp-index`）から読む。Scan はしない。
5. ターンごとに、技術・法令それぞれの最新の assistant 行を選び、Bedrock（`BedrockModelId`）を1回呼ぶ。
6. 結果を assistant 行として ChatLogs に保存し、画面の2つの回答の上に表示する。

## ゲート（この順に判定し、どれかを満たさなければ 403 `FeatureUnavailable`）

1. `ENVIRONMENT == 'dev'`
2. `SENPAI_SYNTHESIS_ENABLED == 'true'`（SAM では `Environment=dev` かつ `SenpaiSynthesisEnabled=true` のときだけ true）
3. 呼び出し者の `cognito:groups` に `admin` が含まれる

続いて、`sub` が無ければ 401、本文が「2つの正規 UUID だけ」でなければ 400 `ValidationError`。`userId` など他のキーは受け付けない。

## 入力とモデルへの渡し方

- 技術KB: 回答本文、資料名とページ（`sourceDocuments` と `pageCandidates` のタイトル・ページ番号）。S3 URI は渡さない。
- 法令KB: 回答本文、法令名・法令番号・条文・施行日。URL は渡さない。
- ノウハウ: 技術KB行に保存された `knowhow.matches` から、ID・版・状態・タイトル・`modelScope`・本文（先頭600文字）を最大8件。「非権威・未承認」と明記したブロックにする。
- すべてユーザーメッセージ内の JSON ブロック（`<` `>` `&` はエスケープ）として渡す。システムプロンプトには指示だけを置き、データ内の指示には従わせない。
- 回答がない・条件確認待ち（`clarify`）・該当なし（`not_found`）の検索先は「回答はありません」と明記して渡し、もう一方だけでまとめる。どちらも使えなければ 422 `NothingToSynthesize`。
- 出力の見出し（固定）: 結論の候補（断定しない）／技術資料から確認できること／法令から確認できること／ノウハウ（未承認・参考）／食い違い・不足／次に確認すること。

## 保存するデータ

| 項目 | 値 |
| --- | --- |
| `messageId` / `sessionId` | `senpai-synthesis-<senpaiTurnId>`（決定的） |
| `ragMode` | `senpai_synthesis` |
| `role` | `assistant` |
| `senpaiConversationId` / `senpaiTurnId` | 元ターンと同じ |
| `ttl` | 60日（他の行と同じ） |
| `synthesisInputs` | `{normal, law, knowhowCount}` |

- 保存は条件付き PutItem（`attribute_not_exists(messageId)`）。2回目以降は再生成せず保存済みを返す。競合に負けた場合は勝った行を読み直して返す。キーが他人の行と衝突した場合は 409 `SynthesisConflict` とし、内容は返さない。
- 日別集計キー（`metricDay` など）は付けない。まとめが回答数などの指標に入らないようにするため。
- 通常の `/chat` 履歴一覧には出ない（先輩タグ付きの行は一覧から除外される。テストあり）。先輩チャットの履歴詳細では、同じターンの `turn.synthesis = {status:'success', content, messageId, inputs?}` として復元される。古い履歴（まとめなし）はそのまま開ける。

## 上限とエラー

- 入力は合計約24,000文字に収める（超えると回答本文・ノウハウ本文を短くし、なお超えればノウハウを外す）。出力は `max_tokens` 2048（環境変数、256〜4096）。
- Bedrock の読み取り待ちは22秒（環境変数 `BEDROCK_READ_TIMEOUT`、上限27秒）、再試行なし。Lambda のタイムアウトは60秒。API Gateway は29秒で切れるため、遅い場合は 504 `SynthesisTimeout`。
- ブラウザ側は35秒で打ち切る。失敗時の画面文言は固定文で、サーバーの詳細は出さない。
- エラー形式は既存の RAG と同じ `{error, message}`。スタックトレースは返さない。
- CloudWatch Logs には `stage` と `status`、例外クラス名だけを構造化して出す。回答本文・質問・ID・トークンは出さない。

## SAM のデプロイ設定（デプロイは itai が行う）

`infrastructure/sam/phase2-template.yaml`

- パラメーター `SenpaiSynthesisEnabled`（既定 `false`）。dev で試すときだけ `true` にする。関数・IAMロール・`POST /rag/senpai/synthesis` は `Environment=dev` かつ `true` のときだけ作成する（2026-10-20 に条件付き作成へ変更。本番に Bedrock・ChatLogs 権限を持つロールと経路を作らない）。
- 画面のボタンは `NEXT_PUBLIC_ENABLE_SENPAI_SYNTHESIS=true` のときだけ表示する（既定オフ）。Amplify の `mona` は push で自動ビルドされ画面だけ先に変わるため、SAM で有効化してから `amplify.yml` に追加して再ビルドする。保存済みのまとめは設定に関係なく表示する。
- 新規リソース: `SenpaiSynthesisLambdaRole`、`SenpaiSynthesisFunction`（`POST /rag/senpai/synthesis`、`RagApi` の Cognito 認可）。
- IAM は最小限: `BedrockModelId` への `bedrock:InvokeModel`（RAG と同じ ARN の組み立て）、ChatLogs への `GetItem` / `PutItem`、ユーザー GSI への `Query`。KB 検索や Scan の権限は持たない。
- 既存の `BedrockModelId` / `BedrockModelIdType` をそのまま使う。モデルの能力差は、`rag-function/model_profile.py` の主な項目を `synthesis_model.py` に最小限で写している（`MODEL_PROFILE_JSON` による上書きは未対応。未知のモデルは最小リクエスト）。
- フロントは `NEXT_PUBLIC_RAG_API_URL` に対して呼ぶ（既存設定のまま）。
- SAM をマージしても AWS には自動では入らない。有効にするまで追加費用は発生しない。

## 先送りしていること

- 非同期ジョブと利用回数の上限（`docs/design-2026-09-24-rag-two-modes.md`）。現状は1回の同期呼び出しで、同じターンは保存済みを返すため再生成されない。
- まとめの品質評価（事実の混入・出典の取り違えの確認）。
- 本番や管理者以外への公開、再生成ボタン、まとめへのフィードバック。

## 確認方法

- Python: `tests/unit/test_senpai_synthesis.py`（ゲート、検証、所有者分離、冪等、競合、入力上限、リクエスト形、ログ、SAM）、`tests/unit/test_senpai_history.py`（通常一覧に出ないこと、履歴詳細に含まれること）。
- フロント: `npm test`（`knowledge-senpai-synthesis` / `knowledge-senpai-chat` / `knowledge-senpai-history` / `knowledge-chat-entry`）、`npm run test:senpai`、`npm run typecheck`、`npm run lint`、`npm run build`。
- 実機確認（dev デプロイ後）: 両方成功したターン、片方だけ成功したターン、履歴から開き直したターンでボタン・表示・保存済みの再表示を見る。
