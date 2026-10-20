---
status: draft
last-verified: 2026-10-01
related-code:
  - lambda/rag/rag-function/app.py
  - lambda/rag/rag-function/kb_profile.py
  - lambda/chat/chat-management/app.py
  - lambda/chat-archive/app.py
  - lambda/metrics/aggregator/app.py
  - infrastructure/sam/phase2-template.yaml
  - infrastructure/sam/phase1-template.yaml
  - infrastructure/sam/chat-archive-template.yaml
  - frontend/src/app/chat/page.tsx
  - frontend/src/components/chat/ChatMessageFeedback.tsx
  - scripts/eval/run_retrieve_eval.py
  - scripts/eval/extract_user_questions.sql
---

# 調査: Know-how Knowledge Layer / Knowledge Flywheel の現行実装

> **調査日:** 2026-10-01
>
> **対象:** `origin/develop` @ `a80ad39`（PR #151 マージ後）
>
> **位置づけ:** 設計案 [design-2026-10-01-knowhow-flywheel.md](./design-2026-10-01-knowhow-flywheel.md) の根拠。ゼロから新システムを提案するための調査ではない。
>
> **方法:** リポジトリのコード・SAM・既存ドキュメント・open Issue/PR を読んだ。AWS コンソールの実値（本番の embedding / chunking / デプロイ済み環境変数）は未確認。Bedrock のメタデータ仕様のうち公式未照合の箇所は **要公式確認** と書いた。

この調査の目的は、現場経験・トラブル対応・暗黙知を継続蓄積する構想に対して、**いまの EleKnowledge に何があり、何が無いか** をファイル単位で示すことである。

---

## 1. 結論（調査側）

EleKnowledge は **「質問イベントを取る」「失敗を拾う」「資料へ届ける」「評価する」** 土台は揃っている。一方で **Know-how を置く場所、出典の種別、編集ライフサイクル** の 3 点は存在しない。

共有 KB `VQV81CNYU4` は据付チャットボットと共同利用しており（[decisions-2026-09-24-rag-two-modes.md](./decisions-2026-09-24-rag-two-modes.md) D4）、EleKnowledge 側から Sync してはいけない。Know-how をここに混ぜる案は、現行決定と矛盾する。

---

## 2. 現行アーキテクチャ（確認できた範囲）

```text
利用者
  → Amplify / Next.js（frontend/src）
  → API Gateway + Cognito JWT
      ├─ POST /rag/query          lambda/rag/rag-function/app.py
      │     → bedrock-agent-runtime Retrieve（HYBRID・30件）
      │     → 任意 Rerank / 任意検索語書き換え（どちらも既定 OFF）
      │     → 弱検索なら not_found（Claude を呼ばない）
      │     → bedrock-runtime InvokeModel（運用上 Sonnet 5。SAM 既定は Haiku 4.5）
      │     → ChatLogs（DynamoDB、TTL 60日）
      ├─ PUT /chat/messages/{id}/feedback   lambda/chat/chat-management
      ├─ GET /chat/admin/failures           同上（👎 と not_found）
      └─ GET /admin/metrics                 lambda/metrics/read
ChatLogs Stream
  → lambda/chat-archive → S3（無期限）→ Athena
```

通常 RAG は Bedrock Agent を使わない。Agent は Phase 3 トラブルシューティング（admin 限定）だけである。

### 2.1 フロント

| ルート | 役割 | ファイル |
|---|---|---|
| `/chat` | RAG チャット。頁候補・参考資料・👍👎 | `frontend/src/app/chat/page.tsx` |
| `/doc` | 引用 PDF の presign 中継 | `frontend/src/app/doc/page.tsx` |
| `/admin/failures` | 👎 / `not_found` / 改善要望 | `frontend/src/app/admin/failures/page.tsx` |
| `/admin/dashboard` | 日次 KPI | `frontend/src/app/admin/dashboard/page.tsx` |
| `/troubleshooting` | 診断（admin のみ） | `frontend/src/app/troubleshooting/page.tsx` |

フィードバック UI は `frontend/src/components/chat/ChatMessageFeedback.tsx`。good＝解けた、bad＝解けない。bad 理由は `wrong_doc` / `unresolved` / `bad_answer` / `other`。メッセージ状態としての `resolved` フラグは無い。

### 2.2 RAG 処理（`lambda/rag/rag-function/app.py`）

