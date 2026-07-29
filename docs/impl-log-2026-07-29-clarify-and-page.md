# 実装ログ: 聞き返し + 頁候補 + 本命優先 retrieve（2026-07-29）

> **目的:** 「なぜこう直したか」を後から辿れるようにする。  
> **設計:** [design-2026-07-29-clarify-and-page.md](./design-2026-07-29-clarify-and-page.md)  
> **前提合意:** [decisions-2026-07-29-rag-nuance.md](./decisions-2026-07-29-rag-nuance.md)

---

## やったこと（コード）

| 変更 | なぜ |
|---|---|
| `needs_clarify` で症状＋機種なし → 検索前に聞き返し | 曖昧なまま検索→見当違い資料→作文が現場の最大不満。**図書番号は聞かない**（RAG の意味を壊すため） |
| `compose_search_query` で聞き返し後の追記を直前質問と結合 | 追記だけだと症状語が落ちて検索が外れる（design §4） |
| `is_weak_retrieval` をゲートとして使用（旧: 死コード） | 弱い根拠で長文を埋めない |
| `responseType` = `clarify` / `pages` / `not_found` | UI が候補・聞き返し・停止を分岐表示できる |
| `pageCandidates[]`（ページ無ければキー省略） | 成功定義＝該当頁到達。無いときは「ページ不明」と嘘をつかない |
| カテゴリ未指定時だけ本命（C/TI/据付基準）を先に retrieve、弱ければ全資料へ | 図が半分で埋もれやすい。**UI の全検索合意は維持**（ユーザー選択カテゴリは尊重）。メタは絞り込みであり本文 HYBRID は残る |
| Claude プロンプトを短い整理向けに変更 | 候補リストが本体、作文は補助 |
| DynamoDB に `responseType` / `pageCandidates` / `clarifyQuestions` を保存 | 履歴から意図を遡れる |
| フロントで候補を本文より上、clarify リスト表示 | 設計 §5 |

## 触ったファイル

- `lambda/rag/rag-function/app.py`
- `frontend/src/app/chat/page.tsx`
- `tests/unit/test_rag_clarify_and_pages.py`
- `docs/api/rag.md`
- `docs/design-2026-07-29-clarify-and-page.md`（状態更新）

## デプロイ注意

- フロント: `develop` マージ後 Amplify
- バックエンド: **RAG Lambda の `sam deploy` が必要**（push だけでは反映されない）
- ページ番号メタが KB に無い場合は候補に `pageNumber` が付かない（verify-checklist 参照）

## やっていない（意図的）

- 図書番号入力の主導線化
- トラブル画面
- GraphRAG / マルチエージェント
- カテゴリ未指定を UI 既定で本命固定（全検索のまま）
