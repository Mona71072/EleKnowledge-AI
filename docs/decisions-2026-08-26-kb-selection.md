---
status: reference
last-verified: 2026-08-27
related-code: infrastructure/sam/phase2-template.yaml, lambda/rag/rag-function/app.py
---

# 決定記録: 使用 Knowledge Base の選定（VQV81CNYU4 採用）2026-08-26

> **この文書の位置づけ:** Phase 2 RAG が参照する Bedrock Knowledge Base として **VQV81CNYU4 を正式採用**し、IaC 既定値（`phase2-template.yaml` の `KnowledgeBaseId`）を実環境と一致させた決定の記録。根拠となる実測はすべて 2026-08-26 の検証記録（下記「正本参照」）に依る（**2026-08-26 確認時点の実環境スナップショット**）。2026-08-26 時点の検証結果は検証記録を正とする。ただし KB / Data Source / Sync 状態 / S3資料 / metadata / デプロイ設定等の実環境が変更された場合は、影響する項目を再確認すること。

---

## 1. 決定

| 項目 | 決定内容 |
|---|---|
| 採用 KB | **`VQV81CNYU4`**（generative-ai-use-cases-jpinstd） |
| 不採用 KB | `DF9XUCSPDM`（generative-ai-use-cases-jp-inst-fmp）。**当面触らない** |
| IaC | `infrastructure/sam/phase2-template.yaml` の `KnowledgeBaseId` 既定値を `DF9XUCSPDM` → `VQV81CNYU4` に是正（本決定と同一 PR） |
| AWS への反映 | 実環境は既に VQV81CNYU4 で稼働中のため**挙動変更なし**。次回 `sam deploy` からパラメータ上書きが不要になるだけ |

---

## 2. VQV81CNYU4 を採用する理由

1. **現行運用の実態である。** `rag-dev` Lambda の実環境変数 `KNOWLEDGE_BASE_ID=VQV81CNYU4`、CloudFormation スタック `EleKnowledge-dev-phase2` のパラメータも `VQV81CNYU4`（テンプレ既定値 `DF9XUCSPDM` をデプロイ時に手動上書きしてきた）。既定値是正はこの乖離の解消であり、システム挙動は変わらない。
2. **Sync が新しい。** s3-data-source `KHPV3CNKOU` が `s3://ragknowledgebasestackinst-datasourcebucket9fa93e04-ybbhm1efhyzb/docs/`（3,745件）を標準 TEXT 抽出で索引。最終 Sync 2026-07-24 で、同日のメタデータ一括更新（2,566件）が反映済み。
3. **テキストチャンクで運用に耐える。** 標準 TEXT 抽出のため本文テキストが検索・引用に使える。フィルタ演算子（listContains 等）の実機挙動も VQV81CNYU4 に対して検証済み。

留意点: VQV81CNYU4 には quick-start（`A0XLFVSX3P`）/ web-crawler（`7NJIOJDD0Z`）データソースもあり、無関係な GenU 文書が混入しうる。アプリ側の category フィルタで遮断する方針（検証記録 §5.4）。

---

## 3. DF9XUCSPDM を不採用とする理由

- **MULTIMODAL パースで IMAGE チャンク多数。** 同じバケット・同じ `docs/` を `BEDROCK_FOUNDATION_MODEL`（Claude Sonnet 4.6 / MULTIMODAL）でパースしており、図表ページが本文なしの IMAGE チャンクになる。実クエリで上位10件中7件が IMAGE チャンクの事例を確認。現行アプリの画像添付上限（`MAX_IMAGE_BLOCKS = 3`）では肝心の文書画像が添付されず誤回答につながる。
- **2026-06-03 以降未 Sync。** 2026-07-24 のメタデータ一括更新が未反映。なお再 Sync してもパース設定起因の IMAGE チャンク問題は直らない（パース設定は作成後変更不可）。共有 KB のため Sync 実施は所有側の作業であり、未調整。
- **前提となるアプリ改修が未着手。** DF9XUCSPDM 活用の本命はアプリ側の画像添付ロジック改修（文書単位の画像選抜など）。それとセットで将来仕切り直す。

---

## 4. SSM パラメータについての注記

- SSM `/eleknowledge/dev/knowledge-base-id` は実環境に**存在しない**（ParameterNotFound。Runbook の「SSM にも書き込む」記載は実態と不一致）。
- テンプレには `KnowledgeBaseIdParameter`（AWS::SSM::Parameter）が定義されているが、実スタックに実体がない状態。テンプレからの削除 or 再作成の扱いは未決（検証記録 §7 の持ち越し事項）。本 PR では変更しない。

---

## 5. 再検討条件（DF9XUCSPDM の仕切り直し）

以下が**両方**そろった時点で再評価する:

1. アプリ側の画像添付ロジック改修（IMAGE チャンク主体の検索結果でも正しい文書の画像を添付できること）
2. DF9XUCSPDM 側の再 Sync（共有 KB のため所有側=共同管理部門との調整が前提）

それまで DF9XUCSPDM には一切手を入れない。

---

## 6. 正本参照

- [docs/verification-2026-08-26-kb-vqv-metadata.md](./verification-2026-08-26-kb-vqv-metadata.md) — 環境実値・両 KB のデータソース・Sync 状況・メタデータ全数調査の確定記録（**PR #55**）
- [docs/rag-model-filter-mapping-2026-08-26.md](./rag-model-filter-mapping-2026-08-26.md) — 機種フィルタ対応表（**PR #54**）

> **注記:** 上記 2 文書は本決定記録の作成時点で**未マージ**（PR #54 / #55 レビュー中）のため、develop 上ではリンク切れの可能性がある。マージ後に解消される。