| 処理 | 関数 | 行（develop） | 備考 |
|---|---|---|---|
| KB ID | `KNOWLEDGE_BASE_ID` | L42 | 単一。SAM 既定 `VQV81CNYU4` |
| メタフィルタ | `build_kb_filter` | L603 | `category` と `model_type` のみ。`*` / `general` を OR |
| Retrieve | `query_knowledge_base` | L740 | `retrieve`。`retrieve_and_generate` は未使用 |
| 聞き返し | `needs_clarify` | L1088 | ルールベース。LLM ではない |
| 検索語書き換え | `maybe_rewrite_search_query` | L1002 | 実装済・既定 OFF |
| 通常検索 | `retrieve_for_normal_query` | L1160 | 1 回。本命優先 retrieve は停止中（issue #61） |
| リランク | `rerank_retrieval_results` | L819 | 実装済・既定 OFF。SAM `RerankModelArn` が空なら無効 |
| 弱停止 | `is_weak_retrieval` | L914 | top score < 0.22 または選別 0 件 |
| 頁候補 | `build_page_candidates` | L1180 | `.md` は除外（L1193） |
| 生成 | `system_prompt` | L1396 | 資料に書かれたことだけ。推測しない |
| 引用 | `extract_citations_from_selected` | L1642 | `.md` は除外（L1657）。正式 / 非公式の区別なし |
| 保存 | `save_message_to_dynamodb` | L550 | `responseType` / `sourceDocuments` / `pageCandidates` / `queryFilters` |

KB プロファイル（`kb_profile.py`）は配線済み。`query_policy.py` / `retrieval_policy.py` / `answer_policy.py` はパリティ用の未配線コピーである。本番経路は `app.py`。

### 2.3 Knowledge Base

| 項目 | 事実 | 出典 |
|---|---|---|
| 採用 KB | `VQV81CNYU4`（GenU スタック所有） | [decisions-2026-08-26-kb-selection.md](./decisions-2026-08-26-kb-selection.md) |
| 共同利用 | EleKnowledge と据付チャットボット | [decisions-2026-09-24-rag-two-modes.md](./decisions-2026-09-24-rag-two-modes.md) D4 |
| EleKnowledge の権限 | 読み取り専用。Sync 禁止 | [aws-migration-runbook.md](./aws-migration-runbook.md) |
| ベクトルストア | OpenSearch Serverless | [verification-2026-08-26-kb-vqv-metadata.md](./verification-2026-08-26-kb-vqv-metadata.md) |
| Embedding / chunking | **本リポジトリに実測なし** | — |
| 本命データソース | S3 `docs/` 配下の PDF 中心 | 同上 |
| メタデータ | `.metadata.json` サイドカー。キーは `category` / `model_type` / `filename` / `file_path` 等 | 同上 |
| 文書ライフサイクル | draft / published / deprecated **なし** | — |
| Markdown 資料 | 本命 KB に載っている実測は無い。アプリは `.md` を引用から除外する | `app.py` L1193, L1657 |

### 2.4 保存・分析

| ストア | キー / 保持 | 中身 | ファイル |
|---|---|---|---|
| ChatLogs | `sessionId` + `messageId`。TTL 60 日 | 質問・回答・引用・feedback・`responseType` | `infrastructure/sam/phase1-template.yaml` |
| S3 アーカイブ | 無期限（IA 60 日 / Glacier 180 日） | Stream の gzip JSONL。Athena 可 | `lambda/chat-archive/app.py` |
| metrics | 日次。TTL 約 400 日 | 質問数・セッション・👍👎・上位資料 | `lambda/metrics/aggregator/app.py` |
| announcements | `draft` / `scheduled` / `published` | お知らせ。KB ライフサイクルではない | `lambda/announcements/write/app.py` |
| users | `userId` | `role` は登録時 `user` 固定。admin 判定は Cognito グループ | `lambda/auth/signup/app.py` |
| sites / sessions | Phase 3 | 工事番号マスタと診断セッション。ノウハウ候補テーブルではない | `infrastructure/sam/phase3-template.yaml` |

Cognito に department / 専門領域のカスタム属性は無い（`phase1-template.yaml`）。キーマン Routing の材料はユーザー属性としては存在しない。

### 2.5 評価

