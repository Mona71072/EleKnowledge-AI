# 実装ログ: 聞き返し + 頁候補 + 本命優先 retrieve（2026-07-29）

> **目的:** 「なぜこう直したか」を後から辿れるようにする。  
> **設計:** [design-2026-07-29-clarify-and-page.md](./design-2026-07-29-clarify-and-page.md)  
> **前提合意:** [decisions-2026-07-29-rag-nuance.md](./decisions-2026-07-29-rag-nuance.md)（共同確認ブランチ）  
> **成功定義（訂正）:** 該当**資料**到達＋疑問解決。頁は副次（共同確認側 `decisions-2026-07-29-success-document-reach.md`）

---

## やったこと（コード）

| 変更 | なぜ |
|---|---|
| `needs_clarify` で症状＋機種なし → 検索前に聞き返し | 曖昧なまま検索→見当違い資料→作文が現場の最大不満。**図書番号は聞かない**（RAG の意味を壊すため） |
| `compose_search_query` で聞き返し後の追記を直前質問と結合 | 追記だけだと症状語が落ちて検索が外れる（design §4） |
| `is_weak_retrieval` をゲートとして使用（旧: 死コード） | 弱い根拠で長文を埋めない |
| `responseType` = `clarify` / `pages` / `not_found` | UI が候補・聞き返し・停止を分岐表示できる |
| `pageCandidates[]`（ページ無ければキー省略） | **資料候補が本体**。頁はメタがあれば付与（捏造しない）。成功必須ではない |
| カテゴリ未指定時だけ本命（C/TI/据付基準）を先に retrieve、弱ければ全資料へ | 図が半分で埋もれやすい。**UI の全検索合意は維持**（ユーザー選択カテゴリは尊重）。メタは絞り込みであり本文 HYBRID は残る |
| Claude プロンプトを短い整理向けに変更 | 候補リストが本体、作文は補助 |
| DynamoDB に `responseType` / `pageCandidates` / `clarifyQuestions` を保存 | 履歴から意図を遡れる |
| フロントで候補を本文より上、clarify リスト表示 | 設計 §5 |
| Claude messages の role 交互保証（refs+質問を最終 user に結合） | 連続 user で Bedrock ValidationException になるのを防ぐ |
| 追記結合クエリを Claude にも渡す | retrieve だけ結合だと整理が薄い |
| UI から到達不能カテゴリ（site_agent / quality_mgmt）を除外 | 選択すると常時弱／not_found |
| not_found 時にカテゴリ解除の誘導 | ユーザー指定カテゴリ過絞りの逃げ道 |
| feedback UpdateItem に Condition / 失敗一覧 Scan 後ソート / 履歴・お知らせのページング | 幽霊 message・取りこぼし・欠落を防ぐ |
| 予約公開は日時必須（UI+サーバ） | 空欄で即時公開に落ちる事故防止 |
| 弱ゲートでも低信頼 pageCandidates 最大2件 | 作文せず手がかりだけ残す（design §7） |
| needs_clarify: 症状語彙拡充・機種ありでも部位/状況不足時は聞き返し | design §4 の「手がかりが薄い」 |
| ABBREV_MAP 拡充・chat の debug console.log 削除 | 検索 recall / ノイズ削減 |
| `/chat?session=` でセッションを開く | failures → 会話確認の導線 |
| `useAdminGate` で admin 判定を共有 | layout と AdminOnlyGuard のずれ防止 |
| `mode=spec` を normal+本命カテゴリへ正規化 | UI 廃止後のデッドパス整理 |

## 触ったファイル

- `lambda/rag/rag-function/app.py`
- `frontend/src/app/chat/page.tsx`
- `tests/unit/test_rag_clarify_and_pages.py`
- `docs/api/rag.md`
- `docs/design-2026-07-29-clarify-and-page.md`（状態更新）

## デプロイ注意

- フロント: `develop` マージ後 Amplify
- バックエンド: **RAG Lambda の `sam deploy` が必要**（push だけでは反映されない）
- ページ番号メタが KB に無い場合は候補に `pageNumber` が付かない（verify-checklist 参照）。**資料到達の成功判定には頁メタは必須ではない**

## やっていない（意図的）

- 図書番号入力の主導線化
- トラブル画面
- GraphRAG / マルチエージェント
- カテゴリ未指定を UI 既定で本命固定（全検索のまま）
- `#page` ジャンプ／アプリ内 PDF ビューア（成功必須ではないため当面やらない）