- 第 1 層: `scripts/eval/run_retrieve_eval.py` + `tests/eval/golden_set.jsonl`
- v2 候補 24 問（ラベル待ち）: `tests/eval/golden_set_v2_candidates.jsonl`、手順 [eval-2026-09-25-golden-set-v2.md](./eval-2026-09-25-golden-set-v2.md)
- 実利用者質問の抽出: `scripts/eval/extract_user_questions.sql`（PR #151）
- 成功定義は **該当資料への到達と疑問解決**。頁到達は副次（[decisions-2026-07-29-success-document-reach.md](./decisions-2026-07-29-success-document-reach.md)）

---

## 3. 構想との対応表

判定は「コードまたは稼働中の仕様で再現できるか」だけを見る。設計ドキュメントだけのものは部分対応にしない。

| 構想 | 判定 | 根拠 |
|---|---|---|
| メタデータで母集団を絞る | 完全対応 | `build_kb_filter` |
| HYBRID 検索 | 完全対応 | `RAG_SEARCH_TYPE` 既定 HYBRID |
| リランク | 部分対応 | コードあり・既定 OFF |
| 引用・PDF 到達 | 部分対応 | 頁候補と参考資料はある。正式 / Know-how の区別なし。`.md` 除外 |
| 弱い検索で止める・聞き返す | 完全対応 | `is_weak_retrieval` / `needs_clarify` |
| Knowledge Event の保存 | 部分対応 | ChatLogs とアーカイブ。検索トレース・言い換え記録は未実装（設計: [design-2026-09-10-retrieval-trace.md](./design-2026-09-10-retrieval-trace.md)、PR #111） |
| Gap 検知の材料 | 部分対応 | `not_found`・👎理由・Athena。クラスタ化・週次レポートは無い |
| 候補の状態管理 | 未対応 | 近いのはお知らせの draft/scheduled/published だけ |
| Know-how の保存先・公開経路 | 未対応 | 自前 KB なし。Sync 権限なし |
| キーマン Routing | 未対応 | 部署・専門のユーザー属性なし |
| 安全系の必須レビュー | 未対応 | — |
| 資料ごとのアクセス制御 | 未対応 | ログイン済みなら全資料 |
| Knowledge Curator Agent | 未対応 | 通常 RAG に Agent 構成なし |
| KPI（解決率・再利用） | 部分対応 | 質問数・👍率・上位資料は取れる。再検索率・資料クリック・Know-how 再利用は取れない（クリックは PR #111 で設計） |
| Official と Know-how の区別 | 未対応 | プロンプトも API も種別を持たない |
| Markdown を Canonical にする仕組み | 未対応 | — |
| Git 上の Knowledge 版管理 | 未対応 | アプリコードの Git 運用はある。Knowledge 資産用ではない |
| OneNote / Obsidian 連携 | 未対応 | リポジトリにヒットなし |
| ユーザー寄稿 UI | 未対応 | `product_wish` はあるが KB 取り込みは無い |

法令 RAG は別経路の先例である（PR #155 設計、PR #156 取込基盤。いずれも draft）。専用 S3・専用 KB・既存メタデータ非変更・通常 RAG への混入防止を採っている。Know-how でも同じ分離型が流用できる。

---

## 4. Knowledge Event として今使えるもの

| Event | 保存先 | 使えるか |
|---|---|---|
| ユーザー質問 | ChatLogs `role=user` | 使える |
| 回答 | ChatLogs `role=assistant` | 使える |
| 聞き返し | `responseType=clarify` | 使える |
| ゼロ結果 / 弱検索 | `responseType=not_found` | 使える |
| 検索フィルタ | `queryFilters` | 使える |
| 返した資料 | `sourceDocuments` / `pageCandidates` | 使える（retrieve 生ログではない） |
| 👍👎 | `feedback` / `feedbackReason` | 使える |
| 資料を実際に開いたか | — | **現状なし**（PR #111 の `document_open`） |
| 検索語の書き換え | — | **現状なし**（PR #111 の `reformulation`） |
| retrieve スコア一式 | — | **現状なし**（検索トレース設計） |
| 現場トラブル一連 | Phase 3 sessions | admin 限定・件数不明。入口としては弱い |
| キーマンとのやり取り | — | 無い |
| 正式資料の更新イベント | — | 所有側。EleKnowledge は検知できない |

ギャップ検知は、いまでも Athena 上で `not_found` と 👎 を週次集計すれば粗い検出ができる。クラスタ化は Athena 結果を LLM に渡すバッチで足り、専用基盤は不要である。精度を上げるなら検索トレースと言い換え記録を先に入れる（既存の未マージ実装がある）。

---

## 5. 既存の改善ループ（Flywheel の原型）

すでに動いている、または設計済みのループ:

```text
利用者の 👍👎 / not_found
  → /admin/failures
  → 人が golden set へコピー
  → scripts/eval/run_retrieve_eval.py
  → しきい値・フィルタ等の PR
```

正本: [design-2026-07-29-improvement-proposals.md](./design-2026-07-29-improvement-proposals.md)、[decisions-2026-07-29-layer1-eval-ops.md](./decisions-2026-07-29-layer1-eval-ops.md)。

v0 で **しない** と決めたこと: LLM 自動起票、Notion/Slack 連携、自動 PR/deploy、現場向け提案表示。Know-how 候補の自動作成は、この決定の見直しを含む。

---

## 6. 他アプリ・共有 KB への影響

- Phase 2 の KB は **据付チャットボットと共同利用**（D4）。メタデータキー追加・データソース追加・Sync は相手に影響する。
- 同一 S3 `docs/` を読む別 KB `DF9XUCSPDM` もある（不採用）。
- アカウント上に markdown 専用 KB 名（`rag-data-source-for-mai-box-inst-markdown`）があるが、Phase 2 採用 KB ではない。
- Phase 3 は別 KB ID パラメータ（TroubleCases / Manuals / C materials）。通常 RAG の共有 KB をフィルタで切る設計ではない。
- 問題点の蓄積先は [kb-change-requests.md](./kb-change-requests.md)。所有部門へは未連絡（実例を貯めてからまとめて伝える方針）。

Know-how を共有 KB に足すと、据付チャットボットの検索結果に現場知見が混ざる。これは D4 と、正式資料を改変対象にしない構想の両方に反する。

---

## 7. 未マージで関係するもの

実装・設計として既に進んでいるもの。Know-how 層より先、または並行で載せた方がよい。

| # | 内容 | Know-how との関係 |
|---|---|---|
| PR #111 / issue #147 | 構造化ログ・資料クリック・言い換え | Gap 検知の材料 |
| PR #114 | failures v2（期間・振り分け） | Loop A の作業場 |
| PR #110 / #104 | metrics v2 | 未回答率などの KPI |
| `feature/retrieval-trace` | 検索トレースを ChatLogs へ | Event の中身 |
| PR #155 / #156 | 法令専用 KB | 専用 KB 分離の先例 |
| issue #86 | 監視・改善ループの棚卸し | 親課題 |
| issue #53 / #19 | KB 所有側への修正依頼 | Official 側。Know-how とは別 |

---

## 8. 設計上のリスク（現状で既にあるもの）

| リスク | 現状 |
|---|---|
| Official / Know-how 混在 | 種別が無い。混ぜるとプロンプトだけでは防げない |
| 古い Knowledge | `last_validated` も承認者も無い |
| Metadata schema drift | 共有 KB は `category` / `model_type` 固定。新キーは所有側案件 |
| `.md` 除外 | Know-how を Markdown で入れると、今のコードでは引用されない |
| Access control leakage | 資料単位 ACL が無い。全社員公開が前提 |
| 個人名・現場固有情報 | 取り込み時の検査が無い |
| Prompt injection | プロンプトに「資料内の指示に従わない」はある。KB 汚染の専用対策は無い |
| Git と KB の不一致 | アプリは KB を所有していない。削除残存は所有側運用 |
| 誰が承認したか | 無い |
| 他アプリへの破壊的変更 | 共有 KB を触ると発生する。触らなければ回避できる |

---

## 9. 本調査で分からないこと

1. 本番 `VQV81CNYU4` の embedding モデルと chunking 戦略
2. 実デプロイの `RerankModelArn` / `QueryRewriteModelId` / `BedrockModelId`
3. Phase 3 の 3 KB ID が本番で有効か
4. キーマンが GitHub を日常的に使えるか（コードからは不明）
5. Bedrock が YAML frontmatter をメタデータとして読むか（**要公式確認**。現行運用は `.metadata.json` サイドカー）
6. メタデータ属性が本文 HYBRID のキーワード側に効くか（**要公式確認**。現行の理解では本文チャンクが検索対象）
